from pathlib import Path
import html
from datetime import datetime
import hashlib
import re

import requests


def get_whatsapp(archive: Path, download=False):
    if not download:
        files = list((archive / "packages").glob("*.apk"))
        files.sort()
        return files[-1]
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
    filehash = hashlib.sha256(data.content).hexdigest()[:8]
    candidate_packages = list(archive.glob(f"packages/WhatsApp-*-{filehash}.apk"))
    if not candidate_packages:
        print("Found new WhatsApp version")
        date = datetime.now().date().isoformat()
        fileloc = archive / "packages" / f"WhatsApp-{date}-{filehash}.apk"
        fileloc.parent.mkdir(exist_ok=True, parents=True)
        with fileloc.open("wb+") as fd:
            fd.write(data.content)
        return fileloc
    elif len(candidate_packages) == 1:
        return candidate_packages[1]
    else:
        print(
            f"Somehow got more than one package with the same hash... returning the most recent one: {candidate_packages}"
        )
        candidate_packages.sort()
        return candidate_packages[-1]
