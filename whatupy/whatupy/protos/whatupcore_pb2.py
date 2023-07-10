"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from . import whatsappweb_pb2 as whatsappweb__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10whatupcore.proto\x12\x06protos\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x11whatsappweb.proto"\x92\x01\n\x12SendMessageOptions\x12\x1e\n\trecipient\x18\x01 \x01(\x0b2\x0b.protos.JID\x12\x14\n\nsimpleText\x18\x02 \x01(\tH\x00\x12$\n\nrawMessage\x18\x03 \x01(\x0b2\x0e.proto.MessageH\x00\x12\x15\n\rcomposingTime\x18\x04 \x01(\rB\t\n\x07payload"_\n\x14DownloadMediaOptions\x12$\n\x0cmediaMessage\x18\x01 \x01(\x0b2\x0e.proto.Message\x12!\n\x04info\x18\x02 \x01(\x0b2\x13.protos.MessageInfo"3\n\x15PendingHistoryOptions\x12\x1a\n\x12historyReadTimeout\x18\x01 \x01(\r"S\n\x12SendMessageReceipt\x12*\n\x06sentAt\x18\x01 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\x11\n\tmessageId\x18\x02 \x01(\t"\x1a\n\nInviteCode\x12\x0c\n\x04link\x18\x01 \x01(\t"h\n\tGroupName\x12\x0c\n\x04name\x18\x01 \x01(\t\x12-\n\tupdatedAt\x18\x02 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\x1e\n\tupdatedBy\x18\x03 \x01(\x0b2\x0b.protos.JID"\x91\x01\n\nGroupTopic\x12\r\n\x05topic\x18\x01 \x01(\t\x12\x0f\n\x07topicId\x18\x02 \x01(\t\x12-\n\tupdatedAt\x18\x03 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\x1e\n\tupdatedBy\x18\x04 \x01(\x0b2\x0b.protos.JID\x12\x14\n\x0ctopicDeleted\x18\x05 \x01(\x08"f\n\x10GroupParticipant\x12\x18\n\x03JID\x18\x01 \x01(\x0b2\x0b.protos.JID\x12\x0f\n\x07isAdmin\x18\x02 \x01(\x08\x12\x14\n\x0cisSuperAdmin\x18\x03 \x01(\x08\x12\x11\n\tjoinError\x18\x04 \x01(\r"\xe2\x02\n\tGroupInfo\x12-\n\tcreatedAt\x18\x01 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\x18\n\x03JID\x18\x02 \x01(\x0b2\x0b.protos.JID\x12$\n\tgroupName\x18\x03 \x01(\x0b2\x11.protos.GroupName\x12&\n\ngroupTopic\x18\x04 \x01(\x0b2\x12.protos.GroupTopic\x12\x15\n\rmemberAddMode\x18\x05 \x01(\t\x12\x10\n\x08isLocked\x18\x06 \x01(\x08\x12\x12\n\nisAnnounce\x18\x07 \x01(\x08\x12\x13\n\x0bisEphemeral\x18\x08 \x01(\x08\x12\x1c\n\x14participantVersionId\x18\t \x01(\t\x12.\n\x0cparticipants\x18\n \x03(\x0b2\x18.protos.GroupParticipant\x12\x1e\n\tparentJID\x18\x0b \x01(\x0b2\x0b.protos.JID"\x19\n\x17ConnectionStatusOptions"+\n\x0fMessagesOptions\x12\x18\n\x10markMessagesRead\x18\x01 \x01(\x08"Q\n\x0cSessionToken\x12\r\n\x05token\x18\x01 \x01(\t\x122\n\x0eexpirationTime\x18\x02 \x01(\x0b2\x1a.google.protobuf.Timestamp"Y\n\x10RegisterMessages\x12\x0e\n\x06qrcode\x18\x01 \x01(\t\x12\x10\n\x08loggedIn\x18\x02 \x01(\x08\x12#\n\x05token\x18\x03 \x01(\x0b2\x14.protos.SessionToken"5\n\rWUCredentials\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x12\n\npassphrase\x18\x02 \x01(\t"N\n\x03JID\x12\x0c\n\x04user\x18\x01 \x01(\t\x12\r\n\x05agent\x18\x02 \x01(\r\x12\x0e\n\x06device\x18\x03 \x01(\r\x12\x0e\n\x06server\x18\x04 \x01(\t\x12\n\n\x02ad\x18\x05 \x01(\x08"j\n\x10ConnectionStatus\x12\x13\n\x0bisConnected\x18\x01 \x01(\x08\x12\x12\n\nisLoggedIn\x18\x02 \x01(\x08\x12-\n\ttimestamp\x18\x03 \x01(\x0b2\x1a.google.protobuf.Timestamp"\xb6\x01\n\tWUMessage\x12!\n\x04info\x18\x01 \x01(\x0b2\x13.protos.MessageInfo\x12\'\n\x07content\x18\x02 \x01(\x0b2\x16.protos.MessageContent\x124\n\x11messageProperties\x18\x03 \x01(\x0b2\x19.protos.MessageProperties\x12\'\n\x0foriginalMessage\x18\x04 \x01(\x0b2\x0e.proto.Message"\x93\x01\n\rMessageSource\x12\x19\n\x04chat\x18\x01 \x01(\x0b2\x0b.protos.JID\x12\x1b\n\x06sender\x18\x02 \x01(\x0b2\x0b.protos.JID\x12\'\n\x12broadcastListOwner\x18\x03 \x01(\x0b2\x0b.protos.JID\x12\x10\n\x08isFromMe\x18\x04 \x01(\x08\x12\x0f\n\x07isGroup\x18\x05 \x01(\x08"\xb4\x01\n\x0bMessageInfo\x12%\n\x06source\x18\x01 \x01(\x0b2\x15.protos.MessageSource\x12-\n\ttimestamp\x18\x02 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\n\n\x02id\x18\x03 \x01(\t\x12\x10\n\x08pushName\x18\x04 \x01(\t\x12\x0c\n\x04type\x18\x05 \x01(\t\x12\x10\n\x08category\x18\x06 \x01(\t\x12\x11\n\tmulticast\x18\x07 \x01(\x08"\xe9\x01\n\x0eMessageContent\x12\r\n\x05title\x18\x01 \x01(\t\x12\x0c\n\x04text\x18\x02 \x01(\t\x12\x0c\n\x04link\x18\x03 \x01(\t\x12:\n\nproperties\x18\x04 \x03(\x0b2&.protos.MessageContent.PropertiesEntry\x12\x11\n\tthumbnail\x18\x05 \x01(\x0c\x12*\n\x0cmediaMessage\x18\x06 \x01(\x0b2\x14.protos.MediaMessage\x1a1\n\x0fPropertiesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x028\x01"\xaa\x01\n\x11MessageProperties\x12\x13\n\x0bisEphemeral\x18\x01 \x01(\x08\x12\x12\n\nisViewOnce\x18\x02 \x01(\x08\x12\x1d\n\x15isDocumentWithCaption\x18\x03 \x01(\x08\x12\x0e\n\x06isEdit\x18\x04 \x01(\x08\x12\x13\n\x0bisForwarded\x18\x05 \x01(\x08\x12\x16\n\x0eforwardedScore\x18\x06 \x01(\r\x12\x10\n\x08isInvite\x18\x07 \x01(\x08"\xb7\x02\n\x0cMediaMessage\x12+\n\x0cimageMessage\x18\x01 \x01(\x0b2\x13.proto.ImageMessageH\x00\x12+\n\x0cvideoMessage\x18\x02 \x01(\x0b2\x13.proto.VideoMessageH\x00\x12+\n\x0caudioMessage\x18\x03 \x01(\x0b2\x13.proto.AudioMessageH\x00\x121\n\x0fdocumentMessage\x18\x04 \x01(\x0b2\x16.proto.DocumentMessageH\x00\x12/\n\x0estickerMessage\x18\x05 \x01(\x0b2\x15.proto.StickerMessageH\x00\x121\n\x0freactionMessage\x18\x06 \x01(\x0b2\x16.proto.ReactionMessageH\x00B\t\n\x07payload"\x1c\n\x0cMediaContent\x12\x0c\n\x04Body\x18\x01 \x01(\x0c2\xc5\x01\n\x0eWhatUpCoreAuth\x126\n\x05Login\x12\x15.protos.WUCredentials\x1a\x14.protos.SessionToken"\x00\x12?\n\x08Register\x12\x15.protos.WUCredentials\x1a\x18.protos.RegisterMessages"\x000\x01\x12:\n\nRenewToken\x12\x14.protos.SessionToken\x1a\x14.protos.SessionToken"\x002\xa1\x04\n\nWhatUpCore\x12R\n\x13GetConnectionStatus\x12\x1f.protos.ConnectionStatusOptions\x1a\x18.protos.ConnectionStatus"\x00\x120\n\x0cGetGroupInfo\x12\x0b.protos.JID\x1a\x11.protos.GroupInfo"\x00\x12=\n\x12GetGroupInfoInvite\x12\x12.protos.InviteCode\x1a\x11.protos.GroupInfo"\x00\x124\n\tJoinGroup\x12\x12.protos.InviteCode\x1a\x11.protos.GroupInfo"\x00\x12=\n\x0bGetMessages\x12\x17.protos.MessagesOptions\x1a\x11.protos.WUMessage"\x000\x01\x12I\n\x11GetPendingHistory\x12\x1d.protos.PendingHistoryOptions\x1a\x11.protos.WUMessage"\x000\x01\x12E\n\rDownloadMedia\x12\x1c.protos.DownloadMediaOptions\x1a\x14.protos.MediaContent"\x00\x12G\n\x0bSendMessage\x12\x1a.protos.SendMessageOptions\x1a\x1a.protos.SendMessageReceipt"\x00B.Z,github.com/digital-witness-lab/whatup/protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'whatupcore_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'Z,github.com/digital-witness-lab/whatup/protos'
    _MESSAGECONTENT_PROPERTIESENTRY._options = None
    _MESSAGECONTENT_PROPERTIESENTRY._serialized_options = b'8\x01'
    _globals['_SENDMESSAGEOPTIONS']._serialized_start = 81
    _globals['_SENDMESSAGEOPTIONS']._serialized_end = 227
    _globals['_DOWNLOADMEDIAOPTIONS']._serialized_start = 229
    _globals['_DOWNLOADMEDIAOPTIONS']._serialized_end = 324
    _globals['_PENDINGHISTORYOPTIONS']._serialized_start = 326
    _globals['_PENDINGHISTORYOPTIONS']._serialized_end = 377
    _globals['_SENDMESSAGERECEIPT']._serialized_start = 379
    _globals['_SENDMESSAGERECEIPT']._serialized_end = 462
    _globals['_INVITECODE']._serialized_start = 464
    _globals['_INVITECODE']._serialized_end = 490
    _globals['_GROUPNAME']._serialized_start = 492
    _globals['_GROUPNAME']._serialized_end = 596
    _globals['_GROUPTOPIC']._serialized_start = 599
    _globals['_GROUPTOPIC']._serialized_end = 744
    _globals['_GROUPPARTICIPANT']._serialized_start = 746
    _globals['_GROUPPARTICIPANT']._serialized_end = 848
    _globals['_GROUPINFO']._serialized_start = 851
    _globals['_GROUPINFO']._serialized_end = 1205
    _globals['_CONNECTIONSTATUSOPTIONS']._serialized_start = 1207
    _globals['_CONNECTIONSTATUSOPTIONS']._serialized_end = 1232
    _globals['_MESSAGESOPTIONS']._serialized_start = 1234
    _globals['_MESSAGESOPTIONS']._serialized_end = 1277
    _globals['_SESSIONTOKEN']._serialized_start = 1279
    _globals['_SESSIONTOKEN']._serialized_end = 1360
    _globals['_REGISTERMESSAGES']._serialized_start = 1362
    _globals['_REGISTERMESSAGES']._serialized_end = 1451
    _globals['_WUCREDENTIALS']._serialized_start = 1453
    _globals['_WUCREDENTIALS']._serialized_end = 1506
    _globals['_JID']._serialized_start = 1508
    _globals['_JID']._serialized_end = 1586
    _globals['_CONNECTIONSTATUS']._serialized_start = 1588
    _globals['_CONNECTIONSTATUS']._serialized_end = 1694
    _globals['_WUMESSAGE']._serialized_start = 1697
    _globals['_WUMESSAGE']._serialized_end = 1879
    _globals['_MESSAGESOURCE']._serialized_start = 1882
    _globals['_MESSAGESOURCE']._serialized_end = 2029
    _globals['_MESSAGEINFO']._serialized_start = 2032
    _globals['_MESSAGEINFO']._serialized_end = 2212
    _globals['_MESSAGECONTENT']._serialized_start = 2215
    _globals['_MESSAGECONTENT']._serialized_end = 2448
    _globals['_MESSAGECONTENT_PROPERTIESENTRY']._serialized_start = 2399
    _globals['_MESSAGECONTENT_PROPERTIESENTRY']._serialized_end = 2448
    _globals['_MESSAGEPROPERTIES']._serialized_start = 2451
    _globals['_MESSAGEPROPERTIES']._serialized_end = 2621
    _globals['_MEDIAMESSAGE']._serialized_start = 2624
    _globals['_MEDIAMESSAGE']._serialized_end = 2935
    _globals['_MEDIACONTENT']._serialized_start = 2937
    _globals['_MEDIACONTENT']._serialized_end = 2965
    _globals['_WHATUPCOREAUTH']._serialized_start = 2968
    _globals['_WHATUPCOREAUTH']._serialized_end = 3165
    _globals['_WHATUPCORE']._serialized_start = 3168
    _globals['_WHATUPCORE']._serialized_end = 3713