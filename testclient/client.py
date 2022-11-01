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
    sio.emit("read:messages:subscribe")


@sio.event
def disconnect():
    print("disconnected from server")


@sio.on("read:messages")
def message(msg):
    rjid = msg["key"]["remoteJid"]
    media = sio.call("read:messages:downloadMedia", msg)
    print(f"Got Message: {msg=}")
    print(f"Got meda: {media=}")
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
