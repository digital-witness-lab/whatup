# GCP Infrastructure

```bash
$ gcloud auth application-default login
$ pulumu up --stack test
$ gcloud auth configure-docker europe-west3-docker.pkg.dev
```

## Development

### Prerequisites

-   [Install](https://cloud.google.com/sdk/docs/install) the latest `gcloud` CLI and login to the `whatup-deploy` GCP project with `gcloud auth login`.
-   [Install](https://www.pulumi.com/docs/install/) the latest `pulumi` CLI and login to your Pulumi account with `pulumi login`.
-   [Configure Docker](https://cloud.google.com/artifact-registry/docs/docker/authentication) to use your GCP credentials.

### Pulumi crash-course

Activate the stack you want to operate on:

```sh
pulumi stack select <stack name>
# Check for the currently selected stack.
# The currently-selected stack is indicated
# with an '*' next to it.
pulumi stack ls
```

Set stack config settings:

```sh
pulumi config set <key> <value> -s <stack name>
# Always pass --secret for secret configs.
# pulumi config set --secret <key> -s <stack name>
```

Set lists and objects in stack config:

```sh
pulumi config set --path 'key[0]' value
pulumi config set --path 'key[1]' value
```

## Private Networking

### Cloud Run Service

We have two Cloud Run services at the time of writing that are not accessible
via the internet. One of the services `whatupy` needs to be able to call the
`whatupcore2` service using gRPC. This traffic between the two services needs
to be within the network and not egress via the internet.

https://cloud.google.com/run/docs/securing/private-networking#from-other-services

### Cloud SQL

https://cloud.google.com/vpc/docs/private-services-access
https://cloud.google.com/sql/docs/postgres/connect-run#private-ip_1

## Jobs

The `databasebot-load-archive` and `onboardbulk` jobs are guarded by a flag.
Once set to `true` in the Pulumi stack config for a stack, the respective
jobs will be created and executed.

The jobs are one-off jobs that will to completion and terminate.
However, the job definition itself will continue to exist in GCP.
You can still run future executions from that by using the GCP
console. Alternatively, you may also flip the flags back to
`false` and let Pulumi destroy the jobs. You can once again
at a later time set them to `true` to have them re-created
and executed.

### Executing jobs

Jobs can be executed in a [few ways](https://cloud.google.com/run/docs/execute/jobs#console).
We have a `jobs/execute_job.py` that uses the Cloud Run Python client to execute the job.
See `jobs/db_migration.py` for an example of how it's used.

If you are going to use the `run_job_sync` to run a job, you should ensure that it is ok
if you run it every time pulumi up runs. If that is not desired, then you should promptly
remove any calls to `run_job_sync` after you've executed a job successfully...OR use this
func outside of this infrastructure app in some other way, or trigger the execution
directly using one of the other ways GCP supports. This is not a problem for our DB
migrations job since migrations once applied will be a no-op on subsequent executions
due to the way we apply migrations.

## Deleting Cloud SQL Instance

The Cloud SQL instance has deletion protection enabled to prevent accidental deletion.
If you are sure you would like to delete the DB, you should first run a `pulumi up` with
deletion protection set to `False` first, then run a `pulumi destroy`.

## Destroying Infrastructure

**Note:** Ensure that you have the correct stack selected.

You can teardown all the resources in a stack with `pulumi destroy`.
In addition to the above section about [deleting the database instance](#deleting-cloud-sql-instance)
you are also likely to encounter other failures during deletion.
Some of these only apply to production stacks.

### Failure deleting subnetworks/subnets

GCP seems to take a while to release the private IP address reservations
that we make for the purpose of Cloud SQL private IP enablement.
If that happens, wait for a few hours (> 4 hours; best if you just try again the next day)
and try re-running `pulumi destroy` to fully remove all the resources.

### Failure deleting cloud storage buckets

You will need to explicitly delete all the objects in the buckets
before the buckets themselves can be deleted. This is especially
the case for the production stack.

```
Error trying to delete bucket dwl-core2-6eaba0c containing objects without `force_destroy` set to true
```

# Future Notes

-   if bigquery sync is slow, we can use DMS on the SQL side
-   move repository for whatupy into a global thing all jobs/services use if it becomes an issue having so many repositories
