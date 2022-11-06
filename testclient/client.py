import socketio
import json

from util import qrcode_gen

sio = socketio.Client()

try:
    SESSION_AUTH = json.load(open("sessionauth.dat"))
except FileNotFoundError:
    SESSION_AUTH = None


@sio.event
def connect():
    print("connection established")
    if SESSION_AUTH:
        error = sio.call(
            "connection:auth",
            data={"sharedConnection": True, **SESSION_AUTH}
        )
    else:
        sio.emit("connection:auth:anonymous", {"name": 'testClient'})

@sio.on("connection:auth:locator")
def new_locator(data):
    with open("sessionauth.dat", "w+") as fd:
        json.dump(data, fd)


@sio.on("connection:qr")
def qr(data):
    print(qrcode_gen(data["qr"]))
    print(data)


@sio.on("connection:ready")
def ready(data):
    print(f"Connection ready: {data=}")
    print("Subscribing to messages")
    sio.emit("read:messages:subscribe")


@sio.event
def disconnect():
    print("disconnected from server")


@sio.on("read:messages")
def message(msg):
    rjid = msg["key"]["remoteJid"]
    print(f"Got Message: {msg=}")
    return
    media = sio.call("read:messages:downloadMedia", msg)
    print(f"Got media: {media=}")
    if False and "@g.us" in rjid:
        group_metadata = sio.call("read:groups:metadata", rjid)
        print(f"Group metadata: {group_metadata=}")


if __name__ == "__main__":
    sio.connect("ws://localhost:3000")
    try:
        sio.wait()
    except KeyboardInterrupt:
        print("Exiting")
    finally:
        sio.disconnect()
