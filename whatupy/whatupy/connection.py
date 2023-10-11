import asyncio
import logging
import time
import typing as T
from pathlib import Path

import grpc

from .protos import whatupcore_pb2 as wuc
from .protos.whatupcore_pb2_grpc import WhatUpCoreAuthStub, WhatUpCoreStub

logger = logging.getLogger(__name__)


class NotRegisteredError(Exception):
    pass


def create_whatupcore_clients(host: str, port: int, cert_path: T.Optional[Path] = None):
    authenticator = WhatUpAuthentication()

    cert = None
    if cert_path:
        with cert_path.open("rb") as f:
            cert = f.read()
    options = [("grpc.max_receive_message_length", 200 * 1024 * 1024)]
    channel = grpc.aio.secure_channel(
        f"{host}:{port}",
        grpc.composite_channel_credentials(
            grpc.ssl_channel_credentials(root_certificates=cert or None),
            grpc.metadata_call_credentials(GRPCAuth(authenticator)),
        ),
        options=options,
    )

    auth_client = WhatUpCoreAuthStub(channel)
    core_client = WhatUpCoreStub(channel)
    authenticator.set_auth_client(auth_client)

    return core_client, authenticator


class WhatUpAuthentication:
    def __init__(self, auth_client: T.Optional[WhatUpCoreAuthStub] = None):
        self.auth_client: T.Optional[WhatUpCoreAuthStub] = auth_client
        self.session_token: T.Optional[wuc.SessionToken] = None
        self.logger = logger.getChild("GRPCAuthentication")

    def set_auth_client(self, auth_client: WhatUpCoreAuthStub):
        self.auth_client = auth_client

    def token(self) -> T.Optional[str]:
        if self.session_token is None:
            return None
        return self.session_token.token

    async def login(self, username: str, passphrase: str):
        if not self.auth_client:
            raise Exception("Must set an auth client")
        self.logger = self.logger.getChild(f"u:{username}")
        credentials = wuc.WUCredentials(username=username, passphrase=passphrase)
        session = await self.auth_client.Login(credentials)
        self.session_token = session

    async def register(
        self,
        username: str,
        passphrase: str,
        default_group_permission: wuc.GroupPermission.ValueType = wuc.GroupPermission.DENIED,
    ) -> T.AsyncIterator[str]:
        if not self.auth_client:
            raise Exception("Must set an auth client")
        self.logger = self.logger.getChild(username)
        credentials = wuc.WUCredentials(username=username, passphrase=passphrase)
        register_options = wuc.RegisterOptions(
            credentials=credentials,
            defaultGroupPermission=default_group_permission,
        )
        registerStream = self.auth_client.Register(register_options)
        async for msg in registerStream:
            if msg.qrcode:
                yield msg.qrcode
            elif msg.token:
                self.session_token = msg.token
                registerStream.cancel()
                return
        raise NotRegisteredError("Could not register user")

    async def start(self):
        if not self.auth_client:
            raise Exception("Must set an auth client")
        if not self.session_token:
            raise Exception("Must be authenticated before starting")
        while True:
            sleep_time = (
                self.session_token.expirationTime.ToSeconds() - time.time() - 60
            )
            self.logger.debug(
                "Renewing token in: %s: %s",
                sleep_time,
                self.session_token.expirationTime.ToSeconds(),
            )
            await asyncio.sleep(sleep_time)
            session_token = await self.auth_client.RenewToken(self.session_token)
            self.logger.debug(
                "Got new session token: %s: %s",
                self.session_token.expirationTime.ToSeconds(),
                session_token.expirationTime,
            )
            self.session_token = session_token


class GRPCAuth(grpc.AuthMetadataPlugin):
    def __init__(self, authenticator: WhatUpAuthentication):
        self.authenticator = authenticator
        super().__init__()

    def __call__(self, context, callback):
        if "/protos.WhatUpCoreAuth" in context.service_url:
            return callback(None, None)
        return callback(
            (("authorization", f"bearer {self.authenticator.token()}"),), None
        )
