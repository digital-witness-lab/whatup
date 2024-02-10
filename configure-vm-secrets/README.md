# Secrets configurator for GCE VMs

This Go-based app reads the instance metadata attributes of the instance it's running in
and checks if any of them are references to secrets inside Google Secret Manager.
For all such attributes, it accesses the secret value and writes them to a file
`/tmp/whatup/.env`. An app can then load this .env file to load all the necessary env
vars at startup.

The recommended way to run this app is inside your container image so that the file
it creates is only available to the main app running inside the container and not
in the VM, even though the VM itself has access to the service account that can
access these secrets. It allows the container's dependencies to be contained
within the container rather than leaving lingering files on the VM's disk.

**What about when a container image runs this inside a non-GCE env?**

It'll be a no-op and exit silently.
