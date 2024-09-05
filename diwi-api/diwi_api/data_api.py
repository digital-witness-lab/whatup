from aiohttp import web

from .lib import authorization
from .lib import bucket_proxy


@authorization.authorized()
@bucket_proxy.bucket_proxy("gs://dashboard.digitalwitnesslab.org/")
async def dashboard(request: authorization.AuthorizedRequest):
    pass


def run(*args, **kwargs):
    data_app = web.Application()
    authorization.init(data_app)

    bucket_proxy.register_bucket_proxy(
        data_app,
        "/dashboard",
        dashboard,
    )

    print("Starting Data API")
    web.run_app(data_app, *args, **kwargs)
