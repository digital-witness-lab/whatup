import click

from . import data_api


@click.group()
def cli():
    return


@cli.command("data-api")
def dataapi_cli():
    data_api.run()


if __name__ == "__main__":
    cli()
