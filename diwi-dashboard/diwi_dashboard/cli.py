import click

from . import dashboard_app


@click.command()
@click.option("--gs-path", envvar="DASHBOARD_GS_PATH")
@click.option("--dashboard-path", default="/", envvar="DASHBOARD_PATH")
@click.option(
    "--auth-group",
    multiple=True,
    envvar="DASHBOARD_AUTH_GROUP",
    help="Google auth groups, separated by : if in envvar",
)
def dashboard_run_cli(dashboard_path, gs_path, auth_group):
    dashboard_app.run(dashboard_path, gs_path, auth_group)


def main():
    dashboard_run_cli(auto_envvar_prefix="DIWI")


if __name__ == "__main__":
    main()
