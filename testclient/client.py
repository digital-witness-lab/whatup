import socketio

from util import qrcode_gen, forcestr

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
def qr(code):
    print(code)
    print(qrcode_gen(code))


@sio.on("connection:auth")
def connection_auth(data):
    print(f"connection:auth: {data=}")
    if "sessionAuth" in data:
        print("Got new auth... storing")
        SESSION_AUTH = data["sessionAuth"]
        with open("sessionauth.dat", "w") as fd:
            fd.write(SESSION_AUTH)


@sio.on("connection:ready")
def ready(data):
    print(f"Connection ready: {data=}")
    sio.emit("read:messages:subscribe")


@sio.on("read:messages")
def message(data):
    print(f"Got Message: {data=}")


@sio.event
def my_message(data):
    print("message received with ", data)
    sio.emit("my response", {"response": "my response"})


@sio.event
def disconnect():
    print("disconnected from server")


if __name__ == "__main__":
    sio.connect("ws://localhost:3000")
    sio.wait()
