"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from . import whatsappweb_pb2 as whatsappweb__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10whatupcore.proto\x12\x06protos\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x11whatsappweb.proto"w\n\rMessageStream\x12-\n\ttimestamp\x18\x01 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\x13\n\x0bisHeartbeat\x18\x02 \x01(\x08\x12"\n\x07content\x18\x14 \x01(\x0b2\x11.protos.WUMessage"\x13\n\x11UnregisterOptions"R\n\x0bJoinedGroup\x12$\n\tgroupInfo\x18\x01 \x01(\x0b2\x11.protos.GroupInfo\x12\x1d\n\x03acl\x18\x14 \x01(\x0b2\x10.protos.GroupACL"\x18\n\x16GetJoinedGroupsOptions"\x12\n\x10GetACLAllOptions"\x8a\x01\n\x0fRegisterOptions\x12*\n\x0bcredentials\x18\x01 \x01(\x0b2\x15.protos.WUCredentials\x127\n\x16defaultGroupPermission\x18\n \x01(\x0e2\x17.protos.GroupPermission\x12\x12\n\ngetHistory\x18\x0b \x01(\x08"\x93\x01\n\x08GroupACL\x12-\n\tupdatedAt\x18\x01 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\x18\n\x03JID\x18\x02 \x01(\x0b2\x0b.protos.JID\x12\x11\n\tisDefault\x18\x03 \x01(\x08\x12+\n\npermission\x18\x14 \x01(\x0e2\x17.protos.GroupPermission"\xfc\x01\n\x1aDisappearingMessageOptions\x12\x1e\n\trecipient\x18\x01 \x01(\x0b2\x0b.protos.JID\x12N\n\x10disappearingTime\x18\x02 \x01(\x0e24.protos.DisappearingMessageOptions.DISAPPEARING_TIME\x12\x15\n\rautoClearTime\x18\x03 \x01(\r"W\n\x11DISAPPEARING_TIME\x12\r\n\tTIMER_OFF\x10\x00\x12\x10\n\x0cTIMER_24HOUR\x10\x01\x12\x0f\n\x0bTIMER_7DAYS\x10\x02\x12\x10\n\x0cTIMER_90DAYS\x10\x03"\x1d\n\x1bDisappearingMessageResponse"\xc8\x01\n\x12SendMessageOptions\x12\x1e\n\trecipient\x18\x01 \x01(\x0b2\x0b.protos.JID\x12\x14\n\nsimpleText\x18\x14 \x01(\tH\x00\x124\n\x10sendMessageMedia\x18\x15 \x01(\x0b2\x18.protos.SendMessageMediaH\x00\x12$\n\nrawMessage\x18\x16 \x01(\x0b2\x0e.proto.MessageH\x00\x12\x15\n\rcomposingTime\x18< \x01(\rB\t\n\x07payload"\xee\x01\n\x10SendMessageMedia\x125\n\tmediaType\x18\x14 \x01(\x0e2".protos.SendMessageMedia.MediaType\x12\x0f\n\x07content\x18\x15 \x01(\x0c\x12\x0f\n\x07caption\x18\x16 \x01(\t\x12\r\n\x05title\x18\x17 \x01(\t\x12\x10\n\x08filename\x18\x18 \x01(\t\x12\x10\n\x08mimetype\x18( \x01(\t"N\n\tMediaType\x12\x0e\n\nMediaImage\x10\x00\x12\x0e\n\nMediaVideo\x10\x01\x12\x0e\n\nMediaAudio\x10\x02\x12\x11\n\rMediaDocument\x10\x03"_\n\x14DownloadMediaOptions\x12$\n\x0cmediaMessage\x18\x01 \x01(\x0b2\x0e.proto.Message\x12!\n\x04info\x18\x02 \x01(\x0b2\x13.protos.MessageInfo"\x7f\n\x15HistoryRequestOptions\x12\x19\n\x04chat\x18\x01 \x01(\x0b2\x0b.protos.JID\x12\n\n\x02id\x18\x02 \x01(\t\x12\x10\n\x08isFromMe\x18\x03 \x01(\x08\x12-\n\ttimestamp\x18\x04 \x01(\x0b2\x1a.google.protobuf.Timestamp"K\n\x15PendingHistoryOptions\x12\x18\n\x10heartbeatTimeout\x18( \x01(\rJ\x04\x08\x01\x10\x02R\x12historyReadTimeout"S\n\x12SendMessageReceipt\x12*\n\x06sentAt\x18\x01 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\x11\n\tmessageId\x18\x02 \x01(\t"\x1a\n\nInviteCode\x12\x0c\n\x04link\x18\x01 \x01(\t"V\n\x07Contact\x12\x11\n\tfirstName\x18\x01 \x01(\t\x12\x10\n\x08fullName\x18\x02 \x01(\t\x12\x10\n\x08pushName\x18\x03 \x01(\t\x12\x14\n\x0cbusinessName\x18\x04 \x01(\t"h\n\tGroupName\x12\x0c\n\x04name\x18\x01 \x01(\t\x12-\n\tupdatedAt\x18\x02 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\x1e\n\tupdatedBy\x18\x03 \x01(\x0b2\x0b.protos.JID"\x91\x01\n\nGroupTopic\x12\r\n\x05topic\x18\x01 \x01(\t\x12\x0f\n\x07topicId\x18\x02 \x01(\t\x12-\n\tupdatedAt\x18\x03 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\x1e\n\tupdatedBy\x18\x04 \x01(\x0b2\x0b.protos.JID\x12\x14\n\x0ctopicDeleted\x18\x05 \x01(\x08"\x88\x01\n\x10GroupParticipant\x12\x18\n\x03JID\x18\x01 \x01(\x0b2\x0b.protos.JID\x12 \n\x07contact\x18\x02 \x01(\x0b2\x0f.protos.Contact\x12\x0f\n\x07isAdmin\x182 \x01(\x08\x12\x14\n\x0cisSuperAdmin\x183 \x01(\x08\x12\x11\n\tjoinError\x184 \x01(\r"\xe8\x04\n\tGroupInfo\x12-\n\tcreatedAt\x18\x01 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\x18\n\x03JID\x18\x02 \x01(\x0b2\x0b.protos.JID\x12\x1d\n\x08ownerJID\x18\x03 \x01(\x0b2\x0b.protos.JID\x12$\n\tgroupName\x18\x14 \x01(\x0b2\x11.protos.GroupName\x12&\n\ngroupTopic\x18\x15 \x01(\x0b2\x12.protos.GroupTopic\x12\x15\n\rmemberAddMode\x18( \x01(\t\x12\x10\n\x08isLocked\x18) \x01(\x08\x12\x12\n\nisAnnounce\x18* \x01(\x08\x12\x13\n\x0bisEphemeral\x18+ \x01(\x08\x12\x19\n\x11disappearingTimer\x180 \x01(\r\x12\x13\n\x0bisCommunity\x18, \x01(\x08\x12\x1f\n\x17isCommunityDefaultGroup\x18- \x01(\x08\x12\x15\n\risPartialInfo\x18. \x01(\x08\x12\x13\n\x0bisIncognito\x18/ \x01(\x08\x12\x1c\n\x14participantVersionId\x18< \x01(\t\x12.\n\x0cparticipants\x18= \x03(\x0b2\x18.protos.GroupParticipant\x12\x1e\n\tparentJID\x18P \x01(\x0b2\x0b.protos.JID\x125\n\nprovenance\x18d \x03(\x0b2!.protos.GroupInfo.ProvenanceEntry\x1a1\n\x0fProvenanceEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x028\x01"\x19\n\x17ConnectionStatusOptions"\x7f\n\x0fMessagesOptions\x12\x18\n\x10markMessagesRead\x18\x01 \x01(\x08\x128\n\x14lastMessageTimestamp\x18\x14 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\x18\n\x10heartbeatTimeout\x18( \x01(\r"Q\n\x0cSessionToken\x12\r\n\x05token\x18\x01 \x01(\t\x122\n\x0eexpirationTime\x18\x02 \x01(\x0b2\x1a.google.protobuf.Timestamp"Y\n\x10RegisterMessages\x12\x0e\n\x06qrcode\x18\x01 \x01(\t\x12\x10\n\x08loggedIn\x18\x02 \x01(\x08\x12#\n\x05token\x18\x03 \x01(\x0b2\x14.protos.SessionToken"5\n\rWUCredentials\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x12\n\npassphrase\x18\x02 \x01(\t"w\n\x03JID\x12\x0c\n\x04user\x18\x01 \x01(\t\x12\r\n\x05agent\x18\x02 \x01(\r\x12\x0e\n\x06device\x18\x03 \x01(\r\x12\x0e\n\x06server\x18\x04 \x01(\t\x12\x14\n\x0cisAnonymized\x18\x14 \x01(\x08\x12\x13\n\x0buserGeocode\x182 \x01(\tJ\x04\x08\x05\x10\x06R\x02ad"\xa2\x01\n\x10ConnectionStatus\x12\x13\n\x0bisConnected\x18\x01 \x01(\x08\x12\x12\n\nisLoggedIn\x18\x02 \x01(\x08\x12-\n\ttimestamp\x18\x03 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\x18\n\x03JID\x18\x14 \x01(\x0b2\x0b.protos.JID\x12\x1c\n\x07JIDAnon\x18\x15 \x01(\x0b2\x0b.protos.JID"\xa0\x02\n\tWUMessage\x12!\n\x04info\x18\x01 \x01(\x0b2\x13.protos.MessageInfo\x12\'\n\x07content\x18\x02 \x01(\x0b2\x16.protos.MessageContent\x124\n\x11messageProperties\x18\x03 \x01(\x0b2\x19.protos.MessageProperties\x125\n\nprovenance\x18Z \x03(\x0b2!.protos.WUMessage.ProvenanceEntry\x12\'\n\x0foriginalMessage\x18d \x01(\x0b2\x0e.proto.Message\x1a1\n\x0fProvenanceEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x028\x01"\xda\x01\n\rMessageSource\x12\x19\n\x04chat\x18\x01 \x01(\x0b2\x0b.protos.JID\x12\x1b\n\x06sender\x18\x02 \x01(\x0b2\x0b.protos.JID\x12\x1d\n\x08reciever\x18\x03 \x01(\x0b2\x0b.protos.JID\x12&\n\rsenderContact\x18\x04 \x01(\x0b2\x0f.protos.Contact\x12\'\n\x12broadcastListOwner\x18\x14 \x01(\x0b2\x0b.protos.JID\x12\x10\n\x08isFromMe\x182 \x01(\x08\x12\x0f\n\x07isGroup\x183 \x01(\x08"\xb4\x01\n\x0bMessageInfo\x12%\n\x06source\x18\x01 \x01(\x0b2\x15.protos.MessageSource\x12-\n\ttimestamp\x18\x02 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\n\n\x02id\x18\x03 \x01(\t\x12\x10\n\x08pushName\x18\x04 \x01(\t\x12\x0c\n\x04type\x18\x05 \x01(\t\x12\x10\n\x08category\x18\x06 \x01(\t\x12\x11\n\tmulticast\x18\x07 \x01(\x08"\x93\x01\n\x0eMessageContent\x12\r\n\x05title\x18\x01 \x01(\t\x12\x0c\n\x04text\x18\x02 \x01(\t\x12\x0c\n\x04link\x18\x03 \x01(\t\x12\x11\n\tthumbnail\x18\x05 \x01(\x0c\x12*\n\x0cmediaMessage\x18\x06 \x01(\x0b2\x14.protos.MediaMessage\x12\x17\n\x0finReferenceToId\x18\x07 \x01(\t"\xe1\x01\n\x11MessageProperties\x12\x13\n\x0bisEphemeral\x18\x01 \x01(\x08\x12\x12\n\nisViewOnce\x18\x02 \x01(\x08\x12\x1d\n\x15isDocumentWithCaption\x18\x03 \x01(\x08\x12\x0e\n\x06isEdit\x18\x04 \x01(\x08\x12\x10\n\x08isDelete\x18\x05 \x01(\x08\x12\x13\n\x0bisForwarded\x18\x06 \x01(\x08\x12\x16\n\x0eforwardedScore\x18\x07 \x01(\r\x12\x10\n\x08isInvite\x18\x08 \x01(\x08\x12\x0f\n\x07isMedia\x18\t \x01(\x08\x12\x12\n\nisReaction\x18\n \x01(\x08"\xb7\x02\n\x0cMediaMessage\x12+\n\x0cimageMessage\x18\x01 \x01(\x0b2\x13.proto.ImageMessageH\x00\x12+\n\x0cvideoMessage\x18\x02 \x01(\x0b2\x13.proto.VideoMessageH\x00\x12+\n\x0caudioMessage\x18\x03 \x01(\x0b2\x13.proto.AudioMessageH\x00\x121\n\x0fdocumentMessage\x18\x04 \x01(\x0b2\x16.proto.DocumentMessageH\x00\x12/\n\x0estickerMessage\x18\x05 \x01(\x0b2\x15.proto.StickerMessageH\x00\x121\n\x0freactionMessage\x18\x06 \x01(\x0b2\x16.proto.ReactionMessageH\x00B\t\n\x07payload"\x1c\n\x0cMediaContent\x12\x0c\n\x04Body\x18\x01 \x01(\x0c*V\n\x0fGroupPermission\x12\n\n\x06DENIED\x10\x00\x12\x0c\n\x08READONLY\x10\x01\x12\r\n\tREADWRITE\x10\x02\x12\r\n\tWRITEONLY\x10\x03\x12\x0b\n\x07UNKNOWN\x10\x142\xc7\x01\n\x0eWhatUpCoreAuth\x126\n\x05Login\x12\x15.protos.WUCredentials\x1a\x14.protos.SessionToken"\x00\x12A\n\x08Register\x12\x17.protos.RegisterOptions\x1a\x18.protos.RegisterMessages"\x000\x01\x12:\n\nRenewToken\x12\x14.protos.SessionToken\x1a\x14.protos.SessionToken"\x002\xbd\x08\n\nWhatUpCore\x12R\n\x13GetConnectionStatus\x12\x1f.protos.ConnectionStatusOptions\x1a\x18.protos.ConnectionStatus"\x00\x12;\n\tGetACLAll\x12\x18.protos.GetACLAllOptions\x1a\x10.protos.GroupACL"\x000\x01\x12.\n\x06SetACL\x12\x10.protos.GroupACL\x1a\x10.protos.GroupACL"\x00\x12)\n\x06GetACL\x12\x0b.protos.JID\x1a\x10.protos.GroupACL"\x00\x12J\n\x0fGetJoinedGroups\x12\x1e.protos.GetJoinedGroupsOptions\x1a\x13.protos.JoinedGroup"\x000\x01\x120\n\x0cGetGroupInfo\x12\x0b.protos.JID\x1a\x11.protos.GroupInfo"\x00\x126\n\x10GetCommunityInfo\x12\x0b.protos.JID\x1a\x11.protos.GroupInfo"\x000\x01\x12=\n\x12GetGroupInfoInvite\x12\x12.protos.InviteCode\x1a\x11.protos.GroupInfo"\x00\x124\n\tJoinGroup\x12\x12.protos.InviteCode\x1a\x11.protos.GroupInfo"\x00\x12A\n\x0bGetMessages\x12\x17.protos.MessagesOptions\x1a\x15.protos.MessageStream"\x000\x01\x12M\n\x11GetPendingHistory\x12\x1d.protos.PendingHistoryOptions\x1a\x15.protos.MessageStream"\x000\x01\x12H\n\x12RequestChatHistory\x12\x1d.protos.HistoryRequestOptions\x1a\x11.protos.GroupInfo"\x00\x12E\n\rDownloadMedia\x12\x1c.protos.DownloadMediaOptions\x1a\x14.protos.MediaContent"\x00\x12G\n\x0bSendMessage\x12\x1a.protos.SendMessageOptions\x1a\x1a.protos.SendMessageReceipt"\x00\x12g\n\x1aSetDisappearingMessageTime\x12".protos.DisappearingMessageOptions\x1a#.protos.DisappearingMessageResponse"\x00\x12C\n\nUnregister\x12\x19.protos.UnregisterOptions\x1a\x18.protos.ConnectionStatus"\x00B.Z,github.com/digital-witness-lab/whatup/protosb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'whatupcore_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'Z,github.com/digital-witness-lab/whatup/protos'
    _GROUPINFO_PROVENANCEENTRY._options = None
    _GROUPINFO_PROVENANCEENTRY._serialized_options = b'8\x01'
    _WUMESSAGE_PROVENANCEENTRY._options = None
    _WUMESSAGE_PROVENANCEENTRY._serialized_options = b'8\x01'
    _globals['_GROUPPERMISSION']._serialized_start = 4977
    _globals['_GROUPPERMISSION']._serialized_end = 5063
    _globals['_MESSAGESTREAM']._serialized_start = 80
    _globals['_MESSAGESTREAM']._serialized_end = 199
    _globals['_UNREGISTEROPTIONS']._serialized_start = 201
    _globals['_UNREGISTEROPTIONS']._serialized_end = 220
    _globals['_JOINEDGROUP']._serialized_start = 222
    _globals['_JOINEDGROUP']._serialized_end = 304
    _globals['_GETJOINEDGROUPSOPTIONS']._serialized_start = 306
    _globals['_GETJOINEDGROUPSOPTIONS']._serialized_end = 330
    _globals['_GETACLALLOPTIONS']._serialized_start = 332
    _globals['_GETACLALLOPTIONS']._serialized_end = 350
    _globals['_REGISTEROPTIONS']._serialized_start = 353
    _globals['_REGISTEROPTIONS']._serialized_end = 491
    _globals['_GROUPACL']._serialized_start = 494
    _globals['_GROUPACL']._serialized_end = 641
    _globals['_DISAPPEARINGMESSAGEOPTIONS']._serialized_start = 644
    _globals['_DISAPPEARINGMESSAGEOPTIONS']._serialized_end = 896
    _globals['_DISAPPEARINGMESSAGEOPTIONS_DISAPPEARING_TIME']._serialized_start = 809
    _globals['_DISAPPEARINGMESSAGEOPTIONS_DISAPPEARING_TIME']._serialized_end = 896
    _globals['_DISAPPEARINGMESSAGERESPONSE']._serialized_start = 898
    _globals['_DISAPPEARINGMESSAGERESPONSE']._serialized_end = 927
    _globals['_SENDMESSAGEOPTIONS']._serialized_start = 930
    _globals['_SENDMESSAGEOPTIONS']._serialized_end = 1130
    _globals['_SENDMESSAGEMEDIA']._serialized_start = 1133
    _globals['_SENDMESSAGEMEDIA']._serialized_end = 1371
    _globals['_SENDMESSAGEMEDIA_MEDIATYPE']._serialized_start = 1293
    _globals['_SENDMESSAGEMEDIA_MEDIATYPE']._serialized_end = 1371
    _globals['_DOWNLOADMEDIAOPTIONS']._serialized_start = 1373
    _globals['_DOWNLOADMEDIAOPTIONS']._serialized_end = 1468
    _globals['_HISTORYREQUESTOPTIONS']._serialized_start = 1470
    _globals['_HISTORYREQUESTOPTIONS']._serialized_end = 1597
    _globals['_PENDINGHISTORYOPTIONS']._serialized_start = 1599
    _globals['_PENDINGHISTORYOPTIONS']._serialized_end = 1674
    _globals['_SENDMESSAGERECEIPT']._serialized_start = 1676
    _globals['_SENDMESSAGERECEIPT']._serialized_end = 1759
    _globals['_INVITECODE']._serialized_start = 1761
    _globals['_INVITECODE']._serialized_end = 1787
    _globals['_CONTACT']._serialized_start = 1789
    _globals['_CONTACT']._serialized_end = 1875
    _globals['_GROUPNAME']._serialized_start = 1877
    _globals['_GROUPNAME']._serialized_end = 1981
    _globals['_GROUPTOPIC']._serialized_start = 1984
    _globals['_GROUPTOPIC']._serialized_end = 2129
    _globals['_GROUPPARTICIPANT']._serialized_start = 2132
    _globals['_GROUPPARTICIPANT']._serialized_end = 2268
    _globals['_GROUPINFO']._serialized_start = 2271
    _globals['_GROUPINFO']._serialized_end = 2887
    _globals['_GROUPINFO_PROVENANCEENTRY']._serialized_start = 2838
    _globals['_GROUPINFO_PROVENANCEENTRY']._serialized_end = 2887
    _globals['_CONNECTIONSTATUSOPTIONS']._serialized_start = 2889
    _globals['_CONNECTIONSTATUSOPTIONS']._serialized_end = 2914
    _globals['_MESSAGESOPTIONS']._serialized_start = 2916
    _globals['_MESSAGESOPTIONS']._serialized_end = 3043
    _globals['_SESSIONTOKEN']._serialized_start = 3045
    _globals['_SESSIONTOKEN']._serialized_end = 3126
    _globals['_REGISTERMESSAGES']._serialized_start = 3128
    _globals['_REGISTERMESSAGES']._serialized_end = 3217
    _globals['_WUCREDENTIALS']._serialized_start = 3219
    _globals['_WUCREDENTIALS']._serialized_end = 3272
    _globals['_JID']._serialized_start = 3274
    _globals['_JID']._serialized_end = 3393
    _globals['_CONNECTIONSTATUS']._serialized_start = 3396
    _globals['_CONNECTIONSTATUS']._serialized_end = 3558
    _globals['_WUMESSAGE']._serialized_start = 3561
    _globals['_WUMESSAGE']._serialized_end = 3849
    _globals['_WUMESSAGE_PROVENANCEENTRY']._serialized_start = 2838
    _globals['_WUMESSAGE_PROVENANCEENTRY']._serialized_end = 2887
    _globals['_MESSAGESOURCE']._serialized_start = 3852
    _globals['_MESSAGESOURCE']._serialized_end = 4070
    _globals['_MESSAGEINFO']._serialized_start = 4073
    _globals['_MESSAGEINFO']._serialized_end = 4253
    _globals['_MESSAGECONTENT']._serialized_start = 4256
    _globals['_MESSAGECONTENT']._serialized_end = 4403
    _globals['_MESSAGEPROPERTIES']._serialized_start = 4406
    _globals['_MESSAGEPROPERTIES']._serialized_end = 4631
    _globals['_MEDIAMESSAGE']._serialized_start = 4634
    _globals['_MEDIAMESSAGE']._serialized_end = 4945
    _globals['_MEDIACONTENT']._serialized_start = 4947
    _globals['_MEDIACONTENT']._serialized_end = 4975
    _globals['_WHATUPCOREAUTH']._serialized_start = 5066
    _globals['_WHATUPCOREAUTH']._serialized_end = 5265
    _globals['_WHATUPCORE']._serialized_start = 5268
    _globals['_WHATUPCORE']._serialized_end = 6353