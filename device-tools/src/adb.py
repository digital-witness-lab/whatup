from pathlib import Path
from packaging.version import Version
import ipaddress
import re
import time

from . import utils

ADB_PATH = "adb"


def adb_command(cmd) -> str:
    full_command = f"{ADB_PATH} {cmd}"
    print(f"Running: {full_command}")
    response = utils.run_command(full_command)
    print(f"Got response: {response}")
    return response


class ADB:
    def __init__(self, name):
        self.name = name
        self.devices_identifier = None

    def connect_network(self, host: str, port: int):
        assert isinstance(port, int)
        assert ipaddress.IPv4Address(host)
        self.devices_identifier = f"{host}:{port}"
        response = adb_command(f"connect {host}:{port}")
        if "connected" not in response:
            raise ConnectionRefusedError(
                f"Could not connect to host: {self.name}: {host}:{port}"
            )

    def connect_usb(self, device_name, interactive=False):
        self.devices_identifier = device_name
        if interactive:
            print(f"Please plug in device {self.name}:{device_name}")
        while True:
            if not self.is_connected():
                if not interactive:
                    raise EnvironmentError(
                        f"Device not connected: {self.name}: {device_name}"
                    )
            else:
                if interactive:
                    print("Device connected")
                return
            time.sleep(1)

    def update_whatsapp(self, version, apk):
        current_version = self.get_package_version("com.whatsapp")
        if current_version < version:
            print(f"Updating WhatsApp: {current_version} < {version}")
            self.install_package(apk)
        else:
            print(f"WhatsApp already at newest version: {current_version}")
            return
        self.run_app("com.whatsapp")

    def is_connected(self) -> bool:
        devices = self.connected_devices()
        if len(devices) == 1 and devices[0] == self.devices_identifier:
            return True
        return False

    def get_package_version(self, package) -> Version:
        if not self.is_connected():
            raise ValueError("Must connect to device")
        response = adb_command(f"shell dumpsys package '{package}'")
        version = re.findall("versionName=([1-9\.]+)", response, re.MULTILINE)
        print(f"Found version: {version}")
        if len(version) != 1:
            raise ValueError(f"Could not find package version: {package}: {version}")
        return Version(version[0])

    def install_package(self, path: Path):
        if not self.is_connected():
            raise ValueError("Must connect to device")
        response = adb_command(f"install -d -r '{path.absolute()}'")
        if "Success" not in response:
            raise ValueError(f"Did not sucessfully install package: {response}")

    def clean_directory(self, path: Path, max_days=14, max_mb=24, interactive=False):
        assert max_days or max_mb
        conditions = []
        if max_days:
            conditions.append(f"-mtime +{max_days}")
        if max_mb:
            conditions.append(f"-size +{max_mb}M")
        condition = " -or ".join(conditions)
        find_cmd = f"""find "{path}" -type f -and \\( {condition} \\)"""
        if interactive:
            files = adb_command(f"shell '{find_cmd}'").split("\n")
            if not files:
                return
            print("\t" + "\n\t".join(files))
            resp = (
                input(
                    f"Going to delete the above files ({len(files)}). Input [Y] to continue, [N] to skip or [Q] to raise an exception> "
                )
                .strip()
                .lower()
            )
            match resp:
                case "n":
                    return
                case "q":
                    raise KeyboardInterrupt
        files = adb_command(f"shell '{find_cmd} -delete'").split("\n")
        print(f"Deleted {len(files)} files older than {max_days} days")

    def run_app(self, app_name):
        if not self.is_connected():
            raise ValueError("Must connect to device")
        adb_command(f"shell am start -n '{app_name}/{app_name}.Main'")

    @classmethod
    def from_config(cls, config, interactive=False):
        cls.disconnect()
        device = cls(config["name"])
        if config["type"] == "network":
            device.connect_network(config["host"], config.get("port", 5555))
        elif config["type"] == "usb":
            device.connect_usb(config["device"], interactive=interactive)
        return device

    @classmethod
    def register(cls, name, port=5555):
        config = {"name": name}
        devices = cls.connected_devices()
        if len(devices) > 1:
            raise EnvironmentError(
                "Only one device can be connected durring registration"
            )
        elif len(devices) == 0:
            raise EnvironmentError("Device not found in `adb devices`")
        config["device"] = devices[0]
        version = cls.get_android_version()
        if version.major < 11:
            config["type"] = "usb"
        else:
            config["port"] = port
            config["type"] = "network"
            config["host"] = cls.get_ip_address()
            adb_command(f"tcpip {port}")
            time.sleep(2)
            cls.connected_devices()  # this effectively waits for the above TCPIP command to complete
        config["whatsapp_dir"] = str(cls.get_whatsapp_media_dir())
        return config

    @classmethod
    def get_whatsapp_media_dir(cls):
        video_dir = adb_command(
            """shell 'find -L /storage/ -type d -name "WhatsApp Video" 2> /dev/null' | head -n 1"""
        )
        if not video_dir:
            raise ValueError(f"Could not find WhatsApp media directory: {video_dir}")
        return Path(video_dir).parent

    @classmethod
    def connected_devices(cls):
        response = adb_command("devices")
        return re.findall("^([^ ]+)\s+device$", response, re.MULTILINE)

    @classmethod
    def disconnect(cls):
        adb_command("disconnect")
        time.sleep(2)

    @classmethod
    def get_android_version(cls) -> Version:
        try:
            version = Version(
                adb_command("shell getprop ro.build.version.release").strip()
            )
        except (ValueError, TypeError) as e:
            print(f"Could not get version info: {e}")
            version = Version("0.0.0")
        return version

    @classmethod
    def get_ip_address(cls):
        response = adb_command("shell ip addr show wlan0")
        ipaddresses = re.findall(
            r"inet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", response, re.MULTILINE
        )
        if not ipaddresses:
            raise EnvironmentError(f"Could not extract IP address: {response}")
        return ipaddresses[0]

    @staticmethod
    def set_adb_executable(path):
        global ADB_PATH
        ADB_PATH = path
