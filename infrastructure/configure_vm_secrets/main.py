import logging
import urllib.parse
import requests
import os


def main():
    # Write environment variables to a file-system path

    # https://cloud.google.com/compute/docs/instances/startup-scripts/linux#accessing-metadata
    # # https://cloud.google.com/compute/docs/instances/startup-scripts/linux#accessing-metadata
    # TS_AUTH_KEY=$(curl http://metadata.google.internal/computeMetadata/v1/instance/attributes/TS_AUTH_KEY -H "Metadata-Flavor: Google")
    attributes_resp = requests.get(
        "http://metadata.google.internal/computeMetadata/v1/instance/attributes/",
        headers={"Metadata-Flavor": "Google"},
    )

    attributes_resp.close()

    raw_value = attributes_resp.text
    logging.info("Instance metadata attributes", raw_value)

    attributes = raw_value.split("\n")

    secrets = {}

    for attr in attributes:
        attribute_value = requests.get(
            f"http://metadata.google.internal/computeMetadata/v1/instance/attributes/{attr}",
            headers={"Metadata-Flavor": "Google"},
        )

        audience = f"https://secretmanager.googleapis.com/v1/{attribute_value}"

        id_token = requests.get(
            f"http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity?audience={urllib.parse.quote(audience)}",
            headers={"Metadata-Flavor": "Google"},
        )

        # TODO: Request the secret value from Secret Manager.
        # secrets[attr] = ""

    with open(os.path.join("", "tmp", "secrets.env"), "w") as f:
        for k, v in secrets.items():
            f.write(f"{k}={v}")

    logging.info("Wrote secrets file")


if __name__ == "main":
    main()
