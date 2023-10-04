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
