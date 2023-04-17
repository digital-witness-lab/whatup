# WHATUPY

> Clients and CLI tools to interface with whatupcore

## Installation


```bash
$ git clone --recursive git@github.com:digital-witness-lab/whatupy.git
$ cd whatupy
$ virtualenv -p python3.11 venv
$ source ./venv/bin/activate
(venv)$ pip install -e .[dev]
``` 

If you forget to clone with `--recursive` you can run the following command to pull in the dependencies:

```bash
$ git submodule update --checkout --recursive --remote --init
```


## Usage

```bash
$ whatupy
Usage: whatupy [OPTIONS] COMMAND [ARGS]...

Options:
  -d, --debug
  -H, --host TEXT
  -p, --port INTEGER
  --cert FILE
  --help              Show this message and exit.

Commands:
  archivebot    Bot to archive all the data the provided bots have access...
  chatbot       Create a bot-evasion chat-bot.
  onboard       Creates a QR code for provided bot.
  onboard-bulk  Starts an interaction to simplify onboarding multiple bots.
```
