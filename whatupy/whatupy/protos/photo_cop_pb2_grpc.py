"""Client and server classes corresponding to protobuf-defined services."""
import grpc
from . import photo_cop_pb2 as photo__cop__pb2

class PhotoCopStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.CheckPhoto = channel.unary_unary('/photocop.PhotoCop/CheckPhoto', request_serializer=photo__cop__pb2.CheckPhotoRequest.SerializeToString, response_deserializer=photo__cop__pb2.PhotoCopDecision.FromString)
        self.GetPhotoHash = channel.unary_unary('/photocop.PhotoCop/GetPhotoHash', request_serializer=photo__cop__pb2.GetPhotoHashRequest.SerializeToString, response_deserializer=photo__cop__pb2.PhotoCopHash.FromString)

class PhotoCopServicer(object):
    """Missing associated documentation comment in .proto file."""

    def CheckPhoto(self, request, context):
        """Checks the photo cop.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetPhotoHash(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_PhotoCopServicer_to_server(servicer, server):
    rpc_method_handlers = {'CheckPhoto': grpc.unary_unary_rpc_method_handler(servicer.CheckPhoto, request_deserializer=photo__cop__pb2.CheckPhotoRequest.FromString, response_serializer=photo__cop__pb2.PhotoCopDecision.SerializeToString), 'GetPhotoHash': grpc.unary_unary_rpc_method_handler(servicer.GetPhotoHash, request_deserializer=photo__cop__pb2.GetPhotoHashRequest.FromString, response_serializer=photo__cop__pb2.PhotoCopHash.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('photocop.PhotoCop', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))

class PhotoCop(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def CheckPhoto(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/photocop.PhotoCop/CheckPhoto', photo__cop__pb2.CheckPhotoRequest.SerializeToString, photo__cop__pb2.PhotoCopDecision.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetPhotoHash(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/photocop.PhotoCop/GetPhotoHash', photo__cop__pb2.GetPhotoHashRequest.SerializeToString, photo__cop__pb2.PhotoCopHash.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata)