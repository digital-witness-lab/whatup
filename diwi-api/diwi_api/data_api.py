from aiohttp import web

from .lib import dashboard
from .lib import authorization


def run(dashboard_path, gs_path, auth_group, *args, **kwargs):
    data_app = web.Application()

    authorization.init(data_app)
    dashboard.add_dashboard(
        data_app,
        dashboard_path,
        gs_path,
        auth_group,
    )

    print("Starting Data API")
    web.run_app(data_app, *args, **kwargs)
