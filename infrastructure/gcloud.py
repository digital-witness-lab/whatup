import json
from functools import cache

import google.auth.transport.requests
import requests
from pulumi import Output
from pulumi_gcp import projects


@cache
def get_current_user_email() -> str:
    credentials, _ = google.auth.default()
    credentials.refresh(google.auth.transport.requests.Request())
    if credentials.id_token is None:  # type: ignore
        raise Exception(
            "Could not get id_token from default credentials chain"
        )
    response = requests.get(
        "https://www.googleapis.com/oauth2/v1/tokeninfo?id_token="
        + credentials.id_token  # type: ignore
    )
    token_info = json.loads(response.text)
    return token_info["email"]


@cache
def get_project_number(project) -> Output[int]:
    proj = projects.get_project_output(filter=f"id:{project}")
    return proj.apply(lambda p: p.projects[0].number)
