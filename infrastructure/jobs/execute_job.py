import pulumi

from config import location, project

from google.cloud import run_v2
from google.api_core import exceptions


def run_job_sync(job_name: str, polling_timeout: int):
    """
    Runs the job immediately and waits (blocks)
    for its completion or until the ``polling_timeout``.

    Jobs will not execute during Pulumi's dry-run phase.
    """

    if pulumi.runtime.is_dry_run():
        return False

    # Create a client using the ambient environment
    # credentials. That is, this will detect the
    # credentials from the host (your machine or
    # on CI) that is running this code. It is
    # likely that you are using gcloud when
    # running locally or using non-interactive
    # credentials when running in an
    # environment like GitHub Actions,
    # for example.
    client = run_v2.JobsClient()

    request = run_v2.RunJobRequest(
        name=f"projects/{project}/locations/{location}/jobs/{job_name}",
    )

    operation = client.run_job(request=request)

    pulumi.log.info(f"Waiting for {job_name} to complete...")

    try:
        operation.result(timeout=polling_timeout)
    except Exception as e:
        ex = operation.exception()
        if ex is not None:
            api_error: exceptions.GoogleAPICallError = ex
            pulumi.log.error(
                f"{job_name} failed execution: {api_error.message}"
            )  # noqa: E501
        else:
            pulumi.log.error(
                f"Unknown exception occurred while executing {job_name}"
            )  # noqa: E501

        raise e

    return True
