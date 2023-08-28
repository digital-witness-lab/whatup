# WhatUpCore2

> GoLang WhatsApp gRPC Server

WhatupCore2 is the second iteration of the WhatUp project's core backend service. The role of this service is to,

- Manage device login credentials
- Manage bot connection sessions
- Multiplex multiple bot connections for the same device
- Translate WhatsApp's protocol madness into a cleaner [WhatUpCore.proto](../protos/whatupcore.proto)
- Be. Reliable.


## Installation

You can either run whatupcore with docker-compose, locally or with docker. Either way, you'll have a gRPC server listening on port *3447* for connections following the [WhatUpCore protocol](../protos/whatupcore.proto)

*NOTE:* All methods of running assume the `whatupcore2` binary has access to an SSL cert at `/run/secrets/ssl-cert` and an SSL key at `/run/secrets/ssl-key`. Using the `docker-compose` method is the only way to have this automatically taken care for you.  Otherwise you need to ensure these files are there yourself


### Building/Running with docker-compose (preferred)


In the root directory of this project (where the `docker-compose.yaml` file is located) run,

```bash
$ docker compose up --build whatupcore
```


### Building/Running locally

Requirements,
- golang
- libsqlite3-0
- libsqlite3-dev
- libsqlcipher0
- libsqlcipher-dev
- libssl-dev

```bash
$ sudo apt install golang-1.20 libsqlite3-0 libsqlite3-dev libsqlcipher0 libsqlcipher-dev libssl-dev
$ make whatupcore2
$ ./whatupcore2 rpc
```


### Building/Running with docker

```bash
$ docker build -t whatupcore2:latest .
$ docker run -p 3447:3447 whatupcore2:latest
```


## Code Run-through

// TODO


## TODO

- [ ] Global config that 
- [ ] Any way to persist sessions on restart without storing too many secrets?
