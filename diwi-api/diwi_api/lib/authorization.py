from functools import wraps
from typing import List
from dataclasses import dataclass

import aiohttp
from aiohttp import web
from oauthlib.oauth2 import WebApplicationClient
from google.oauth2 import credentials as google_credentials
import google_auth_oauthlib.flow
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
GOOGLE_AUTH_FILE = os.environ["GOOGLE_AUTH_FILE"]
with open(GOOGLE_AUTH_FILE, "r") as f:
    google_creds = json.load(f)

# Extract the client ID and client secret
GOOGLE_CLIENT_ID = google_creds["web"]["client_id"]
GOOGLE_CLIENT_SECRET = google_creds["web"]["client_secret"]

GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
GOOGLE_AUTH_GROUP_DEFAULT = os.environ["GOOGLE_AUTH_GROUP_DEFAULT"]
client = WebApplicationClient(GOOGLE_CLIENT_ID)


@dataclass
class User:
    email: str
    name: str
    picture: str
    groups: List[str]


class AuthorizedRequest(web.BaseRequest):
    user: User


def authorized(authorized_groups: List[str] | str = GOOGLE_AUTH_GROUP_DEFAULT):
    if isinstance(authorized_groups, str):
        authorized_groups = authorized_groups.split(",")
    groups = set(authorized_groups)

    def _(fxn):
        @wraps(fxn)
        async def __(request: web.BaseRequest):
            token = request.cookies.get("access_token")

            if not token:
                return web.json_response({"error": "Unauthorized"}, status=401)

            try:
                payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            except jwt.ExpiredSignatureError:
                return web.json_response({"error": "Token expired"}, status=401)
            except jwt.InvalidTokenError:
                return web.json_response({"error": "Invalid token"}, status=401)

            print(payload)
            print(groups)
            if not groups.intersection(payload["groups"]):
                return web.json_response({"error": "User not authorized"}, status=403)

            user = User(
                email=payload["email"],
                name=payload["name"],
                picture=payload["picture"],
                groups=payload["groups"],
            )
            request.user = user
            return await fxn(request)

        return __

    return _


async def get_google_provider_cfg():
    async with aiohttp.ClientSession() as session:
        async with session.get(GOOGLE_DISCOVERY_URL) as response:
            return await response.json()


async def login(request):
    google_provider_cfg = await get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=str(request.url.with_path("/callback")),
        scope=[
            "openid",
            "email",
            "profile",
            "https://www.googleapis.com/auth/admin.directory.group.readonly",
        ],
    )
    return web.HTTPFound(location=request_uri)


async def callback(request):
    code = request.query.get("code")

    google_provider_cfg = await get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=str(request.url),
        redirect_url=str(request.url.with_path("/callback")),
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

    client.parse_request_body_response(json.dumps(token_response_data))

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)

    async with aiohttp.ClientSession() as session:
        async with session.get(uri, headers=headers, data=body) as userinfo_response:
            userinfo = await userinfo_response.json()

    if not userinfo.get("email_verified"):
        return web.json_response(
            {"error": "User email not verified by Google"}, status=400
        )

    user_groups = await get_user_groups(userinfo["email"], token_response_data)
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

    response = web.HTTPFound(location="/dashboard")
    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=True,
        max_age=JWT_EXP_DELTA_SECONDS,
    )
    return response


async def logout(request):
    response = web.json_response({"msg": "Logout successful"})
    response.del_cookie("access_token")
    return response


async def get_user_groups(
    user_email, token_response_data, domain="digitalwitnesslab.org"
):
    """
    Retrieves all groups that the user is a member of within the specified domain.

    :param user_email: The email of the user whose groups are being fetched.
    :param token_response_data: The token data obtained after user authentication.
    :param domain: The domain within which to look for groups (default is "digitalwitnesslab.org").
    :return: A list of group names that the user is a member of within the specified domain.
    """
    creds = google_credentials.Credentials(token_response_data["access_token"])
    service = googleapiclient.discovery.build(
        "admin", "directory_v1", credentials=creds
    )

    user_groups = []
    page_token = None

    try:
        # Iterate over all groups in the domain
        while True:
            results = (
                service.groups()
                .list(domain=domain, userKey=user_email, pageToken=page_token)
                .execute()
            )
            groups = results.get("groups", [])

            for group in groups:
                user_groups.append(group["email"])

            page_token = results.get("nextPageToken", None)
            if not page_token:
                break

    except Exception as e:
        print(f"Error fetching user groups: {e}")
        return []

    return user_groups


def init(app: web.Application) -> web.Application:
    app.router.add_get("/login", login)
    app.router.add_get("/callback", callback)
    app.router.add_get("/logout", logout)
