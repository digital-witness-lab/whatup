# GCP Infrastructure

## Private Networking

### Cloud Run Service

We have two Cloud Run services at the time of writing that are not accessible
via the internet. One of the services `whatupy` needs to be able to call the
`whatupcore2` service using gRPC. This traffic between the two services needs
to be within the network and not egress via the internet.

https://cloud.google.com/run/docs/securing/private-networking#from-other-services

### Cloud SQL

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
