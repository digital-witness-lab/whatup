from functools import wraps
from typing import List, cast
from dataclasses import dataclass
import urllib.parse

import aiohttp
from yarl import URL
from aiohttp import web
from oauthlib.oauth2 import WebApplicationClient
from google.oauth2 import credentials as google_credentials
import google.auth
import googleapiclient.discovery
from datetime import timedelta, datetime, timezone
import json
import jwt
import os

# JWT configuration
JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 48 * 60 * 60  # 48 hours

# OAuth2 client configuration
if "GOOGLE_AUTH_DATA" in os.environ:
    google_creds = json.loads(os.environ["GOOGLE_AUTH_DATA"])
else:
    GOOGLE_AUTH_FILE = os.environ["GOOGLE_AUTH_FILE"]
    with open(GOOGLE_AUTH_FILE, "r") as f:
        google_creds = json.load(f)

# Extract the client ID and client secret
GOOGLE_CLIENT_ID = google_creds["web"]["client_id"]
GOOGLE_CLIENT_SECRET = google_creds["web"]["client_secret"]

GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
client = WebApplicationClient(GOOGLE_CLIENT_ID)


AuthGroupType = List[str] | str


def url_for_absolute(request: web.Request, name: str) -> URL:
    relative_url = request.app.router[name].url_for()
    return request.url.join(relative_url)


@dataclass
class User:
    email: str
    name: str
    picture: str
    groups: List[str]


class AuthorizedRequest(web.Request):
    user: User

    @classmethod
    def authorize_request(cls, request: web.Request, user: User):
        arequest = cast(AuthorizedRequest, request)
        arequest.user = user
        return arequest


def create_redirect(request: web.Request, reason=None):
    redirect_to = str(request.rel_url)
    path = request.app.router["login"].url_for().with_query({"redirect": redirect_to})
    return web.HTTPTemporaryRedirect(path, reason=reason)


def authorized(
    authorized_groups: AuthGroupType,
    redirect: bool = False,
):
    if not authorized_groups:
        raise ValueError("Authorized decorator must have non-empty authorization group")
    if isinstance(authorized_groups, str):
        authorized_groups = authorized_groups.split(",")
    groups = set(authorized_groups)

    def _(fxn):
        @wraps(fxn)
        async def __(request: web.Request):
            token = request.cookies.get("access_token")

            if not token:
                if redirect:
                    raise create_redirect(request, reason="Unauthorized")
                return web.json_response({"error": "Unauthorized"}, status=401)

            try:
                payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            except jwt.ExpiredSignatureError:
                if redirect:
                    raise create_redirect(request, reason="Token Expired")
                return web.json_response({"error": "Token expired"}, status=401)
            except jwt.InvalidTokenError:
                if redirect:
                    raise create_redirect(request, reason="Invalid Token")
                return web.json_response({"error": "Invalid token"}, status=401)

            if not groups.intersection(payload["groups"]):
                return web.json_response({"error": "User not authorized"}, status=403)

            user = User(
                email=payload["email"],
                name=payload["name"],
                picture=payload["picture"],
                groups=payload["groups"],
            )
            arequest = AuthorizedRequest.authorize_request(request, user)
            return await fxn(arequest)

        return __

    return _


async def get_google_provider_cfg():
    async with aiohttp.ClientSession() as session:
        async with session.get(GOOGLE_DISCOVERY_URL) as response:
            return await response.json()


async def login(request):
    google_provider_cfg = await get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    redirect = request.query.get("redirect", "/")

    redirect_url = url_for_absolute(request, "callback")
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=str(redirect_url),
        scope=[
            "openid",
            "email",
            "profile",
            "https://www.googleapis.com/auth/cloud-identity.groups.readonly",
        ],
        state=urllib.parse.urlencode({"redirect": redirect}),
    )
    return web.HTTPFound(location=request_uri)


async def callback(request):
    code = request.query.get("code")
    state = request.query.get("state")

    google_provider_cfg = await get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    redirect_url = url_for_absolute(request, "callback")
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=str(request.url),
        redirect_url=str(redirect_url),
        code=code,
    )

    async with aiohttp.ClientSession() as session:
        async with session.post(
            token_url,
            headers=headers,
            data=body,
            auth=aiohttp.BasicAuth(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        ) as token_response:
            token_response_data = await token_response.json()

    try:
        client.parse_request_body_response(json.dumps(token_response_data))
    except Exception as e:
        return web.json_response(
            {"invalid_oauth_response": token_response_data, "error": str(e)}, status=401
        )

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)

    async with aiohttp.ClientSession() as session:
        async with session.get(uri, headers=headers, data=body) as userinfo_response:
            userinfo = await userinfo_response.json()

    if not userinfo.get("email_verified"):
        return web.json_response(
            {"error": "User email not verified by Google"}, status=400
        )

    user_groups = await get_user_groups(userinfo["email"])
    if not user_groups:
        return web.json_response(
            {"error": "User has no possible authorizations"}, status=403
        )

    exp = datetime.now(tz=timezone.utc) + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    access_token = jwt.encode(
        {
            "email": userinfo["email"],
            "name": userinfo["given_name"],
            "picture": userinfo["picture"],
            "groups": list(user_groups),
            "exp": exp,
        },
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )

    state_params = urllib.parse.parse_qs(state)
    redirect_url = state_params.get("redirect", ["/"])[0]
    response = web.HTTPFound(location=redirect_url)
    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=True,
        max_age=JWT_EXP_DELTA_SECONDS,
    )
    return response


async def logout(_: web.Request):
    response = web.json_response({"msg": "Logout successful"})
    response.del_cookie("access_token")
    return response


async def get_user_groups(user_email):
    # Use the application default credentials (e.g., for Cloud Run, GKE)
    credentials, project = google.auth.default()

    # Build the Cloud Identity API service
    service = googleapiclient.discovery.build(
        "cloudidentity", "v1", credentials=credentials
    )

    groups = []
    page_token = None

    try:
        while True:
            # Make the request to get the groups for the member email
            response = (
                service.groups()
                .memberships()
                .list(
                    parent="groups/-",
                    query=f'member_key_id == "{user_email}"',
                    pageToken=page_token,  # pass the page token for pagination
                )
                .execute()
            )

            # Extract group memberships from the response
            memberships = response.get("memberships", [])
            groups.extend([group["groupKey"]["id"] for group in memberships])

            # Check if there is another page
            page_token = response.get("nextPageToken")
            if not page_token:
                break  # Exit loop if there are no more pages

        return groups

    except Exception as e:
        print(f"Error fetching groups for {email}: {str(e)}")
        return []


def init(app: web.Application, login_path="/login") -> web.Application:
    app.router.add_get(login_path, login, name="login")
    app.router.add_get("/callback", callback, name="callback")
    app.router.add_get("/logout", logout, name="logout")
    return app
