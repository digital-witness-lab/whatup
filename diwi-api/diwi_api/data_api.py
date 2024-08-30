from aiohttp import web

from .lib import authorization


@authorization.authorized
async def dashboard(request: web.BaseRequest, user: authorization.User):
    return web.json_response({"logged_in_as": user.email, "name": user.name})


def run(*args, **kwargs):
    data_app = web.Application()
    authorization.init(data_app)

    data_app.router.add_get("/dashboard", dashboard)

    print("Starting Data API")
    web.run_app(data_app, *args, **kwargs)
