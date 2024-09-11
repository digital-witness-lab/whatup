from typing import cast

from aiohttp import web
from aiohttp.typedefs import Handler

from . import authorization
from . import bucket_proxy


def add_dashboard(
    app: web.Application,
    path: str,
    gs_path: str,
    auth_group: authorization.AuthGroupType,
):

    @authorization.authorized(auth_group, redirect=True)
    @bucket_proxy.bucket_proxy(gs_path)
    async def dashboard(_: authorization.AuthorizedRequest):
        pass

    bucket_proxy.register_bucket_proxy(
        app,
        path,
        cast(Handler, dashboard),
    )

    return app
