# WHATUP

> Core mono-repo for the WhatsApp Watch project

## Contents

### Architecture Philosophy

Throughout this project, you'll hear about *devices*, *bots*, *sessions* and *control groups* quite a lot.

Devices are the physical phones that have a valid WhatsApp account on them. They can be devices that we have provisioned ourselves that we have full control of or phones who have logged into our system once which we have a limited view into. Devices are ephemeral and every-changing since WhatsApp will ban our bots regularly.

Bots are logical services that run on a device. A bot can be connected to multiple devices. The idea is that a bot does the work we actually care about and it will connect to as many devices as it can in order to accomplish it's goal. For example, a bot that archives all messages will connect to all available devices and read all the messages it has access to in order to archive those messages. However, another bot that doesn't read messages but instead only responds to user-queries through it's command interface only needs to connect to one bot in order to send/recieve messages.

In order to deal with the fact that bots can be running on some/all/one/many devices at once and that devices are constantly changing, in order to communicate with bots we have control groups. These are "announcement only" WhatsApp groups where all bots are read-only members and people allowed to issue commands are admins. When you want to speak to a bot, you simply send a message (such as `@DatabaseBot --help`) and an available bot will directly message you

Finally, we try to keep the actual WhatsApp login credentials quite safe. For the bots we have provisioned ourselves this is less important, but for other people's devices this is quite critical. Because of this, the WhatsApp login credentials are stores encrypted and instead we use our own credentials system, or sessions, in order to authenticate as a given device.


### File tree overview

```
.
├── data                  # static data
│   ├── db                # local postgres data
│   ├── keys              # encryption keys for communication between services
│   ├── message-archive   # local archive of messages from ArchiveBot
│   ├── sessions          # login credentials for local whatupcore devices to WhatsApp
│   ├── static            # static assets (keys should live here)
│   └── whatupcore2       # state for WhatUpCore2 (encrypted)
├── docker-compose.yml    # docker-compose for local deploys
├── protos                # protocol spec for communications layer
│   ├── Makefile          # makefile to generate project-specific protocol files
│   ├── whatsappweb.proto # extracted protocol spec for WhatsApp Web
│   └── whatupcore.proto  # protocol spec for WhatUp
├── refresh-bigquery.sh   # helper tool to sync local postgres to bigquery
├── scripts               # other helper scripts
├── utils.sh              # local bash functions to simplify dev life
├── whatupcore2           # core whatsapp connection layer
└── whatupy               # logic for the bots communicating with whatupcore
```

Inside each project you (should) find a README going into more detail on that subproject. This README focuses on giving a project-wide description of whats up.


### How Services Connect

The two main projects are `whatupcore2` and `whatupy` and they communicate using the protocol spec in the [protos](protos/) directory.

*whatupcore* is responsible for connecting to WhatsApp Web on behalf of our devices and exposing a friendly and unified view of that API to our bots defined in whatupy. In order to simplify connecting to WhatsApp, whatupcore maintains the encrytped state of each device in it's own set of sqlite databases (in [data/whatupcore2/db](data/whatupcore2/db/), encrypted with sqlcypher) that get decrypted with device-specific passphrases. For dev, these credentials are stored in [data/sessions](data/sessions/) and contain JSON blobs of the form,

```JSON
{
    "username": "alice",
    "passphrase": "a-long-passphrase"
}
```

In this example, "alice" refers to the friendly name given to a physical phone with a real wold phone number. If any bot wants to connect to this device and manipulate it's state, it would log into whatupcore using these credentials and issue any gRPC commands it would like.


*whatupy* is the library for implementing bots in python. That is to say, any business logic _using_ whatsapp accounts should be implemented as bots here. The current bot definitions can be found in the [bots directory](whatupy/whatupy/bots/) with the bot invocation found in the [cli file](whatupy/whatupy/cli.py).

An example of a bot is [ArchiveBot](whatupy/whatupy/bots/archivebot.py) who simply reads messages from all given sessions and saves them (and any media + group metadata) to JSON files for backup. However, more complex bots can be made that do deep analysis of data or perform specific actions based on messages recieved. One interesting aspect about the bot implementation are their ability to run through WhatsApp messages defined through the normal python CLI modules. This functionality is discussed further in [whatupy's README](whatupy/README.md).

The *protos* files define how whatupy and whatupcore communicate. The main protocol file of interest is (protos/whatupcore.proto)[protos/whatupcore.proto]. In it we defined two services, `WhatUpCoreAuth` which is responsible for logging into WhatUpCore and refreshing session credentials and `WhatUpCore` which contains all the actions you can perform on a device you are authenticated into. In the [Makefile](protos/Makefile), and using [protoc](https://github.com/protocolbuffers/protobuf), these protocol files are compiled into language-specific modules which can be used to call the services in a language-native way. This way, we can define a global protocol for communications between services in the protobuf file and compile it to whatever language we are using. Examples of the compiled modules can be found in [whatupy/whatupy/protos/](whatupy/whatupy/protos/) and [whatupcore2/protos/](whatupcore2/protos/).

More information about gRPC can be found [here](https://grpc.io/docs/what-is-grpc/introduction/)


```
 *------*                                                *---*
 |device| =={WhatsApp}==,,                          ,,== |bot|
 *------*               ||                          ||   *---*
                        ||                          ||
 *------*               ||        *-----------*     ||   *---*
 |device| =={WhatsApp}==websock== |whatupcore2| ==gRPC== |bot|
 *------*               ||        *-----------*     ||   *---*
                        ||                          ||
 *------*               ||                          ||   *---*
 |device| =={WhatsApp}==``                          ``== |bot|
 *------*                                                *---*


```


## Setup

### Local Development Environment

There are several steps necessary to start your local development environment.

0. Install dependencies
    - git
    - git crypt
    - docker
1. Clone this repo
2. Decrypt the static assets
3. Start the core resources
4. On-board your first device (only needed once)
5. Launch the bots you are interested in


#### Decrypting

Once the dependencies have been installed and this repo has been cloned, you can decrypt the static assets by running,

```bash
$ git crypt unlock
```

*NOTE:* You can only unlock the repo once you have provided your GPG public key to an existing member of the development team and you have been added to the keyring.


#### Core Services

The core resources necessary for development are `whatupcore` and `db`. These can be started with docker using the command,

```bash
$ docker compose up --build db whatupcore
```

This will start `db` and `whatupcore` in a blocking way, meaning that terminal is now busy running those commands. If you ^C, it will terminate the database and whatupcore. To run them in the background, add the `-d` flag and then you can use `docker compose logs` to monitor the processes,

```bash
$ docker compose up --build -d db whatupcore
$ docker compose logs --follow --tail 50 db whatupcore
```

To stop services running in the background, run

```bash
$ docker compose stop db whatupcore
```

*NOTE:* the `--build` flag is only necessary on the first run and when you have changed relevant code to the service you are starting. Because of docker's build cache, I generally always use this flag since it only adds a few extra seconds. Be aware that without the build flag, the version of the service that is being run is the version from the last time you built it!! When doing development, this can lead to some false-turns while debugging.


#### On-Boarding a device

Some services in our [docker-compose.yml](docker-compose.yml) are marked with the "donotrun" profile. This means these services won't run automatically and they're generally used for ad-hoc jobs. One of these ad-hoc jobs is on-boarding new devices into the system.

The service `bot-onboard-bulk` is one such service which helps you log in devices into your dev environment. To begin the process, first have a phone ready that you would like to use as the development device for your dev environment. This is the device all of your bots will connect to WhatsApp with.

Next, run the following command to go into on-boarding mode,

```bash
$ docker compose run --interactive --build bot-onboard-bulk
```

Once the service runs, it will ask you for a username for the device you are about to on-board. This name is simply a user-friendly way of referencing the device (for production, we use names with ascending letters of the alphabet. ie; Alice, Beatrice, Cathy, etc..).

Once the name is entered, you'll see a QR code. On your device, click on the three dots in the upper-right, then Linked devices and Link a device (official instructions [here](https://faq.whatsapp.com/1317564962315842/). This should open up a QR code scanner which you can use to scan the QR code.

If everything worked, you should see WhatUp listed as a linked device! If not, try restarting WhatsApp and scanning the QR code again. Note that the QR codes change frequently and the on-boarding bot will always display the most up-to-date code.

If you'd like to disconnect the system from your device, simply go to the "Linked Devices" page on your device's WhatsApp, click on "WhatUp" and click "Log Out".

*NOTE:* if you are interested in archiving your message history, you should move to the next step within 10 minutes of logging in. For security reasons, we only store the historical messages of newly on-boarded devices for 10 minutes before deleting them. Also, historical messages are only delivered to use from WhatsApp during on-boarding.

*NOTE:* You must turn on your device at least once every 14 days for the session to remain valid. After this, WhatsApp invalidates the login credentials and you will have to on-board again.


#### Launching Bots

Now it's time to run some bots! We will use `bot-archive` as an example, however you can run other bots or multiple bots using similar commands.

To run the archive bot, run the command,

```bash
$ docker compose up --build bot-archive
```

*NOTE:* Similar to the db/whatupcore, you can run this in the background using `-d` and then monitor the logs of the services.

This will connect to all devices that have valid sessions in the [data/sessions/](data/sessions/) directory. In addition, the bot will periodically look for new sessions in that directory and log into those as well. 


#### Celebrate 🎊

You now have a functional dev environment with messages being stored to the archive. You should see messages starting to be saved in [data/message-archive/](data/message-archive/) as they come into your device.
