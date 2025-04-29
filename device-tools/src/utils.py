import subprocess
import shlex
from pathlib import Path
import html
from datetime import datetime
import hashlib
import re
import tempfile
from packaging.version import Version

import requests


def get_whatsapp(archive: Path):
    with requests.Session() as session:
        download_page = session.get("https://www.whatsapp.com/android/")
        download_link = re.findall(
            r'href="(https[^"]+WhatsApp.apk[^"]+)"', download_page.text
        )
        if len(download_link) != 1:
            raise ValueError(
                f"Could not extract one download link from whatsapp: {download_link}"
            )
        download_link_decoded = html.unescape(download_link[0])
        print(f"Found download link at: {download_link_decoded}")
        data = session.get(download_link_decoded, allow_redirects=True)
        if data.status_code != 200:
            raise ValueError(
                f"Got non 200 response code from WhatsApp download: {data.text}"
            )
    with tempfile.NamedTemporaryFile("wb+") as tfd:
        tfd.write(data.content)
        version = get_apk_version(tfd.name)

        candidate = archive / "packages" / f"WhatsApp-{version}.apk"
        if candidate.exists():
            print(f"Using existing WhatsApp apk: {version}")
            return version, candidate

        print(f"Found new WhatsApp version: {version}")
        tfd.seek(0)
        candidate.write_bytes(tfd.read())
        return version, candidate


def get_apk_version(path):
    result = run_command(f"aapt dump badging '{path}'").strip()
    version = re.findall("versionName='([^']+)'", result, re.MULTILINE)
    if len(version) != 1:
        raise ValueError(f"Could not find APK version: {version}")
    return Version(version[0])


def run_command(command):
    proc = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    outs, _ = proc.communicate()
    return outs.decode("utf-8").strip()
