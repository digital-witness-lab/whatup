import socketio
import json
import qrcode

sio = socketio.Client()
SESSION_AUTH = open("sessionauth.json").read().strip()


@sio.event
def connect():
    print("connection established")
    sio.emit(
        "connection:auth", data={"sessionAuth": SESSION_AUTH, "sharedConnection": True}
    )


@sio.on("connection:qr")
def qr(code):
    q = qrcode.QRCode(version=None)
    q.add_data(code)
    q.make(fit=True)
    q.print_ascii()


@sio.on("connection:auth")
def connection_auth(data):
    print(f"connection:auth: {data=}")
    if "sessionAuth" in data:
        print("Got new auth... storing")
        SESSION_AUTH = data["sessionAuth"]
        with open("sessionauth.json", "w") as fd:
            json.dump(SESSION_AUTH, fd)


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


sio.connect("ws://localhost:3000")
sio.wait()
