from pathlib import Path
import pprint
import click

from .config import Config
from . import utils
from .adb import ADB


@click.group()
@click.option(
    "--config",
    type=click.Path(path_type=Path, dir_okay=False, readable=True),
    default="./config.yml",
)
@click.option("--device", multiple=True, type=str)
@click.option(
    "--adb",
    default="adb",
)
@click.pass_context
def cli(ctx, config, adb, device):
    ADB.set_adb_executable(adb)
    if device:
        print("only connecting to devices:", device)
    ctx.obj = {"config": Config(config), "devices": device}


@cli.command("register")
@click.option("--port", type=int, default=5555)
@click.argument("name", type=str)
@click.pass_context
def register_cli(ctx, name, port):
    config = ADB.register(name, port)
    print(f"Extracted config for {name}:")
    pprint.pprint(config, indent=4)
    input("Press enter to save config")
    try:
        ctx.obj["config"]["devices"].append(config)
    except (KeyError, AttributeError):
        ctx.obj["config"]["devices"] = [config]
    ctx.obj["config"].save()


@cli.command("update-whatsapp")
@click.option(
    "--package-location",
    required=None,
    type=click.Path(path_type=Path, dir_okay=False, readable=True),
)
@click.option(
    "--archive",
    default=Path("./data/package-archive/"),
    type=click.Path(path_type=Path, file_okay=False, readable=True),
)
@click.pass_context
def update_whatsapp_cli(ctx, archive, package_location):
    config = ctx.obj["config"]
    devices = ctx.obj["devices"]
    if not package_location:
        package_location = utils.get_whatsapp(archive)
    for device_config in config["devices"]:
        if not devices or device_config["name"] in devices:
            device = ADB.from_config(device_config, interactive=True)
            device.install_package(package_location)
            device.run_app("com.whatsapp")


@cli.command("clean-media")
@click.option("--max-days", type=int, default=30)
@click.option("--no-interactive", type=bool, default=False, is_flag=True)
@click.pass_context
def clean_media_cli(ctx, max_days, no_interactive):
    config = ctx.obj["config"]
    devices = ctx.obj["devices"]
    for device_config in config["devices"]:
        if not devices or device_config["name"] in devices:
            device = ADB.from_config(device_config, interactive=True)
            if not (media_path := device_config.get("whatsapp_dir")):
                media_path = device.get_whatsapp_media_dir()
            device.clean_directory(media_path, max_days, interactive=not no_interactive)


@cli.command("maintenance")
@click.pass_context
def maintenance_cli(ctx):
    config = ctx.obj["config"]
    devices = ctx.obj["devices"]
    package_location = utils.get_whatsapp(Path("./data/package-archive"))
    for device_config in config["devices"]:
        if not devices or device_config["name"] in devices:
            device = ADB.from_config(device_config, interactive=True)
            print("Updating WhatsApp")
            device.install_package(package_location)
            device.run_app("com.whatsapp")
            print("Cleaning old media")
            if not (media_path := device_config.get("whatsapp_dir")):
                media_path = device.get_whatsapp_media_dir()
            device.clean_directory(media_path, 30, interactive=False)


if __name__ == "__main__":
    cli()
