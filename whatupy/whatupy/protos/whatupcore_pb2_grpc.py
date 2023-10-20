"""Client and server classes corresponding to protobuf-defined services."""
import grpc
from . import whatupcore_pb2 as whatupcore__pb2


class WhatUpCoreAuthStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Login = channel.unary_unary(
            "/protos.WhatUpCoreAuth/Login",
            request_serializer=whatupcore__pb2.WUCredentials.SerializeToString,
            response_deserializer=whatupcore__pb2.SessionToken.FromString,
        )
        self.Register = channel.unary_stream(
            "/protos.WhatUpCoreAuth/Register",
            request_serializer=whatupcore__pb2.RegisterOptions.SerializeToString,
            response_deserializer=whatupcore__pb2.RegisterMessages.FromString,
        )
        self.RenewToken = channel.unary_unary(
            "/protos.WhatUpCoreAuth/RenewToken",
            request_serializer=whatupcore__pb2.SessionToken.SerializeToString,
            response_deserializer=whatupcore__pb2.SessionToken.FromString,
        )


class WhatUpCoreAuthServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Login(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def Register(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def RenewToken(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_WhatUpCoreAuthServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "Login": grpc.unary_unary_rpc_method_handler(
            servicer.Login,
            request_deserializer=whatupcore__pb2.WUCredentials.FromString,
            response_serializer=whatupcore__pb2.SessionToken.SerializeToString,
        ),
        "Register": grpc.unary_stream_rpc_method_handler(
            servicer.Register,
            request_deserializer=whatupcore__pb2.RegisterOptions.FromString,
            response_serializer=whatupcore__pb2.RegisterMessages.SerializeToString,
        ),
        "RenewToken": grpc.unary_unary_rpc_method_handler(
            servicer.RenewToken,
            request_deserializer=whatupcore__pb2.SessionToken.FromString,
            response_serializer=whatupcore__pb2.SessionToken.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "protos.WhatUpCoreAuth", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))


class WhatUpCoreAuth(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Login(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/protos.WhatUpCoreAuth/Login",
            whatupcore__pb2.WUCredentials.SerializeToString,
            whatupcore__pb2.SessionToken.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def Register(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_stream(
            request,
            target,
            "/protos.WhatUpCoreAuth/Register",
            whatupcore__pb2.RegisterOptions.SerializeToString,
            whatupcore__pb2.RegisterMessages.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def RenewToken(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/protos.WhatUpCoreAuth/RenewToken",
            whatupcore__pb2.SessionToken.SerializeToString,
            whatupcore__pb2.SessionToken.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )


class WhatUpCoreStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetConnectionStatus = channel.unary_unary(
            "/protos.WhatUpCore/GetConnectionStatus",
            request_serializer=whatupcore__pb2.ConnectionStatusOptions.SerializeToString,
            response_deserializer=whatupcore__pb2.ConnectionStatus.FromString,
        )
        self.GetACLAll = channel.unary_stream(
            "/protos.WhatUpCore/GetACLAll",
            request_serializer=whatupcore__pb2.GetACLAllOptions.SerializeToString,
            response_deserializer=whatupcore__pb2.GroupACL.FromString,
        )
        self.SetACL = channel.unary_unary(
            "/protos.WhatUpCore/SetACL",
            request_serializer=whatupcore__pb2.GroupACL.SerializeToString,
            response_deserializer=whatupcore__pb2.GroupACL.FromString,
        )
        self.GetACL = channel.unary_unary(
            "/protos.WhatUpCore/GetACL",
            request_serializer=whatupcore__pb2.JID.SerializeToString,
            response_deserializer=whatupcore__pb2.GroupACL.FromString,
        )
        self.GetJoinedGroups = channel.unary_stream(
            "/protos.WhatUpCore/GetJoinedGroups",
            request_serializer=whatupcore__pb2.GetJoinedGroupsOptions.SerializeToString,
            response_deserializer=whatupcore__pb2.JoinedGroup.FromString,
        )
        self.GetGroupInfo = channel.unary_unary(
            "/protos.WhatUpCore/GetGroupInfo",
            request_serializer=whatupcore__pb2.JID.SerializeToString,
            response_deserializer=whatupcore__pb2.GroupInfo.FromString,
        )
        self.GetGroupInfoInvite = channel.unary_unary(
            "/protos.WhatUpCore/GetGroupInfoInvite",
            request_serializer=whatupcore__pb2.InviteCode.SerializeToString,
            response_deserializer=whatupcore__pb2.GroupInfo.FromString,
        )
        self.JoinGroup = channel.unary_unary(
            "/protos.WhatUpCore/JoinGroup",
            request_serializer=whatupcore__pb2.InviteCode.SerializeToString,
            response_deserializer=whatupcore__pb2.GroupInfo.FromString,
        )
        self.GetMessages = channel.unary_stream(
            "/protos.WhatUpCore/GetMessages",
            request_serializer=whatupcore__pb2.MessagesOptions.SerializeToString,
            response_deserializer=whatupcore__pb2.WUMessage.FromString,
        )
        self.GetPendingHistory = channel.unary_stream(
            "/protos.WhatUpCore/GetPendingHistory",
            request_serializer=whatupcore__pb2.PendingHistoryOptions.SerializeToString,
            response_deserializer=whatupcore__pb2.WUMessage.FromString,
        )
        self.DownloadMedia = channel.unary_unary(
            "/protos.WhatUpCore/DownloadMedia",
            request_serializer=whatupcore__pb2.DownloadMediaOptions.SerializeToString,
            response_deserializer=whatupcore__pb2.MediaContent.FromString,
        )
        self.SendMessage = channel.unary_unary(
            "/protos.WhatUpCore/SendMessage",
            request_serializer=whatupcore__pb2.SendMessageOptions.SerializeToString,
            response_deserializer=whatupcore__pb2.SendMessageReceipt.FromString,
        )
        self.SetDisappearingMessageTime = channel.unary_unary(
            "/protos.WhatUpCore/SetDisappearingMessageTime",
            request_serializer=whatupcore__pb2.DisappearingMessageOptions.SerializeToString,
            response_deserializer=whatupcore__pb2.DisappearingMessageResponse.FromString,
        )
        self.Unregister = channel.unary_unary(
            "/protos.WhatUpCore/Unregister",
            request_serializer=whatupcore__pb2.UnregisterOptions.SerializeToString,
            response_deserializer=whatupcore__pb2.ConnectionStatus.FromString,
        )


class WhatUpCoreServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetConnectionStatus(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GetACLAll(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def SetACL(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GetACL(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GetJoinedGroups(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GetGroupInfo(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GetGroupInfoInvite(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def JoinGroup(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GetMessages(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GetPendingHistory(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def DownloadMedia(self, request, context):
        """DownloadMedia can take in a MediaMessage since this is a subset of the proto.Message"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def SendMessage(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def SetDisappearingMessageTime(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def Unregister(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_WhatUpCoreServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "GetConnectionStatus": grpc.unary_unary_rpc_method_handler(
            servicer.GetConnectionStatus,
            request_deserializer=whatupcore__pb2.ConnectionStatusOptions.FromString,
            response_serializer=whatupcore__pb2.ConnectionStatus.SerializeToString,
        ),
        "GetACLAll": grpc.unary_stream_rpc_method_handler(
            servicer.GetACLAll,
            request_deserializer=whatupcore__pb2.GetACLAllOptions.FromString,
            response_serializer=whatupcore__pb2.GroupACL.SerializeToString,
        ),
        "SetACL": grpc.unary_unary_rpc_method_handler(
            servicer.SetACL,
            request_deserializer=whatupcore__pb2.GroupACL.FromString,
            response_serializer=whatupcore__pb2.GroupACL.SerializeToString,
        ),
        "GetACL": grpc.unary_unary_rpc_method_handler(
            servicer.GetACL,
            request_deserializer=whatupcore__pb2.JID.FromString,
            response_serializer=whatupcore__pb2.GroupACL.SerializeToString,
        ),
        "GetJoinedGroups": grpc.unary_stream_rpc_method_handler(
            servicer.GetJoinedGroups,
            request_deserializer=whatupcore__pb2.GetJoinedGroupsOptions.FromString,
            response_serializer=whatupcore__pb2.JoinedGroup.SerializeToString,
        ),
        "GetGroupInfo": grpc.unary_unary_rpc_method_handler(
            servicer.GetGroupInfo,
            request_deserializer=whatupcore__pb2.JID.FromString,
            response_serializer=whatupcore__pb2.GroupInfo.SerializeToString,
        ),
        "GetGroupInfoInvite": grpc.unary_unary_rpc_method_handler(
            servicer.GetGroupInfoInvite,
            request_deserializer=whatupcore__pb2.InviteCode.FromString,
            response_serializer=whatupcore__pb2.GroupInfo.SerializeToString,
        ),
        "JoinGroup": grpc.unary_unary_rpc_method_handler(
            servicer.JoinGroup,
            request_deserializer=whatupcore__pb2.InviteCode.FromString,
            response_serializer=whatupcore__pb2.GroupInfo.SerializeToString,
        ),
        "GetMessages": grpc.unary_stream_rpc_method_handler(
            servicer.GetMessages,
            request_deserializer=whatupcore__pb2.MessagesOptions.FromString,
            response_serializer=whatupcore__pb2.WUMessage.SerializeToString,
        ),
        "GetPendingHistory": grpc.unary_stream_rpc_method_handler(
            servicer.GetPendingHistory,
            request_deserializer=whatupcore__pb2.PendingHistoryOptions.FromString,
            response_serializer=whatupcore__pb2.WUMessage.SerializeToString,
        ),
        "DownloadMedia": grpc.unary_unary_rpc_method_handler(
            servicer.DownloadMedia,
            request_deserializer=whatupcore__pb2.DownloadMediaOptions.FromString,
            response_serializer=whatupcore__pb2.MediaContent.SerializeToString,
        ),
        "SendMessage": grpc.unary_unary_rpc_method_handler(
            servicer.SendMessage,
            request_deserializer=whatupcore__pb2.SendMessageOptions.FromString,
            response_serializer=whatupcore__pb2.SendMessageReceipt.SerializeToString,
        ),
        "SetDisappearingMessageTime": grpc.unary_unary_rpc_method_handler(
            servicer.SetDisappearingMessageTime,
            request_deserializer=whatupcore__pb2.DisappearingMessageOptions.FromString,
            response_serializer=whatupcore__pb2.DisappearingMessageResponse.SerializeToString,
        ),
        "Unregister": grpc.unary_unary_rpc_method_handler(
            servicer.Unregister,
            request_deserializer=whatupcore__pb2.UnregisterOptions.FromString,
            response_serializer=whatupcore__pb2.ConnectionStatus.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "protos.WhatUpCore", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))


class WhatUpCore(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetConnectionStatus(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/protos.WhatUpCore/GetConnectionStatus",
            whatupcore__pb2.ConnectionStatusOptions.SerializeToString,
            whatupcore__pb2.ConnectionStatus.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def GetACLAll(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_stream(
            request,
            target,
            "/protos.WhatUpCore/GetACLAll",
            whatupcore__pb2.GetACLAllOptions.SerializeToString,
            whatupcore__pb2.GroupACL.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def SetACL(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/protos.WhatUpCore/SetACL",
            whatupcore__pb2.GroupACL.SerializeToString,
            whatupcore__pb2.GroupACL.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def GetACL(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/protos.WhatUpCore/GetACL",
            whatupcore__pb2.JID.SerializeToString,
            whatupcore__pb2.GroupACL.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def GetJoinedGroups(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_stream(
            request,
            target,
            "/protos.WhatUpCore/GetJoinedGroups",
            whatupcore__pb2.GetJoinedGroupsOptions.SerializeToString,
            whatupcore__pb2.JoinedGroup.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def GetGroupInfo(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/protos.WhatUpCore/GetGroupInfo",
            whatupcore__pb2.JID.SerializeToString,
            whatupcore__pb2.GroupInfo.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def GetGroupInfoInvite(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/protos.WhatUpCore/GetGroupInfoInvite",
            whatupcore__pb2.InviteCode.SerializeToString,
            whatupcore__pb2.GroupInfo.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def JoinGroup(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/protos.WhatUpCore/JoinGroup",
            whatupcore__pb2.InviteCode.SerializeToString,
            whatupcore__pb2.GroupInfo.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def GetMessages(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_stream(
            request,
            target,
            "/protos.WhatUpCore/GetMessages",
            whatupcore__pb2.MessagesOptions.SerializeToString,
            whatupcore__pb2.WUMessage.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def GetPendingHistory(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_stream(
            request,
            target,
            "/protos.WhatUpCore/GetPendingHistory",
            whatupcore__pb2.PendingHistoryOptions.SerializeToString,
            whatupcore__pb2.WUMessage.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def DownloadMedia(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/protos.WhatUpCore/DownloadMedia",
            whatupcore__pb2.DownloadMediaOptions.SerializeToString,
            whatupcore__pb2.MediaContent.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def SendMessage(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/protos.WhatUpCore/SendMessage",
            whatupcore__pb2.SendMessageOptions.SerializeToString,
            whatupcore__pb2.SendMessageReceipt.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def SetDisappearingMessageTime(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/protos.WhatUpCore/SetDisappearingMessageTime",
            whatupcore__pb2.DisappearingMessageOptions.SerializeToString,
            whatupcore__pb2.DisappearingMessageResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def Unregister(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/protos.WhatUpCore/Unregister",
            whatupcore__pb2.UnregisterOptions.SerializeToString,
            whatupcore__pb2.ConnectionStatus.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
