"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import collections.abc
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.internal.enum_type_wrapper
import google.protobuf.message
import google.protobuf.timestamp_pb2
import sys
import typing
from . import whatsappweb_pb2
if sys.version_info >= (3, 10):
    import typing as typing_extensions
else:
    import typing_extensions
DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

class _GroupPermission:
    ValueType = typing.NewType('ValueType', builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _GroupPermissionEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_GroupPermission.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    DENIED: _GroupPermission.ValueType
    READONLY: _GroupPermission.ValueType
    READWRITE: _GroupPermission.ValueType
    WRITEONLY: _GroupPermission.ValueType
    'useful?'
    UNKNOWN: _GroupPermission.ValueType

class GroupPermission(_GroupPermission, metaclass=_GroupPermissionEnumTypeWrapper):
    ...
DENIED: GroupPermission.ValueType
READONLY: GroupPermission.ValueType
READWRITE: GroupPermission.ValueType
WRITEONLY: GroupPermission.ValueType
'useful?'
UNKNOWN: GroupPermission.ValueType
global___GroupPermission = GroupPermission

@typing_extensions.final
class UnregisterOptions(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    def __init__(self) -> None:
        ...
global___UnregisterOptions = UnregisterOptions

@typing_extensions.final
class JoinedGroup(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    GROUPINFO_FIELD_NUMBER: builtins.int
    ACL_FIELD_NUMBER: builtins.int

    @property
    def groupInfo(self) -> global___GroupInfo:
        ...

    @property
    def acl(self) -> global___GroupACL:
        ...

    def __init__(self, *, groupInfo: global___GroupInfo | None=..., acl: global___GroupACL | None=...) -> None:
        ...

    def HasField(self, field_name: typing_extensions.Literal['acl', b'acl', 'groupInfo', b'groupInfo']) -> builtins.bool:
        ...

    def ClearField(self, field_name: typing_extensions.Literal['acl', b'acl', 'groupInfo', b'groupInfo']) -> None:
        ...
global___JoinedGroup = JoinedGroup

@typing_extensions.final
class GetJoinedGroupsOptions(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    def __init__(self) -> None:
        ...
global___GetJoinedGroupsOptions = GetJoinedGroupsOptions

@typing_extensions.final
class GetACLAllOptions(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    def __init__(self) -> None:
        ...
global___GetACLAllOptions = GetACLAllOptions

@typing_extensions.final
class RegisterOptions(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    CREDENTIALS_FIELD_NUMBER: builtins.int
    DEFAULTGROUPPERMISSION_FIELD_NUMBER: builtins.int

    @property
    def credentials(self) -> global___WUCredentials:
        ...
    defaultGroupPermission: global___GroupPermission.ValueType

    def __init__(self, *, credentials: global___WUCredentials | None=..., defaultGroupPermission: global___GroupPermission.ValueType=...) -> None:
        ...

    def HasField(self, field_name: typing_extensions.Literal['credentials', b'credentials']) -> builtins.bool:
        ...

    def ClearField(self, field_name: typing_extensions.Literal['credentials', b'credentials', 'defaultGroupPermission', b'defaultGroupPermission']) -> None:
        ...
global___RegisterOptions = RegisterOptions

@typing_extensions.final
class GroupACL(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    UPDATEDAT_FIELD_NUMBER: builtins.int
    JID_FIELD_NUMBER: builtins.int
    ISDEFAULT_FIELD_NUMBER: builtins.int
    PERMISSION_FIELD_NUMBER: builtins.int

    @property
    def updatedAt(self) -> google.protobuf.timestamp_pb2.Timestamp:
        ...

    @property
    def JID(self) -> global___JID:
        ...
    isDefault: builtins.bool
    permission: global___GroupPermission.ValueType

    def __init__(self, *, updatedAt: google.protobuf.timestamp_pb2.Timestamp | None=..., JID: global___JID | None=..., isDefault: builtins.bool=..., permission: global___GroupPermission.ValueType=...) -> None:
        ...

    def HasField(self, field_name: typing_extensions.Literal['JID', b'JID', 'updatedAt', b'updatedAt']) -> builtins.bool:
        ...

    def ClearField(self, field_name: typing_extensions.Literal['JID', b'JID', 'isDefault', b'isDefault', 'permission', b'permission', 'updatedAt', b'updatedAt']) -> None:
        ...
global___GroupACL = GroupACL

@typing_extensions.final
class DisappearingMessageOptions(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    class _DISAPPEARING_TIME:
        ValueType = typing.NewType('ValueType', builtins.int)
        V: typing_extensions.TypeAlias = ValueType

    class _DISAPPEARING_TIMEEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[DisappearingMessageOptions._DISAPPEARING_TIME.ValueType], builtins.type):
        DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
        TIMER_OFF: DisappearingMessageOptions._DISAPPEARING_TIME.ValueType
        TIMER_24HOUR: DisappearingMessageOptions._DISAPPEARING_TIME.ValueType
        TIMER_7DAYS: DisappearingMessageOptions._DISAPPEARING_TIME.ValueType
        TIMER_90DAYS: DisappearingMessageOptions._DISAPPEARING_TIME.ValueType

    class DISAPPEARING_TIME(_DISAPPEARING_TIME, metaclass=_DISAPPEARING_TIMEEnumTypeWrapper):
        ...
    TIMER_OFF: DisappearingMessageOptions.DISAPPEARING_TIME.ValueType
    TIMER_24HOUR: DisappearingMessageOptions.DISAPPEARING_TIME.ValueType
    TIMER_7DAYS: DisappearingMessageOptions.DISAPPEARING_TIME.ValueType
    TIMER_90DAYS: DisappearingMessageOptions.DISAPPEARING_TIME.ValueType
    RECIPIENT_FIELD_NUMBER: builtins.int
    DISAPPEARINGTIME_FIELD_NUMBER: builtins.int
    AUTOCLEARTIME_FIELD_NUMBER: builtins.int

    @property
    def recipient(self) -> global___JID:
        ...
    disappearingTime: global___DisappearingMessageOptions.DISAPPEARING_TIME.ValueType
    autoClearTime: builtins.int

    def __init__(self, *, recipient: global___JID | None=..., disappearingTime: global___DisappearingMessageOptions.DISAPPEARING_TIME.ValueType=..., autoClearTime: builtins.int=...) -> None:
        ...

    def HasField(self, field_name: typing_extensions.Literal['recipient', b'recipient']) -> builtins.bool:
        ...

    def ClearField(self, field_name: typing_extensions.Literal['autoClearTime', b'autoClearTime', 'disappearingTime', b'disappearingTime', 'recipient', b'recipient']) -> None:
        ...
global___DisappearingMessageOptions = DisappearingMessageOptions

@typing_extensions.final
class DisappearingMessageResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    def __init__(self) -> None:
        ...
global___DisappearingMessageResponse = DisappearingMessageResponse

@typing_extensions.final
class SendMessageOptions(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    RECIPIENT_FIELD_NUMBER: builtins.int
    SIMPLETEXT_FIELD_NUMBER: builtins.int
    SENDMESSAGEMEDIA_FIELD_NUMBER: builtins.int
    RAWMESSAGE_FIELD_NUMBER: builtins.int
    COMPOSINGTIME_FIELD_NUMBER: builtins.int

    @property
    def recipient(self) -> global___JID:
        ...
    simpleText: builtins.str

    @property
    def sendMessageMedia(self) -> global___SendMessageMedia:
        ...

    @property
    def rawMessage(self) -> whatsappweb_pb2.Message:
        ...
    composingTime: builtins.int
    'seconds'

    def __init__(self, *, recipient: global___JID | None=..., simpleText: builtins.str=..., sendMessageMedia: global___SendMessageMedia | None=..., rawMessage: whatsappweb_pb2.Message | None=..., composingTime: builtins.int=...) -> None:
        ...

    def HasField(self, field_name: typing_extensions.Literal['payload', b'payload', 'rawMessage', b'rawMessage', 'recipient', b'recipient', 'sendMessageMedia', b'sendMessageMedia', 'simpleText', b'simpleText']) -> builtins.bool:
        ...

    def ClearField(self, field_name: typing_extensions.Literal['composingTime', b'composingTime', 'payload', b'payload', 'rawMessage', b'rawMessage', 'recipient', b'recipient', 'sendMessageMedia', b'sendMessageMedia', 'simpleText', b'simpleText']) -> None:
        ...

    def WhichOneof(self, oneof_group: typing_extensions.Literal['payload', b'payload']) -> typing_extensions.Literal['simpleText', 'sendMessageMedia', 'rawMessage'] | None:
        ...
global___SendMessageOptions = SendMessageOptions

@typing_extensions.final
class SendMessageMedia(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    class _MediaType:
        ValueType = typing.NewType('ValueType', builtins.int)
        V: typing_extensions.TypeAlias = ValueType

    class _MediaTypeEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[SendMessageMedia._MediaType.ValueType], builtins.type):
        DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
        MediaImage: SendMessageMedia._MediaType.ValueType
        MediaVideo: SendMessageMedia._MediaType.ValueType
        MediaAudio: SendMessageMedia._MediaType.ValueType
        MediaDocument: SendMessageMedia._MediaType.ValueType

    class MediaType(_MediaType, metaclass=_MediaTypeEnumTypeWrapper):
        ...
    MediaImage: SendMessageMedia.MediaType.ValueType
    MediaVideo: SendMessageMedia.MediaType.ValueType
    MediaAudio: SendMessageMedia.MediaType.ValueType
    MediaDocument: SendMessageMedia.MediaType.ValueType
    MEDIATYPE_FIELD_NUMBER: builtins.int
    CONTENT_FIELD_NUMBER: builtins.int
    CAPTION_FIELD_NUMBER: builtins.int
    TITLE_FIELD_NUMBER: builtins.int
    FILENAME_FIELD_NUMBER: builtins.int
    MIMETYPE_FIELD_NUMBER: builtins.int
    mediaType: global___SendMessageMedia.MediaType.ValueType
    content: builtins.bytes
    caption: builtins.str
    title: builtins.str
    filename: builtins.str
    mimetype: builtins.str

    def __init__(self, *, mediaType: global___SendMessageMedia.MediaType.ValueType=..., content: builtins.bytes=..., caption: builtins.str=..., title: builtins.str=..., filename: builtins.str=..., mimetype: builtins.str=...) -> None:
        ...

    def ClearField(self, field_name: typing_extensions.Literal['caption', b'caption', 'content', b'content', 'filename', b'filename', 'mediaType', b'mediaType', 'mimetype', b'mimetype', 'title', b'title']) -> None:
        ...
global___SendMessageMedia = SendMessageMedia

@typing_extensions.final
class DownloadMediaOptions(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    MEDIAMESSAGE_FIELD_NUMBER: builtins.int
    INFO_FIELD_NUMBER: builtins.int

    @property
    def mediaMessage(self) -> whatsappweb_pb2.Message:
        ...

    @property
    def info(self) -> global___MessageInfo:
        ...

    def __init__(self, *, mediaMessage: whatsappweb_pb2.Message | None=..., info: global___MessageInfo | None=...) -> None:
        ...

    def HasField(self, field_name: typing_extensions.Literal['info', b'info', 'mediaMessage', b'mediaMessage']) -> builtins.bool:
        ...

    def ClearField(self, field_name: typing_extensions.Literal['info', b'info', 'mediaMessage', b'mediaMessage']) -> None:
        ...
global___DownloadMediaOptions = DownloadMediaOptions

@typing_extensions.final
class PendingHistoryOptions(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    HISTORYREADTIMEOUT_FIELD_NUMBER: builtins.int
    historyReadTimeout: builtins.int

    def __init__(self, *, historyReadTimeout: builtins.int=...) -> None:
        ...

    def ClearField(self, field_name: typing_extensions.Literal['historyReadTimeout', b'historyReadTimeout']) -> None:
        ...
global___PendingHistoryOptions = PendingHistoryOptions

@typing_extensions.final
class SendMessageReceipt(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    SENTAT_FIELD_NUMBER: builtins.int
    MESSAGEID_FIELD_NUMBER: builtins.int

    @property
    def sentAt(self) -> google.protobuf.timestamp_pb2.Timestamp:
        ...
    messageId: builtins.str

    def __init__(self, *, sentAt: google.protobuf.timestamp_pb2.Timestamp | None=..., messageId: builtins.str=...) -> None:
        ...

    def HasField(self, field_name: typing_extensions.Literal['sentAt', b'sentAt']) -> builtins.bool:
        ...

    def ClearField(self, field_name: typing_extensions.Literal['messageId', b'messageId', 'sentAt', b'sentAt']) -> None:
        ...
global___SendMessageReceipt = SendMessageReceipt

@typing_extensions.final
class InviteCode(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    LINK_FIELD_NUMBER: builtins.int
    link: builtins.str

    def __init__(self, *, link: builtins.str=...) -> None:
        ...

    def ClearField(self, field_name: typing_extensions.Literal['link', b'link']) -> None:
        ...
global___InviteCode = InviteCode

@typing_extensions.final
class Contact(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    FIRSTNAME_FIELD_NUMBER: builtins.int
    FULLNAME_FIELD_NUMBER: builtins.int
    PUSHNAME_FIELD_NUMBER: builtins.int
    BUSINESSNAME_FIELD_NUMBER: builtins.int
    firstName: builtins.str
    fullName: builtins.str
    pushName: builtins.str
    businessName: builtins.str

    def __init__(self, *, firstName: builtins.str=..., fullName: builtins.str=..., pushName: builtins.str=..., businessName: builtins.str=...) -> None:
        ...

    def ClearField(self, field_name: typing_extensions.Literal['businessName', b'businessName', 'firstName', b'firstName', 'fullName', b'fullName', 'pushName', b'pushName']) -> None:
        ...
global___Contact = Contact

@typing_extensions.final
class GroupName(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    NAME_FIELD_NUMBER: builtins.int
    UPDATEDAT_FIELD_NUMBER: builtins.int
    UPDATEDBY_FIELD_NUMBER: builtins.int
    name: builtins.str

    @property
    def updatedAt(self) -> google.protobuf.timestamp_pb2.Timestamp:
        ...

    @property
    def updatedBy(self) -> global___JID:
        ...

    def __init__(self, *, name: builtins.str=..., updatedAt: google.protobuf.timestamp_pb2.Timestamp | None=..., updatedBy: global___JID | None=...) -> None:
        ...

    def HasField(self, field_name: typing_extensions.Literal['updatedAt', b'updatedAt', 'updatedBy', b'updatedBy']) -> builtins.bool:
        ...

    def ClearField(self, field_name: typing_extensions.Literal['name', b'name', 'updatedAt', b'updatedAt', 'updatedBy', b'updatedBy']) -> None:
        ...
global___GroupName = GroupName

@typing_extensions.final
class GroupTopic(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    TOPIC_FIELD_NUMBER: builtins.int
    TOPICID_FIELD_NUMBER: builtins.int
    UPDATEDAT_FIELD_NUMBER: builtins.int
    UPDATEDBY_FIELD_NUMBER: builtins.int
    TOPICDELETED_FIELD_NUMBER: builtins.int
    topic: builtins.str
    topicId: builtins.str

    @property
    def updatedAt(self) -> google.protobuf.timestamp_pb2.Timestamp:
        ...

    @property
    def updatedBy(self) -> global___JID:
        ...
    topicDeleted: builtins.bool

    def __init__(self, *, topic: builtins.str=..., topicId: builtins.str=..., updatedAt: google.protobuf.timestamp_pb2.Timestamp | None=..., updatedBy: global___JID | None=..., topicDeleted: builtins.bool=...) -> None:
        ...

    def HasField(self, field_name: typing_extensions.Literal['updatedAt', b'updatedAt', 'updatedBy', b'updatedBy']) -> builtins.bool:
        ...

    def ClearField(self, field_name: typing_extensions.Literal['topic', b'topic', 'topicDeleted', b'topicDeleted', 'topicId', b'topicId', 'updatedAt', b'updatedAt', 'updatedBy', b'updatedBy']) -> None:
        ...
global___GroupTopic = GroupTopic

@typing_extensions.final
class GroupParticipant(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    JID_FIELD_NUMBER: builtins.int
    CONTACT_FIELD_NUMBER: builtins.int
    ISADMIN_FIELD_NUMBER: builtins.int
    ISSUPERADMIN_FIELD_NUMBER: builtins.int
    JOINERROR_FIELD_NUMBER: builtins.int

    @property
    def JID(self) -> global___JID:
        ...

    @property
    def contact(self) -> global___Contact:
        ...
    isAdmin: builtins.bool
    isSuperAdmin: builtins.bool
    joinError: builtins.int

    def __init__(self, *, JID: global___JID | None=..., contact: global___Contact | None=..., isAdmin: builtins.bool=..., isSuperAdmin: builtins.bool=..., joinError: builtins.int=...) -> None:
        ...

    def HasField(self, field_name: typing_extensions.Literal['JID', b'JID', 'contact', b'contact']) -> builtins.bool:
        ...

    def ClearField(self, field_name: typing_extensions.Literal['JID', b'JID', 'contact', b'contact', 'isAdmin', b'isAdmin', 'isSuperAdmin', b'isSuperAdmin', 'joinError', b'joinError']) -> None:
        ...
global___GroupParticipant = GroupParticipant

@typing_extensions.final
class GroupInfo(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    @typing_extensions.final
    class ProvenanceEntry(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor
        KEY_FIELD_NUMBER: builtins.int
        VALUE_FIELD_NUMBER: builtins.int
        key: builtins.str
        value: builtins.str

        def __init__(self, *, key: builtins.str=..., value: builtins.str=...) -> None:
            ...

        def ClearField(self, field_name: typing_extensions.Literal['key', b'key', 'value', b'value']) -> None:
            ...
    CREATEDAT_FIELD_NUMBER: builtins.int
    JID_FIELD_NUMBER: builtins.int
    GROUPNAME_FIELD_NUMBER: builtins.int
    GROUPTOPIC_FIELD_NUMBER: builtins.int
    MEMBERADDMODE_FIELD_NUMBER: builtins.int
    ISLOCKED_FIELD_NUMBER: builtins.int
    ISANNOUNCE_FIELD_NUMBER: builtins.int
    ISEPHEMERAL_FIELD_NUMBER: builtins.int
    PARTICIPANTVERSIONID_FIELD_NUMBER: builtins.int
    PARTICIPANTS_FIELD_NUMBER: builtins.int
    PARENTJID_FIELD_NUMBER: builtins.int
    PROVENANCE_FIELD_NUMBER: builtins.int

    @property
    def createdAt(self) -> google.protobuf.timestamp_pb2.Timestamp:
        """types.GroupInfo"""

    @property
    def JID(self) -> global___JID:
        ...

    @property
    def groupName(self) -> global___GroupName:
        ...

    @property
    def groupTopic(self) -> global___GroupTopic:
        ...
    memberAddMode: builtins.str
    isLocked: builtins.bool
    isAnnounce: builtins.bool
    isEphemeral: builtins.bool
    participantVersionId: builtins.str

    @property
    def participants(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___GroupParticipant]:
        ...

    @property
    def parentJID(self) -> global___JID:
        ...

    @property
    def provenance(self) -> google.protobuf.internal.containers.ScalarMap[builtins.str, builtins.str]:
        ...

    def __init__(self, *, createdAt: google.protobuf.timestamp_pb2.Timestamp | None=..., JID: global___JID | None=..., groupName: global___GroupName | None=..., groupTopic: global___GroupTopic | None=..., memberAddMode: builtins.str=..., isLocked: builtins.bool=..., isAnnounce: builtins.bool=..., isEphemeral: builtins.bool=..., participantVersionId: builtins.str=..., participants: collections.abc.Iterable[global___GroupParticipant] | None=..., parentJID: global___JID | None=..., provenance: collections.abc.Mapping[builtins.str, builtins.str] | None=...) -> None:
        ...

    def HasField(self, field_name: typing_extensions.Literal['JID', b'JID', 'createdAt', b'createdAt', 'groupName', b'groupName', 'groupTopic', b'groupTopic', 'parentJID', b'parentJID']) -> builtins.bool:
        ...

    def ClearField(self, field_name: typing_extensions.Literal['JID', b'JID', 'createdAt', b'createdAt', 'groupName', b'groupName', 'groupTopic', b'groupTopic', 'isAnnounce', b'isAnnounce', 'isEphemeral', b'isEphemeral', 'isLocked', b'isLocked', 'memberAddMode', b'memberAddMode', 'parentJID', b'parentJID', 'participantVersionId', b'participantVersionId', 'participants', b'participants', 'provenance', b'provenance']) -> None:
        ...
global___GroupInfo = GroupInfo

@typing_extensions.final
class ConnectionStatusOptions(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    def __init__(self) -> None:
        ...
global___ConnectionStatusOptions = ConnectionStatusOptions

@typing_extensions.final
class MessagesOptions(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    MARKMESSAGESREAD_FIELD_NUMBER: builtins.int
    markMessagesRead: builtins.bool
    'Whether to mark messages as read when they are recieved'

    def __init__(self, *, markMessagesRead: builtins.bool=...) -> None:
        ...

    def ClearField(self, field_name: typing_extensions.Literal['markMessagesRead', b'markMessagesRead']) -> None:
        ...
global___MessagesOptions = MessagesOptions

@typing_extensions.final
class SessionToken(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    TOKEN_FIELD_NUMBER: builtins.int
    EXPIRATIONTIME_FIELD_NUMBER: builtins.int
    token: builtins.str

    @property
    def expirationTime(self) -> google.protobuf.timestamp_pb2.Timestamp:
        ...

    def __init__(self, *, token: builtins.str=..., expirationTime: google.protobuf.timestamp_pb2.Timestamp | None=...) -> None:
        ...

    def HasField(self, field_name: typing_extensions.Literal['expirationTime', b'expirationTime']) -> builtins.bool:
        ...

    def ClearField(self, field_name: typing_extensions.Literal['expirationTime', b'expirationTime', 'token', b'token']) -> None:
        ...
global___SessionToken = SessionToken

@typing_extensions.final
class RegisterMessages(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    QRCODE_FIELD_NUMBER: builtins.int
    LOGGEDIN_FIELD_NUMBER: builtins.int
    TOKEN_FIELD_NUMBER: builtins.int
    qrcode: builtins.str
    loggedIn: builtins.bool

    @property
    def token(self) -> global___SessionToken:
        ...

    def __init__(self, *, qrcode: builtins.str=..., loggedIn: builtins.bool=..., token: global___SessionToken | None=...) -> None:
        ...

    def HasField(self, field_name: typing_extensions.Literal['token', b'token']) -> builtins.bool:
        ...

    def ClearField(self, field_name: typing_extensions.Literal['loggedIn', b'loggedIn', 'qrcode', b'qrcode', 'token', b'token']) -> None:
        ...
global___RegisterMessages = RegisterMessages

@typing_extensions.final
class WUCredentials(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    USERNAME_FIELD_NUMBER: builtins.int
    PASSPHRASE_FIELD_NUMBER: builtins.int
    username: builtins.str
    passphrase: builtins.str

    def __init__(self, *, username: builtins.str=..., passphrase: builtins.str=...) -> None:
        ...

    def ClearField(self, field_name: typing_extensions.Literal['passphrase', b'passphrase', 'username', b'username']) -> None:
        ...
global___WUCredentials = WUCredentials

@typing_extensions.final
class JID(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    USER_FIELD_NUMBER: builtins.int
    AGENT_FIELD_NUMBER: builtins.int
    DEVICE_FIELD_NUMBER: builtins.int
    SERVER_FIELD_NUMBER: builtins.int
    ISANONYMIZED_FIELD_NUMBER: builtins.int
    USERGEOCODE_FIELD_NUMBER: builtins.int
    user: builtins.str
    agent: builtins.int
    device: builtins.int
    server: builtins.str
    isAnonymized: builtins.bool
    userGeocode: builtins.str

    def __init__(self, *, user: builtins.str=..., agent: builtins.int=..., device: builtins.int=..., server: builtins.str=..., isAnonymized: builtins.bool=..., userGeocode: builtins.str=...) -> None:
        ...

    def ClearField(self, field_name: typing_extensions.Literal['agent', b'agent', 'device', b'device', 'isAnonymized', b'isAnonymized', 'server', b'server', 'user', b'user', 'userGeocode', b'userGeocode']) -> None:
        ...
global___JID = JID

@typing_extensions.final
class ConnectionStatus(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    ISCONNECTED_FIELD_NUMBER: builtins.int
    ISLOGGEDIN_FIELD_NUMBER: builtins.int
    TIMESTAMP_FIELD_NUMBER: builtins.int
    JID_FIELD_NUMBER: builtins.int
    JIDANON_FIELD_NUMBER: builtins.int
    isConnected: builtins.bool
    isLoggedIn: builtins.bool

    @property
    def timestamp(self) -> google.protobuf.timestamp_pb2.Timestamp:
        ...

    @property
    def JID(self) -> global___JID:
        ...

    @property
    def JIDAnon(self) -> global___JID:
        ...

    def __init__(self, *, isConnected: builtins.bool=..., isLoggedIn: builtins.bool=..., timestamp: google.protobuf.timestamp_pb2.Timestamp | None=..., JID: global___JID | None=..., JIDAnon: global___JID | None=...) -> None:
        ...

    def HasField(self, field_name: typing_extensions.Literal['JID', b'JID', 'JIDAnon', b'JIDAnon', 'timestamp', b'timestamp']) -> builtins.bool:
        ...

    def ClearField(self, field_name: typing_extensions.Literal['JID', b'JID', 'JIDAnon', b'JIDAnon', 'isConnected', b'isConnected', 'isLoggedIn', b'isLoggedIn', 'timestamp', b'timestamp']) -> None:
        ...
global___ConnectionStatus = ConnectionStatus

@typing_extensions.final
class WUMessage(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    @typing_extensions.final
    class ProvenanceEntry(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor
        KEY_FIELD_NUMBER: builtins.int
        VALUE_FIELD_NUMBER: builtins.int
        key: builtins.str
        value: builtins.str

        def __init__(self, *, key: builtins.str=..., value: builtins.str=...) -> None:
            ...

        def ClearField(self, field_name: typing_extensions.Literal['key', b'key', 'value', b'value']) -> None:
            ...
    INFO_FIELD_NUMBER: builtins.int
    CONTENT_FIELD_NUMBER: builtins.int
    MESSAGEPROPERTIES_FIELD_NUMBER: builtins.int
    PROVENANCE_FIELD_NUMBER: builtins.int
    ORIGINALMESSAGE_FIELD_NUMBER: builtins.int

    @property
    def info(self) -> global___MessageInfo:
        ...

    @property
    def content(self) -> global___MessageContent:
        ...

    @property
    def messageProperties(self) -> global___MessageProperties:
        ...

    @property
    def provenance(self) -> google.protobuf.internal.containers.ScalarMap[builtins.str, builtins.str]:
        ...

    @property
    def originalMessage(self) -> whatsappweb_pb2.Message:
        ...

    def __init__(self, *, info: global___MessageInfo | None=..., content: global___MessageContent | None=..., messageProperties: global___MessageProperties | None=..., provenance: collections.abc.Mapping[builtins.str, builtins.str] | None=..., originalMessage: whatsappweb_pb2.Message | None=...) -> None:
        ...

    def HasField(self, field_name: typing_extensions.Literal['content', b'content', 'info', b'info', 'messageProperties', b'messageProperties', 'originalMessage', b'originalMessage']) -> builtins.bool:
        ...

    def ClearField(self, field_name: typing_extensions.Literal['content', b'content', 'info', b'info', 'messageProperties', b'messageProperties', 'originalMessage', b'originalMessage', 'provenance', b'provenance']) -> None:
        ...
global___WUMessage = WUMessage

@typing_extensions.final
class MessageSource(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    CHAT_FIELD_NUMBER: builtins.int
    SENDER_FIELD_NUMBER: builtins.int
    RECIEVER_FIELD_NUMBER: builtins.int
    SENDERCONTACT_FIELD_NUMBER: builtins.int
    BROADCASTLISTOWNER_FIELD_NUMBER: builtins.int
    ISFROMME_FIELD_NUMBER: builtins.int
    ISGROUP_FIELD_NUMBER: builtins.int

    @property
    def chat(self) -> global___JID:
        ...

    @property
    def sender(self) -> global___JID:
        ...

    @property
    def reciever(self) -> global___JID:
        ...

    @property
    def senderContact(self) -> global___Contact:
        ...

    @property
    def broadcastListOwner(self) -> global___JID:
        ...
    isFromMe: builtins.bool
    isGroup: builtins.bool

    def __init__(self, *, chat: global___JID | None=..., sender: global___JID | None=..., reciever: global___JID | None=..., senderContact: global___Contact | None=..., broadcastListOwner: global___JID | None=..., isFromMe: builtins.bool=..., isGroup: builtins.bool=...) -> None:
        ...

    def HasField(self, field_name: typing_extensions.Literal['broadcastListOwner', b'broadcastListOwner', 'chat', b'chat', 'reciever', b'reciever', 'sender', b'sender', 'senderContact', b'senderContact']) -> builtins.bool:
        ...

    def ClearField(self, field_name: typing_extensions.Literal['broadcastListOwner', b'broadcastListOwner', 'chat', b'chat', 'isFromMe', b'isFromMe', 'isGroup', b'isGroup', 'reciever', b'reciever', 'sender', b'sender', 'senderContact', b'senderContact']) -> None:
        ...
global___MessageSource = MessageSource

@typing_extensions.final
class MessageInfo(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    SOURCE_FIELD_NUMBER: builtins.int
    TIMESTAMP_FIELD_NUMBER: builtins.int
    ID_FIELD_NUMBER: builtins.int
    PUSHNAME_FIELD_NUMBER: builtins.int
    TYPE_FIELD_NUMBER: builtins.int
    CATEGORY_FIELD_NUMBER: builtins.int
    MULTICAST_FIELD_NUMBER: builtins.int

    @property
    def source(self) -> global___MessageSource:
        ...

    @property
    def timestamp(self) -> google.protobuf.timestamp_pb2.Timestamp:
        ...
    id: builtins.str
    pushName: builtins.str
    type: builtins.str
    'TODO: turn into enum!'
    category: builtins.str
    'TODO: turn into enum!'
    multicast: builtins.bool

    def __init__(self, *, source: global___MessageSource | None=..., timestamp: google.protobuf.timestamp_pb2.Timestamp | None=..., id: builtins.str=..., pushName: builtins.str=..., type: builtins.str=..., category: builtins.str=..., multicast: builtins.bool=...) -> None:
        ...

    def HasField(self, field_name: typing_extensions.Literal['source', b'source', 'timestamp', b'timestamp']) -> builtins.bool:
        ...

    def ClearField(self, field_name: typing_extensions.Literal['category', b'category', 'id', b'id', 'multicast', b'multicast', 'pushName', b'pushName', 'source', b'source', 'timestamp', b'timestamp', 'type', b'type']) -> None:
        ...
global___MessageInfo = MessageInfo

@typing_extensions.final
class MessageContent(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    TITLE_FIELD_NUMBER: builtins.int
    TEXT_FIELD_NUMBER: builtins.int
    LINK_FIELD_NUMBER: builtins.int
    THUMBNAIL_FIELD_NUMBER: builtins.int
    MEDIAMESSAGE_FIELD_NUMBER: builtins.int
    INREFERENCETOID_FIELD_NUMBER: builtins.int
    title: builtins.str
    text: builtins.str
    link: builtins.str
    thumbnail: builtins.bytes

    @property
    def mediaMessage(self) -> global___MediaMessage:
        ...
    inReferenceToId: builtins.str

    def __init__(self, *, title: builtins.str=..., text: builtins.str=..., link: builtins.str=..., thumbnail: builtins.bytes=..., mediaMessage: global___MediaMessage | None=..., inReferenceToId: builtins.str=...) -> None:
        ...

    def HasField(self, field_name: typing_extensions.Literal['mediaMessage', b'mediaMessage']) -> builtins.bool:
        ...

    def ClearField(self, field_name: typing_extensions.Literal['inReferenceToId', b'inReferenceToId', 'link', b'link', 'mediaMessage', b'mediaMessage', 'text', b'text', 'thumbnail', b'thumbnail', 'title', b'title']) -> None:
        ...
global___MessageContent = MessageContent

@typing_extensions.final
class MessageProperties(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    ISEPHEMERAL_FIELD_NUMBER: builtins.int
    ISVIEWONCE_FIELD_NUMBER: builtins.int
    ISDOCUMENTWITHCAPTION_FIELD_NUMBER: builtins.int
    ISEDIT_FIELD_NUMBER: builtins.int
    ISDELETE_FIELD_NUMBER: builtins.int
    ISFORWARDED_FIELD_NUMBER: builtins.int
    FORWARDEDSCORE_FIELD_NUMBER: builtins.int
    ISINVITE_FIELD_NUMBER: builtins.int
    ISMEDIA_FIELD_NUMBER: builtins.int
    ISREACTION_FIELD_NUMBER: builtins.int
    isEphemeral: builtins.bool
    isViewOnce: builtins.bool
    isDocumentWithCaption: builtins.bool
    isEdit: builtins.bool
    isDelete: builtins.bool
    isForwarded: builtins.bool
    forwardedScore: builtins.int
    isInvite: builtins.bool
    isMedia: builtins.bool
    isReaction: builtins.bool

    def __init__(self, *, isEphemeral: builtins.bool=..., isViewOnce: builtins.bool=..., isDocumentWithCaption: builtins.bool=..., isEdit: builtins.bool=..., isDelete: builtins.bool=..., isForwarded: builtins.bool=..., forwardedScore: builtins.int=..., isInvite: builtins.bool=..., isMedia: builtins.bool=..., isReaction: builtins.bool=...) -> None:
        ...

    def ClearField(self, field_name: typing_extensions.Literal['forwardedScore', b'forwardedScore', 'isDelete', b'isDelete', 'isDocumentWithCaption', b'isDocumentWithCaption', 'isEdit', b'isEdit', 'isEphemeral', b'isEphemeral', 'isForwarded', b'isForwarded', 'isInvite', b'isInvite', 'isMedia', b'isMedia', 'isReaction', b'isReaction', 'isViewOnce', b'isViewOnce']) -> None:
        ...
global___MessageProperties = MessageProperties

@typing_extensions.final
class MediaMessage(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    IMAGEMESSAGE_FIELD_NUMBER: builtins.int
    VIDEOMESSAGE_FIELD_NUMBER: builtins.int
    AUDIOMESSAGE_FIELD_NUMBER: builtins.int
    DOCUMENTMESSAGE_FIELD_NUMBER: builtins.int
    STICKERMESSAGE_FIELD_NUMBER: builtins.int
    REACTIONMESSAGE_FIELD_NUMBER: builtins.int

    @property
    def imageMessage(self) -> whatsappweb_pb2.ImageMessage:
        ...

    @property
    def videoMessage(self) -> whatsappweb_pb2.VideoMessage:
        ...

    @property
    def audioMessage(self) -> whatsappweb_pb2.AudioMessage:
        ...

    @property
    def documentMessage(self) -> whatsappweb_pb2.DocumentMessage:
        ...

    @property
    def stickerMessage(self) -> whatsappweb_pb2.StickerMessage:
        ...

    @property
    def reactionMessage(self) -> whatsappweb_pb2.ReactionMessage:
        ...

    def __init__(self, *, imageMessage: whatsappweb_pb2.ImageMessage | None=..., videoMessage: whatsappweb_pb2.VideoMessage | None=..., audioMessage: whatsappweb_pb2.AudioMessage | None=..., documentMessage: whatsappweb_pb2.DocumentMessage | None=..., stickerMessage: whatsappweb_pb2.StickerMessage | None=..., reactionMessage: whatsappweb_pb2.ReactionMessage | None=...) -> None:
        ...

    def HasField(self, field_name: typing_extensions.Literal['audioMessage', b'audioMessage', 'documentMessage', b'documentMessage', 'imageMessage', b'imageMessage', 'payload', b'payload', 'reactionMessage', b'reactionMessage', 'stickerMessage', b'stickerMessage', 'videoMessage', b'videoMessage']) -> builtins.bool:
        ...

    def ClearField(self, field_name: typing_extensions.Literal['audioMessage', b'audioMessage', 'documentMessage', b'documentMessage', 'imageMessage', b'imageMessage', 'payload', b'payload', 'reactionMessage', b'reactionMessage', 'stickerMessage', b'stickerMessage', 'videoMessage', b'videoMessage']) -> None:
        ...

    def WhichOneof(self, oneof_group: typing_extensions.Literal['payload', b'payload']) -> typing_extensions.Literal['imageMessage', 'videoMessage', 'audioMessage', 'documentMessage', 'stickerMessage', 'reactionMessage'] | None:
        ...
global___MediaMessage = MediaMessage

@typing_extensions.final
class MediaContent(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    BODY_FIELD_NUMBER: builtins.int
    Body: builtins.bytes

    def __init__(self, *, Body: builtins.bytes=...) -> None:
        ...

    def ClearField(self, field_name: typing_extensions.Literal['Body', b'Body']) -> None:
        ...
global___MediaContent = MediaContent