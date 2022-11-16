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
        print("using authenticated connection")
        error = sio.call(
                "connection_auth", data={"sharedConnection": True, "sessionLocator": SESSION_AUTH}
        )
        sio.emit("read_messages_subscribe")
        print(f"Auth error: {error}")
    else:
        sio.emit("connection_auth_anonymous", {"name": "testClient"})


@sio.on("connection_auth_locator")
def new_locator(data):
    with open("sessionauth.dat", "w+") as fd:
        json.dump(data, fd)


@sio.on("connection_qr")
def qr(data):
    print(qrcode_gen(data["qr"]))
    print(data)


@sio.event
def disconnect():
    print("disconnected from server")


@sio.on("read_messages")
def message(msg):
    rjid = msg["key"]["remoteJid"]
    print(f"Got Message: {msg=}")
    return
    media = sio.call("read_messages_downloadMedia", msg)
    print(f"Got media: {media=}")
    if False and "@g.us" in rjid:
        group_metadata = sio.call("read_groups_metadata", rjid)
        print(f"Group metadata: {group_metadata=}")


if __name__ == "__main__":
    sio.connect("ws://localhost:3000")
    try:
        sio.wait()
    except KeyboardInterrupt:
        print("Exiting")
    finally:
        sio.disconnect()
