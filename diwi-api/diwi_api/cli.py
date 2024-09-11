import click

from . import data_api


@click.group()
def cli():
    return


@cli.command("data-api")
@click.option("--gs-path", required=True)
@click.option("--dasbhoard-path", default="/")
@click.option(
    "--auth-group",
    multiple=True,
    help="Google auth groups, separated by : if in envvar",
)
def dataapi_cli(dashboard_path, gs_path, auth_group):
    data_api.run(dashboard_path, gs_path, auth_group)


if __name__ == "__main__":
    cli(auto_envvar_prefix="DIWI_API")
