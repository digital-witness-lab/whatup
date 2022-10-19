import socketio

from util import qrcode_gen

sio = socketio.Client()

try:
    SESSION_AUTH = open("sessionauth.dat").read().strip()
except FileNotFoundError:
    SESSION_AUTH = None


@sio.event
def connect():
    print("connection established")
    if SESSION_AUTH:
        sio.emit(
            "connection:auth",
            data={"sessionAuth": SESSION_AUTH, "sharedConnection": True},
        )
    else:
        sio.emit("connection:auth:anonymous")


@sio.on("connection:qr")
def qr(data):
    print(qrcode_gen(data["qr"]))
    print(data)


@sio.on("connection:auth")
def connection_auth(data):
    if "sessionAuth" in data:
        print("Got new auth... storing")
        SESSION_AUTH = data["sessionAuth"]
        with open("sessionauth.dat", "w") as fd:
            fd.write(SESSION_AUTH)


@sio.on("connection:ready")
def ready(data):
    print(f"Connection ready: {data=}")
    sio.emit("read:messages:subscribe", callback=message)


@sio.event
def disconnect():
    print("disconnected from server")


def message(data):
    print(f"Got Message: {data=}")
    rjid = data["message"]["key"]["remoteJid"]
    if "@g.us" in rjid:
        sio.emit("read:groupMetadata", rjid, callback=group_metadata)


def group_metadata(data):
    print(f"Got group metadata: {data=}")


if __name__ == "__main__":
    sio.connect("ws://localhost:3000")
    sio.wait()
