"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0fphoto_cop.proto\x12\x08photocop"$\n\x13GetPhotoHashRequest\x12\r\n\x05Photo\x18\x01 \x01(\x0c"\x1d\n\x0cPhotoCopHash\x12\r\n\x05Value\x18\x01 \x01(\x0c"E\n\x11CheckPhotoRequest\x12\r\n\x05Photo\x18\x01 \x01(\x0c\x12\x0f\n\x07GetHash\x18\x02 \x01(\x08\x12\x10\n\x08Priority\x18\x03 \x01(\x05"o\n\x10PhotoCopDecision\x12\x0f\n\x07IsMatch\x18\x01 \x01(\x08\x12$\n\x04Hash\x18\x02 \x01(\x0b2\x16.photocop.PhotoCopHash\x12$\n\x07Matches\x18\x03 \x03(\x0b2\x13.photocop.MatchInfo"A\n\tMatchInfo\x12\x0e\n\x06Source\x18\x01 \x01(\t\x12\x10\n\x08Distance\x18\x02 \x01(\x05\x12\x12\n\nViolations\x18\x03 \x03(\t2\x98\x01\n\x08PhotoCop\x12E\n\nCheckPhoto\x12\x1b.photocop.CheckPhotoRequest\x1a\x1a.photocop.PhotoCopDecision\x12E\n\x0cGetPhotoHash\x12\x1d.photocop.GetPhotoHashRequest\x1a\x16.photocop.PhotoCopHashB_\n\x1eorg.digitalwitnesslab.photocopB\rPhotoCopProtoP\x01Z,github.com/digital-witness-lab/whatup/protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'photo_cop_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'\n\x1eorg.digitalwitnesslab.photocopB\rPhotoCopProtoP\x01Z,github.com/digital-witness-lab/whatup/protos'
    _globals['_GETPHOTOHASHREQUEST']._serialized_start = 29
    _globals['_GETPHOTOHASHREQUEST']._serialized_end = 65
    _globals['_PHOTOCOPHASH']._serialized_start = 67
    _globals['_PHOTOCOPHASH']._serialized_end = 96
    _globals['_CHECKPHOTOREQUEST']._serialized_start = 98
    _globals['_CHECKPHOTOREQUEST']._serialized_end = 167
    _globals['_PHOTOCOPDECISION']._serialized_start = 169
    _globals['_PHOTOCOPDECISION']._serialized_end = 280
    _globals['_MATCHINFO']._serialized_start = 282
    _globals['_MATCHINFO']._serialized_end = 347
    _globals['_PHOTOCOP']._serialized_start = 350
    _globals['_PHOTOCOP']._serialized_end = 502