"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x11whatsappweb.proto\x12\x05proto"B\n\x15ADVSignedKeyIndexList\x12\x0f\n\x07details\x18\x01 \x01(\x0c\x12\x18\n\x10accountSignature\x18\x02 \x01(\x0c"z\n\x17ADVSignedDeviceIdentity\x12\x0f\n\x07details\x18\x01 \x01(\x0c\x12\x1b\n\x13accountSignatureKey\x18\x02 \x01(\x0c\x12\x18\n\x10accountSignature\x18\x03 \x01(\x0c\x12\x17\n\x0fdeviceSignature\x18\x04 \x01(\x0c"<\n\x1bADVSignedDeviceIdentityHMAC\x12\x0f\n\x07details\x18\x01 \x01(\x0c\x12\x0c\n\x04hmac\x18\x02 \x01(\x0c"\x92\x01\n\x0fADVKeyIndexList\x12\r\n\x05rawId\x18\x01 \x01(\r\x12\x11\n\ttimestamp\x18\x02 \x01(\x04\x12\x14\n\x0ccurrentIndex\x18\x03 \x01(\r\x12\x18\n\x0cvalidIndexes\x18\x04 \x03(\rB\x02\x10\x01\x12-\n\x0baccountType\x18\x05 \x01(\x0e2\x18.proto.ADVEncryptionType"\xa4\x01\n\x11ADVDeviceIdentity\x12\r\n\x05rawId\x18\x01 \x01(\r\x12\x11\n\ttimestamp\x18\x02 \x01(\x04\x12\x10\n\x08keyIndex\x18\x03 \x01(\r\x12-\n\x0baccountType\x18\x04 \x01(\x0e2\x18.proto.ADVEncryptionType\x12,\n\ndeviceType\x18\x05 \x01(\x0e2\x18.proto.ADVEncryptionType"\xf3\x05\n\x0bDeviceProps\x12\n\n\x02os\x18\x01 \x01(\t\x12.\n\x07version\x18\x02 \x01(\x0b2\x1d.proto.DeviceProps.AppVersion\x125\n\x0cplatformType\x18\x03 \x01(\x0e2\x1f.proto.DeviceProps.PlatformType\x12\x17\n\x0frequireFullSync\x18\x04 \x01(\x08\x12?\n\x11historySyncConfig\x18\x05 \x01(\x0b2$.proto.DeviceProps.HistorySyncConfig\x1a\xa7\x01\n\x11HistorySyncConfig\x12\x19\n\x11fullSyncDaysLimit\x18\x01 \x01(\r\x12\x1b\n\x13fullSyncSizeMbLimit\x18\x02 \x01(\r\x12\x16\n\x0estorageQuotaMb\x18\x03 \x01(\r\x12%\n\x1dinlineInitialPayloadInE2EeMsg\x18\x04 \x01(\x08\x12\x1b\n\x13recentSyncDaysLimit\x18\x05 \x01(\r\x1ag\n\nAppVersion\x12\x0f\n\x07primary\x18\x01 \x01(\r\x12\x11\n\tsecondary\x18\x02 \x01(\r\x12\x10\n\x08tertiary\x18\x03 \x01(\r\x12\x12\n\nquaternary\x18\x04 \x01(\r\x12\x0f\n\x07quinary\x18\x05 \x01(\r"\x83\x02\n\x0cPlatformType\x12\x0b\n\x07UNKNOWN\x10\x00\x12\n\n\x06CHROME\x10\x01\x12\x0b\n\x07FIREFOX\x10\x02\x12\x06\n\x02IE\x10\x03\x12\t\n\x05OPERA\x10\x04\x12\n\n\x06SAFARI\x10\x05\x12\x08\n\x04EDGE\x10\x06\x12\x0b\n\x07DESKTOP\x10\x07\x12\x08\n\x04IPAD\x10\x08\x12\x12\n\x0eANDROID_TABLET\x10\t\x12\t\n\x05OHANA\x10\n\x12\t\n\x05ALOHA\x10\x0b\x12\x0c\n\x08CATALINA\x10\x0c\x12\n\n\x06TCL_TV\x10\r\x12\r\n\tIOS_PHONE\x10\x0e\x12\x10\n\x0cIOS_CATALYST\x10\x0f\x12\x11\n\rANDROID_PHONE\x10\x10\x12\x15\n\x11ANDROID_AMBIGUOUS\x10\x11"\xa7\x01\n\x14PaymentInviteMessage\x12<\n\x0bserviceType\x18\x01 \x01(\x0e2\'.proto.PaymentInviteMessage.ServiceType\x12\x17\n\x0fexpiryTimestamp\x18\x02 \x01(\x03"8\n\x0bServiceType\x12\x0b\n\x07UNKNOWN\x10\x00\x12\t\n\x05FBPAY\x10\x01\x12\x08\n\x04NOVI\x10\x02\x12\x07\n\x03UPI\x10\x03"\x86\x03\n\x0cOrderMessage\x12\x0f\n\x07orderId\x18\x01 \x01(\t\x12\x11\n\tthumbnail\x18\x02 \x01(\x0c\x12\x11\n\titemCount\x18\x03 \x01(\x05\x12/\n\x06status\x18\x04 \x01(\x0e2\x1f.proto.OrderMessage.OrderStatus\x121\n\x07surface\x18\x05 \x01(\x0e2 .proto.OrderMessage.OrderSurface\x12\x0f\n\x07message\x18\x06 \x01(\t\x12\x12\n\norderTitle\x18\x07 \x01(\t\x12\x11\n\tsellerJid\x18\x08 \x01(\t\x12\r\n\x05token\x18\t \x01(\t\x12\x17\n\x0ftotalAmount1000\x18\n \x01(\x03\x12\x19\n\x11totalCurrencyCode\x18\x0b \x01(\t\x12\'\n\x0bcontextInfo\x18\x11 \x01(\x0b2\x12.proto.ContextInfo"\x1b\n\x0cOrderSurface\x12\x0b\n\x07CATALOG\x10\x01"\x1a\n\x0bOrderStatus\x12\x0b\n\x07INQUIRY\x10\x01"\xaa\x02\n\x0fLocationMessage\x12\x17\n\x0fdegreesLatitude\x18\x01 \x01(\x01\x12\x18\n\x10degreesLongitude\x18\x02 \x01(\x01\x12\x0c\n\x04name\x18\x03 \x01(\t\x12\x0f\n\x07address\x18\x04 \x01(\t\x12\x0b\n\x03url\x18\x05 \x01(\t\x12\x0e\n\x06isLive\x18\x06 \x01(\x08\x12\x18\n\x10accuracyInMeters\x18\x07 \x01(\r\x12\x12\n\nspeedInMps\x18\x08 \x01(\x02\x12)\n!degreesClockwiseFromMagneticNorth\x18\t \x01(\r\x12\x0f\n\x07comment\x18\x0b \x01(\t\x12\x15\n\rjpegThumbnail\x18\x10 \x01(\x0c\x12\'\n\x0bcontextInfo\x18\x11 \x01(\x0b2\x12.proto.ContextInfo"\x9e\x02\n\x13LiveLocationMessage\x12\x17\n\x0fdegreesLatitude\x18\x01 \x01(\x01\x12\x18\n\x10degreesLongitude\x18\x02 \x01(\x01\x12\x18\n\x10accuracyInMeters\x18\x03 \x01(\r\x12\x12\n\nspeedInMps\x18\x04 \x01(\x02\x12)\n!degreesClockwiseFromMagneticNorth\x18\x05 \x01(\r\x12\x0f\n\x07caption\x18\x06 \x01(\t\x12\x16\n\x0esequenceNumber\x18\x07 \x01(\x03\x12\x12\n\ntimeOffset\x18\x08 \x01(\r\x12\x15\n\rjpegThumbnail\x18\x10 \x01(\x0c\x12\'\n\x0bcontextInfo\x18\x11 \x01(\x0b2\x12.proto.ContextInfo"\xba\x02\n\x13ListResponseMessage\x12\r\n\x05title\x18\x01 \x01(\t\x125\n\x08listType\x18\x02 \x01(\x0e2#.proto.ListResponseMessage.ListType\x12G\n\x11singleSelectReply\x18\x03 \x01(\x0b2,.proto.ListResponseMessage.SingleSelectReply\x12\'\n\x0bcontextInfo\x18\x04 \x01(\x0b2\x12.proto.ContextInfo\x12\x13\n\x0bdescription\x18\x05 \x01(\t\x1a*\n\x11SingleSelectReply\x12\x15\n\rselectedRowId\x18\x01 \x01(\t"*\n\x08ListType\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x11\n\rSINGLE_SELECT\x10\x01"\xaf\x06\n\x0bListMessage\x12\r\n\x05title\x18\x01 \x01(\t\x12\x13\n\x0bdescription\x18\x02 \x01(\t\x12\x12\n\nbuttonText\x18\x03 \x01(\t\x12-\n\x08listType\x18\x04 \x01(\x0e2\x1b.proto.ListMessage.ListType\x12,\n\x08sections\x18\x05 \x03(\x0b2\x1a.proto.ListMessage.Section\x12;\n\x0fproductListInfo\x18\x06 \x01(\x0b2".proto.ListMessage.ProductListInfo\x12\x12\n\nfooterText\x18\x07 \x01(\t\x12\'\n\x0bcontextInfo\x18\x08 \x01(\x0b2\x12.proto.ContextInfo\x1a>\n\x07Section\x12\r\n\x05title\x18\x01 \x01(\t\x12$\n\x04rows\x18\x02 \x03(\x0b2\x16.proto.ListMessage.Row\x1a8\n\x03Row\x12\r\n\x05title\x18\x01 \x01(\t\x12\x13\n\x0bdescription\x18\x02 \x01(\t\x12\r\n\x05rowId\x18\x03 \x01(\t\x1a\x1c\n\x07Product\x12\x11\n\tproductId\x18\x01 \x01(\t\x1aM\n\x0eProductSection\x12\r\n\x05title\x18\x01 \x01(\t\x12,\n\x08products\x18\x02 \x03(\x0b2\x1a.proto.ListMessage.Product\x1a\xa7\x01\n\x0fProductListInfo\x12:\n\x0fproductSections\x18\x01 \x03(\x0b2!.proto.ListMessage.ProductSection\x12>\n\x0bheaderImage\x18\x02 \x01(\x0b2).proto.ListMessage.ProductListHeaderImage\x12\x18\n\x10businessOwnerJid\x18\x03 \x01(\t\x1aB\n\x16ProductListHeaderImage\x12\x11\n\tproductId\x18\x01 \x01(\t\x12\x15\n\rjpegThumbnail\x18\x02 \x01(\x0c"<\n\x08ListType\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x11\n\rSINGLE_SELECT\x10\x01\x12\x10\n\x0cPRODUCT_LIST\x10\x02"k\n\x11KeepInChatMessage\x12\x1e\n\x03key\x18\x01 \x01(\x0b2\x11.proto.MessageKey\x12!\n\x08keepType\x18\x02 \x01(\x0e2\x0f.proto.KeepType\x12\x13\n\x0btimestampMs\x18\x03 \x01(\x03"\xec\x02\n\x0eInvoiceMessage\x12\x0c\n\x04note\x18\x01 \x01(\t\x12\r\n\x05token\x18\x02 \x01(\t\x12<\n\x0eattachmentType\x18\x03 \x01(\x0e2$.proto.InvoiceMessage.AttachmentType\x12\x1a\n\x12attachmentMimetype\x18\x04 \x01(\t\x12\x1a\n\x12attachmentMediaKey\x18\x05 \x01(\x0c\x12#\n\x1battachmentMediaKeyTimestamp\x18\x06 \x01(\x03\x12\x1c\n\x14attachmentFileSha256\x18\x07 \x01(\x0c\x12\x1f\n\x17attachmentFileEncSha256\x18\x08 \x01(\x0c\x12\x1c\n\x14attachmentDirectPath\x18\t \x01(\t\x12\x1f\n\x17attachmentJpegThumbnail\x18\n \x01(\x0c"$\n\x0eAttachmentType\x12\t\n\x05IMAGE\x10\x00\x12\x07\n\x03PDF\x10\x01"\xc9\x03\n\x1aInteractiveResponseMessage\x124\n\x04body\x18\x01 \x01(\x0b2&.proto.InteractiveResponseMessage.Body\x12\'\n\x0bcontextInfo\x18\x0f \x01(\x0b2\x12.proto.ContextInfo\x12`\n\x19nativeFlowResponseMessage\x18\x02 \x01(\x0b2;.proto.InteractiveResponseMessage.NativeFlowResponseMessageH\x00\x1aN\n\x19NativeFlowResponseMessage\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x12\n\nparamsJson\x18\x02 \x01(\t\x12\x0f\n\x07version\x18\x03 \x01(\x05\x1a|\n\x04Body\x12\x0c\n\x04text\x18\x01 \x01(\t\x12=\n\x06format\x18\x02 \x01(\x0e2-.proto.InteractiveResponseMessage.Body.Format"\'\n\x06Format\x12\x0b\n\x07DEFAULT\x10\x00\x12\x10\n\x0cEXTENSIONS_1\x10\x01B\x1c\n\x1ainteractiveResponseMessage"\xaf\t\n\x12InteractiveMessage\x120\n\x06header\x18\x01 \x01(\x0b2 .proto.InteractiveMessage.Header\x12,\n\x04body\x18\x02 \x01(\x0b2\x1e.proto.InteractiveMessage.Body\x120\n\x06footer\x18\x03 \x01(\x0b2 .proto.InteractiveMessage.Footer\x12\'\n\x0bcontextInfo\x18\x0f \x01(\x0b2\x12.proto.ContextInfo\x12F\n\x15shopStorefrontMessage\x18\x04 \x01(\x0b2%.proto.InteractiveMessage.ShopMessageH\x00\x12H\n\x11collectionMessage\x18\x05 \x01(\x0b2+.proto.InteractiveMessage.CollectionMessageH\x00\x12H\n\x11nativeFlowMessage\x18\x06 \x01(\x0b2+.proto.InteractiveMessage.NativeFlowMessageH\x00\x1a\xa9\x01\n\x0bShopMessage\x12\n\n\x02id\x18\x01 \x01(\t\x12>\n\x07surface\x18\x02 \x01(\x0e2-.proto.InteractiveMessage.ShopMessage.Surface\x12\x16\n\x0emessageVersion\x18\x03 \x01(\x05"6\n\x07Surface\x12\x13\n\x0fUNKNOWN_SURFACE\x10\x00\x12\x06\n\x02FB\x10\x01\x12\x06\n\x02IG\x10\x02\x12\x06\n\x02WA\x10\x03\x1a\xd1\x01\n\x11NativeFlowMessage\x12M\n\x07buttons\x18\x01 \x03(\x0b2<.proto.InteractiveMessage.NativeFlowMessage.NativeFlowButton\x12\x19\n\x11messageParamsJson\x18\x02 \x01(\t\x12\x16\n\x0emessageVersion\x18\x03 \x01(\x05\x1a:\n\x10NativeFlowButton\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x18\n\x10buttonParamsJson\x18\x02 \x01(\t\x1a\xf4\x01\n\x06Header\x12\r\n\x05title\x18\x01 \x01(\t\x12\x10\n\x08subtitle\x18\x02 \x01(\t\x12\x1a\n\x12hasMediaAttachment\x18\x05 \x01(\x08\x121\n\x0fdocumentMessage\x18\x03 \x01(\x0b2\x16.proto.DocumentMessageH\x00\x12+\n\x0cimageMessage\x18\x04 \x01(\x0b2\x13.proto.ImageMessageH\x00\x12\x17\n\rjpegThumbnail\x18\x06 \x01(\x0cH\x00\x12+\n\x0cvideoMessage\x18\x07 \x01(\x0b2\x13.proto.VideoMessageH\x00B\x07\n\x05media\x1a\x16\n\x06Footer\x12\x0c\n\x04text\x18\x01 \x01(\t\x1aG\n\x11CollectionMessage\x12\x0e\n\x06bizJid\x18\x01 \x01(\t\x12\n\n\x02id\x18\x02 \x01(\t\x12\x16\n\x0emessageVersion\x18\x03 \x01(\x05\x1a\x14\n\x04Body\x12\x0c\n\x04text\x18\x01 \x01(\tB\x14\n\x12interactiveMessage"M\n&InitialSecurityNotificationSettingSync\x12#\n\x1bsecurityNotificationEnabled\x18\x01 \x01(\x08"\x8a\x05\n\x0cImageMessage\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\x10\n\x08mimetype\x18\x02 \x01(\t\x12\x0f\n\x07caption\x18\x03 \x01(\t\x12\x12\n\nfileSha256\x18\x04 \x01(\x0c\x12\x12\n\nfileLength\x18\x05 \x01(\x04\x12\x0e\n\x06height\x18\x06 \x01(\r\x12\r\n\x05width\x18\x07 \x01(\r\x12\x10\n\x08mediaKey\x18\x08 \x01(\x0c\x12\x15\n\rfileEncSha256\x18\t \x01(\x0c\x12<\n\x16interactiveAnnotations\x18\n \x03(\x0b2\x1c.proto.InteractiveAnnotation\x12\x12\n\ndirectPath\x18\x0b \x01(\t\x12\x19\n\x11mediaKeyTimestamp\x18\x0c \x01(\x03\x12\x15\n\rjpegThumbnail\x18\x10 \x01(\x0c\x12\'\n\x0bcontextInfo\x18\x11 \x01(\x0b2\x12.proto.ContextInfo\x12\x18\n\x10firstScanSidecar\x18\x12 \x01(\x0c\x12\x17\n\x0ffirstScanLength\x18\x13 \x01(\r\x12\x19\n\x11experimentGroupId\x18\x14 \x01(\r\x12\x14\n\x0cscansSidecar\x18\x15 \x01(\x0c\x12\x13\n\x0bscanLengths\x18\x16 \x03(\r\x12\x1c\n\x14midQualityFileSha256\x18\x17 \x01(\x0c\x12\x1f\n\x17midQualityFileEncSha256\x18\x18 \x01(\x0c\x12\x10\n\x08viewOnce\x18\x19 \x01(\x08\x12\x1b\n\x13thumbnailDirectPath\x18\x1a \x01(\t\x12\x17\n\x0fthumbnailSha256\x18\x1b \x01(\x0c\x12\x1a\n\x12thumbnailEncSha256\x18\x1c \x01(\x0c\x12\x11\n\tstaticUrl\x18\x1d \x01(\t"\x81\x04\n\x17HistorySyncNotification\x12\x12\n\nfileSha256\x18\x01 \x01(\x0c\x12\x12\n\nfileLength\x18\x02 \x01(\x04\x12\x10\n\x08mediaKey\x18\x03 \x01(\x0c\x12\x15\n\rfileEncSha256\x18\x04 \x01(\x0c\x12\x12\n\ndirectPath\x18\x05 \x01(\t\x12@\n\x08syncType\x18\x06 \x01(\x0e2..proto.HistorySyncNotification.HistorySyncType\x12\x12\n\nchunkOrder\x18\x07 \x01(\r\x12\x19\n\x11originalMessageId\x18\x08 \x01(\t\x12\x10\n\x08progress\x18\t \x01(\r\x12$\n\x1coldestMsgInChunkTimestampSec\x18\n \x01(\x03\x12)\n!initialHistBootstrapInlinePayload\x18\x0b \x01(\x0c\x12 \n\x18peerDataRequestSessionId\x18\x0c \x01(\t"\x8a\x01\n\x0fHistorySyncType\x12\x15\n\x11INITIAL_BOOTSTRAP\x10\x00\x12\x15\n\x11INITIAL_STATUS_V3\x10\x01\x12\x08\n\x04FULL\x10\x02\x12\n\n\x06RECENT\x10\x03\x12\r\n\tPUSH_NAME\x10\x04\x12\x15\n\x11NON_BLOCKING_DATA\x10\x05\x12\r\n\tON_DEMAND\x10\x06"\xee\n\n\x17HighlyStructuredMessage\x12\x11\n\tnamespace\x18\x01 \x01(\t\x12\x13\n\x0belementName\x18\x02 \x01(\t\x12\x0e\n\x06params\x18\x03 \x03(\t\x12\x12\n\nfallbackLg\x18\x04 \x01(\t\x12\x12\n\nfallbackLc\x18\x05 \x01(\t\x12Q\n\x11localizableParams\x18\x06 \x03(\x0b26.proto.HighlyStructuredMessage.HSMLocalizableParameter\x12\x17\n\x0fdeterministicLg\x18\x07 \x01(\t\x12\x17\n\x0fdeterministicLc\x18\x08 \x01(\t\x12+\n\x0bhydratedHsm\x18\t \x01(\x0b2\x16.proto.TemplateMessage\x1a\xc0\x08\n\x17HSMLocalizableParameter\x12\x0f\n\x07default\x18\x01 \x01(\t\x12V\n\x08currency\x18\x02 \x01(\x0b2B.proto.HighlyStructuredMessage.HSMLocalizableParameter.HSMCurrencyH\x00\x12V\n\x08dateTime\x18\x03 \x01(\x0b2B.proto.HighlyStructuredMessage.HSMLocalizableParameter.HSMDateTimeH\x00\x1a\x9c\x06\n\x0bHSMDateTime\x12l\n\tcomponent\x18\x01 \x01(\x0b2W.proto.HighlyStructuredMessage.HSMLocalizableParameter.HSMDateTime.HSMDateTimeComponentH\x00\x12l\n\tunixEpoch\x18\x02 \x01(\x0b2W.proto.HighlyStructuredMessage.HSMLocalizableParameter.HSMDateTime.HSMDateTimeUnixEpochH\x00\x1a)\n\x14HSMDateTimeUnixEpoch\x12\x11\n\ttimestamp\x18\x01 \x01(\x03\x1a\xf4\x03\n\x14HSMDateTimeComponent\x12x\n\tdayOfWeek\x18\x01 \x01(\x0e2e.proto.HighlyStructuredMessage.HSMLocalizableParameter.HSMDateTime.HSMDateTimeComponent.DayOfWeekType\x12\x0c\n\x04year\x18\x02 \x01(\r\x12\r\n\x05month\x18\x03 \x01(\r\x12\x12\n\ndayOfMonth\x18\x04 \x01(\r\x12\x0c\n\x04hour\x18\x05 \x01(\r\x12\x0e\n\x06minute\x18\x06 \x01(\r\x12v\n\x08calendar\x18\x07 \x01(\x0e2d.proto.HighlyStructuredMessage.HSMLocalizableParameter.HSMDateTime.HSMDateTimeComponent.CalendarType"k\n\rDayOfWeekType\x12\n\n\x06MONDAY\x10\x01\x12\x0b\n\x07TUESDAY\x10\x02\x12\r\n\tWEDNESDAY\x10\x03\x12\x0c\n\x08THURSDAY\x10\x04\x12\n\n\x06FRIDAY\x10\x05\x12\x0c\n\x08SATURDAY\x10\x06\x12\n\n\x06SUNDAY\x10\x07".\n\x0cCalendarType\x12\r\n\tGREGORIAN\x10\x01\x12\x0f\n\x0bSOLAR_HIJRI\x10\x02B\x0f\n\rdatetimeOneof\x1a7\n\x0bHSMCurrency\x12\x14\n\x0ccurrencyCode\x18\x01 \x01(\t\x12\x12\n\namount1000\x18\x02 \x01(\x03B\x0c\n\nparamOneof"\x96\x02\n\x12GroupInviteMessage\x12\x10\n\x08groupJid\x18\x01 \x01(\t\x12\x12\n\ninviteCode\x18\x02 \x01(\t\x12\x18\n\x10inviteExpiration\x18\x03 \x01(\x03\x12\x11\n\tgroupName\x18\x04 \x01(\t\x12\x15\n\rjpegThumbnail\x18\x05 \x01(\x0c\x12\x0f\n\x07caption\x18\x06 \x01(\t\x12\'\n\x0bcontextInfo\x18\x07 \x01(\x0b2\x12.proto.ContextInfo\x126\n\tgroupType\x18\x08 \x01(\x0e2#.proto.GroupInviteMessage.GroupType"$\n\tGroupType\x12\x0b\n\x07DEFAULT\x10\x00\x12\n\n\x06PARENT\x10\x01"5\n\x12FutureProofMessage\x12\x1f\n\x07message\x18\x01 \x01(\x0b2\x0e.proto.Message"\xea\x08\n\x13ExtendedTextMessage\x12\x0c\n\x04text\x18\x01 \x01(\t\x12\x13\n\x0bmatchedText\x18\x02 \x01(\t\x12\x14\n\x0ccanonicalUrl\x18\x04 \x01(\t\x12\x13\n\x0bdescription\x18\x05 \x01(\t\x12\r\n\x05title\x18\x06 \x01(\t\x12\x10\n\x08textArgb\x18\x07 \x01(\x07\x12\x16\n\x0ebackgroundArgb\x18\x08 \x01(\x07\x121\n\x04font\x18\t \x01(\x0e2#.proto.ExtendedTextMessage.FontType\x12;\n\x0bpreviewType\x18\n \x01(\x0e2&.proto.ExtendedTextMessage.PreviewType\x12\x15\n\rjpegThumbnail\x18\x10 \x01(\x0c\x12\'\n\x0bcontextInfo\x18\x11 \x01(\x0b2\x12.proto.ContextInfo\x12\x17\n\x0fdoNotPlayInline\x18\x12 \x01(\x08\x12\x1b\n\x13thumbnailDirectPath\x18\x13 \x01(\t\x12\x17\n\x0fthumbnailSha256\x18\x14 \x01(\x0c\x12\x1a\n\x12thumbnailEncSha256\x18\x15 \x01(\x0c\x12\x10\n\x08mediaKey\x18\x16 \x01(\x0c\x12\x19\n\x11mediaKeyTimestamp\x18\x17 \x01(\x03\x12\x17\n\x0fthumbnailHeight\x18\x18 \x01(\r\x12\x16\n\x0ethumbnailWidth\x18\x19 \x01(\r\x12K\n\x13inviteLinkGroupType\x18\x1a \x01(\x0e2..proto.ExtendedTextMessage.InviteLinkGroupType\x12&\n\x1einviteLinkParentGroupSubjectV2\x18\x1b \x01(\t\x12(\n inviteLinkParentGroupThumbnailV2\x18\x1c \x01(\x0c\x12M\n\x15inviteLinkGroupTypeV2\x18\x1d \x01(\x0e2..proto.ExtendedTextMessage.InviteLinkGroupType\x12\x10\n\x08viewOnce\x18\x1e \x01(\x08""\n\x0bPreviewType\x12\x08\n\x04NONE\x10\x00\x12\t\n\x05VIDEO\x10\x01"H\n\x13InviteLinkGroupType\x12\x0b\n\x07DEFAULT\x10\x00\x12\n\n\x06PARENT\x10\x01\x12\x07\n\x03SUB\x10\x02\x12\x0f\n\x0bDEFAULT_SUB\x10\x03"\xe4\x01\n\x08FontType\x12\x0e\n\nSANS_SERIF\x10\x00\x12\t\n\x05SERIF\x10\x01\x12\x13\n\x0fNORICAN_REGULAR\x10\x02\x12\x11\n\rBRYNDAN_WRITE\x10\x03\x12\x15\n\x11BEBASNEUE_REGULAR\x10\x04\x12\x10\n\x0cOSWALD_HEAVY\x10\x05\x12\x0f\n\x0bSYSTEM_BOLD\x10\x06\x12\x19\n\x15MORNINGBREEZE_REGULAR\x10\x07\x12\x15\n\x11CALISTOGA_REGULAR\x10\x08\x12\x12\n\x0eEXO2_EXTRABOLD\x10\t\x12\x15\n\x11COURIERPRIME_BOLD\x10\n"d\n\x12EncReactionMessage\x12+\n\x10targetMessageKey\x18\x01 \x01(\x0b2\x11.proto.MessageKey\x12\x12\n\nencPayload\x18\x02 \x01(\x0c\x12\r\n\x05encIv\x18\x03 \x01(\x0c"\xce\x03\n\x0fDocumentMessage\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\x10\n\x08mimetype\x18\x02 \x01(\t\x12\r\n\x05title\x18\x03 \x01(\t\x12\x12\n\nfileSha256\x18\x04 \x01(\x0c\x12\x12\n\nfileLength\x18\x05 \x01(\x04\x12\x11\n\tpageCount\x18\x06 \x01(\r\x12\x10\n\x08mediaKey\x18\x07 \x01(\x0c\x12\x10\n\x08fileName\x18\x08 \x01(\t\x12\x15\n\rfileEncSha256\x18\t \x01(\x0c\x12\x12\n\ndirectPath\x18\n \x01(\t\x12\x19\n\x11mediaKeyTimestamp\x18\x0b \x01(\x03\x12\x14\n\x0ccontactVcard\x18\x0c \x01(\x08\x12\x1b\n\x13thumbnailDirectPath\x18\r \x01(\t\x12\x17\n\x0fthumbnailSha256\x18\x0e \x01(\x0c\x12\x1a\n\x12thumbnailEncSha256\x18\x0f \x01(\x0c\x12\x15\n\rjpegThumbnail\x18\x10 \x01(\x0c\x12\'\n\x0bcontextInfo\x18\x11 \x01(\x0b2\x12.proto.ContextInfo\x12\x17\n\x0fthumbnailHeight\x18\x12 \x01(\r\x12\x16\n\x0ethumbnailWidth\x18\x13 \x01(\r\x12\x0f\n\x07caption\x18\x14 \x01(\t"[\n\x11DeviceSentMessage\x12\x16\n\x0edestinationJid\x18\x01 \x01(\t\x12\x1f\n\x07message\x18\x02 \x01(\x0b2\x0e.proto.Message\x12\r\n\x05phash\x18\x03 \x01(\t">\n\x1cDeclinePaymentRequestMessage\x12\x1e\n\x03key\x18\x01 \x01(\x0b2\x11.proto.MessageKey"}\n\x14ContactsArrayMessage\x12\x13\n\x0bdisplayName\x18\x01 \x01(\t\x12\'\n\x08contacts\x18\x02 \x03(\x0b2\x15.proto.ContactMessage\x12\'\n\x0bcontextInfo\x18\x11 \x01(\x0b2\x12.proto.ContextInfo"]\n\x0eContactMessage\x12\x13\n\x0bdisplayName\x18\x01 \x01(\t\x12\r\n\x05vcard\x18\x10 \x01(\t\x12\'\n\x0bcontextInfo\x18\x11 \x01(\x0b2\x12.proto.ContextInfo"\'\n\x04Chat\x12\x13\n\x0bdisplayName\x18\x01 \x01(\t\x12\n\n\x02id\x18\x02 \x01(\t"=\n\x1bCancelPaymentRequestMessage\x12\x1e\n\x03key\x18\x01 \x01(\x0b2\x11.proto.MessageKey"i\n\x04Call\x12\x0f\n\x07callKey\x18\x01 \x01(\x0c\x12\x18\n\x10conversionSource\x18\x02 \x01(\t\x12\x16\n\x0econversionData\x18\x03 \x01(\x0c\x12\x1e\n\x16conversionDelaySeconds\x18\x04 \x01(\r"\xdf\x01\n\x16ButtonsResponseMessage\x12\x18\n\x10selectedButtonId\x18\x01 \x01(\t\x12\'\n\x0bcontextInfo\x18\x03 \x01(\x0b2\x12.proto.ContextInfo\x120\n\x04type\x18\x04 \x01(\x0e2".proto.ButtonsResponseMessage.Type\x12\x1d\n\x13selectedDisplayText\x18\x02 \x01(\tH\x00"%\n\x04Type\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x10\n\x0cDISPLAY_TEXT\x10\x01B\n\n\x08response"\xde\x06\n\x0eButtonsMessage\x12\x13\n\x0bcontentText\x18\x06 \x01(\t\x12\x12\n\nfooterText\x18\x07 \x01(\t\x12\'\n\x0bcontextInfo\x18\x08 \x01(\x0b2\x12.proto.ContextInfo\x12-\n\x07buttons\x18\t \x03(\x0b2\x1c.proto.ButtonsMessage.Button\x124\n\nheaderType\x18\n \x01(\x0e2 .proto.ButtonsMessage.HeaderType\x12\x0e\n\x04text\x18\x01 \x01(\tH\x00\x121\n\x0fdocumentMessage\x18\x02 \x01(\x0b2\x16.proto.DocumentMessageH\x00\x12+\n\x0cimageMessage\x18\x03 \x01(\x0b2\x13.proto.ImageMessageH\x00\x12+\n\x0cvideoMessage\x18\x04 \x01(\x0b2\x13.proto.VideoMessageH\x00\x121\n\x0flocationMessage\x18\x05 \x01(\x0b2\x16.proto.LocationMessageH\x00\x1a\xd8\x02\n\x06Button\x12\x10\n\x08buttonId\x18\x01 \x01(\t\x12;\n\nbuttonText\x18\x02 \x01(\x0b2\'.proto.ButtonsMessage.Button.ButtonText\x12/\n\x04type\x18\x03 \x01(\x0e2!.proto.ButtonsMessage.Button.Type\x12C\n\x0enativeFlowInfo\x18\x04 \x01(\x0b2+.proto.ButtonsMessage.Button.NativeFlowInfo\x1a2\n\x0eNativeFlowInfo\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x12\n\nparamsJson\x18\x02 \x01(\t\x1a!\n\nButtonText\x12\x13\n\x0bdisplayText\x18\x01 \x01(\t"2\n\x04Type\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x0c\n\x08RESPONSE\x10\x01\x12\x0f\n\x0bNATIVE_FLOW\x10\x02"`\n\nHeaderType\x12\x0b\n\x07UNKNOWN\x10\x00\x12\t\n\x05EMPTY\x10\x01\x12\x08\n\x04TEXT\x10\x02\x12\x0c\n\x08DOCUMENT\x10\x03\x12\t\n\x05IMAGE\x10\x04\x12\t\n\x05VIDEO\x10\x05\x12\x0c\n\x08LOCATION\x10\x06B\x08\n\x06header"\xca\x02\n\x0cAudioMessage\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\x10\n\x08mimetype\x18\x02 \x01(\t\x12\x12\n\nfileSha256\x18\x03 \x01(\x0c\x12\x12\n\nfileLength\x18\x04 \x01(\x04\x12\x0f\n\x07seconds\x18\x05 \x01(\r\x12\x0b\n\x03ptt\x18\x06 \x01(\x08\x12\x10\n\x08mediaKey\x18\x07 \x01(\x0c\x12\x15\n\rfileEncSha256\x18\x08 \x01(\x0c\x12\x12\n\ndirectPath\x18\t \x01(\t\x12\x19\n\x11mediaKeyTimestamp\x18\n \x01(\x03\x12\'\n\x0bcontextInfo\x18\x11 \x01(\x0b2\x12.proto.ContextInfo\x12\x18\n\x10streamingSidecar\x18\x12 \x01(\x0c\x12\x10\n\x08waveform\x18\x13 \x01(\x0c\x12\x16\n\x0ebackgroundArgb\x18\x14 \x01(\x07\x12\x10\n\x08viewOnce\x18\x15 \x01(\x08"g\n\x0fAppStateSyncKey\x12\'\n\x05keyId\x18\x01 \x01(\x0b2\x18.proto.AppStateSyncKeyId\x12+\n\x07keyData\x18\x02 \x01(\x0b2\x1a.proto.AppStateSyncKeyData"<\n\x14AppStateSyncKeyShare\x12$\n\x04keys\x18\x01 \x03(\x0b2\x16.proto.AppStateSyncKey"B\n\x16AppStateSyncKeyRequest\x12(\n\x06keyIds\x18\x01 \x03(\x0b2\x18.proto.AppStateSyncKeyId""\n\x11AppStateSyncKeyId\x12\r\n\x05keyId\x18\x01 \x01(\x0c"\\\n\x1aAppStateSyncKeyFingerprint\x12\r\n\x05rawId\x18\x01 \x01(\r\x12\x14\n\x0ccurrentIndex\x18\x02 \x01(\r\x12\x19\n\rdeviceIndexes\x18\x03 \x03(\rB\x02\x10\x01"q\n\x13AppStateSyncKeyData\x12\x0f\n\x07keyData\x18\x01 \x01(\x0c\x126\n\x0bfingerprint\x18\x02 \x01(\x0b2!.proto.AppStateSyncKeyFingerprint\x12\x11\n\ttimestamp\x18\x03 \x01(\x03"P\n"AppStateFatalExceptionNotification\x12\x17\n\x0fcollectionNames\x18\x01 \x03(\t\x12\x11\n\ttimestamp\x18\x02 \x01(\x03"K\n\x08Location\x12\x17\n\x0fdegreesLatitude\x18\x01 \x01(\x01\x12\x18\n\x10degreesLongitude\x18\x02 \x01(\x01\x12\x0c\n\x04name\x18\x03 \x01(\t"m\n\x15InteractiveAnnotation\x12%\n\x0fpolygonVertices\x18\x01 \x03(\x0b2\x0c.proto.Point\x12#\n\x08location\x18\x02 \x01(\x0b2\x0f.proto.LocationH\x00B\x08\n\x06action"\xcf\x03\n\x16HydratedTemplateButton\x12\r\n\x05index\x18\x04 \x01(\r\x12R\n\x10quickReplyButton\x18\x01 \x01(\x0b26.proto.HydratedTemplateButton.HydratedQuickReplyButtonH\x00\x12D\n\turlButton\x18\x02 \x01(\x0b2/.proto.HydratedTemplateButton.HydratedURLButtonH\x00\x12F\n\ncallButton\x18\x03 \x01(\x0b20.proto.HydratedTemplateButton.HydratedCallButtonH\x00\x1a5\n\x11HydratedURLButton\x12\x13\n\x0bdisplayText\x18\x01 \x01(\t\x12\x0b\n\x03url\x18\x02 \x01(\t\x1a;\n\x18HydratedQuickReplyButton\x12\x13\n\x0bdisplayText\x18\x01 \x01(\t\x12\n\n\x02id\x18\x02 \x01(\t\x1a>\n\x12HydratedCallButton\x12\x13\n\x0bdisplayText\x18\x01 \x01(\t\x12\x13\n\x0bphoneNumber\x18\x02 \x01(\tB\x10\n\x0ehydratedButton"6\n\x0cGroupMention\x12\x10\n\x08groupJid\x18\x01 \x01(\t\x12\x14\n\x0cgroupSubject\x18\x02 \x01(\t"\x97\x01\n\x10DisappearingMode\x124\n\tinitiator\x18\x01 \x01(\x0e2!.proto.DisappearingMode.Initiator"M\n\tInitiator\x12\x13\n\x0fCHANGED_IN_CHAT\x10\x00\x12\x13\n\x0fINITIATED_BY_ME\x10\x01\x12\x16\n\x12INITIATED_BY_OTHER\x10\x02"\xb9\x01\n\x12DeviceListMetadata\x12\x15\n\rsenderKeyHash\x18\x01 \x01(\x0c\x12\x17\n\x0fsenderTimestamp\x18\x02 \x01(\x04\x12\x1c\n\x10senderKeyIndexes\x18\x03 \x03(\rB\x02\x10\x01\x12\x18\n\x10recipientKeyHash\x18\x08 \x01(\x0c\x12\x1a\n\x12recipientTimestamp\x18\t \x01(\x04\x12\x1f\n\x13recipientKeyIndexes\x18\n \x03(\rB\x02\x10\x01"\xfa\x0b\n\x0bContextInfo\x12\x10\n\x08stanzaId\x18\x01 \x01(\t\x12\x13\n\x0bparticipant\x18\x02 \x01(\t\x12%\n\rquotedMessage\x18\x03 \x01(\x0b2\x0e.proto.Message\x12\x11\n\tremoteJid\x18\x04 \x01(\t\x12\x14\n\x0cmentionedJid\x18\x0f \x03(\t\x12\x18\n\x10conversionSource\x18\x12 \x01(\t\x12\x16\n\x0econversionData\x18\x13 \x01(\x0c\x12\x1e\n\x16conversionDelaySeconds\x18\x14 \x01(\r\x12\x17\n\x0fforwardingScore\x18\x15 \x01(\r\x12\x13\n\x0bisForwarded\x18\x16 \x01(\x08\x120\n\x08quotedAd\x18\x17 \x01(\x0b2\x1e.proto.ContextInfo.AdReplyInfo\x12)\n\x0eplaceholderKey\x18\x18 \x01(\x0b2\x11.proto.MessageKey\x12\x12\n\nexpiration\x18\x19 \x01(\r\x12!\n\x19ephemeralSettingTimestamp\x18\x1a \x01(\x03\x12\x1d\n\x15ephemeralSharedSecret\x18\x1b \x01(\x0c\x12?\n\x0fexternalAdReply\x18\x1c \x01(\x0b2&.proto.ContextInfo.ExternalAdReplyInfo\x12"\n\x1aentryPointConversionSource\x18\x1d \x01(\t\x12\x1f\n\x17entryPointConversionApp\x18\x1e \x01(\t\x12(\n entryPointConversionDelaySeconds\x18\x1f \x01(\r\x121\n\x10disappearingMode\x18  \x01(\x0b2\x17.proto.DisappearingMode\x12%\n\nactionLink\x18! \x01(\x0b2\x11.proto.ActionLink\x12\x14\n\x0cgroupSubject\x18" \x01(\t\x12\x16\n\x0eparentGroupJid\x18# \x01(\t\x12\x17\n\x0ftrustBannerType\x18% \x01(\t\x12\x19\n\x11trustBannerAction\x18& \x01(\r\x12\x11\n\tisSampled\x18\' \x01(\x08\x12*\n\rgroupMentions\x18( \x03(\x0b2\x13.proto.GroupMention\x12\'\n\x03utm\x18) \x01(\x0b2\x1a.proto.ContextInfo.UTMInfo\x1a1\n\x07UTMInfo\x12\x11\n\tutmSource\x18\x01 \x01(\t\x12\x13\n\x0butmCampaign\x18\x02 \x01(\t\x1a\xff\x02\n\x13ExternalAdReplyInfo\x12\r\n\x05title\x18\x01 \x01(\t\x12\x0c\n\x04body\x18\x02 \x01(\t\x12C\n\tmediaType\x18\x03 \x01(\x0e20.proto.ContextInfo.ExternalAdReplyInfo.MediaType\x12\x14\n\x0cthumbnailUrl\x18\x04 \x01(\t\x12\x10\n\x08mediaUrl\x18\x05 \x01(\t\x12\x11\n\tthumbnail\x18\x06 \x01(\x0c\x12\x12\n\nsourceType\x18\x07 \x01(\t\x12\x10\n\x08sourceId\x18\x08 \x01(\t\x12\x11\n\tsourceUrl\x18\t \x01(\t\x12\x19\n\x11containsAutoReply\x18\n \x01(\x08\x12\x1d\n\x15renderLargerThumbnail\x18\x0b \x01(\x08\x12\x19\n\x11showAdAttribution\x18\x0c \x01(\x08\x12\x10\n\x08ctwaClid\x18\r \x01(\t"+\n\tMediaType\x12\x08\n\x04NONE\x10\x00\x12\t\n\x05IMAGE\x10\x01\x12\t\n\x05VIDEO\x10\x02\x1a\xb7\x01\n\x0bAdReplyInfo\x12\x16\n\x0eadvertiserName\x18\x01 \x01(\t\x12;\n\tmediaType\x18\x02 \x01(\x0e2(.proto.ContextInfo.AdReplyInfo.MediaType\x12\x15\n\rjpegThumbnail\x18\x10 \x01(\x0c\x12\x0f\n\x07caption\x18\x11 \x01(\t"+\n\tMediaType\x12\x08\n\x04NONE\x10\x00\x12\t\n\x05IMAGE\x10\x01\x12\t\n\x05VIDEO\x10\x02".\n\nActionLink\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\x13\n\x0bbuttonTitle\x18\x02 \x01(\t"\x97\x04\n\x0eTemplateButton\x12\r\n\x05index\x18\x04 \x01(\r\x12B\n\x10quickReplyButton\x18\x01 \x01(\x0b2&.proto.TemplateButton.QuickReplyButtonH\x00\x124\n\turlButton\x18\x02 \x01(\x0b2\x1f.proto.TemplateButton.URLButtonH\x00\x126\n\ncallButton\x18\x03 \x01(\x0b2 .proto.TemplateButton.CallButtonH\x00\x1am\n\tURLButton\x123\n\x0bdisplayText\x18\x01 \x01(\x0b2\x1e.proto.HighlyStructuredMessage\x12+\n\x03url\x18\x02 \x01(\x0b2\x1e.proto.HighlyStructuredMessage\x1aS\n\x10QuickReplyButton\x123\n\x0bdisplayText\x18\x01 \x01(\x0b2\x1e.proto.HighlyStructuredMessage\x12\n\n\x02id\x18\x02 \x01(\t\x1av\n\nCallButton\x123\n\x0bdisplayText\x18\x01 \x01(\x0b2\x1e.proto.HighlyStructuredMessage\x123\n\x0bphoneNumber\x18\x02 \x01(\x0b2\x1e.proto.HighlyStructuredMessageB\x08\n\x06button"G\n\x05Point\x12\x13\n\x0bxDeprecated\x18\x01 \x01(\x05\x12\x13\n\x0byDeprecated\x18\x02 \x01(\x05\x12\t\n\x01x\x18\x03 \x01(\x01\x12\t\n\x01y\x18\x04 \x01(\x01"\xa3\x03\n\x11PaymentBackground\x12\n\n\x02id\x18\x01 \x01(\t\x12\x12\n\nfileLength\x18\x02 \x01(\x04\x12\r\n\x05width\x18\x03 \x01(\r\x12\x0e\n\x06height\x18\x04 \x01(\r\x12\x10\n\x08mimetype\x18\x05 \x01(\t\x12\x17\n\x0fplaceholderArgb\x18\x06 \x01(\x07\x12\x10\n\x08textArgb\x18\x07 \x01(\x07\x12\x13\n\x0bsubtextArgb\x18\x08 \x01(\x07\x125\n\tmediaData\x18\t \x01(\x0b2".proto.PaymentBackground.MediaData\x12+\n\x04type\x18\n \x01(\x0e2\x1d.proto.PaymentBackground.Type\x1aw\n\tMediaData\x12\x10\n\x08mediaKey\x18\x01 \x01(\x0c\x12\x19\n\x11mediaKeyTimestamp\x18\x02 \x01(\x03\x12\x12\n\nfileSha256\x18\x03 \x01(\x0c\x12\x15\n\rfileEncSha256\x18\x04 \x01(\x0c\x12\x12\n\ndirectPath\x18\x05 \x01(\t" \n\x04Type\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x0b\n\x07DEFAULT\x10\x01"<\n\x05Money\x12\r\n\x05value\x18\x01 \x01(\x03\x12\x0e\n\x06offset\x18\x02 \x01(\r\x12\x14\n\x0ccurrencyCode\x18\x03 \x01(\t"\x84\x18\n\x07Message\x12\x14\n\x0cconversation\x18\x01 \x01(\t\x12I\n\x1csenderKeyDistributionMessage\x18\x02 \x01(\x0b2#.proto.SenderKeyDistributionMessage\x12)\n\x0cimageMessage\x18\x03 \x01(\x0b2\x13.proto.ImageMessage\x12-\n\x0econtactMessage\x18\x04 \x01(\x0b2\x15.proto.ContactMessage\x12/\n\x0flocationMessage\x18\x05 \x01(\x0b2\x16.proto.LocationMessage\x127\n\x13extendedTextMessage\x18\x06 \x01(\x0b2\x1a.proto.ExtendedTextMessage\x12/\n\x0fdocumentMessage\x18\x07 \x01(\x0b2\x16.proto.DocumentMessage\x12)\n\x0caudioMessage\x18\x08 \x01(\x0b2\x13.proto.AudioMessage\x12)\n\x0cvideoMessage\x18\t \x01(\x0b2\x13.proto.VideoMessage\x12\x19\n\x04call\x18\n \x01(\x0b2\x0b.proto.Call\x12\x19\n\x04chat\x18\x0b \x01(\x0b2\x0b.proto.Chat\x12/\n\x0fprotocolMessage\x18\x0c \x01(\x0b2\x16.proto.ProtocolMessage\x129\n\x14contactsArrayMessage\x18\r \x01(\x0b2\x1b.proto.ContactsArrayMessage\x12?\n\x17highlyStructuredMessage\x18\x0e \x01(\x0b2\x1e.proto.HighlyStructuredMessage\x12W\n*fastRatchetKeySenderKeyDistributionMessage\x18\x0f \x01(\x0b2#.proto.SenderKeyDistributionMessage\x125\n\x12sendPaymentMessage\x18\x10 \x01(\x0b2\x19.proto.SendPaymentMessage\x127\n\x13liveLocationMessage\x18\x12 \x01(\x0b2\x1a.proto.LiveLocationMessage\x12;\n\x15requestPaymentMessage\x18\x16 \x01(\x0b2\x1c.proto.RequestPaymentMessage\x12I\n\x1cdeclinePaymentRequestMessage\x18\x17 \x01(\x0b2#.proto.DeclinePaymentRequestMessage\x12G\n\x1bcancelPaymentRequestMessage\x18\x18 \x01(\x0b2".proto.CancelPaymentRequestMessage\x12/\n\x0ftemplateMessage\x18\x19 \x01(\x0b2\x16.proto.TemplateMessage\x12-\n\x0estickerMessage\x18\x1a \x01(\x0b2\x15.proto.StickerMessage\x125\n\x12groupInviteMessage\x18\x1c \x01(\x0b2\x19.proto.GroupInviteMessage\x12E\n\x1atemplateButtonReplyMessage\x18\x1d \x01(\x0b2!.proto.TemplateButtonReplyMessage\x12-\n\x0eproductMessage\x18\x1e \x01(\x0b2\x15.proto.ProductMessage\x123\n\x11deviceSentMessage\x18\x1f \x01(\x0b2\x18.proto.DeviceSentMessage\x125\n\x12messageContextInfo\x18# \x01(\x0b2\x19.proto.MessageContextInfo\x12\'\n\x0blistMessage\x18$ \x01(\x0b2\x12.proto.ListMessage\x122\n\x0fviewOnceMessage\x18% \x01(\x0b2\x19.proto.FutureProofMessage\x12)\n\x0corderMessage\x18& \x01(\x0b2\x13.proto.OrderMessage\x127\n\x13listResponseMessage\x18\' \x01(\x0b2\x1a.proto.ListResponseMessage\x123\n\x10ephemeralMessage\x18( \x01(\x0b2\x19.proto.FutureProofMessage\x12-\n\x0einvoiceMessage\x18) \x01(\x0b2\x15.proto.InvoiceMessage\x12-\n\x0ebuttonsMessage\x18* \x01(\x0b2\x15.proto.ButtonsMessage\x12=\n\x16buttonsResponseMessage\x18+ \x01(\x0b2\x1d.proto.ButtonsResponseMessage\x129\n\x14paymentInviteMessage\x18, \x01(\x0b2\x1b.proto.PaymentInviteMessage\x125\n\x12interactiveMessage\x18- \x01(\x0b2\x19.proto.InteractiveMessage\x12/\n\x0freactionMessage\x18. \x01(\x0b2\x16.proto.ReactionMessage\x12;\n\x15stickerSyncRmrMessage\x18/ \x01(\x0b2\x1c.proto.StickerSyncRMRMessage\x12E\n\x1ainteractiveResponseMessage\x180 \x01(\x0b2!.proto.InteractiveResponseMessage\x127\n\x13pollCreationMessage\x181 \x01(\x0b2\x1a.proto.PollCreationMessage\x123\n\x11pollUpdateMessage\x182 \x01(\x0b2\x18.proto.PollUpdateMessage\x123\n\x11keepInChatMessage\x183 \x01(\x0b2\x18.proto.KeepInChatMessage\x12=\n\x1adocumentWithCaptionMessage\x185 \x01(\x0b2\x19.proto.FutureProofMessage\x12C\n\x19requestPhoneNumberMessage\x186 \x01(\x0b2 .proto.RequestPhoneNumberMessage\x124\n\x11viewOnceMessageV2\x187 \x01(\x0b2\x19.proto.FutureProofMessage\x125\n\x12encReactionMessage\x188 \x01(\x0b2\x19.proto.EncReactionMessage\x120\n\reditedMessage\x18: \x01(\x0b2\x19.proto.FutureProofMessage\x12=\n\x1aviewOnceMessageV2Extension\x18; \x01(\x0b2\x19.proto.FutureProofMessage\x129\n\x15pollCreationMessageV2\x18< \x01(\x0b2\x1a.proto.PollCreationMessage\x12I\n\x1cscheduledCallCreationMessage\x18= \x01(\x0b2#.proto.ScheduledCallCreationMessage\x128\n\x15groupMentionedMessage\x18> \x01(\x0b2\x19.proto.FutureProofMessage\x121\n\x10pinInChatMessage\x18? \x01(\x0b2\x17.proto.PinInChatMessage\x129\n\x15pollCreationMessageV3\x18@ \x01(\x0b2\x1a.proto.PollCreationMessage\x12A\n\x18scheduledCallEditMessage\x18A \x01(\x0b2\x1f.proto.ScheduledCallEditMessage\x12\'\n\nptvMessage\x18B \x01(\x0b2\x13.proto.VideoMessage"\xbf\x01\n\x12MessageContextInfo\x125\n\x12deviceListMetadata\x18\x01 \x01(\x0b2\x19.proto.DeviceListMetadata\x12!\n\x19deviceListMetadataVersion\x18\x02 \x01(\x05\x12\x15\n\rmessageSecret\x18\x03 \x01(\x0c\x12\x14\n\x0cpaddingBytes\x18\x04 \x01(\x0c\x12"\n\x1amessageAddOnDurationInSecs\x18\x05 \x01(\r"\xfa\x04\n\x0cVideoMessage\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\x10\n\x08mimetype\x18\x02 \x01(\t\x12\x12\n\nfileSha256\x18\x03 \x01(\x0c\x12\x12\n\nfileLength\x18\x04 \x01(\x04\x12\x0f\n\x07seconds\x18\x05 \x01(\r\x12\x10\n\x08mediaKey\x18\x06 \x01(\x0c\x12\x0f\n\x07caption\x18\x07 \x01(\t\x12\x13\n\x0bgifPlayback\x18\x08 \x01(\x08\x12\x0e\n\x06height\x18\t \x01(\r\x12\r\n\x05width\x18\n \x01(\r\x12\x15\n\rfileEncSha256\x18\x0b \x01(\x0c\x12<\n\x16interactiveAnnotations\x18\x0c \x03(\x0b2\x1c.proto.InteractiveAnnotation\x12\x12\n\ndirectPath\x18\r \x01(\t\x12\x19\n\x11mediaKeyTimestamp\x18\x0e \x01(\x03\x12\x15\n\rjpegThumbnail\x18\x10 \x01(\x0c\x12\'\n\x0bcontextInfo\x18\x11 \x01(\x0b2\x12.proto.ContextInfo\x12\x18\n\x10streamingSidecar\x18\x12 \x01(\x0c\x127\n\x0egifAttribution\x18\x13 \x01(\x0e2\x1f.proto.VideoMessage.Attribution\x12\x10\n\x08viewOnce\x18\x14 \x01(\x08\x12\x1b\n\x13thumbnailDirectPath\x18\x15 \x01(\t\x12\x17\n\x0fthumbnailSha256\x18\x16 \x01(\x0c\x12\x1a\n\x12thumbnailEncSha256\x18\x17 \x01(\x0c\x12\x11\n\tstaticUrl\x18\x18 \x01(\t"-\n\x0bAttribution\x12\x08\n\x04NONE\x10\x00\x12\t\n\x05GIPHY\x10\x01\x12\t\n\x05TENOR\x10\x02"\xa9\t\n\x0fTemplateMessage\x12\'\n\x0bcontextInfo\x18\x03 \x01(\x0b2\x12.proto.ContextInfo\x12H\n\x10hydratedTemplate\x18\x04 \x01(\x0b2..proto.TemplateMessage.HydratedFourRowTemplate\x12\x12\n\ntemplateId\x18\t \x01(\t\x12A\n\x0ffourRowTemplate\x18\x01 \x01(\x0b2&.proto.TemplateMessage.FourRowTemplateH\x00\x12Q\n\x17hydratedFourRowTemplate\x18\x02 \x01(\x0b2..proto.TemplateMessage.HydratedFourRowTemplateH\x00\x12?\n\x1ainteractiveMessageTemplate\x18\x05 \x01(\x0b2\x19.proto.InteractiveMessageH\x00\x1a\x84\x03\n\x17HydratedFourRowTemplate\x12\x1b\n\x13hydratedContentText\x18\x06 \x01(\t\x12\x1a\n\x12hydratedFooterText\x18\x07 \x01(\t\x126\n\x0fhydratedButtons\x18\x08 \x03(\x0b2\x1d.proto.HydratedTemplateButton\x12\x12\n\ntemplateId\x18\t \x01(\t\x121\n\x0fdocumentMessage\x18\x01 \x01(\x0b2\x16.proto.DocumentMessageH\x00\x12\x1b\n\x11hydratedTitleText\x18\x02 \x01(\tH\x00\x12+\n\x0cimageMessage\x18\x03 \x01(\x0b2\x13.proto.ImageMessageH\x00\x12+\n\x0cvideoMessage\x18\x04 \x01(\x0b2\x13.proto.VideoMessageH\x00\x121\n\x0flocationMessage\x18\x05 \x01(\x0b2\x16.proto.LocationMessageH\x00B\x07\n\x05title\x1a\xa6\x03\n\x0fFourRowTemplate\x12/\n\x07content\x18\x06 \x01(\x0b2\x1e.proto.HighlyStructuredMessage\x12.\n\x06footer\x18\x07 \x01(\x0b2\x1e.proto.HighlyStructuredMessage\x12&\n\x07buttons\x18\x08 \x03(\x0b2\x15.proto.TemplateButton\x121\n\x0fdocumentMessage\x18\x01 \x01(\x0b2\x16.proto.DocumentMessageH\x00\x12A\n\x17highlyStructuredMessage\x18\x02 \x01(\x0b2\x1e.proto.HighlyStructuredMessageH\x00\x12+\n\x0cimageMessage\x18\x03 \x01(\x0b2\x13.proto.ImageMessageH\x00\x12+\n\x0cvideoMessage\x18\x04 \x01(\x0b2\x13.proto.VideoMessageH\x00\x121\n\x0flocationMessage\x18\x05 \x01(\x0b2\x16.proto.LocationMessageH\x00B\x07\n\x05titleB\x08\n\x06format"\x8d\x01\n\x1aTemplateButtonReplyMessage\x12\x12\n\nselectedId\x18\x01 \x01(\t\x12\x1b\n\x13selectedDisplayText\x18\x02 \x01(\t\x12\'\n\x0bcontextInfo\x18\x03 \x01(\x0b2\x12.proto.ContextInfo\x12\x15\n\rselectedIndex\x18\x04 \x01(\r"V\n\x15StickerSyncRMRMessage\x12\x10\n\x08filehash\x18\x01 \x03(\t\x12\x11\n\trmrSource\x18\x02 \x01(\t\x12\x18\n\x10requestTimestamp\x18\x03 \x01(\x03"\xff\x02\n\x0eStickerMessage\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\x12\n\nfileSha256\x18\x02 \x01(\x0c\x12\x15\n\rfileEncSha256\x18\x03 \x01(\x0c\x12\x10\n\x08mediaKey\x18\x04 \x01(\x0c\x12\x10\n\x08mimetype\x18\x05 \x01(\t\x12\x0e\n\x06height\x18\x06 \x01(\r\x12\r\n\x05width\x18\x07 \x01(\r\x12\x12\n\ndirectPath\x18\x08 \x01(\t\x12\x12\n\nfileLength\x18\t \x01(\x04\x12\x19\n\x11mediaKeyTimestamp\x18\n \x01(\x03\x12\x18\n\x10firstFrameLength\x18\x0b \x01(\r\x12\x19\n\x11firstFrameSidecar\x18\x0c \x01(\x0c\x12\x12\n\nisAnimated\x18\r \x01(\x08\x12\x14\n\x0cpngThumbnail\x18\x10 \x01(\x0c\x12\'\n\x0bcontextInfo\x18\x11 \x01(\x0b2\x12.proto.ContextInfo\x12\x15\n\rstickerSentTs\x18\x12 \x01(\x03\x12\x10\n\x08isAvatar\x18\x13 \x01(\x08"\\\n\x1cSenderKeyDistributionMessage\x12\x0f\n\x07groupId\x18\x01 \x01(\t\x12+\n#axolotlSenderKeyDistributionMessage\x18\x02 \x01(\x0c"\x95\x01\n\x12SendPaymentMessage\x12#\n\x0bnoteMessage\x18\x02 \x01(\x0b2\x0e.proto.Message\x12,\n\x11requestMessageKey\x18\x03 \x01(\x0b2\x11.proto.MessageKey\x12,\n\nbackground\x18\x04 \x01(\x0b2\x18.proto.PaymentBackground"\x9b\x01\n\x18ScheduledCallEditMessage\x12\x1e\n\x03key\x18\x01 \x01(\x0b2\x11.proto.MessageKey\x12:\n\x08editType\x18\x02 \x01(\x0e2(.proto.ScheduledCallEditMessage.EditType"#\n\x08EditType\x12\x0b\n\x07UNKNOWN\x10\x00\x12\n\n\x06CANCEL\x10\x01"\xba\x01\n\x1cScheduledCallCreationMessage\x12\x1c\n\x14scheduledTimestampMs\x18\x01 \x01(\x03\x12>\n\x08callType\x18\x02 \x01(\x0e2,.proto.ScheduledCallCreationMessage.CallType\x12\r\n\x05title\x18\x03 \x01(\t"-\n\x08CallType\x12\x0b\n\x07UNKNOWN\x10\x00\x12\t\n\x05VOICE\x10\x01\x12\t\n\x05VIDEO\x10\x02"D\n\x19RequestPhoneNumberMessage\x12\'\n\x0bcontextInfo\x18\x01 \x01(\x0b2\x12.proto.ContextInfo"\xe7\x01\n\x15RequestPaymentMessage\x12#\n\x0bnoteMessage\x18\x04 \x01(\x0b2\x0e.proto.Message\x12\x1b\n\x13currencyCodeIso4217\x18\x01 \x01(\t\x12\x12\n\namount1000\x18\x02 \x01(\x04\x12\x13\n\x0brequestFrom\x18\x03 \x01(\t\x12\x17\n\x0fexpiryTimestamp\x18\x05 \x01(\x03\x12\x1c\n\x06amount\x18\x06 \x01(\x0b2\x0c.proto.Money\x12,\n\nbackground\x18\x07 \x01(\x0b2\x18.proto.PaymentBackground"o\n\x0fReactionMessage\x12\x1e\n\x03key\x18\x01 \x01(\x0b2\x11.proto.MessageKey\x12\x0c\n\x04text\x18\x02 \x01(\t\x12\x13\n\x0bgroupingKey\x18\x03 \x01(\t\x12\x19\n\x11senderTimestampMs\x18\x04 \x01(\x03"\xd6\t\n\x0fProtocolMessage\x12\x1e\n\x03key\x18\x01 \x01(\x0b2\x11.proto.MessageKey\x12)\n\x04type\x18\x02 \x01(\x0e2\x1b.proto.ProtocolMessage.Type\x12\x1b\n\x13ephemeralExpiration\x18\x04 \x01(\r\x12!\n\x19ephemeralSettingTimestamp\x18\x05 \x01(\x03\x12?\n\x17historySyncNotification\x18\x06 \x01(\x0b2\x1e.proto.HistorySyncNotification\x129\n\x14appStateSyncKeyShare\x18\x07 \x01(\x0b2\x1b.proto.AppStateSyncKeyShare\x12=\n\x16appStateSyncKeyRequest\x18\x08 \x01(\x0b2\x1d.proto.AppStateSyncKeyRequest\x12]\n&initialSecurityNotificationSettingSync\x18\t \x01(\x0b2-.proto.InitialSecurityNotificationSettingSync\x12U\n"appStateFatalExceptionNotification\x18\n \x01(\x0b2).proto.AppStateFatalExceptionNotification\x121\n\x10disappearingMode\x18\x0b \x01(\x0b2\x17.proto.DisappearingMode\x12%\n\reditedMessage\x18\x0e \x01(\x0b2\x0e.proto.Message\x12\x13\n\x0btimestampMs\x18\x0f \x01(\x03\x12O\n\x1fpeerDataOperationRequestMessage\x18\x10 \x01(\x0b2&.proto.PeerDataOperationRequestMessage\x12_\n\'peerDataOperationRequestResponseMessage\x18\x11 \x01(\x0b2..proto.PeerDataOperationRequestResponseMessage"\xa5\x03\n\x04Type\x12\n\n\x06REVOKE\x10\x00\x12\x15\n\x11EPHEMERAL_SETTING\x10\x03\x12\x1b\n\x17EPHEMERAL_SYNC_RESPONSE\x10\x04\x12\x1d\n\x19HISTORY_SYNC_NOTIFICATION\x10\x05\x12\x1c\n\x18APP_STATE_SYNC_KEY_SHARE\x10\x06\x12\x1e\n\x1aAPP_STATE_SYNC_KEY_REQUEST\x10\x07\x12\x1f\n\x1bMSG_FANOUT_BACKFILL_REQUEST\x10\x08\x12.\n*INITIAL_SECURITY_NOTIFICATION_SETTING_SYNC\x10\t\x12*\n&APP_STATE_FATAL_EXCEPTION_NOTIFICATION\x10\n\x12\x16\n\x12SHARE_PHONE_NUMBER\x10\x0b\x12\x10\n\x0cMESSAGE_EDIT\x10\x0e\x12\'\n#PEER_DATA_OPERATION_REQUEST_MESSAGE\x10\x10\x120\n,PEER_DATA_OPERATION_REQUEST_RESPONSE_MESSAGE\x10\x11"\xd7\x04\n\x0eProductMessage\x126\n\x07product\x18\x01 \x01(\x0b2%.proto.ProductMessage.ProductSnapshot\x12\x18\n\x10businessOwnerJid\x18\x02 \x01(\t\x126\n\x07catalog\x18\x04 \x01(\x0b2%.proto.ProductMessage.CatalogSnapshot\x12\x0c\n\x04body\x18\x05 \x01(\t\x12\x0e\n\x06footer\x18\x06 \x01(\t\x12\'\n\x0bcontextInfo\x18\x11 \x01(\x0b2\x12.proto.ContextInfo\x1a\x91\x02\n\x0fProductSnapshot\x12)\n\x0cproductImage\x18\x01 \x01(\x0b2\x13.proto.ImageMessage\x12\x11\n\tproductId\x18\x02 \x01(\t\x12\r\n\x05title\x18\x03 \x01(\t\x12\x13\n\x0bdescription\x18\x04 \x01(\t\x12\x14\n\x0ccurrencyCode\x18\x05 \x01(\t\x12\x17\n\x0fpriceAmount1000\x18\x06 \x01(\x03\x12\x12\n\nretailerId\x18\x07 \x01(\t\x12\x0b\n\x03url\x18\x08 \x01(\t\x12\x19\n\x11productImageCount\x18\t \x01(\r\x12\x14\n\x0cfirstImageId\x18\x0b \x01(\t\x12\x1b\n\x13salePriceAmount1000\x18\x0c \x01(\x03\x1a`\n\x0fCatalogSnapshot\x12)\n\x0ccatalogImage\x18\x01 \x01(\x0b2\x13.proto.ImageMessage\x12\r\n\x05title\x18\x02 \x01(\t\x12\x13\n\x0bdescription\x18\x03 \x01(\t"*\n\x0fPollVoteMessage\x12\x17\n\x0fselectedOptions\x18\x01 \x03(\x0c"\xb8\x01\n\x11PollUpdateMessage\x121\n\x16pollCreationMessageKey\x18\x01 \x01(\x0b2\x11.proto.MessageKey\x12!\n\x04vote\x18\x02 \x01(\x0b2\x13.proto.PollEncValue\x122\n\x08metadata\x18\x03 \x01(\x0b2 .proto.PollUpdateMessageMetadata\x12\x19\n\x11senderTimestampMs\x18\x04 \x01(\x03"\x1b\n\x19PollUpdateMessageMetadata"1\n\x0cPollEncValue\x12\x12\n\nencPayload\x18\x01 \x01(\x0c\x12\r\n\x05encIv\x18\x02 \x01(\x0c"\xce\x01\n\x13PollCreationMessage\x12\x0e\n\x06encKey\x18\x01 \x01(\x0c\x12\x0c\n\x04name\x18\x02 \x01(\t\x122\n\x07options\x18\x03 \x03(\x0b2!.proto.PollCreationMessage.Option\x12\x1e\n\x16selectableOptionsCount\x18\x04 \x01(\r\x12\'\n\x0bcontextInfo\x18\x05 \x01(\x0b2\x12.proto.ContextInfo\x1a\x1c\n\x06Option\x12\x12\n\noptionName\x18\x01 \x01(\t"\xb7\x01\n\x10PinInChatMessage\x12\x1e\n\x03key\x18\x01 \x01(\x0b2\x11.proto.MessageKey\x12*\n\x04type\x18\x02 \x01(\x0e2\x1c.proto.PinInChatMessage.Type\x12\x19\n\x11senderTimestampMs\x18\x03 \x01(\x03"<\n\x04Type\x12\x10\n\x0cUNKNOWN_TYPE\x10\x00\x12\x0f\n\x0bPIN_FOR_ALL\x10\x01\x12\x11\n\rUNPIN_FOR_ALL\x10\x02"\xb2\t\n\'PeerDataOperationRequestResponseMessage\x12I\n\x1cpeerDataOperationRequestType\x18\x01 \x01(\x0e2#.proto.PeerDataOperationRequestType\x12\x10\n\x08stanzaId\x18\x02 \x01(\t\x12g\n\x17peerDataOperationResult\x18\x03 \x03(\x0b2F.proto.PeerDataOperationRequestResponseMessage.PeerDataOperationResult\x1a\xc0\x07\n\x17PeerDataOperationResult\x12C\n\x11mediaUploadResult\x18\x01 \x01(\x0e2(.proto.MediaRetryNotification.ResultType\x12-\n\x0estickerMessage\x18\x02 \x01(\x0b2\x15.proto.StickerMessage\x12w\n\x13linkPreviewResponse\x18\x03 \x01(\x0b2Z.proto.PeerDataOperationRequestResponseMessage.PeerDataOperationResult.LinkPreviewResponse\x12\x91\x01\n placeholderMessageResendResponse\x18\x04 \x01(\x0b2g.proto.PeerDataOperationRequestResponseMessage.PeerDataOperationResult.PlaceholderMessageResendResponse\x1a?\n PlaceholderMessageResendResponse\x12\x1b\n\x13webMessageInfoBytes\x18\x01 \x01(\x0c\x1a\xe2\x03\n\x13LinkPreviewResponse\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\r\n\x05title\x18\x02 \x01(\t\x12\x13\n\x0bdescription\x18\x03 \x01(\t\x12\x11\n\tthumbData\x18\x04 \x01(\x0c\x12\x14\n\x0ccanonicalUrl\x18\x05 \x01(\t\x12\x11\n\tmatchText\x18\x06 \x01(\t\x12\x13\n\x0bpreviewType\x18\x07 \x01(\t\x12\x8f\x01\n\x0bhqThumbnail\x18\x08 \x01(\x0b2z.proto.PeerDataOperationRequestResponseMessage.PeerDataOperationResult.LinkPreviewResponse.LinkPreviewHighQualityThumbnail\x1a\xb6\x01\n\x1fLinkPreviewHighQualityThumbnail\x12\x12\n\ndirectPath\x18\x01 \x01(\t\x12\x11\n\tthumbHash\x18\x02 \x01(\t\x12\x14\n\x0cencThumbHash\x18\x03 \x01(\t\x12\x10\n\x08mediaKey\x18\x04 \x01(\x0c\x12\x1b\n\x13mediaKeyTimestampMs\x18\x05 \x01(\x03\x12\x12\n\nthumbWidth\x18\x06 \x01(\x05\x12\x13\n\x0bthumbHeight\x18\x07 \x01(\x05"\xc4\x06\n\x1fPeerDataOperationRequestMessage\x12I\n\x1cpeerDataOperationRequestType\x18\x01 \x01(\x0e2#.proto.PeerDataOperationRequestType\x12]\n\x16requestStickerReupload\x18\x02 \x03(\x0b2=.proto.PeerDataOperationRequestMessage.RequestStickerReupload\x12S\n\x11requestUrlPreview\x18\x03 \x03(\x0b28.proto.PeerDataOperationRequestMessage.RequestUrlPreview\x12e\n\x1ahistorySyncOnDemandRequest\x18\x04 \x01(\x0b2A.proto.PeerDataOperationRequestMessage.HistorySyncOnDemandRequest\x12o\n\x1fplaceholderMessageResendRequest\x18\x05 \x03(\x0b2F.proto.PeerDataOperationRequestMessage.PlaceholderMessageResendRequest\x1a<\n\x11RequestUrlPreview\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\x1a\n\x12includeHqThumbnail\x18\x02 \x01(\x08\x1a,\n\x16RequestStickerReupload\x12\x12\n\nfileSha256\x18\x01 \x01(\t\x1aH\n\x1fPlaceholderMessageResendRequest\x12%\n\nmessageKey\x18\x01 \x01(\x0b2\x11.proto.MessageKey\x1a\x93\x01\n\x1aHistorySyncOnDemandRequest\x12\x0f\n\x07chatJid\x18\x01 \x01(\t\x12\x13\n\x0boldestMsgId\x18\x02 \x01(\t\x12\x17\n\x0foldestMsgFromMe\x18\x03 \x01(\x08\x12\x18\n\x10onDemandMsgCount\x18\x04 \x01(\x05\x12\x1c\n\x14oldestMsgTimestampMs\x18\x05 \x01(\x03"7\n\x10EphemeralSetting\x12\x10\n\x08duration\x18\x01 \x01(\x0f\x12\x11\n\ttimestamp\x18\x02 \x01(\x10"6\n\x11WallpaperSettings\x12\x10\n\x08filename\x18\x01 \x01(\t\x12\x0f\n\x07opacity\x18\x02 \x01(\r"\xdf\x01\n\x0fStickerMetadata\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\x12\n\nfileSha256\x18\x02 \x01(\x0c\x12\x15\n\rfileEncSha256\x18\x03 \x01(\x0c\x12\x10\n\x08mediaKey\x18\x04 \x01(\x0c\x12\x10\n\x08mimetype\x18\x05 \x01(\t\x12\x0e\n\x06height\x18\x06 \x01(\r\x12\r\n\x05width\x18\x07 \x01(\r\x12\x12\n\ndirectPath\x18\x08 \x01(\t\x12\x12\n\nfileLength\x18\t \x01(\x04\x12\x0e\n\x06weight\x18\n \x01(\x02\x12\x19\n\x11lastStickerSentTs\x18\x0b \x01(\x03"(\n\x08Pushname\x12\n\n\x02id\x18\x01 \x01(\t\x12\x10\n\x08pushname\x18\x02 \x01(\t"V\n\x10PastParticipants\x12\x10\n\x08groupJid\x18\x01 \x01(\t\x120\n\x10pastParticipants\x18\x02 \x03(\x0b2\x16.proto.PastParticipant"\x92\x01\n\x0fPastParticipant\x12\x0f\n\x07userJid\x18\x01 \x01(\t\x127\n\x0bleaveReason\x18\x02 \x01(\x0e2".proto.PastParticipant.LeaveReason\x12\x0f\n\x07leaveTs\x18\x03 \x01(\x04"$\n\x0bLeaveReason\x12\x08\n\x04LEFT\x10\x00\x12\x0b\n\x07REMOVED\x10\x01"\xa9\x01\n\x14NotificationSettings\x12\x16\n\x0emessageVibrate\x18\x01 \x01(\t\x12\x14\n\x0cmessagePopup\x18\x02 \x01(\t\x12\x14\n\x0cmessageLight\x18\x03 \x01(\t\x12 \n\x18lowPriorityNotifications\x18\x04 \x01(\x08\x12\x16\n\x0ereactionsMuted\x18\x05 \x01(\x08\x12\x13\n\x0bcallVibrate\x18\x06 \x01(\t"\xc6\x04\n\x0bHistorySync\x124\n\x08syncType\x18\x01 \x02(\x0e2".proto.HistorySync.HistorySyncType\x12*\n\rconversations\x18\x02 \x03(\x0b2\x13.proto.Conversation\x12/\n\x10statusV3Messages\x18\x03 \x03(\x0b2\x15.proto.WebMessageInfo\x12\x12\n\nchunkOrder\x18\x05 \x01(\r\x12\x10\n\x08progress\x18\x06 \x01(\r\x12"\n\tpushnames\x18\x07 \x03(\x0b2\x0f.proto.Pushname\x12-\n\x0eglobalSettings\x18\x08 \x01(\x0b2\x15.proto.GlobalSettings\x12\x1a\n\x12threadIdUserSecret\x18\t \x01(\x0c\x12\x1f\n\x17threadDsTimeframeOffset\x18\n \x01(\r\x12.\n\x0erecentStickers\x18\x0b \x03(\x0b2\x16.proto.StickerMetadata\x121\n\x10pastParticipants\x18\x0c \x03(\x0b2\x17.proto.PastParticipants"\x8a\x01\n\x0fHistorySyncType\x12\x15\n\x11INITIAL_BOOTSTRAP\x10\x00\x12\x15\n\x11INITIAL_STATUS_V3\x10\x01\x12\x08\n\x04FULL\x10\x02\x12\n\n\x06RECENT\x10\x03\x12\r\n\tPUSH_NAME\x10\x04\x12\x15\n\x11NON_BLOCKING_DATA\x10\x05\x12\r\n\tON_DEMAND\x10\x06"L\n\x0eHistorySyncMsg\x12&\n\x07message\x18\x01 \x01(\x0b2\x15.proto.WebMessageInfo\x12\x12\n\nmsgOrderId\x18\x02 \x01(\x04"\x7f\n\x10GroupParticipant\x12\x0f\n\x07userJid\x18\x01 \x02(\t\x12*\n\x04rank\x18\x02 \x01(\x0e2\x1c.proto.GroupParticipant.Rank".\n\x04Rank\x12\x0b\n\x07REGULAR\x10\x00\x12\t\n\x05ADMIN\x10\x01\x12\x0e\n\nSUPERADMIN\x10\x02"\xaf\x06\n\x0eGlobalSettings\x125\n\x13lightThemeWallpaper\x18\x01 \x01(\x0b2\x18.proto.WallpaperSettings\x12/\n\x0fmediaVisibility\x18\x02 \x01(\x0e2\x16.proto.MediaVisibility\x124\n\x12darkThemeWallpaper\x18\x03 \x01(\x0b2\x18.proto.WallpaperSettings\x125\n\x10autoDownloadWiFi\x18\x04 \x01(\x0b2\x1b.proto.AutoDownloadSettings\x129\n\x14autoDownloadCellular\x18\x05 \x01(\x0b2\x1b.proto.AutoDownloadSettings\x128\n\x13autoDownloadRoaming\x18\x06 \x01(\x0b2\x1b.proto.AutoDownloadSettings\x12*\n"showIndividualNotificationsPreview\x18\x07 \x01(\x08\x12%\n\x1dshowGroupNotificationsPreview\x18\x08 \x01(\x08\x12 \n\x18disappearingModeDuration\x18\t \x01(\x05\x12!\n\x19disappearingModeTimestamp\x18\n \x01(\x03\x125\n\x12avatarUserSettings\x18\x0b \x01(\x0b2\x19.proto.AvatarUserSettings\x12\x10\n\x08fontSize\x18\x0c \x01(\x05\x12\x1d\n\x15securityNotifications\x18\r \x01(\x08\x12\x1a\n\x12autoUnarchiveChats\x18\x0e \x01(\x08\x12\x18\n\x10videoQualityMode\x18\x0f \x01(\x05\x12\x18\n\x10photoQualityMode\x18\x10 \x01(\x05\x12C\n\x1eindividualNotificationSettings\x18\x11 \x01(\x0b2\x1b.proto.NotificationSettings\x12>\n\x19groupNotificationSettings\x18\x12 \x01(\x0b2\x1b.proto.NotificationSettings"\x99\n\n\x0cConversation\x12\n\n\x02id\x18\x01 \x02(\t\x12\'\n\x08messages\x18\x02 \x03(\x0b2\x15.proto.HistorySyncMsg\x12\x0e\n\x06newJid\x18\x03 \x01(\t\x12\x0e\n\x06oldJid\x18\x04 \x01(\t\x12\x18\n\x10lastMsgTimestamp\x18\x05 \x01(\x04\x12\x13\n\x0bunreadCount\x18\x06 \x01(\r\x12\x10\n\x08readOnly\x18\x07 \x01(\x08\x12\x1c\n\x14endOfHistoryTransfer\x18\x08 \x01(\x08\x12\x1b\n\x13ephemeralExpiration\x18\t \x01(\r\x12!\n\x19ephemeralSettingTimestamp\x18\n \x01(\x03\x12N\n\x18endOfHistoryTransferType\x18\x0b \x01(\x0e2,.proto.Conversation.EndOfHistoryTransferType\x12\x1d\n\x15conversationTimestamp\x18\x0c \x01(\x04\x12\x0c\n\x04name\x18\r \x01(\t\x12\r\n\x05pHash\x18\x0e \x01(\t\x12\x0f\n\x07notSpam\x18\x0f \x01(\x08\x12\x10\n\x08archived\x18\x10 \x01(\x08\x121\n\x10disappearingMode\x18\x11 \x01(\x0b2\x17.proto.DisappearingMode\x12\x1a\n\x12unreadMentionCount\x18\x12 \x01(\r\x12\x16\n\x0emarkedAsUnread\x18\x13 \x01(\x08\x12,\n\x0bparticipant\x18\x14 \x03(\x0b2\x17.proto.GroupParticipant\x12\x0f\n\x07tcToken\x18\x15 \x01(\x0c\x12\x18\n\x10tcTokenTimestamp\x18\x16 \x01(\x04\x12!\n\x19contactPrimaryIdentityKey\x18\x17 \x01(\x0c\x12\x0e\n\x06pinned\x18\x18 \x01(\r\x12\x13\n\x0bmuteEndTime\x18\x19 \x01(\x04\x12+\n\twallpaper\x18\x1a \x01(\x0b2\x18.proto.WallpaperSettings\x12/\n\x0fmediaVisibility\x18\x1b \x01(\x0e2\x16.proto.MediaVisibility\x12\x1e\n\x16tcTokenSenderTimestamp\x18\x1c \x01(\x04\x12\x11\n\tsuspended\x18\x1d \x01(\x08\x12\x12\n\nterminated\x18\x1e \x01(\x08\x12\x11\n\tcreatedAt\x18\x1f \x01(\x04\x12\x11\n\tcreatedBy\x18  \x01(\t\x12\x13\n\x0bdescription\x18! \x01(\t\x12\x0f\n\x07support\x18" \x01(\x08\x12\x15\n\risParentGroup\x18# \x01(\x08\x12\x15\n\rparentGroupId\x18% \x01(\t\x12\x19\n\x11isDefaultSubgroup\x18$ \x01(\x08\x12\x13\n\x0bdisplayName\x18& \x01(\t\x12\r\n\x05pnJid\x18\' \x01(\t\x12\x12\n\nshareOwnPn\x18( \x01(\x08\x12\x1d\n\x15pnhDuplicateLidThread\x18) \x01(\x08\x12\x0e\n\x06lidJid\x18* \x01(\t"\xbc\x01\n\x18EndOfHistoryTransferType\x120\n,COMPLETE_BUT_MORE_MESSAGES_REMAIN_ON_PRIMARY\x10\x00\x122\n.COMPLETE_AND_NO_MORE_MESSAGE_REMAIN_ON_PRIMARY\x10\x01\x12:\n6COMPLETE_ON_DEMAND_SYNC_BUT_MORE_MSG_REMAIN_ON_PRIMARY\x10\x02"4\n\x12AvatarUserSettings\x12\x0c\n\x04fbid\x18\x01 \x01(\t\x12\x10\n\x08password\x18\x02 \x01(\t"w\n\x14AutoDownloadSettings\x12\x16\n\x0edownloadImages\x18\x01 \x01(\x08\x12\x15\n\rdownloadAudio\x18\x02 \x01(\x08\x12\x15\n\rdownloadVideo\x18\x03 \x01(\x08\x12\x19\n\x11downloadDocuments\x18\x04 \x01(\x08"e\n\x10MsgRowOpaqueData\x12(\n\ncurrentMsg\x18\x01 \x01(\x0b2\x14.proto.MsgOpaqueData\x12\'\n\tquotedMsg\x18\x02 \x01(\x0b2\x14.proto.MsgOpaqueData"\xb3\x05\n\rMsgOpaqueData\x12\x0c\n\x04body\x18\x01 \x01(\t\x12\x0f\n\x07caption\x18\x03 \x01(\t\x12\x0b\n\x03lng\x18\x05 \x01(\x01\x12\x0e\n\x06isLive\x18\x06 \x01(\x08\x12\x0b\n\x03lat\x18\x07 \x01(\x01\x12\x19\n\x11paymentAmount1000\x18\x08 \x01(\x05\x12\x1a\n\x12paymentNoteMsgBody\x18\t \x01(\t\x12\x14\n\x0ccanonicalUrl\x18\n \x01(\t\x12\x13\n\x0bmatchedText\x18\x0b \x01(\t\x12\r\n\x05title\x18\x0c \x01(\t\x12\x13\n\x0bdescription\x18\r \x01(\t\x12\x19\n\x11futureproofBuffer\x18\x0e \x01(\x0c\x12\x11\n\tclientUrl\x18\x0f \x01(\t\x12\x0b\n\x03loc\x18\x10 \x01(\t\x12\x10\n\x08pollName\x18\x11 \x01(\t\x124\n\x0bpollOptions\x18\x12 \x03(\x0b2\x1f.proto.MsgOpaqueData.PollOption\x12"\n\x1apollSelectableOptionsCount\x18\x14 \x01(\r\x12\x15\n\rmessageSecret\x18\x15 \x01(\x0c\x12\x1a\n\x12originalSelfAuthor\x183 \x01(\t\x12\x19\n\x11senderTimestampMs\x18\x16 \x01(\x03\x12\x1b\n\x13pollUpdateParentKey\x18\x17 \x01(\t\x12(\n\x0bencPollVote\x18\x18 \x01(\x0b2\x13.proto.PollEncValue\x12\x1d\n\x15isSentCagPollCreation\x18\x1c \x01(\x08\x12#\n\x1bencReactionTargetMessageKey\x18\x19 \x01(\t\x12\x1d\n\x15encReactionEncPayload\x18\x1a \x01(\x0c\x12\x18\n\x10encReactionEncIv\x18\x1b \x01(\x0c\x1a\x1a\n\nPollOption\x12\x0c\n\x04name\x18\x01 \x01(\t"&\n\x12ServerErrorReceipt\x12\x10\n\x08stanzaId\x18\x01 \x01(\t"\xcb\x01\n\x16MediaRetryNotification\x12\x10\n\x08stanzaId\x18\x01 \x01(\t\x12\x12\n\ndirectPath\x18\x02 \x01(\t\x128\n\x06result\x18\x03 \x01(\x0e2(.proto.MediaRetryNotification.ResultType"Q\n\nResultType\x12\x11\n\rGENERAL_ERROR\x10\x00\x12\x0b\n\x07SUCCESS\x10\x01\x12\r\n\tNOT_FOUND\x10\x02\x12\x14\n\x10DECRYPTION_ERROR\x10\x03"P\n\nMessageKey\x12\x11\n\tremoteJid\x18\x01 \x01(\t\x12\x0e\n\x06fromMe\x18\x02 \x01(\x08\x12\n\n\x02id\x18\x03 \x01(\t\x12\x13\n\x0bparticipant\x18\x04 \x01(\t"\x1f\n\x0cSyncdVersion\x12\x0f\n\x07version\x18\x01 \x01(\x04"\x1a\n\nSyncdValue\x12\x0c\n\x04blob\x18\x01 \x01(\x0c"\x84\x01\n\rSyncdSnapshot\x12$\n\x07version\x18\x01 \x01(\x0b2\x13.proto.SyncdVersion\x12#\n\x07records\x18\x02 \x03(\x0b2\x12.proto.SyncdRecord\x12\x0b\n\x03mac\x18\x03 \x01(\x0c\x12\x1b\n\x05keyId\x18\x04 \x01(\x0b2\x0c.proto.KeyId"n\n\x0bSyncdRecord\x12 \n\x05index\x18\x01 \x01(\x0b2\x11.proto.SyncdIndex\x12 \n\x05value\x18\x02 \x01(\x0b2\x11.proto.SyncdValue\x12\x1b\n\x05keyId\x18\x03 \x01(\x0b2\x0c.proto.KeyId"\x90\x02\n\nSyncdPatch\x12$\n\x07version\x18\x01 \x01(\x0b2\x13.proto.SyncdVersion\x12\'\n\tmutations\x18\x02 \x03(\x0b2\x14.proto.SyncdMutation\x127\n\x11externalMutations\x18\x03 \x01(\x0b2\x1c.proto.ExternalBlobReference\x12\x13\n\x0bsnapshotMac\x18\x04 \x01(\x0c\x12\x10\n\x08patchMac\x18\x05 \x01(\x0c\x12\x1b\n\x05keyId\x18\x06 \x01(\x0b2\x0c.proto.KeyId\x12!\n\x08exitCode\x18\x07 \x01(\x0b2\x0f.proto.ExitCode\x12\x13\n\x0bdeviceIndex\x18\x08 \x01(\r"9\n\x0eSyncdMutations\x12\'\n\tmutations\x18\x01 \x03(\x0b2\x14.proto.SyncdMutation"\x92\x01\n\rSyncdMutation\x126\n\toperation\x18\x01 \x01(\x0e2#.proto.SyncdMutation.SyncdOperation\x12"\n\x06record\x18\x02 \x01(\x0b2\x12.proto.SyncdRecord"%\n\x0eSyncdOperation\x12\x07\n\x03SET\x10\x00\x12\n\n\x06REMOVE\x10\x01"\x1a\n\nSyncdIndex\x12\x0c\n\x04blob\x18\x01 \x01(\x0c"\x13\n\x05KeyId\x12\n\n\x02id\x18\x01 \x01(\x0c"\x8f\x01\n\x15ExternalBlobReference\x12\x10\n\x08mediaKey\x18\x01 \x01(\x0c\x12\x12\n\ndirectPath\x18\x02 \x01(\t\x12\x0e\n\x06handle\x18\x03 \x01(\t\x12\x15\n\rfileSizeBytes\x18\x04 \x01(\x04\x12\x12\n\nfileSha256\x18\x05 \x01(\x0c\x12\x15\n\rfileEncSha256\x18\x06 \x01(\x0c"&\n\x08ExitCode\x12\x0c\n\x04code\x18\x01 \x01(\x04\x12\x0c\n\x04text\x18\x02 \x01(\t"\xb5\x0f\n\x0fSyncActionValue\x12\x11\n\ttimestamp\x18\x01 \x01(\x03\x12%\n\nstarAction\x18\x02 \x01(\x0b2\x11.proto.StarAction\x12+\n\rcontactAction\x18\x03 \x01(\x0b2\x14.proto.ContactAction\x12%\n\nmuteAction\x18\x04 \x01(\x0b2\x11.proto.MuteAction\x12#\n\tpinAction\x18\x05 \x01(\x0b2\x10.proto.PinAction\x12G\n\x1bsecurityNotificationSetting\x18\x06 \x01(\x0b2".proto.SecurityNotificationSetting\x12/\n\x0fpushNameSetting\x18\x07 \x01(\x0b2\x16.proto.PushNameSetting\x121\n\x10quickReplyAction\x18\x08 \x01(\x0b2\x17.proto.QuickReplyAction\x12A\n\x18recentEmojiWeightsAction\x18\x0b \x01(\x0b2\x1f.proto.RecentEmojiWeightsAction\x12/\n\x0flabelEditAction\x18\x0e \x01(\x0b2\x16.proto.LabelEditAction\x12=\n\x16labelAssociationAction\x18\x0f \x01(\x0b2\x1d.proto.LabelAssociationAction\x12+\n\rlocaleSetting\x18\x10 \x01(\x0b2\x14.proto.LocaleSetting\x123\n\x11archiveChatAction\x18\x11 \x01(\x0b2\x18.proto.ArchiveChatAction\x12A\n\x18deleteMessageForMeAction\x18\x12 \x01(\x0b2\x1f.proto.DeleteMessageForMeAction\x12+\n\rkeyExpiration\x18\x13 \x01(\x0b2\x14.proto.KeyExpiration\x129\n\x14markChatAsReadAction\x18\x14 \x01(\x0b2\x1b.proto.MarkChatAsReadAction\x12/\n\x0fclearChatAction\x18\x15 \x01(\x0b2\x16.proto.ClearChatAction\x121\n\x10deleteChatAction\x18\x16 \x01(\x0b2\x17.proto.DeleteChatAction\x12;\n\x15unarchiveChatsSetting\x18\x17 \x01(\x0b2\x1c.proto.UnarchiveChatsSetting\x12-\n\x0eprimaryFeature\x18\x18 \x01(\x0b2\x15.proto.PrimaryFeature\x12C\n\x19androidUnsupportedActions\x18\x1a \x01(\x0b2 .proto.AndroidUnsupportedActions\x12\'\n\x0bagentAction\x18\x1b \x01(\x0b2\x12.proto.AgentAction\x125\n\x12subscriptionAction\x18\x1c \x01(\x0b2\x19.proto.SubscriptionAction\x129\n\x14userStatusMuteAction\x18\x1d \x01(\x0b2\x1b.proto.UserStatusMuteAction\x121\n\x10timeFormatAction\x18\x1e \x01(\x0b2\x17.proto.TimeFormatAction\x12#\n\tnuxAction\x18\x1f \x01(\x0b2\x10.proto.NuxAction\x129\n\x14primaryVersionAction\x18  \x01(\x0b2\x1b.proto.PrimaryVersionAction\x12+\n\rstickerAction\x18! \x01(\x0b2\x14.proto.StickerAction\x12C\n\x19removeRecentStickerAction\x18" \x01(\x0b2 .proto.RemoveRecentStickerAction\x123\n\x0echatAssignment\x18# \x01(\x0b2\x1b.proto.ChatAssignmentAction\x12K\n\x1achatAssignmentOpenedStatus\x18$ \x01(\x0b2\'.proto.ChatAssignmentOpenedStatusAction\x125\n\x12pnForLidChatAction\x18% \x01(\x0b2\x19.proto.PnForLidChatAction\x12=\n\x16marketingMessageAction\x18& \x01(\x0b2\x1d.proto.MarketingMessageAction\x12O\n\x1fmarketingMessageBroadcastAction\x18\' \x01(\x0b2&.proto.MarketingMessageBroadcastAction\x12;\n\x15externalWebBetaAction\x18( \x01(\x0b2\x1c.proto.ExternalWebBetaAction\x12G\n\x1bprivacySettingRelayAllCalls\x18) \x01(\x0b2".proto.PrivacySettingRelayAllCalls"%\n\x14UserStatusMuteAction\x12\r\n\x05muted\x18\x01 \x01(\x08"/\n\x15UnarchiveChatsSetting\x12\x16\n\x0eunarchiveChats\x18\x01 \x01(\x08"9\n\x10TimeFormatAction\x12%\n\x1disTwentyFourHourFormatEnabled\x18\x01 \x01(\x08"F\n\x11SyncActionMessage\x12\x1e\n\x03key\x18\x01 \x01(\x0b2\x11.proto.MessageKey\x12\x11\n\ttimestamp\x18\x02 \x01(\x03"\x86\x01\n\x16SyncActionMessageRange\x12\x1c\n\x14lastMessageTimestamp\x18\x01 \x01(\x03\x12"\n\x1alastSystemMessageTimestamp\x18\x02 \x01(\x03\x12*\n\x08messages\x18\x03 \x03(\x0b2\x18.proto.SyncActionMessage"[\n\x12SubscriptionAction\x12\x15\n\risDeactivated\x18\x01 \x01(\x08\x12\x16\n\x0eisAutoRenewing\x18\x02 \x01(\x08\x12\x16\n\x0eexpirationDate\x18\x03 \x01(\x03"\xc8\x01\n\rStickerAction\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\x15\n\rfileEncSha256\x18\x02 \x01(\x0c\x12\x10\n\x08mediaKey\x18\x03 \x01(\x0c\x12\x10\n\x08mimetype\x18\x04 \x01(\t\x12\x0e\n\x06height\x18\x05 \x01(\r\x12\r\n\x05width\x18\x06 \x01(\r\x12\x12\n\ndirectPath\x18\x07 \x01(\t\x12\x12\n\nfileLength\x18\x08 \x01(\x04\x12\x12\n\nisFavorite\x18\t \x01(\x08\x12\x14\n\x0cdeviceIdHint\x18\n \x01(\r"\x1d\n\nStarAction\x12\x0f\n\x07starred\x18\x01 \x01(\x08"7\n\x1bSecurityNotificationSetting\x12\x18\n\x10showNotification\x18\x01 \x01(\x08"6\n\x19RemoveRecentStickerAction\x12\x19\n\x11lastStickerSentTs\x18\x01 \x01(\x03"E\n\x18RecentEmojiWeightsAction\x12)\n\x07weights\x18\x01 \x03(\x0b2\x18.proto.RecentEmojiWeight"g\n\x10QuickReplyAction\x12\x10\n\x08shortcut\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x10\n\x08keywords\x18\x03 \x03(\t\x12\r\n\x05count\x18\x04 \x01(\x05\x12\x0f\n\x07deleted\x18\x05 \x01(\x08"\x1f\n\x0fPushNameSetting\x12\x0c\n\x04name\x18\x01 \x01(\t"0\n\x1bPrivacySettingRelayAllCalls\x12\x11\n\tisEnabled\x18\x01 \x01(\x08"\'\n\x14PrimaryVersionAction\x12\x0f\n\x07version\x18\x01 \x01(\t"\x1f\n\x0ePrimaryFeature\x12\r\n\x05flags\x18\x01 \x03(\t"#\n\x12PnForLidChatAction\x12\r\n\x05pnJid\x18\x01 \x01(\t"\x1b\n\tPinAction\x12\x0e\n\x06pinned\x18\x01 \x01(\x08"!\n\tNuxAction\x12\x14\n\x0cacknowledged\x18\x01 \x01(\x08"H\n\nMuteAction\x12\r\n\x05muted\x18\x01 \x01(\x08\x12\x18\n\x10muteEndTimestamp\x18\x02 \x01(\x03\x12\x11\n\tautoMuted\x18\x03 \x01(\x08"7\n\x1fMarketingMessageBroadcastAction\x12\x14\n\x0crepliedCount\x18\x01 \x01(\x05"\x80\x02\n\x16MarketingMessageAction\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\x12I\n\x04type\x18\x03 \x01(\x0e2;.proto.MarketingMessageAction.MarketingMessagePrototypeType\x12\x11\n\tcreatedAt\x18\x04 \x01(\x03\x12\x12\n\nlastSentAt\x18\x05 \x01(\x03\x12\x11\n\tisDeleted\x18\x06 \x01(\x08\x12\x0f\n\x07mediaId\x18\x07 \x01(\t"1\n\x1dMarketingMessagePrototypeType\x12\x10\n\x0cPERSONALIZED\x10\x00"Y\n\x14MarkChatAsReadAction\x12\x0c\n\x04read\x18\x01 \x01(\x08\x123\n\x0cmessageRange\x18\x02 \x01(\x0b2\x1d.proto.SyncActionMessageRange"\x1f\n\rLocaleSetting\x12\x0e\n\x06locale\x18\x01 \x01(\t"U\n\x0fLabelEditAction\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\r\n\x05color\x18\x02 \x01(\x05\x12\x14\n\x0cpredefinedId\x18\x03 \x01(\x05\x12\x0f\n\x07deleted\x18\x04 \x01(\x08")\n\x16LabelAssociationAction\x12\x0f\n\x07labeled\x18\x01 \x01(\x08"(\n\rKeyExpiration\x12\x17\n\x0fexpiredKeyEpoch\x18\x01 \x01(\x05"(\n\x15ExternalWebBetaAction\x12\x0f\n\x07isOptIn\x18\x01 \x01(\x08"I\n\x18DeleteMessageForMeAction\x12\x13\n\x0bdeleteMedia\x18\x01 \x01(\x08\x12\x18\n\x10messageTimestamp\x18\x02 \x01(\x03"G\n\x10DeleteChatAction\x123\n\x0cmessageRange\x18\x01 \x01(\x0b2\x1d.proto.SyncActionMessageRange"D\n\rContactAction\x12\x10\n\x08fullName\x18\x01 \x01(\t\x12\x11\n\tfirstName\x18\x02 \x01(\t\x12\x0e\n\x06lidJid\x18\x03 \x01(\t"F\n\x0fClearChatAction\x123\n\x0cmessageRange\x18\x01 \x01(\x0b2\x1d.proto.SyncActionMessageRange"6\n ChatAssignmentOpenedStatusAction\x12\x12\n\nchatOpened\x18\x01 \x01(\x08"-\n\x14ChatAssignmentAction\x12\x15\n\rdeviceAgentID\x18\x01 \x01(\t"Z\n\x11ArchiveChatAction\x12\x10\n\x08archived\x18\x01 \x01(\x08\x123\n\x0cmessageRange\x18\x02 \x01(\x0b2\x1d.proto.SyncActionMessageRange",\n\x19AndroidUnsupportedActions\x12\x0f\n\x07allowed\x18\x01 \x01(\x08"@\n\x0bAgentAction\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x10\n\x08deviceID\x18\x02 \x01(\x05\x12\x11\n\tisDeleted\x18\x03 \x01(\x08"h\n\x0eSyncActionData\x12\r\n\x05index\x18\x01 \x01(\x0c\x12%\n\x05value\x18\x02 \x01(\x0b2\x16.proto.SyncActionValue\x12\x0f\n\x07padding\x18\x03 \x01(\x0c\x12\x0f\n\x07version\x18\x04 \x01(\x05"2\n\x11RecentEmojiWeight\x12\r\n\x05emoji\x18\x01 \x01(\t\x12\x0e\n\x06weight\x18\x02 \x01(\x02"\xd9\x01\n\x17VerifiedNameCertificate\x12\x0f\n\x07details\x18\x01 \x01(\x0c\x12\x11\n\tsignature\x18\x02 \x01(\x0c\x12\x17\n\x0fserverSignature\x18\x03 \x01(\x0c\x1a\x80\x01\n\x07Details\x12\x0e\n\x06serial\x18\x01 \x01(\x04\x12\x0e\n\x06issuer\x18\x02 \x01(\t\x12\x14\n\x0cverifiedName\x18\x04 \x01(\t\x12,\n\x0elocalizedNames\x18\x08 \x03(\x0b2\x14.proto.LocalizedName\x12\x11\n\tissueTime\x18\n \x01(\x04"=\n\rLocalizedName\x12\n\n\x02lg\x18\x01 \x01(\t\x12\n\n\x02lc\x18\x02 \x01(\t\x12\x14\n\x0cverifiedName\x18\x03 \x01(\t"\xda\x03\n\x0fBizIdentityInfo\x129\n\x06vlevel\x18\x01 \x01(\x0e2).proto.BizIdentityInfo.VerifiedLevelValue\x121\n\tvnameCert\x18\x02 \x01(\x0b2\x1e.proto.VerifiedNameCertificate\x12\x0e\n\x06signed\x18\x03 \x01(\x08\x12\x0f\n\x07revoked\x18\x04 \x01(\x08\x12;\n\x0bhostStorage\x18\x05 \x01(\x0e2&.proto.BizIdentityInfo.HostStorageType\x12=\n\x0cactualActors\x18\x06 \x01(\x0e2\'.proto.BizIdentityInfo.ActualActorsType\x12\x15\n\rprivacyModeTs\x18\x07 \x01(\x04\x12\x17\n\x0ffeatureControls\x18\x08 \x01(\x04"4\n\x12VerifiedLevelValue\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x07\n\x03LOW\x10\x01\x12\x08\n\x04HIGH\x10\x02"/\n\x0fHostStorageType\x12\x0e\n\nON_PREMISE\x10\x00\x12\x0c\n\x08FACEBOOK\x10\x01"%\n\x10ActualActorsType\x12\x08\n\x04SELF\x10\x00\x12\x07\n\x03BSP\x10\x01"_\n\x11BizAccountPayload\x121\n\tvnameCert\x18\x01 \x01(\x0b2\x1e.proto.VerifiedNameCertificate\x12\x17\n\x0fbizAcctLinkInfo\x18\x02 \x01(\x0c"\xac\x02\n\x12BizAccountLinkInfo\x12\x1b\n\x13whatsappBizAcctFbid\x18\x01 \x01(\x04\x12\x1a\n\x12whatsappAcctNumber\x18\x02 \x01(\t\x12\x11\n\tissueTime\x18\x03 \x01(\x04\x12>\n\x0bhostStorage\x18\x04 \x01(\x0e2).proto.BizAccountLinkInfo.HostStorageType\x12:\n\x0baccountType\x18\x05 \x01(\x0e2%.proto.BizAccountLinkInfo.AccountType"/\n\x0fHostStorageType\x12\x0e\n\nON_PREMISE\x10\x00\x12\x0c\n\x08FACEBOOK\x10\x01"\x1d\n\x0bAccountType\x12\x0e\n\nENTERPRISE\x10\x00"\xaa\x01\n\x10HandshakeMessage\x120\n\x0bclientHello\x18\x02 \x01(\x0b2\x1b.proto.HandshakeClientHello\x120\n\x0bserverHello\x18\x03 \x01(\x0b2\x1b.proto.HandshakeServerHello\x122\n\x0cclientFinish\x18\x04 \x01(\x0b2\x1c.proto.HandshakeClientFinish"J\n\x14HandshakeServerHello\x12\x11\n\tephemeral\x18\x01 \x01(\x0c\x12\x0e\n\x06static\x18\x02 \x01(\x0c\x12\x0f\n\x07payload\x18\x03 \x01(\x0c"J\n\x14HandshakeClientHello\x12\x11\n\tephemeral\x18\x01 \x01(\x0c\x12\x0e\n\x06static\x18\x02 \x01(\x0c\x12\x0f\n\x07payload\x18\x03 \x01(\x0c"8\n\x15HandshakeClientFinish\x12\x0e\n\x06static\x18\x01 \x01(\x0c\x12\x0f\n\x07payload\x18\x02 \x01(\x0c"\xd4\x1b\n\rClientPayload\x12\x10\n\x08username\x18\x01 \x01(\x04\x12\x0f\n\x07passive\x18\x03 \x01(\x08\x121\n\tuserAgent\x18\x05 \x01(\x0b2\x1e.proto.ClientPayload.UserAgent\x12-\n\x07webInfo\x18\x06 \x01(\x0b2\x1c.proto.ClientPayload.WebInfo\x12\x10\n\x08pushName\x18\x07 \x01(\t\x12\x11\n\tsessionId\x18\t \x01(\x0f\x12\x14\n\x0cshortConnect\x18\n \x01(\x08\x125\n\x0bconnectType\x18\x0c \x01(\x0e2 .proto.ClientPayload.ConnectType\x129\n\rconnectReason\x18\r \x01(\x0e2".proto.ClientPayload.ConnectReason\x12\x0e\n\x06shards\x18\x0e \x03(\x05\x121\n\tdnsSource\x18\x0f \x01(\x0b2\x1e.proto.ClientPayload.DNSSource\x12\x1b\n\x13connectAttemptCount\x18\x10 \x01(\r\x12\x0e\n\x06device\x18\x12 \x01(\r\x12M\n\x11devicePairingData\x18\x13 \x01(\x0b22.proto.ClientPayload.DevicePairingRegistrationData\x12-\n\x07product\x18\x14 \x01(\x0e2\x1c.proto.ClientPayload.Product\x12\r\n\x05fbCat\x18\x15 \x01(\x0c\x12\x13\n\x0bfbUserAgent\x18\x16 \x01(\x0c\x12\n\n\x02oc\x18\x17 \x01(\x08\x12\n\n\x02lc\x18\x18 \x01(\x05\x12=\n\x0fiosAppExtension\x18\x1e \x01(\x0e2$.proto.ClientPayload.IOSAppExtension\x12\x0f\n\x07fbAppId\x18\x1f \x01(\x04\x12\x12\n\nfbDeviceId\x18  \x01(\x0c\x12\x0c\n\x04pull\x18! \x01(\x08\x12\x14\n\x0cpaddingBytes\x18" \x01(\x0c\x12\x11\n\tyearClass\x18$ \x01(\x05\x12\x10\n\x08memClass\x18% \x01(\x05\x125\n\x0binteropData\x18& \x01(\x0b2 .proto.ClientPayload.InteropData\x1a\xc6\x04\n\x07WebInfo\x12\x10\n\x08refToken\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\t\x12=\n\x0bwebdPayload\x18\x03 \x01(\x0b2(.proto.ClientPayload.WebInfo.WebdPayload\x12C\n\x0ewebSubPlatform\x18\x04 \x01(\x0e2+.proto.ClientPayload.WebInfo.WebSubPlatform\x1a\xbb\x02\n\x0bWebdPayload\x12\x1c\n\x14usesParticipantInKey\x18\x01 \x01(\x08\x12\x1f\n\x17supportsStarredMessages\x18\x02 \x01(\x08\x12 \n\x18supportsDocumentMessages\x18\x03 \x01(\x08\x12\x1b\n\x13supportsUrlMessages\x18\x04 \x01(\x08\x12\x1a\n\x12supportsMediaRetry\x18\x05 \x01(\x08\x12\x18\n\x10supportsE2EImage\x18\x06 \x01(\x08\x12\x18\n\x10supportsE2EVideo\x18\x07 \x01(\x08\x12\x18\n\x10supportsE2EAudio\x18\x08 \x01(\x08\x12\x1b\n\x13supportsE2EDocument\x18\t \x01(\x08\x12\x15\n\rdocumentTypes\x18\n \x01(\t\x12\x10\n\x08features\x18\x0b \x01(\x0c"V\n\x0eWebSubPlatform\x12\x0f\n\x0bWEB_BROWSER\x10\x00\x12\r\n\tAPP_STORE\x10\x01\x12\r\n\tWIN_STORE\x10\x02\x12\n\n\x06DARWIN\x10\x03\x12\t\n\x05WIN32\x10\x04\x1a\xb8\x08\n\tUserAgent\x129\n\x08platform\x18\x01 \x01(\x0e2\'.proto.ClientPayload.UserAgent.Platform\x12=\n\nappVersion\x18\x02 \x01(\x0b2).proto.ClientPayload.UserAgent.AppVersion\x12\x0b\n\x03mcc\x18\x03 \x01(\t\x12\x0b\n\x03mnc\x18\x04 \x01(\t\x12\x11\n\tosVersion\x18\x05 \x01(\t\x12\x14\n\x0cmanufacturer\x18\x06 \x01(\t\x12\x0e\n\x06device\x18\x07 \x01(\t\x12\x15\n\rosBuildNumber\x18\x08 \x01(\t\x12\x0f\n\x07phoneId\x18\t \x01(\t\x12E\n\x0ereleaseChannel\x18\n \x01(\x0e2-.proto.ClientPayload.UserAgent.ReleaseChannel\x12\x1d\n\x15localeLanguageIso6391\x18\x0b \x01(\t\x12#\n\x1blocaleCountryIso31661Alpha2\x18\x0c \x01(\t\x12\x13\n\x0bdeviceBoard\x18\r \x01(\t\x1ag\n\nAppVersion\x12\x0f\n\x07primary\x18\x01 \x01(\r\x12\x11\n\tsecondary\x18\x02 \x01(\r\x12\x10\n\x08tertiary\x18\x03 \x01(\r\x12\x12\n\nquaternary\x18\x04 \x01(\r\x12\x0f\n\x07quinary\x18\x05 \x01(\r"=\n\x0eReleaseChannel\x12\x0b\n\x07RELEASE\x10\x00\x12\x08\n\x04BETA\x10\x01\x12\t\n\x05ALPHA\x10\x02\x12\t\n\x05DEBUG\x10\x03"\xed\x03\n\x08Platform\x12\x0b\n\x07ANDROID\x10\x00\x12\x07\n\x03IOS\x10\x01\x12\x11\n\rWINDOWS_PHONE\x10\x02\x12\x0e\n\nBLACKBERRY\x10\x03\x12\x0f\n\x0bBLACKBERRYX\x10\x04\x12\x07\n\x03S40\x10\x05\x12\x07\n\x03S60\x10\x06\x12\x11\n\rPYTHON_CLIENT\x10\x07\x12\t\n\x05TIZEN\x10\x08\x12\x0e\n\nENTERPRISE\x10\t\x12\x0f\n\x0bSMB_ANDROID\x10\n\x12\t\n\x05KAIOS\x10\x0b\x12\x0b\n\x07SMB_IOS\x10\x0c\x12\x0b\n\x07WINDOWS\x10\r\x12\x07\n\x03WEB\x10\x0e\x12\n\n\x06PORTAL\x10\x0f\x12\x11\n\rGREEN_ANDROID\x10\x10\x12\x10\n\x0cGREEN_IPHONE\x10\x11\x12\x10\n\x0cBLUE_ANDROID\x10\x12\x12\x0f\n\x0bBLUE_IPHONE\x10\x13\x12\x12\n\x0eFBLITE_ANDROID\x10\x14\x12\x11\n\rMLITE_ANDROID\x10\x15\x12\x12\n\x0eIGLITE_ANDROID\x10\x16\x12\x08\n\x04PAGE\x10\x17\x12\t\n\x05MACOS\x10\x18\x12\x0e\n\nOCULUS_MSG\x10\x19\x12\x0f\n\x0bOCULUS_CALL\x10\x1a\x12\t\n\x05MILAN\x10\x1b\x12\x08\n\x04CAPI\x10\x1c\x12\n\n\x06WEAROS\x10\x1d\x12\x0c\n\x08ARDEVICE\x10\x1e\x12\x0c\n\x08VRDEVICE\x10\x1f\x12\x0c\n\x08BLUE_WEB\x10 \x12\x08\n\x04IPAD\x10!\x1aE\n\x0bInteropData\x12\x11\n\taccountId\x18\x01 \x01(\x04\x12\x14\n\x0cintegratorId\x18\x02 \x01(\r\x12\r\n\x05token\x18\x03 \x01(\x0c\x1a\xae\x01\n\x1dDevicePairingRegistrationData\x12\x0e\n\x06eRegid\x18\x01 \x01(\x0c\x12\x10\n\x08eKeytype\x18\x02 \x01(\x0c\x12\x0e\n\x06eIdent\x18\x03 \x01(\x0c\x12\x0f\n\x07eSkeyId\x18\x04 \x01(\x0c\x12\x10\n\x08eSkeyVal\x18\x05 \x01(\x0c\x12\x10\n\x08eSkeySig\x18\x06 \x01(\x0c\x12\x11\n\tbuildHash\x18\x07 \x01(\x0c\x12\x13\n\x0bdeviceProps\x18\x08 \x01(\x0c\x1a\xbf\x01\n\tDNSSource\x12E\n\tdnsMethod\x18\x0f \x01(\x0e22.proto.ClientPayload.DNSSource.DNSResolutionMethod\x12\x11\n\tappCached\x18\x10 \x01(\x08"X\n\x13DNSResolutionMethod\x12\n\n\x06SYSTEM\x10\x00\x12\n\n\x06GOOGLE\x10\x01\x12\r\n\tHARDCODED\x10\x02\x12\x0c\n\x08OVERRIDE\x10\x03\x12\x0c\n\x08FALLBACK\x10\x04"3\n\x07Product\x12\x0c\n\x08WHATSAPP\x10\x00\x12\r\n\tMESSENGER\x10\x01\x12\x0b\n\x07INTEROP\x10\x02"T\n\x0fIOSAppExtension\x12\x13\n\x0fSHARE_EXTENSION\x10\x00\x12\x15\n\x11SERVICE_EXTENSION\x10\x01\x12\x15\n\x11INTENTS_EXTENSION\x10\x02"\xb0\x02\n\x0bConnectType\x12\x14\n\x10CELLULAR_UNKNOWN\x10\x00\x12\x10\n\x0cWIFI_UNKNOWN\x10\x01\x12\x11\n\rCELLULAR_EDGE\x10d\x12\x11\n\rCELLULAR_IDEN\x10e\x12\x11\n\rCELLULAR_UMTS\x10f\x12\x11\n\rCELLULAR_EVDO\x10g\x12\x11\n\rCELLULAR_GPRS\x10h\x12\x12\n\x0eCELLULAR_HSDPA\x10i\x12\x12\n\x0eCELLULAR_HSUPA\x10j\x12\x11\n\rCELLULAR_HSPA\x10k\x12\x11\n\rCELLULAR_CDMA\x10l\x12\x12\n\x0eCELLULAR_1XRTT\x10m\x12\x12\n\x0eCELLULAR_EHRPD\x10n\x12\x10\n\x0cCELLULAR_LTE\x10o\x12\x12\n\x0eCELLULAR_HSPAP\x10p"\x86\x01\n\rConnectReason\x12\x08\n\x04PUSH\x10\x00\x12\x12\n\x0eUSER_ACTIVATED\x10\x01\x12\r\n\tSCHEDULED\x10\x02\x12\x13\n\x0fERROR_RECONNECT\x10\x03\x12\x12\n\x0eNETWORK_SWITCH\x10\x04\x12\x12\n\x0ePING_RECONNECT\x10\x05\x12\x0b\n\x07UNKNOWN\x10\x06"\x89\x01\n\x14WebNotificationsInfo\x12\x11\n\ttimestamp\x18\x02 \x01(\x04\x12\x13\n\x0bunreadChats\x18\x03 \x01(\r\x12\x1a\n\x12notifyMessageCount\x18\x04 \x01(\r\x12-\n\x0enotifyMessages\x18\x05 \x03(\x0b2\x15.proto.WebMessageInfo"\xf9;\n\x0eWebMessageInfo\x12\x1e\n\x03key\x18\x01 \x02(\x0b2\x11.proto.MessageKey\x12\x1f\n\x07message\x18\x02 \x01(\x0b2\x0e.proto.Message\x12\x18\n\x10messageTimestamp\x18\x03 \x01(\x04\x12,\n\x06status\x18\x04 \x01(\x0e2\x1c.proto.WebMessageInfo.Status\x12\x13\n\x0bparticipant\x18\x05 \x01(\t\x12\x1b\n\x13messageC2STimestamp\x18\x06 \x01(\x04\x12\x0e\n\x06ignore\x18\x10 \x01(\x08\x12\x0f\n\x07starred\x18\x11 \x01(\x08\x12\x11\n\tbroadcast\x18\x12 \x01(\x08\x12\x10\n\x08pushName\x18\x13 \x01(\t\x12\x1d\n\x15mediaCiphertextSha256\x18\x14 \x01(\x0c\x12\x11\n\tmulticast\x18\x15 \x01(\x08\x12\x0f\n\x07urlText\x18\x16 \x01(\x08\x12\x11\n\turlNumber\x18\x17 \x01(\x08\x127\n\x0fmessageStubType\x18\x18 \x01(\x0e2\x1e.proto.WebMessageInfo.StubType\x12\x12\n\nclearMedia\x18\x19 \x01(\x08\x12\x1d\n\x15messageStubParameters\x18\x1a \x03(\t\x12\x10\n\x08duration\x18\x1b \x01(\r\x12\x0e\n\x06labels\x18\x1c \x03(\t\x12\'\n\x0bpaymentInfo\x18\x1d \x01(\x0b2\x12.proto.PaymentInfo\x125\n\x11finalLiveLocation\x18\x1e \x01(\x0b2\x1a.proto.LiveLocationMessage\x12-\n\x11quotedPaymentInfo\x18\x1f \x01(\x0b2\x12.proto.PaymentInfo\x12\x1f\n\x17ephemeralStartTimestamp\x18  \x01(\x04\x12\x19\n\x11ephemeralDuration\x18! \x01(\r\x12\x18\n\x10ephemeralOffToOn\x18" \x01(\x08\x12\x1a\n\x12ephemeralOutOfSync\x18# \x01(\x08\x12@\n\x10bizPrivacyStatus\x18$ \x01(\x0e2&.proto.WebMessageInfo.BizPrivacyStatus\x12\x17\n\x0fverifiedBizName\x18% \x01(\t\x12#\n\tmediaData\x18& \x01(\x0b2\x10.proto.MediaData\x12\'\n\x0bphotoChange\x18\' \x01(\x0b2\x12.proto.PhotoChange\x12\'\n\x0buserReceipt\x18( \x03(\x0b2\x12.proto.UserReceipt\x12"\n\treactions\x18) \x03(\x0b2\x0f.proto.Reaction\x12+\n\x11quotedStickerData\x18* \x01(\x0b2\x10.proto.MediaData\x12\x17\n\x0ffutureproofData\x18+ \x01(\x0c\x12#\n\tstatusPsa\x18, \x01(\x0b2\x10.proto.StatusPSA\x12&\n\x0bpollUpdates\x18- \x03(\x0b2\x11.proto.PollUpdate\x12=\n\x16pollAdditionalMetadata\x18. \x01(\x0b2\x1d.proto.PollAdditionalMetadata\x12\x0f\n\x07agentId\x18/ \x01(\t\x12\x1b\n\x13statusAlreadyViewed\x180 \x01(\x08\x12\x15\n\rmessageSecret\x181 \x01(\x0c\x12%\n\nkeepInChat\x182 \x01(\x0b2\x11.proto.KeepInChat\x12\'\n\x1foriginalSelfAuthorUserJidString\x183 \x01(\t\x12\x1e\n\x16revokeMessageTimestamp\x184 \x01(\x04\x12#\n\tpinInChat\x186 \x01(\x0b2\x10.proto.PinInChat"\xc5/\n\x08StubType\x12\x0b\n\x07UNKNOWN\x10\x00\x12\n\n\x06REVOKE\x10\x01\x12\x0e\n\nCIPHERTEXT\x10\x02\x12\x0f\n\x0bFUTUREPROOF\x10\x03\x12\x1b\n\x17NON_VERIFIED_TRANSITION\x10\x04\x12\x19\n\x15UNVERIFIED_TRANSITION\x10\x05\x12\x17\n\x13VERIFIED_TRANSITION\x10\x06\x12\x18\n\x14VERIFIED_LOW_UNKNOWN\x10\x07\x12\x11\n\rVERIFIED_HIGH\x10\x08\x12\x1c\n\x18VERIFIED_INITIAL_UNKNOWN\x10\t\x12\x18\n\x14VERIFIED_INITIAL_LOW\x10\n\x12\x19\n\x15VERIFIED_INITIAL_HIGH\x10\x0b\x12#\n\x1fVERIFIED_TRANSITION_ANY_TO_NONE\x10\x0c\x12#\n\x1fVERIFIED_TRANSITION_ANY_TO_HIGH\x10\r\x12#\n\x1fVERIFIED_TRANSITION_HIGH_TO_LOW\x10\x0e\x12\'\n#VERIFIED_TRANSITION_HIGH_TO_UNKNOWN\x10\x0f\x12&\n"VERIFIED_TRANSITION_UNKNOWN_TO_LOW\x10\x10\x12&\n"VERIFIED_TRANSITION_LOW_TO_UNKNOWN\x10\x11\x12#\n\x1fVERIFIED_TRANSITION_NONE_TO_LOW\x10\x12\x12\'\n#VERIFIED_TRANSITION_NONE_TO_UNKNOWN\x10\x13\x12\x10\n\x0cGROUP_CREATE\x10\x14\x12\x18\n\x14GROUP_CHANGE_SUBJECT\x10\x15\x12\x15\n\x11GROUP_CHANGE_ICON\x10\x16\x12\x1c\n\x18GROUP_CHANGE_INVITE_LINK\x10\x17\x12\x1c\n\x18GROUP_CHANGE_DESCRIPTION\x10\x18\x12\x19\n\x15GROUP_CHANGE_RESTRICT\x10\x19\x12\x19\n\x15GROUP_CHANGE_ANNOUNCE\x10\x1a\x12\x19\n\x15GROUP_PARTICIPANT_ADD\x10\x1b\x12\x1c\n\x18GROUP_PARTICIPANT_REMOVE\x10\x1c\x12\x1d\n\x19GROUP_PARTICIPANT_PROMOTE\x10\x1d\x12\x1c\n\x18GROUP_PARTICIPANT_DEMOTE\x10\x1e\x12\x1c\n\x18GROUP_PARTICIPANT_INVITE\x10\x1f\x12\x1b\n\x17GROUP_PARTICIPANT_LEAVE\x10 \x12#\n\x1fGROUP_PARTICIPANT_CHANGE_NUMBER\x10!\x12\x14\n\x10BROADCAST_CREATE\x10"\x12\x11\n\rBROADCAST_ADD\x10#\x12\x14\n\x10BROADCAST_REMOVE\x10$\x12\x18\n\x14GENERIC_NOTIFICATION\x10%\x12\x18\n\x14E2E_IDENTITY_CHANGED\x10&\x12\x11\n\rE2E_ENCRYPTED\x10\'\x12\x15\n\x11CALL_MISSED_VOICE\x10(\x12\x15\n\x11CALL_MISSED_VIDEO\x10)\x12\x1c\n\x18INDIVIDUAL_CHANGE_NUMBER\x10*\x12\x10\n\x0cGROUP_DELETE\x10+\x12&\n"GROUP_ANNOUNCE_MODE_MESSAGE_BOUNCE\x10,\x12\x1b\n\x17CALL_MISSED_GROUP_VOICE\x10-\x12\x1b\n\x17CALL_MISSED_GROUP_VIDEO\x10.\x12\x16\n\x12PAYMENT_CIPHERTEXT\x10/\x12\x17\n\x13PAYMENT_FUTUREPROOF\x100\x12,\n(PAYMENT_TRANSACTION_STATUS_UPDATE_FAILED\x101\x12.\n*PAYMENT_TRANSACTION_STATUS_UPDATE_REFUNDED\x102\x123\n/PAYMENT_TRANSACTION_STATUS_UPDATE_REFUND_FAILED\x103\x125\n1PAYMENT_TRANSACTION_STATUS_RECEIVER_PENDING_SETUP\x104\x12<\n8PAYMENT_TRANSACTION_STATUS_RECEIVER_SUCCESS_AFTER_HICCUP\x105\x12)\n%PAYMENT_ACTION_ACCOUNT_SETUP_REMINDER\x106\x12(\n$PAYMENT_ACTION_SEND_PAYMENT_REMINDER\x107\x12*\n&PAYMENT_ACTION_SEND_PAYMENT_INVITATION\x108\x12#\n\x1fPAYMENT_ACTION_REQUEST_DECLINED\x109\x12"\n\x1ePAYMENT_ACTION_REQUEST_EXPIRED\x10:\x12$\n PAYMENT_ACTION_REQUEST_CANCELLED\x10;\x12)\n%BIZ_VERIFIED_TRANSITION_TOP_TO_BOTTOM\x10<\x12)\n%BIZ_VERIFIED_TRANSITION_BOTTOM_TO_TOP\x10=\x12\x11\n\rBIZ_INTRO_TOP\x10>\x12\x14\n\x10BIZ_INTRO_BOTTOM\x10?\x12\x13\n\x0fBIZ_NAME_CHANGE\x10@\x12\x1c\n\x18BIZ_MOVE_TO_CONSUMER_APP\x10A\x12\x1e\n\x1aBIZ_TWO_TIER_MIGRATION_TOP\x10B\x12!\n\x1dBIZ_TWO_TIER_MIGRATION_BOTTOM\x10C\x12\r\n\tOVERSIZED\x10D\x12(\n$GROUP_CHANGE_NO_FREQUENTLY_FORWARDED\x10E\x12\x1c\n\x18GROUP_V4_ADD_INVITE_SENT\x10F\x12&\n"GROUP_PARTICIPANT_ADD_REQUEST_JOIN\x10G\x12\x1c\n\x18CHANGE_EPHEMERAL_SETTING\x10H\x12\x16\n\x12E2E_DEVICE_CHANGED\x10I\x12\x0f\n\x0bVIEWED_ONCE\x10J\x12\x15\n\x11E2E_ENCRYPTED_NOW\x10K\x12"\n\x1eBLUE_MSG_BSP_FB_TO_BSP_PREMISE\x10L\x12\x1e\n\x1aBLUE_MSG_BSP_FB_TO_SELF_FB\x10M\x12#\n\x1fBLUE_MSG_BSP_FB_TO_SELF_PREMISE\x10N\x12\x1e\n\x1aBLUE_MSG_BSP_FB_UNVERIFIED\x10O\x127\n3BLUE_MSG_BSP_FB_UNVERIFIED_TO_SELF_PREMISE_VERIFIED\x10P\x12\x1c\n\x18BLUE_MSG_BSP_FB_VERIFIED\x10Q\x127\n3BLUE_MSG_BSP_FB_VERIFIED_TO_SELF_PREMISE_UNVERIFIED\x10R\x12(\n$BLUE_MSG_BSP_PREMISE_TO_SELF_PREMISE\x10S\x12#\n\x1fBLUE_MSG_BSP_PREMISE_UNVERIFIED\x10T\x12<\n8BLUE_MSG_BSP_PREMISE_UNVERIFIED_TO_SELF_PREMISE_VERIFIED\x10U\x12!\n\x1dBLUE_MSG_BSP_PREMISE_VERIFIED\x10V\x12<\n8BLUE_MSG_BSP_PREMISE_VERIFIED_TO_SELF_PREMISE_UNVERIFIED\x10W\x12*\n&BLUE_MSG_CONSUMER_TO_BSP_FB_UNVERIFIED\x10X\x12/\n+BLUE_MSG_CONSUMER_TO_BSP_PREMISE_UNVERIFIED\x10Y\x12+\n\'BLUE_MSG_CONSUMER_TO_SELF_FB_UNVERIFIED\x10Z\x120\n,BLUE_MSG_CONSUMER_TO_SELF_PREMISE_UNVERIFIED\x10[\x12#\n\x1fBLUE_MSG_SELF_FB_TO_BSP_PREMISE\x10\\\x12$\n BLUE_MSG_SELF_FB_TO_SELF_PREMISE\x10]\x12\x1f\n\x1bBLUE_MSG_SELF_FB_UNVERIFIED\x10^\x128\n4BLUE_MSG_SELF_FB_UNVERIFIED_TO_SELF_PREMISE_VERIFIED\x10_\x12\x1d\n\x19BLUE_MSG_SELF_FB_VERIFIED\x10`\x128\n4BLUE_MSG_SELF_FB_VERIFIED_TO_SELF_PREMISE_UNVERIFIED\x10a\x12(\n$BLUE_MSG_SELF_PREMISE_TO_BSP_PREMISE\x10b\x12$\n BLUE_MSG_SELF_PREMISE_UNVERIFIED\x10c\x12"\n\x1eBLUE_MSG_SELF_PREMISE_VERIFIED\x10d\x12\x16\n\x12BLUE_MSG_TO_BSP_FB\x10e\x12\x18\n\x14BLUE_MSG_TO_CONSUMER\x10f\x12\x17\n\x13BLUE_MSG_TO_SELF_FB\x10g\x12*\n&BLUE_MSG_UNVERIFIED_TO_BSP_FB_VERIFIED\x10h\x12/\n+BLUE_MSG_UNVERIFIED_TO_BSP_PREMISE_VERIFIED\x10i\x12+\n\'BLUE_MSG_UNVERIFIED_TO_SELF_FB_VERIFIED\x10j\x12#\n\x1fBLUE_MSG_UNVERIFIED_TO_VERIFIED\x10k\x12*\n&BLUE_MSG_VERIFIED_TO_BSP_FB_UNVERIFIED\x10l\x12/\n+BLUE_MSG_VERIFIED_TO_BSP_PREMISE_UNVERIFIED\x10m\x12+\n\'BLUE_MSG_VERIFIED_TO_SELF_FB_UNVERIFIED\x10n\x12#\n\x1fBLUE_MSG_VERIFIED_TO_UNVERIFIED\x10o\x126\n2BLUE_MSG_BSP_FB_UNVERIFIED_TO_BSP_PREMISE_VERIFIED\x10p\x122\n.BLUE_MSG_BSP_FB_UNVERIFIED_TO_SELF_FB_VERIFIED\x10q\x126\n2BLUE_MSG_BSP_FB_VERIFIED_TO_BSP_PREMISE_UNVERIFIED\x10r\x122\n.BLUE_MSG_BSP_FB_VERIFIED_TO_SELF_FB_UNVERIFIED\x10s\x127\n3BLUE_MSG_SELF_FB_UNVERIFIED_TO_BSP_PREMISE_VERIFIED\x10t\x127\n3BLUE_MSG_SELF_FB_VERIFIED_TO_BSP_PREMISE_UNVERIFIED\x10u\x12\x1c\n\x18E2E_IDENTITY_UNAVAILABLE\x10v\x12\x12\n\x0eGROUP_CREATING\x10w\x12\x17\n\x13GROUP_CREATE_FAILED\x10x\x12\x11\n\rGROUP_BOUNCED\x10y\x12\x11\n\rBLOCK_CONTACT\x10z\x12!\n\x1dEPHEMERAL_SETTING_NOT_APPLIED\x10{\x12\x0f\n\x0bSYNC_FAILED\x10|\x12\x0b\n\x07SYNCING\x10}\x12\x1c\n\x18BIZ_PRIVACY_MODE_INIT_FB\x10~\x12\x1d\n\x19BIZ_PRIVACY_MODE_INIT_BSP\x10\x7f\x12\x1b\n\x16BIZ_PRIVACY_MODE_TO_FB\x10\x80\x01\x12\x1c\n\x17BIZ_PRIVACY_MODE_TO_BSP\x10\x81\x01\x12\x16\n\x11DISAPPEARING_MODE\x10\x82\x01\x12\x1c\n\x17E2E_DEVICE_FETCH_FAILED\x10\x83\x01\x12\x11\n\x0cADMIN_REVOKE\x10\x84\x01\x12$\n\x1fGROUP_INVITE_LINK_GROWTH_LOCKED\x10\x85\x01\x12 \n\x1bCOMMUNITY_LINK_PARENT_GROUP\x10\x86\x01\x12!\n\x1cCOMMUNITY_LINK_SIBLING_GROUP\x10\x87\x01\x12\x1d\n\x18COMMUNITY_LINK_SUB_GROUP\x10\x88\x01\x12"\n\x1dCOMMUNITY_UNLINK_PARENT_GROUP\x10\x89\x01\x12#\n\x1eCOMMUNITY_UNLINK_SIBLING_GROUP\x10\x8a\x01\x12\x1f\n\x1aCOMMUNITY_UNLINK_SUB_GROUP\x10\x8b\x01\x12\x1d\n\x18GROUP_PARTICIPANT_ACCEPT\x10\x8c\x01\x12(\n#GROUP_PARTICIPANT_LINKED_GROUP_JOIN\x10\x8d\x01\x12\x15\n\x10COMMUNITY_CREATE\x10\x8e\x01\x12\x1b\n\x16EPHEMERAL_KEEP_IN_CHAT\x10\x8f\x01\x12+\n&GROUP_MEMBERSHIP_JOIN_APPROVAL_REQUEST\x10\x90\x01\x12(\n#GROUP_MEMBERSHIP_JOIN_APPROVAL_MODE\x10\x91\x01\x12"\n\x1dINTEGRITY_UNLINK_PARENT_GROUP\x10\x92\x01\x12"\n\x1dCOMMUNITY_PARTICIPANT_PROMOTE\x10\x93\x01\x12!\n\x1cCOMMUNITY_PARTICIPANT_DEMOTE\x10\x94\x01\x12#\n\x1eCOMMUNITY_PARENT_GROUP_DELETED\x10\x95\x01\x124\n/COMMUNITY_LINK_PARENT_GROUP_MEMBERSHIP_APPROVAL\x10\x96\x01\x124\n/GROUP_PARTICIPANT_JOINED_GROUP_AND_PARENT_GROUP\x10\x97\x01\x12\x1a\n\x15MASKED_THREAD_CREATED\x10\x98\x01\x12\x1b\n\x16MASKED_THREAD_UNMASKED\x10\x99\x01\x12\x18\n\x13BIZ_CHAT_ASSIGNMENT\x10\x9a\x01\x12\r\n\x08CHAT_PSA\x10\x9b\x01\x12\x1f\n\x1aCHAT_POLL_CREATION_MESSAGE\x10\x9c\x01\x12\x1e\n\x19CAG_MASKED_THREAD_CREATED\x10\x9d\x01\x12+\n&COMMUNITY_PARENT_GROUP_SUBJECT_CHANGED\x10\x9e\x01\x12\x18\n\x13CAG_INVITE_AUTO_ADD\x10\x9f\x01\x12!\n\x1cBIZ_CHAT_ASSIGNMENT_UNASSIGN\x10\xa0\x01\x12\x1b\n\x16CAG_INVITE_AUTO_JOINED\x10\xa1\x01\x12!\n\x1cSCHEDULED_CALL_START_MESSAGE\x10\xa2\x01\x12\x1a\n\x15COMMUNITY_INVITE_RICH\x10\xa3\x01\x12#\n\x1eCOMMUNITY_INVITE_AUTO_ADD_RICH\x10\xa4\x01\x12\x1a\n\x15SUB_GROUP_INVITE_RICH\x10\xa5\x01\x12#\n\x1eSUB_GROUP_PARTICIPANT_ADD_RICH\x10\xa6\x01\x12%\n COMMUNITY_LINK_PARENT_GROUP_RICH\x10\xa7\x01\x12#\n\x1eCOMMUNITY_PARTICIPANT_ADD_RICH\x10\xa8\x01\x12"\n\x1dSILENCED_UNKNOWN_CALLER_AUDIO\x10\xa9\x01\x12"\n\x1dSILENCED_UNKNOWN_CALLER_VIDEO\x10\xaa\x01\x12\x1a\n\x15GROUP_MEMBER_ADD_MODE\x10\xab\x01\x129\n4GROUP_MEMBERSHIP_JOIN_APPROVAL_REQUEST_NON_ADMIN_ADD\x10\xac\x01\x12!\n\x1cCOMMUNITY_CHANGE_DESCRIPTION\x10\xad\x01\x12\x12\n\rSENDER_INVITE\x10\xae\x01\x12\x14\n\x0fRECEIVER_INVITE\x10\xaf\x01\x12(\n#COMMUNITY_ALLOW_MEMBER_ADDED_GROUPS\x10\xb0\x01\x12\x1b\n\x16PINNED_MESSAGE_IN_CHAT\x10\xb1\x01"X\n\x06Status\x12\t\n\x05ERROR\x10\x00\x12\x0b\n\x07PENDING\x10\x01\x12\x0e\n\nSERVER_ACK\x10\x02\x12\x10\n\x0cDELIVERY_ACK\x10\x03\x12\x08\n\x04READ\x10\x04\x12\n\n\x06PLAYED\x10\x05"=\n\x10BizPrivacyStatus\x12\x08\n\x04E2EE\x10\x00\x12\x06\n\x02FB\x10\x02\x12\x07\n\x03BSP\x10\x01\x12\x0e\n\nBSP_AND_FB\x10\x03"\xdb\x12\n\x0bWebFeatures\x12.\n\rlabelsDisplay\x18\x01 \x01(\x0e2\x17.proto.WebFeatures.Flag\x127\n\x16voipIndividualOutgoing\x18\x02 \x01(\x0e2\x17.proto.WebFeatures.Flag\x12)\n\x08groupsV3\x18\x03 \x01(\x0e2\x17.proto.WebFeatures.Flag\x12/\n\x0egroupsV3Create\x18\x04 \x01(\x0e2\x17.proto.WebFeatures.Flag\x12/\n\x0echangeNumberV2\x18\x05 \x01(\x0e2\x17.proto.WebFeatures.Flag\x127\n\x16queryStatusV3Thumbnail\x18\x06 \x01(\x0e2\x17.proto.WebFeatures.Flag\x12.\n\rliveLocations\x18\x07 \x01(\x0e2\x17.proto.WebFeatures.Flag\x12+\n\nqueryVname\x18\x08 \x01(\x0e2\x17.proto.WebFeatures.Flag\x127\n\x16voipIndividualIncoming\x18\t \x01(\x0e2\x17.proto.WebFeatures.Flag\x122\n\x11quickRepliesQuery\x18\n \x01(\x0e2\x17.proto.WebFeatures.Flag\x12)\n\x08payments\x18\x0b \x01(\x0e2\x17.proto.WebFeatures.Flag\x121\n\x10stickerPackQuery\x18\x0c \x01(\x0e2\x17.proto.WebFeatures.Flag\x123\n\x12liveLocationsFinal\x18\r \x01(\x0e2\x17.proto.WebFeatures.Flag\x12+\n\nlabelsEdit\x18\x0e \x01(\x0e2\x17.proto.WebFeatures.Flag\x12,\n\x0bmediaUpload\x18\x0f \x01(\x0e2\x17.proto.WebFeatures.Flag\x12<\n\x1bmediaUploadRichQuickReplies\x18\x12 \x01(\x0e2\x17.proto.WebFeatures.Flag\x12(\n\x07vnameV2\x18\x13 \x01(\x0e2\x17.proto.WebFeatures.Flag\x121\n\x10videoPlaybackUrl\x18\x14 \x01(\x0e2\x17.proto.WebFeatures.Flag\x12.\n\rstatusRanking\x18\x15 \x01(\x0e2\x17.proto.WebFeatures.Flag\x124\n\x13voipIndividualVideo\x18\x16 \x01(\x0e2\x17.proto.WebFeatures.Flag\x123\n\x12thirdPartyStickers\x18\x17 \x01(\x0e2\x17.proto.WebFeatures.Flag\x12;\n\x1afrequentlyForwardedSetting\x18\x18 \x01(\x0e2\x17.proto.WebFeatures.Flag\x127\n\x16groupsV4JoinPermission\x18\x19 \x01(\x0e2\x17.proto.WebFeatures.Flag\x12/\n\x0erecentStickers\x18\x1a \x01(\x0e2\x17.proto.WebFeatures.Flag\x12(\n\x07catalog\x18\x1b \x01(\x0e2\x17.proto.WebFeatures.Flag\x120\n\x0fstarredStickers\x18\x1c \x01(\x0e2\x17.proto.WebFeatures.Flag\x12.\n\rvoipGroupCall\x18\x1d \x01(\x0e2\x17.proto.WebFeatures.Flag\x120\n\x0ftemplateMessage\x18\x1e \x01(\x0e2\x17.proto.WebFeatures.Flag\x12=\n\x1ctemplateMessageInteractivity\x18\x1f \x01(\x0e2\x17.proto.WebFeatures.Flag\x122\n\x11ephemeralMessages\x18  \x01(\x0e2\x17.proto.WebFeatures.Flag\x124\n\x13e2ENotificationSync\x18! \x01(\x0e2\x17.proto.WebFeatures.Flag\x121\n\x10recentStickersV2\x18" \x01(\x0e2\x17.proto.WebFeatures.Flag\x121\n\x10recentStickersV3\x18$ \x01(\x0e2\x17.proto.WebFeatures.Flag\x12+\n\nuserNotice\x18% \x01(\x0e2\x17.proto.WebFeatures.Flag\x12(\n\x07support\x18\' \x01(\x0e2\x17.proto.WebFeatures.Flag\x120\n\x0fgroupUiiCleanup\x18( \x01(\x0e2\x17.proto.WebFeatures.Flag\x12<\n\x1bgroupDogfoodingInternalOnly\x18) \x01(\x0e2\x17.proto.WebFeatures.Flag\x12-\n\x0csettingsSync\x18* \x01(\x0e2\x17.proto.WebFeatures.Flag\x12*\n\tarchiveV2\x18+ \x01(\x0e2\x17.proto.WebFeatures.Flag\x12;\n\x1aephemeralAllowGroupMembers\x18, \x01(\x0e2\x17.proto.WebFeatures.Flag\x125\n\x14ephemeral24HDuration\x18- \x01(\x0e2\x17.proto.WebFeatures.Flag\x12/\n\x0emdForceUpgrade\x18. \x01(\x0e2\x17.proto.WebFeatures.Flag\x121\n\x10disappearingMode\x18/ \x01(\x0e2\x17.proto.WebFeatures.Flag\x129\n\x18externalMdOptInAvailable\x180 \x01(\x0e2\x17.proto.WebFeatures.Flag\x129\n\x18noDeleteMessageTimeLimit\x181 \x01(\x0e2\x17.proto.WebFeatures.Flag"K\n\x04Flag\x12\x0f\n\x0bNOT_STARTED\x10\x00\x12\x11\n\rFORCE_UPGRADE\x10\x01\x12\x0f\n\x0bDEVELOPMENT\x10\x02\x12\x0e\n\nPRODUCTION\x10\x03"\x9e\x01\n\x0bUserReceipt\x12\x0f\n\x07userJid\x18\x01 \x02(\t\x12\x18\n\x10receiptTimestamp\x18\x02 \x01(\x03\x12\x15\n\rreadTimestamp\x18\x03 \x01(\x03\x12\x17\n\x0fplayedTimestamp\x18\x04 \x01(\x03\x12\x18\n\x10pendingDeviceJid\x18\x05 \x03(\t\x12\x1a\n\x12deliveredDeviceJid\x18\x06 \x03(\t"D\n\tStatusPSA\x12\x12\n\ncampaignId\x18, \x02(\x04\x12#\n\x1bcampaignExpirationTimestamp\x18- \x01(\x04"x\n\x08Reaction\x12\x1e\n\x03key\x18\x01 \x01(\x0b2\x11.proto.MessageKey\x12\x0c\n\x04text\x18\x02 \x01(\t\x12\x13\n\x0bgroupingKey\x18\x03 \x01(\t\x12\x19\n\x11senderTimestampMs\x18\x04 \x01(\x03\x12\x0e\n\x06unread\x18\x05 \x01(\x08"\xa9\x01\n\nPollUpdate\x12/\n\x14pollUpdateMessageKey\x18\x01 \x01(\x0b2\x11.proto.MessageKey\x12$\n\x04vote\x18\x02 \x01(\x0b2\x16.proto.PollVoteMessage\x12\x19\n\x11senderTimestampMs\x18\x03 \x01(\x03\x12\x19\n\x11serverTimestampMs\x18\x04 \x01(\x03\x12\x0e\n\x06unread\x18\x05 \x01(\x08"1\n\x16PollAdditionalMetadata\x12\x17\n\x0fpollInvalidated\x18\x01 \x01(\x08"\x85\x02\n\tPinInChat\x12#\n\x04type\x18\x01 \x01(\x0e2\x15.proto.PinInChat.Type\x12\x1e\n\x03key\x18\x02 \x01(\x0b2\x11.proto.MessageKey\x12\x19\n\x11senderTimestampMs\x18\x03 \x01(\x03\x12\x19\n\x11serverTimestampMs\x18\x04 \x01(\x03\x12?\n\x17messageAddOnContextInfo\x18\x05 \x01(\x0b2\x1e.proto.MessageAddOnContextInfo"<\n\x04Type\x12\x10\n\x0cUNKNOWN_TYPE\x10\x00\x12\x0f\n\x0bPIN_FOR_ALL\x10\x01\x12\x11\n\rUNPIN_FOR_ALL\x10\x02"E\n\x0bPhotoChange\x12\x10\n\x08oldPhoto\x18\x01 \x01(\x0c\x12\x10\n\x08newPhoto\x18\x02 \x01(\x0c\x12\x12\n\nnewPhotoId\x18\x03 \x01(\r"\xd5\n\n\x0bPaymentInfo\x127\n\x12currencyDeprecated\x18\x01 \x01(\x0e2\x1b.proto.PaymentInfo.Currency\x12\x12\n\namount1000\x18\x02 \x01(\x04\x12\x13\n\x0breceiverJid\x18\x03 \x01(\t\x12)\n\x06status\x18\x04 \x01(\x0e2\x19.proto.PaymentInfo.Status\x12\x1c\n\x14transactionTimestamp\x18\x05 \x01(\x04\x12,\n\x11requestMessageKey\x18\x06 \x01(\x0b2\x11.proto.MessageKey\x12\x17\n\x0fexpiryTimestamp\x18\x07 \x01(\x04\x12\x15\n\rfutureproofed\x18\x08 \x01(\x08\x12\x10\n\x08currency\x18\t \x01(\t\x12/\n\ttxnStatus\x18\n \x01(\x0e2\x1c.proto.PaymentInfo.TxnStatus\x12\x19\n\x11useNoviFiatFormat\x18\x0b \x01(\x08\x12#\n\rprimaryAmount\x18\x0c \x01(\x0b2\x0c.proto.Money\x12$\n\x0eexchangeAmount\x18\r \x01(\x0b2\x0c.proto.Money"\x99\x05\n\tTxnStatus\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x11\n\rPENDING_SETUP\x10\x01\x12\x1a\n\x16PENDING_RECEIVER_SETUP\x10\x02\x12\x08\n\x04INIT\x10\x03\x12\x0b\n\x07SUCCESS\x10\x04\x12\r\n\tCOMPLETED\x10\x05\x12\n\n\x06FAILED\x10\x06\x12\x0f\n\x0bFAILED_RISK\x10\x07\x12\x15\n\x11FAILED_PROCESSING\x10\x08\x12\x1e\n\x1aFAILED_RECEIVER_PROCESSING\x10\t\x12\r\n\tFAILED_DA\x10\n\x12\x13\n\x0fFAILED_DA_FINAL\x10\x0b\x12\x10\n\x0cREFUNDED_TXN\x10\x0c\x12\x11\n\rREFUND_FAILED\x10\r\x12\x1c\n\x18REFUND_FAILED_PROCESSING\x10\x0e\x12\x14\n\x10REFUND_FAILED_DA\x10\x0f\x12\x0f\n\x0bEXPIRED_TXN\x10\x10\x12\x11\n\rAUTH_CANCELED\x10\x11\x12!\n\x1dAUTH_CANCEL_FAILED_PROCESSING\x10\x12\x12\x16\n\x12AUTH_CANCEL_FAILED\x10\x13\x12\x10\n\x0cCOLLECT_INIT\x10\x14\x12\x13\n\x0fCOLLECT_SUCCESS\x10\x15\x12\x12\n\x0eCOLLECT_FAILED\x10\x16\x12\x17\n\x13COLLECT_FAILED_RISK\x10\x17\x12\x14\n\x10COLLECT_REJECTED\x10\x18\x12\x13\n\x0fCOLLECT_EXPIRED\x10\x19\x12\x14\n\x10COLLECT_CANCELED\x10\x1a\x12\x16\n\x12COLLECT_CANCELLING\x10\x1b\x12\r\n\tIN_REVIEW\x10\x1c\x12\x14\n\x10REVERSAL_SUCCESS\x10\x1d\x12\x14\n\x10REVERSAL_PENDING\x10\x1e\x12\x12\n\x0eREFUND_PENDING\x10\x1f"\xcc\x01\n\x06Status\x12\x12\n\x0eUNKNOWN_STATUS\x10\x00\x12\x0e\n\nPROCESSING\x10\x01\x12\x08\n\x04SENT\x10\x02\x12\x12\n\x0eNEED_TO_ACCEPT\x10\x03\x12\x0c\n\x08COMPLETE\x10\x04\x12\x16\n\x12COULD_NOT_COMPLETE\x10\x05\x12\x0c\n\x08REFUNDED\x10\x06\x12\x0b\n\x07EXPIRED\x10\x07\x12\x0c\n\x08REJECTED\x10\x08\x12\r\n\tCANCELLED\x10\t\x12\x15\n\x11WAITING_FOR_PAYER\x10\n\x12\x0b\n\x07WAITING\x10\x0b")\n\x08Currency\x12\x14\n\x10UNKNOWN_CURRENCY\x10\x00\x12\x07\n\x03INR\x10\x01"\x89\x01\n\x17NotificationMessageInfo\x12\x1e\n\x03key\x18\x01 \x01(\x0b2\x11.proto.MessageKey\x12\x1f\n\x07message\x18\x02 \x01(\x0b2\x0e.proto.Message\x12\x18\n\x10messageTimestamp\x18\x03 \x01(\x04\x12\x13\n\x0bparticipant\x18\x04 \x01(\t"=\n\x17MessageAddOnContextInfo\x12"\n\x1amessageAddOnDurationInSecs\x18\x01 \x01(\r"\x1e\n\tMediaData\x12\x11\n\tlocalPath\x18\x01 \x01(\t"\xb1\x01\n\nKeepInChat\x12!\n\x08keepType\x18\x01 \x01(\x0e2\x0f.proto.KeepType\x12\x17\n\x0fserverTimestamp\x18\x02 \x01(\x03\x12\x1e\n\x03key\x18\x03 \x01(\x0b2\x11.proto.MessageKey\x12\x11\n\tdeviceJid\x18\x04 \x01(\t\x12\x19\n\x11clientTimestampMs\x18\x05 \x01(\x03\x12\x19\n\x11serverTimestampMs\x18\x06 \x01(\x03"\x90\x01\n\x10NoiseCertificate\x12\x0f\n\x07details\x18\x01 \x01(\x0c\x12\x11\n\tsignature\x18\x02 \x01(\x0c\x1aX\n\x07Details\x12\x0e\n\x06serial\x18\x01 \x01(\r\x12\x0e\n\x06issuer\x18\x02 \x01(\t\x12\x0f\n\x07expires\x18\x03 \x01(\x04\x12\x0f\n\x07subject\x18\x04 \x01(\t\x12\x0b\n\x03key\x18\x05 \x01(\x0c"\x91\x02\n\tCertChain\x12/\n\x04leaf\x18\x01 \x01(\x0b2!.proto.CertChain.NoiseCertificate\x127\n\x0cintermediate\x18\x02 \x01(\x0b2!.proto.CertChain.NoiseCertificate\x1a\x99\x01\n\x10NoiseCertificate\x12\x0f\n\x07details\x18\x01 \x01(\x0c\x12\x11\n\tsignature\x18\x02 \x01(\x0c\x1aa\n\x07Details\x12\x0e\n\x06serial\x18\x01 \x01(\r\x12\x14\n\x0cissuerSerial\x18\x02 \x01(\r\x12\x0b\n\x03key\x18\x03 \x01(\x0c\x12\x11\n\tnotBefore\x18\x04 \x01(\x04\x12\x10\n\x08notAfter\x18\x05 \x01(\x04*)\n\x11ADVEncryptionType\x12\x08\n\x04E2EE\x10\x00\x12\n\n\x06HOSTED\x10\x01*@\n\x08KeepType\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x10\n\x0cKEEP_FOR_ALL\x10\x01\x12\x15\n\x11UNDO_KEEP_FOR_ALL\x10\x02*\xac\x01\n\x1cPeerDataOperationRequestType\x12\x12\n\x0eUPLOAD_STICKER\x10\x00\x12!\n\x1dSEND_RECENT_STICKER_BOOTSTRAP\x10\x01\x12\x19\n\x15GENERATE_LINK_PREVIEW\x10\x02\x12\x1a\n\x16HISTORY_SYNC_ON_DEMAND\x10\x03\x12\x1e\n\x1aPLACEHOLDER_MESSAGE_RESEND\x10\x04*/\n\x0fMediaVisibility\x12\x0b\n\x07DEFAULT\x10\x00\x12\x07\n\x03OFF\x10\x01\x12\x06\n\x02ON\x10\x02B"Z go.mau.fi/whatsmeow/binary/proto'
)
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "whatsappweb_pb2", _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b"Z go.mau.fi/whatsmeow/binary/proto"
    _ADVKEYINDEXLIST.fields_by_name["validIndexes"]._options = None
    _ADVKEYINDEXLIST.fields_by_name["validIndexes"]._serialized_options = b"\x10\x01"
    _APPSTATESYNCKEYFINGERPRINT.fields_by_name["deviceIndexes"]._options = None
    _APPSTATESYNCKEYFINGERPRINT.fields_by_name[
        "deviceIndexes"
    ]._serialized_options = b"\x10\x01"
    _DEVICELISTMETADATA.fields_by_name["senderKeyIndexes"]._options = None
    _DEVICELISTMETADATA.fields_by_name[
        "senderKeyIndexes"
    ]._serialized_options = b"\x10\x01"
    _DEVICELISTMETADATA.fields_by_name["recipientKeyIndexes"]._options = None
    _DEVICELISTMETADATA.fields_by_name[
        "recipientKeyIndexes"
    ]._serialized_options = b"\x10\x01"
    _globals["_ADVENCRYPTIONTYPE"]._serialized_start = 57230
    _globals["_ADVENCRYPTIONTYPE"]._serialized_end = 57271
    _globals["_KEEPTYPE"]._serialized_start = 57273
    _globals["_KEEPTYPE"]._serialized_end = 57337
    _globals["_PEERDATAOPERATIONREQUESTTYPE"]._serialized_start = 57340
    _globals["_PEERDATAOPERATIONREQUESTTYPE"]._serialized_end = 57512
    _globals["_MEDIAVISIBILITY"]._serialized_start = 57514
    _globals["_MEDIAVISIBILITY"]._serialized_end = 57561
    _globals["_ADVSIGNEDKEYINDEXLIST"]._serialized_start = 28
    _globals["_ADVSIGNEDKEYINDEXLIST"]._serialized_end = 94
    _globals["_ADVSIGNEDDEVICEIDENTITY"]._serialized_start = 96
    _globals["_ADVSIGNEDDEVICEIDENTITY"]._serialized_end = 218
    _globals["_ADVSIGNEDDEVICEIDENTITYHMAC"]._serialized_start = 220
    _globals["_ADVSIGNEDDEVICEIDENTITYHMAC"]._serialized_end = 280
    _globals["_ADVKEYINDEXLIST"]._serialized_start = 283
    _globals["_ADVKEYINDEXLIST"]._serialized_end = 429
    _globals["_ADVDEVICEIDENTITY"]._serialized_start = 432
    _globals["_ADVDEVICEIDENTITY"]._serialized_end = 596
    _globals["_DEVICEPROPS"]._serialized_start = 599
    _globals["_DEVICEPROPS"]._serialized_end = 1354
    _globals["_DEVICEPROPS_HISTORYSYNCCONFIG"]._serialized_start = 820
    _globals["_DEVICEPROPS_HISTORYSYNCCONFIG"]._serialized_end = 987
    _globals["_DEVICEPROPS_APPVERSION"]._serialized_start = 989
    _globals["_DEVICEPROPS_APPVERSION"]._serialized_end = 1092
    _globals["_DEVICEPROPS_PLATFORMTYPE"]._serialized_start = 1095
    _globals["_DEVICEPROPS_PLATFORMTYPE"]._serialized_end = 1354
    _globals["_PAYMENTINVITEMESSAGE"]._serialized_start = 1357
    _globals["_PAYMENTINVITEMESSAGE"]._serialized_end = 1524
    _globals["_PAYMENTINVITEMESSAGE_SERVICETYPE"]._serialized_start = 1468
    _globals["_PAYMENTINVITEMESSAGE_SERVICETYPE"]._serialized_end = 1524
    _globals["_ORDERMESSAGE"]._serialized_start = 1527
    _globals["_ORDERMESSAGE"]._serialized_end = 1917
    _globals["_ORDERMESSAGE_ORDERSURFACE"]._serialized_start = 1862
    _globals["_ORDERMESSAGE_ORDERSURFACE"]._serialized_end = 1889
    _globals["_ORDERMESSAGE_ORDERSTATUS"]._serialized_start = 1891
    _globals["_ORDERMESSAGE_ORDERSTATUS"]._serialized_end = 1917
    _globals["_LOCATIONMESSAGE"]._serialized_start = 1920
    _globals["_LOCATIONMESSAGE"]._serialized_end = 2218
    _globals["_LIVELOCATIONMESSAGE"]._serialized_start = 2221
    _globals["_LIVELOCATIONMESSAGE"]._serialized_end = 2507
    _globals["_LISTRESPONSEMESSAGE"]._serialized_start = 2510
    _globals["_LISTRESPONSEMESSAGE"]._serialized_end = 2824
    _globals["_LISTRESPONSEMESSAGE_SINGLESELECTREPLY"]._serialized_start = 2738
    _globals["_LISTRESPONSEMESSAGE_SINGLESELECTREPLY"]._serialized_end = 2780
    _globals["_LISTRESPONSEMESSAGE_LISTTYPE"]._serialized_start = 2782
    _globals["_LISTRESPONSEMESSAGE_LISTTYPE"]._serialized_end = 2824
    _globals["_LISTMESSAGE"]._serialized_start = 2827
    _globals["_LISTMESSAGE"]._serialized_end = 3642
    _globals["_LISTMESSAGE_SECTION"]._serialized_start = 3113
    _globals["_LISTMESSAGE_SECTION"]._serialized_end = 3175
    _globals["_LISTMESSAGE_ROW"]._serialized_start = 3177
    _globals["_LISTMESSAGE_ROW"]._serialized_end = 3233
    _globals["_LISTMESSAGE_PRODUCT"]._serialized_start = 3235
    _globals["_LISTMESSAGE_PRODUCT"]._serialized_end = 3263
    _globals["_LISTMESSAGE_PRODUCTSECTION"]._serialized_start = 3265
    _globals["_LISTMESSAGE_PRODUCTSECTION"]._serialized_end = 3342
    _globals["_LISTMESSAGE_PRODUCTLISTINFO"]._serialized_start = 3345
    _globals["_LISTMESSAGE_PRODUCTLISTINFO"]._serialized_end = 3512
    _globals["_LISTMESSAGE_PRODUCTLISTHEADERIMAGE"]._serialized_start = 3514
    _globals["_LISTMESSAGE_PRODUCTLISTHEADERIMAGE"]._serialized_end = 3580
    _globals["_LISTMESSAGE_LISTTYPE"]._serialized_start = 3582
    _globals["_LISTMESSAGE_LISTTYPE"]._serialized_end = 3642
    _globals["_KEEPINCHATMESSAGE"]._serialized_start = 3644
    _globals["_KEEPINCHATMESSAGE"]._serialized_end = 3751
    _globals["_INVOICEMESSAGE"]._serialized_start = 3754
    _globals["_INVOICEMESSAGE"]._serialized_end = 4118
    _globals["_INVOICEMESSAGE_ATTACHMENTTYPE"]._serialized_start = 4082
    _globals["_INVOICEMESSAGE_ATTACHMENTTYPE"]._serialized_end = 4118
    _globals["_INTERACTIVERESPONSEMESSAGE"]._serialized_start = 4121
    _globals["_INTERACTIVERESPONSEMESSAGE"]._serialized_end = 4578
    _globals[
        "_INTERACTIVERESPONSEMESSAGE_NATIVEFLOWRESPONSEMESSAGE"
    ]._serialized_start = 4344
    _globals[
        "_INTERACTIVERESPONSEMESSAGE_NATIVEFLOWRESPONSEMESSAGE"
    ]._serialized_end = 4422
    _globals["_INTERACTIVERESPONSEMESSAGE_BODY"]._serialized_start = 4424
    _globals["_INTERACTIVERESPONSEMESSAGE_BODY"]._serialized_end = 4548
    _globals["_INTERACTIVERESPONSEMESSAGE_BODY_FORMAT"]._serialized_start = 4509
    _globals["_INTERACTIVERESPONSEMESSAGE_BODY_FORMAT"]._serialized_end = 4548
    _globals["_INTERACTIVEMESSAGE"]._serialized_start = 4581
    _globals["_INTERACTIVEMESSAGE"]._serialized_end = 5780
    _globals["_INTERACTIVEMESSAGE_SHOPMESSAGE"]._serialized_start = 5011
    _globals["_INTERACTIVEMESSAGE_SHOPMESSAGE"]._serialized_end = 5180
    _globals["_INTERACTIVEMESSAGE_SHOPMESSAGE_SURFACE"]._serialized_start = 5126
    _globals["_INTERACTIVEMESSAGE_SHOPMESSAGE_SURFACE"]._serialized_end = 5180
    _globals["_INTERACTIVEMESSAGE_NATIVEFLOWMESSAGE"]._serialized_start = 5183
    _globals["_INTERACTIVEMESSAGE_NATIVEFLOWMESSAGE"]._serialized_end = 5392
    _globals[
        "_INTERACTIVEMESSAGE_NATIVEFLOWMESSAGE_NATIVEFLOWBUTTON"
    ]._serialized_start = 5334
    _globals[
        "_INTERACTIVEMESSAGE_NATIVEFLOWMESSAGE_NATIVEFLOWBUTTON"
    ]._serialized_end = 5392
    _globals["_INTERACTIVEMESSAGE_HEADER"]._serialized_start = 5395
    _globals["_INTERACTIVEMESSAGE_HEADER"]._serialized_end = 5639
    _globals["_INTERACTIVEMESSAGE_FOOTER"]._serialized_start = 5641
    _globals["_INTERACTIVEMESSAGE_FOOTER"]._serialized_end = 5663
    _globals["_INTERACTIVEMESSAGE_COLLECTIONMESSAGE"]._serialized_start = 5665
    _globals["_INTERACTIVEMESSAGE_COLLECTIONMESSAGE"]._serialized_end = 5736
    _globals["_INTERACTIVEMESSAGE_BODY"]._serialized_start = 4424
    _globals["_INTERACTIVEMESSAGE_BODY"]._serialized_end = 4444
    _globals["_INITIALSECURITYNOTIFICATIONSETTINGSYNC"]._serialized_start = 5782
    _globals["_INITIALSECURITYNOTIFICATIONSETTINGSYNC"]._serialized_end = 5859
    _globals["_IMAGEMESSAGE"]._serialized_start = 5862
    _globals["_IMAGEMESSAGE"]._serialized_end = 6512
    _globals["_HISTORYSYNCNOTIFICATION"]._serialized_start = 6515
    _globals["_HISTORYSYNCNOTIFICATION"]._serialized_end = 7028
    _globals["_HISTORYSYNCNOTIFICATION_HISTORYSYNCTYPE"]._serialized_start = 6890
    _globals["_HISTORYSYNCNOTIFICATION_HISTORYSYNCTYPE"]._serialized_end = 7028
    _globals["_HIGHLYSTRUCTUREDMESSAGE"]._serialized_start = 7031
    _globals["_HIGHLYSTRUCTUREDMESSAGE"]._serialized_end = 8421
    _globals[
        "_HIGHLYSTRUCTUREDMESSAGE_HSMLOCALIZABLEPARAMETER"
    ]._serialized_start = 7333
    _globals["_HIGHLYSTRUCTUREDMESSAGE_HSMLOCALIZABLEPARAMETER"]._serialized_end = 8421
    _globals[
        "_HIGHLYSTRUCTUREDMESSAGE_HSMLOCALIZABLEPARAMETER_HSMDATETIME"
    ]._serialized_start = 7554
    _globals[
        "_HIGHLYSTRUCTUREDMESSAGE_HSMLOCALIZABLEPARAMETER_HSMDATETIME"
    ]._serialized_end = 8350
    _globals[
        "_HIGHLYSTRUCTUREDMESSAGE_HSMLOCALIZABLEPARAMETER_HSMDATETIME_HSMDATETIMEUNIXEPOCH"
    ]._serialized_start = 7789
    _globals[
        "_HIGHLYSTRUCTUREDMESSAGE_HSMLOCALIZABLEPARAMETER_HSMDATETIME_HSMDATETIMEUNIXEPOCH"
    ]._serialized_end = 7830
    _globals[
        "_HIGHLYSTRUCTUREDMESSAGE_HSMLOCALIZABLEPARAMETER_HSMDATETIME_HSMDATETIMECOMPONENT"
    ]._serialized_start = 7833
    _globals[
        "_HIGHLYSTRUCTUREDMESSAGE_HSMLOCALIZABLEPARAMETER_HSMDATETIME_HSMDATETIMECOMPONENT"
    ]._serialized_end = 8333
    _globals[
        "_HIGHLYSTRUCTUREDMESSAGE_HSMLOCALIZABLEPARAMETER_HSMDATETIME_HSMDATETIMECOMPONENT_DAYOFWEEKTYPE"
    ]._serialized_start = 8178
    _globals[
        "_HIGHLYSTRUCTUREDMESSAGE_HSMLOCALIZABLEPARAMETER_HSMDATETIME_HSMDATETIMECOMPONENT_DAYOFWEEKTYPE"
    ]._serialized_end = 8285
    _globals[
        "_HIGHLYSTRUCTUREDMESSAGE_HSMLOCALIZABLEPARAMETER_HSMDATETIME_HSMDATETIMECOMPONENT_CALENDARTYPE"
    ]._serialized_start = 8287
    _globals[
        "_HIGHLYSTRUCTUREDMESSAGE_HSMLOCALIZABLEPARAMETER_HSMDATETIME_HSMDATETIMECOMPONENT_CALENDARTYPE"
    ]._serialized_end = 8333
    _globals[
        "_HIGHLYSTRUCTUREDMESSAGE_HSMLOCALIZABLEPARAMETER_HSMCURRENCY"
    ]._serialized_start = 8352
    _globals[
        "_HIGHLYSTRUCTUREDMESSAGE_HSMLOCALIZABLEPARAMETER_HSMCURRENCY"
    ]._serialized_end = 8407
    _globals["_GROUPINVITEMESSAGE"]._serialized_start = 8424
    _globals["_GROUPINVITEMESSAGE"]._serialized_end = 8702
    _globals["_GROUPINVITEMESSAGE_GROUPTYPE"]._serialized_start = 8666
    _globals["_GROUPINVITEMESSAGE_GROUPTYPE"]._serialized_end = 8702
    _globals["_FUTUREPROOFMESSAGE"]._serialized_start = 8704
    _globals["_FUTUREPROOFMESSAGE"]._serialized_end = 8757
    _globals["_EXTENDEDTEXTMESSAGE"]._serialized_start = 8760
    _globals["_EXTENDEDTEXTMESSAGE"]._serialized_end = 9890
    _globals["_EXTENDEDTEXTMESSAGE_PREVIEWTYPE"]._serialized_start = 9551
    _globals["_EXTENDEDTEXTMESSAGE_PREVIEWTYPE"]._serialized_end = 9585
    _globals["_EXTENDEDTEXTMESSAGE_INVITELINKGROUPTYPE"]._serialized_start = 9587
    _globals["_EXTENDEDTEXTMESSAGE_INVITELINKGROUPTYPE"]._serialized_end = 9659
    _globals["_EXTENDEDTEXTMESSAGE_FONTTYPE"]._serialized_start = 9662
    _globals["_EXTENDEDTEXTMESSAGE_FONTTYPE"]._serialized_end = 9890
    _globals["_ENCREACTIONMESSAGE"]._serialized_start = 9892
    _globals["_ENCREACTIONMESSAGE"]._serialized_end = 9992
    _globals["_DOCUMENTMESSAGE"]._serialized_start = 9995
    _globals["_DOCUMENTMESSAGE"]._serialized_end = 10457
    _globals["_DEVICESENTMESSAGE"]._serialized_start = 10459
    _globals["_DEVICESENTMESSAGE"]._serialized_end = 10550
    _globals["_DECLINEPAYMENTREQUESTMESSAGE"]._serialized_start = 10552
    _globals["_DECLINEPAYMENTREQUESTMESSAGE"]._serialized_end = 10614
    _globals["_CONTACTSARRAYMESSAGE"]._serialized_start = 10616
    _globals["_CONTACTSARRAYMESSAGE"]._serialized_end = 10741
    _globals["_CONTACTMESSAGE"]._serialized_start = 10743
    _globals["_CONTACTMESSAGE"]._serialized_end = 10836
    _globals["_CHAT"]._serialized_start = 10838
    _globals["_CHAT"]._serialized_end = 10877
    _globals["_CANCELPAYMENTREQUESTMESSAGE"]._serialized_start = 10879
    _globals["_CANCELPAYMENTREQUESTMESSAGE"]._serialized_end = 10940
    _globals["_CALL"]._serialized_start = 10942
    _globals["_CALL"]._serialized_end = 11047
    _globals["_BUTTONSRESPONSEMESSAGE"]._serialized_start = 11050
    _globals["_BUTTONSRESPONSEMESSAGE"]._serialized_end = 11273
    _globals["_BUTTONSRESPONSEMESSAGE_TYPE"]._serialized_start = 11224
    _globals["_BUTTONSRESPONSEMESSAGE_TYPE"]._serialized_end = 11261
    _globals["_BUTTONSMESSAGE"]._serialized_start = 11276
    _globals["_BUTTONSMESSAGE"]._serialized_end = 12138
    _globals["_BUTTONSMESSAGE_BUTTON"]._serialized_start = 11686
    _globals["_BUTTONSMESSAGE_BUTTON"]._serialized_end = 12030
    _globals["_BUTTONSMESSAGE_BUTTON_NATIVEFLOWINFO"]._serialized_start = 11893
    _globals["_BUTTONSMESSAGE_BUTTON_NATIVEFLOWINFO"]._serialized_end = 11943
    _globals["_BUTTONSMESSAGE_BUTTON_BUTTONTEXT"]._serialized_start = 11945
    _globals["_BUTTONSMESSAGE_BUTTON_BUTTONTEXT"]._serialized_end = 11978
    _globals["_BUTTONSMESSAGE_BUTTON_TYPE"]._serialized_start = 11980
    _globals["_BUTTONSMESSAGE_BUTTON_TYPE"]._serialized_end = 12030
    _globals["_BUTTONSMESSAGE_HEADERTYPE"]._serialized_start = 12032
    _globals["_BUTTONSMESSAGE_HEADERTYPE"]._serialized_end = 12128
    _globals["_AUDIOMESSAGE"]._serialized_start = 12141
    _globals["_AUDIOMESSAGE"]._serialized_end = 12471
    _globals["_APPSTATESYNCKEY"]._serialized_start = 12473
    _globals["_APPSTATESYNCKEY"]._serialized_end = 12576
    _globals["_APPSTATESYNCKEYSHARE"]._serialized_start = 12578
    _globals["_APPSTATESYNCKEYSHARE"]._serialized_end = 12638
    _globals["_APPSTATESYNCKEYREQUEST"]._serialized_start = 12640
    _globals["_APPSTATESYNCKEYREQUEST"]._serialized_end = 12706
    _globals["_APPSTATESYNCKEYID"]._serialized_start = 12708
    _globals["_APPSTATESYNCKEYID"]._serialized_end = 12742
    _globals["_APPSTATESYNCKEYFINGERPRINT"]._serialized_start = 12744
    _globals["_APPSTATESYNCKEYFINGERPRINT"]._serialized_end = 12836
    _globals["_APPSTATESYNCKEYDATA"]._serialized_start = 12838
    _globals["_APPSTATESYNCKEYDATA"]._serialized_end = 12951
    _globals["_APPSTATEFATALEXCEPTIONNOTIFICATION"]._serialized_start = 12953
    _globals["_APPSTATEFATALEXCEPTIONNOTIFICATION"]._serialized_end = 13033
    _globals["_LOCATION"]._serialized_start = 13035
    _globals["_LOCATION"]._serialized_end = 13110
    _globals["_INTERACTIVEANNOTATION"]._serialized_start = 13112
    _globals["_INTERACTIVEANNOTATION"]._serialized_end = 13221
    _globals["_HYDRATEDTEMPLATEBUTTON"]._serialized_start = 13224
    _globals["_HYDRATEDTEMPLATEBUTTON"]._serialized_end = 13687
    _globals["_HYDRATEDTEMPLATEBUTTON_HYDRATEDURLBUTTON"]._serialized_start = 13491
    _globals["_HYDRATEDTEMPLATEBUTTON_HYDRATEDURLBUTTON"]._serialized_end = 13544
    _globals[
        "_HYDRATEDTEMPLATEBUTTON_HYDRATEDQUICKREPLYBUTTON"
    ]._serialized_start = 13546
    _globals["_HYDRATEDTEMPLATEBUTTON_HYDRATEDQUICKREPLYBUTTON"]._serialized_end = 13605
    _globals["_HYDRATEDTEMPLATEBUTTON_HYDRATEDCALLBUTTON"]._serialized_start = 13607
    _globals["_HYDRATEDTEMPLATEBUTTON_HYDRATEDCALLBUTTON"]._serialized_end = 13669
    _globals["_GROUPMENTION"]._serialized_start = 13689
    _globals["_GROUPMENTION"]._serialized_end = 13743
    _globals["_DISAPPEARINGMODE"]._serialized_start = 13746
    _globals["_DISAPPEARINGMODE"]._serialized_end = 13897
    _globals["_DISAPPEARINGMODE_INITIATOR"]._serialized_start = 13820
    _globals["_DISAPPEARINGMODE_INITIATOR"]._serialized_end = 13897
    _globals["_DEVICELISTMETADATA"]._serialized_start = 13900
    _globals["_DEVICELISTMETADATA"]._serialized_end = 14085
    _globals["_CONTEXTINFO"]._serialized_start = 14088
    _globals["_CONTEXTINFO"]._serialized_end = 15618
    _globals["_CONTEXTINFO_UTMINFO"]._serialized_start = 14997
    _globals["_CONTEXTINFO_UTMINFO"]._serialized_end = 15046
    _globals["_CONTEXTINFO_EXTERNALADREPLYINFO"]._serialized_start = 15049
    _globals["_CONTEXTINFO_EXTERNALADREPLYINFO"]._serialized_end = 15432
    _globals["_CONTEXTINFO_EXTERNALADREPLYINFO_MEDIATYPE"]._serialized_start = 15389
    _globals["_CONTEXTINFO_EXTERNALADREPLYINFO_MEDIATYPE"]._serialized_end = 15432
    _globals["_CONTEXTINFO_ADREPLYINFO"]._serialized_start = 15435
    _globals["_CONTEXTINFO_ADREPLYINFO"]._serialized_end = 15618
    _globals["_CONTEXTINFO_ADREPLYINFO_MEDIATYPE"]._serialized_start = 15389
    _globals["_CONTEXTINFO_ADREPLYINFO_MEDIATYPE"]._serialized_end = 15432
    _globals["_ACTIONLINK"]._serialized_start = 15620
    _globals["_ACTIONLINK"]._serialized_end = 15666
    _globals["_TEMPLATEBUTTON"]._serialized_start = 15669
    _globals["_TEMPLATEBUTTON"]._serialized_end = 16204
    _globals["_TEMPLATEBUTTON_URLBUTTON"]._serialized_start = 15880
    _globals["_TEMPLATEBUTTON_URLBUTTON"]._serialized_end = 15989
    _globals["_TEMPLATEBUTTON_QUICKREPLYBUTTON"]._serialized_start = 15991
    _globals["_TEMPLATEBUTTON_QUICKREPLYBUTTON"]._serialized_end = 16074
    _globals["_TEMPLATEBUTTON_CALLBUTTON"]._serialized_start = 16076
    _globals["_TEMPLATEBUTTON_CALLBUTTON"]._serialized_end = 16194
    _globals["_POINT"]._serialized_start = 16206
    _globals["_POINT"]._serialized_end = 16277
    _globals["_PAYMENTBACKGROUND"]._serialized_start = 16280
    _globals["_PAYMENTBACKGROUND"]._serialized_end = 16699
    _globals["_PAYMENTBACKGROUND_MEDIADATA"]._serialized_start = 16546
    _globals["_PAYMENTBACKGROUND_MEDIADATA"]._serialized_end = 16665
    _globals["_PAYMENTBACKGROUND_TYPE"]._serialized_start = 16667
    _globals["_PAYMENTBACKGROUND_TYPE"]._serialized_end = 16699
    _globals["_MONEY"]._serialized_start = 16701
    _globals["_MONEY"]._serialized_end = 16761
    _globals["_MESSAGE"]._serialized_start = 16764
    _globals["_MESSAGE"]._serialized_end = 19840
    _globals["_MESSAGECONTEXTINFO"]._serialized_start = 19843
    _globals["_MESSAGECONTEXTINFO"]._serialized_end = 20034
    _globals["_VIDEOMESSAGE"]._serialized_start = 20037
    _globals["_VIDEOMESSAGE"]._serialized_end = 20671
    _globals["_VIDEOMESSAGE_ATTRIBUTION"]._serialized_start = 20626
    _globals["_VIDEOMESSAGE_ATTRIBUTION"]._serialized_end = 20671
    _globals["_TEMPLATEMESSAGE"]._serialized_start = 20674
    _globals["_TEMPLATEMESSAGE"]._serialized_end = 21867
    _globals["_TEMPLATEMESSAGE_HYDRATEDFOURROWTEMPLATE"]._serialized_start = 21044
    _globals["_TEMPLATEMESSAGE_HYDRATEDFOURROWTEMPLATE"]._serialized_end = 21432
    _globals["_TEMPLATEMESSAGE_FOURROWTEMPLATE"]._serialized_start = 21435
    _globals["_TEMPLATEMESSAGE_FOURROWTEMPLATE"]._serialized_end = 21857
    _globals["_TEMPLATEBUTTONREPLYMESSAGE"]._serialized_start = 21870
    _globals["_TEMPLATEBUTTONREPLYMESSAGE"]._serialized_end = 22011
    _globals["_STICKERSYNCRMRMESSAGE"]._serialized_start = 22013
    _globals["_STICKERSYNCRMRMESSAGE"]._serialized_end = 22099
    _globals["_STICKERMESSAGE"]._serialized_start = 22102
    _globals["_STICKERMESSAGE"]._serialized_end = 22485
    _globals["_SENDERKEYDISTRIBUTIONMESSAGE"]._serialized_start = 22487
    _globals["_SENDERKEYDISTRIBUTIONMESSAGE"]._serialized_end = 22579
    _globals["_SENDPAYMENTMESSAGE"]._serialized_start = 22582
    _globals["_SENDPAYMENTMESSAGE"]._serialized_end = 22731
    _globals["_SCHEDULEDCALLEDITMESSAGE"]._serialized_start = 22734
    _globals["_SCHEDULEDCALLEDITMESSAGE"]._serialized_end = 22889
    _globals["_SCHEDULEDCALLEDITMESSAGE_EDITTYPE"]._serialized_start = 22854
    _globals["_SCHEDULEDCALLEDITMESSAGE_EDITTYPE"]._serialized_end = 22889
    _globals["_SCHEDULEDCALLCREATIONMESSAGE"]._serialized_start = 22892
    _globals["_SCHEDULEDCALLCREATIONMESSAGE"]._serialized_end = 23078
    _globals["_SCHEDULEDCALLCREATIONMESSAGE_CALLTYPE"]._serialized_start = 23033
    _globals["_SCHEDULEDCALLCREATIONMESSAGE_CALLTYPE"]._serialized_end = 23078
    _globals["_REQUESTPHONENUMBERMESSAGE"]._serialized_start = 23080
    _globals["_REQUESTPHONENUMBERMESSAGE"]._serialized_end = 23148
    _globals["_REQUESTPAYMENTMESSAGE"]._serialized_start = 23151
    _globals["_REQUESTPAYMENTMESSAGE"]._serialized_end = 23382
    _globals["_REACTIONMESSAGE"]._serialized_start = 23384
    _globals["_REACTIONMESSAGE"]._serialized_end = 23495
    _globals["_PROTOCOLMESSAGE"]._serialized_start = 23498
    _globals["_PROTOCOLMESSAGE"]._serialized_end = 24736
    _globals["_PROTOCOLMESSAGE_TYPE"]._serialized_start = 24315
    _globals["_PROTOCOLMESSAGE_TYPE"]._serialized_end = 24736
    _globals["_PRODUCTMESSAGE"]._serialized_start = 24739
    _globals["_PRODUCTMESSAGE"]._serialized_end = 25338
    _globals["_PRODUCTMESSAGE_PRODUCTSNAPSHOT"]._serialized_start = 24967
    _globals["_PRODUCTMESSAGE_PRODUCTSNAPSHOT"]._serialized_end = 25240
    _globals["_PRODUCTMESSAGE_CATALOGSNAPSHOT"]._serialized_start = 25242
    _globals["_PRODUCTMESSAGE_CATALOGSNAPSHOT"]._serialized_end = 25338
    _globals["_POLLVOTEMESSAGE"]._serialized_start = 25340
    _globals["_POLLVOTEMESSAGE"]._serialized_end = 25382
    _globals["_POLLUPDATEMESSAGE"]._serialized_start = 25385
    _globals["_POLLUPDATEMESSAGE"]._serialized_end = 25569
    _globals["_POLLUPDATEMESSAGEMETADATA"]._serialized_start = 25571
    _globals["_POLLUPDATEMESSAGEMETADATA"]._serialized_end = 25598
    _globals["_POLLENCVALUE"]._serialized_start = 25600
    _globals["_POLLENCVALUE"]._serialized_end = 25649
    _globals["_POLLCREATIONMESSAGE"]._serialized_start = 25652
    _globals["_POLLCREATIONMESSAGE"]._serialized_end = 25858
    _globals["_POLLCREATIONMESSAGE_OPTION"]._serialized_start = 25830
    _globals["_POLLCREATIONMESSAGE_OPTION"]._serialized_end = 25858
    _globals["_PININCHATMESSAGE"]._serialized_start = 25861
    _globals["_PININCHATMESSAGE"]._serialized_end = 26044
    _globals["_PININCHATMESSAGE_TYPE"]._serialized_start = 25984
    _globals["_PININCHATMESSAGE_TYPE"]._serialized_end = 26044
    _globals["_PEERDATAOPERATIONREQUESTRESPONSEMESSAGE"]._serialized_start = 26047
    _globals["_PEERDATAOPERATIONREQUESTRESPONSEMESSAGE"]._serialized_end = 27249
    _globals[
        "_PEERDATAOPERATIONREQUESTRESPONSEMESSAGE_PEERDATAOPERATIONRESULT"
    ]._serialized_start = 26289
    _globals[
        "_PEERDATAOPERATIONREQUESTRESPONSEMESSAGE_PEERDATAOPERATIONRESULT"
    ]._serialized_end = 27249
    _globals[
        "_PEERDATAOPERATIONREQUESTRESPONSEMESSAGE_PEERDATAOPERATIONRESULT_PLACEHOLDERMESSAGERESENDRESPONSE"
    ]._serialized_start = 26701
    _globals[
        "_PEERDATAOPERATIONREQUESTRESPONSEMESSAGE_PEERDATAOPERATIONRESULT_PLACEHOLDERMESSAGERESENDRESPONSE"
    ]._serialized_end = 26764
    _globals[
        "_PEERDATAOPERATIONREQUESTRESPONSEMESSAGE_PEERDATAOPERATIONRESULT_LINKPREVIEWRESPONSE"
    ]._serialized_start = 26767
    _globals[
        "_PEERDATAOPERATIONREQUESTRESPONSEMESSAGE_PEERDATAOPERATIONRESULT_LINKPREVIEWRESPONSE"
    ]._serialized_end = 27249
    _globals[
        "_PEERDATAOPERATIONREQUESTRESPONSEMESSAGE_PEERDATAOPERATIONRESULT_LINKPREVIEWRESPONSE_LINKPREVIEWHIGHQUALITYTHUMBNAIL"
    ]._serialized_start = 27067
    _globals[
        "_PEERDATAOPERATIONREQUESTRESPONSEMESSAGE_PEERDATAOPERATIONRESULT_LINKPREVIEWRESPONSE_LINKPREVIEWHIGHQUALITYTHUMBNAIL"
    ]._serialized_end = 27249
    _globals["_PEERDATAOPERATIONREQUESTMESSAGE"]._serialized_start = 27252
    _globals["_PEERDATAOPERATIONREQUESTMESSAGE"]._serialized_end = 28088
    _globals[
        "_PEERDATAOPERATIONREQUESTMESSAGE_REQUESTURLPREVIEW"
    ]._serialized_start = 27758
    _globals[
        "_PEERDATAOPERATIONREQUESTMESSAGE_REQUESTURLPREVIEW"
    ]._serialized_end = 27818
    _globals[
        "_PEERDATAOPERATIONREQUESTMESSAGE_REQUESTSTICKERREUPLOAD"
    ]._serialized_start = 27820
    _globals[
        "_PEERDATAOPERATIONREQUESTMESSAGE_REQUESTSTICKERREUPLOAD"
    ]._serialized_end = 27864
    _globals[
        "_PEERDATAOPERATIONREQUESTMESSAGE_PLACEHOLDERMESSAGERESENDREQUEST"
    ]._serialized_start = 27866
    _globals[
        "_PEERDATAOPERATIONREQUESTMESSAGE_PLACEHOLDERMESSAGERESENDREQUEST"
    ]._serialized_end = 27938
    _globals[
        "_PEERDATAOPERATIONREQUESTMESSAGE_HISTORYSYNCONDEMANDREQUEST"
    ]._serialized_start = 27941
    _globals[
        "_PEERDATAOPERATIONREQUESTMESSAGE_HISTORYSYNCONDEMANDREQUEST"
    ]._serialized_end = 28088
    _globals["_EPHEMERALSETTING"]._serialized_start = 28090
    _globals["_EPHEMERALSETTING"]._serialized_end = 28145
    _globals["_WALLPAPERSETTINGS"]._serialized_start = 28147
    _globals["_WALLPAPERSETTINGS"]._serialized_end = 28201
    _globals["_STICKERMETADATA"]._serialized_start = 28204
    _globals["_STICKERMETADATA"]._serialized_end = 28427
    _globals["_PUSHNAME"]._serialized_start = 28429
    _globals["_PUSHNAME"]._serialized_end = 28469
    _globals["_PASTPARTICIPANTS"]._serialized_start = 28471
    _globals["_PASTPARTICIPANTS"]._serialized_end = 28557
    _globals["_PASTPARTICIPANT"]._serialized_start = 28560
    _globals["_PASTPARTICIPANT"]._serialized_end = 28706
    _globals["_PASTPARTICIPANT_LEAVEREASON"]._serialized_start = 28670
    _globals["_PASTPARTICIPANT_LEAVEREASON"]._serialized_end = 28706
    _globals["_NOTIFICATIONSETTINGS"]._serialized_start = 28709
    _globals["_NOTIFICATIONSETTINGS"]._serialized_end = 28878
    _globals["_HISTORYSYNC"]._serialized_start = 28881
    _globals["_HISTORYSYNC"]._serialized_end = 29463
    _globals["_HISTORYSYNC_HISTORYSYNCTYPE"]._serialized_start = 6890
    _globals["_HISTORYSYNC_HISTORYSYNCTYPE"]._serialized_end = 7028
    _globals["_HISTORYSYNCMSG"]._serialized_start = 29465
    _globals["_HISTORYSYNCMSG"]._serialized_end = 29541
    _globals["_GROUPPARTICIPANT"]._serialized_start = 29543
    _globals["_GROUPPARTICIPANT"]._serialized_end = 29670
    _globals["_GROUPPARTICIPANT_RANK"]._serialized_start = 29624
    _globals["_GROUPPARTICIPANT_RANK"]._serialized_end = 29670
    _globals["_GLOBALSETTINGS"]._serialized_start = 29673
    _globals["_GLOBALSETTINGS"]._serialized_end = 30488
    _globals["_CONVERSATION"]._serialized_start = 30491
    _globals["_CONVERSATION"]._serialized_end = 31796
    _globals["_CONVERSATION_ENDOFHISTORYTRANSFERTYPE"]._serialized_start = 31608
    _globals["_CONVERSATION_ENDOFHISTORYTRANSFERTYPE"]._serialized_end = 31796
    _globals["_AVATARUSERSETTINGS"]._serialized_start = 31798
    _globals["_AVATARUSERSETTINGS"]._serialized_end = 31850
    _globals["_AUTODOWNLOADSETTINGS"]._serialized_start = 31852
    _globals["_AUTODOWNLOADSETTINGS"]._serialized_end = 31971
    _globals["_MSGROWOPAQUEDATA"]._serialized_start = 31973
    _globals["_MSGROWOPAQUEDATA"]._serialized_end = 32074
    _globals["_MSGOPAQUEDATA"]._serialized_start = 32077
    _globals["_MSGOPAQUEDATA"]._serialized_end = 32768
    _globals["_MSGOPAQUEDATA_POLLOPTION"]._serialized_start = 32742
    _globals["_MSGOPAQUEDATA_POLLOPTION"]._serialized_end = 32768
    _globals["_SERVERERRORRECEIPT"]._serialized_start = 32770
    _globals["_SERVERERRORRECEIPT"]._serialized_end = 32808
    _globals["_MEDIARETRYNOTIFICATION"]._serialized_start = 32811
    _globals["_MEDIARETRYNOTIFICATION"]._serialized_end = 33014
    _globals["_MEDIARETRYNOTIFICATION_RESULTTYPE"]._serialized_start = 32933
    _globals["_MEDIARETRYNOTIFICATION_RESULTTYPE"]._serialized_end = 33014
    _globals["_MESSAGEKEY"]._serialized_start = 33016
    _globals["_MESSAGEKEY"]._serialized_end = 33096
    _globals["_SYNCDVERSION"]._serialized_start = 33098
    _globals["_SYNCDVERSION"]._serialized_end = 33129
    _globals["_SYNCDVALUE"]._serialized_start = 33131
    _globals["_SYNCDVALUE"]._serialized_end = 33157
    _globals["_SYNCDSNAPSHOT"]._serialized_start = 33160
    _globals["_SYNCDSNAPSHOT"]._serialized_end = 33292
    _globals["_SYNCDRECORD"]._serialized_start = 33294
    _globals["_SYNCDRECORD"]._serialized_end = 33404
    _globals["_SYNCDPATCH"]._serialized_start = 33407
    _globals["_SYNCDPATCH"]._serialized_end = 33679
    _globals["_SYNCDMUTATIONS"]._serialized_start = 33681
    _globals["_SYNCDMUTATIONS"]._serialized_end = 33738
    _globals["_SYNCDMUTATION"]._serialized_start = 33741
    _globals["_SYNCDMUTATION"]._serialized_end = 33887
    _globals["_SYNCDMUTATION_SYNCDOPERATION"]._serialized_start = 33850
    _globals["_SYNCDMUTATION_SYNCDOPERATION"]._serialized_end = 33887
    _globals["_SYNCDINDEX"]._serialized_start = 33889
    _globals["_SYNCDINDEX"]._serialized_end = 33915
    _globals["_KEYID"]._serialized_start = 33917
    _globals["_KEYID"]._serialized_end = 33936
    _globals["_EXTERNALBLOBREFERENCE"]._serialized_start = 33939
    _globals["_EXTERNALBLOBREFERENCE"]._serialized_end = 34082
    _globals["_EXITCODE"]._serialized_start = 34084
    _globals["_EXITCODE"]._serialized_end = 34122
    _globals["_SYNCACTIONVALUE"]._serialized_start = 34125
    _globals["_SYNCACTIONVALUE"]._serialized_end = 36098
    _globals["_USERSTATUSMUTEACTION"]._serialized_start = 36100
    _globals["_USERSTATUSMUTEACTION"]._serialized_end = 36137
    _globals["_UNARCHIVECHATSSETTING"]._serialized_start = 36139
    _globals["_UNARCHIVECHATSSETTING"]._serialized_end = 36186
    _globals["_TIMEFORMATACTION"]._serialized_start = 36188
    _globals["_TIMEFORMATACTION"]._serialized_end = 36245
    _globals["_SYNCACTIONMESSAGE"]._serialized_start = 36247
    _globals["_SYNCACTIONMESSAGE"]._serialized_end = 36317
    _globals["_SYNCACTIONMESSAGERANGE"]._serialized_start = 36320
    _globals["_SYNCACTIONMESSAGERANGE"]._serialized_end = 36454
    _globals["_SUBSCRIPTIONACTION"]._serialized_start = 36456
    _globals["_SUBSCRIPTIONACTION"]._serialized_end = 36547
    _globals["_STICKERACTION"]._serialized_start = 36550
    _globals["_STICKERACTION"]._serialized_end = 36750
    _globals["_STARACTION"]._serialized_start = 36752
    _globals["_STARACTION"]._serialized_end = 36781
    _globals["_SECURITYNOTIFICATIONSETTING"]._serialized_start = 36783
    _globals["_SECURITYNOTIFICATIONSETTING"]._serialized_end = 36838
    _globals["_REMOVERECENTSTICKERACTION"]._serialized_start = 36840
    _globals["_REMOVERECENTSTICKERACTION"]._serialized_end = 36894
    _globals["_RECENTEMOJIWEIGHTSACTION"]._serialized_start = 36896
    _globals["_RECENTEMOJIWEIGHTSACTION"]._serialized_end = 36965
    _globals["_QUICKREPLYACTION"]._serialized_start = 36967
    _globals["_QUICKREPLYACTION"]._serialized_end = 37070
    _globals["_PUSHNAMESETTING"]._serialized_start = 37072
    _globals["_PUSHNAMESETTING"]._serialized_end = 37103
    _globals["_PRIVACYSETTINGRELAYALLCALLS"]._serialized_start = 37105
    _globals["_PRIVACYSETTINGRELAYALLCALLS"]._serialized_end = 37153
    _globals["_PRIMARYVERSIONACTION"]._serialized_start = 37155
    _globals["_PRIMARYVERSIONACTION"]._serialized_end = 37194
    _globals["_PRIMARYFEATURE"]._serialized_start = 37196
    _globals["_PRIMARYFEATURE"]._serialized_end = 37227
    _globals["_PNFORLIDCHATACTION"]._serialized_start = 37229
    _globals["_PNFORLIDCHATACTION"]._serialized_end = 37264
    _globals["_PINACTION"]._serialized_start = 37266
    _globals["_PINACTION"]._serialized_end = 37293
    _globals["_NUXACTION"]._serialized_start = 37295
    _globals["_NUXACTION"]._serialized_end = 37328
    _globals["_MUTEACTION"]._serialized_start = 37330
    _globals["_MUTEACTION"]._serialized_end = 37402
    _globals["_MARKETINGMESSAGEBROADCASTACTION"]._serialized_start = 37404
    _globals["_MARKETINGMESSAGEBROADCASTACTION"]._serialized_end = 37459
    _globals["_MARKETINGMESSAGEACTION"]._serialized_start = 37462
    _globals["_MARKETINGMESSAGEACTION"]._serialized_end = 37718
    _globals[
        "_MARKETINGMESSAGEACTION_MARKETINGMESSAGEPROTOTYPETYPE"
    ]._serialized_start = 37669
    _globals[
        "_MARKETINGMESSAGEACTION_MARKETINGMESSAGEPROTOTYPETYPE"
    ]._serialized_end = 37718
    _globals["_MARKCHATASREADACTION"]._serialized_start = 37720
    _globals["_MARKCHATASREADACTION"]._serialized_end = 37809
    _globals["_LOCALESETTING"]._serialized_start = 37811
    _globals["_LOCALESETTING"]._serialized_end = 37842
    _globals["_LABELEDITACTION"]._serialized_start = 37844
    _globals["_LABELEDITACTION"]._serialized_end = 37929
    _globals["_LABELASSOCIATIONACTION"]._serialized_start = 37931
    _globals["_LABELASSOCIATIONACTION"]._serialized_end = 37972
    _globals["_KEYEXPIRATION"]._serialized_start = 37974
    _globals["_KEYEXPIRATION"]._serialized_end = 38014
    _globals["_EXTERNALWEBBETAACTION"]._serialized_start = 38016
    _globals["_EXTERNALWEBBETAACTION"]._serialized_end = 38056
    _globals["_DELETEMESSAGEFORMEACTION"]._serialized_start = 38058
    _globals["_DELETEMESSAGEFORMEACTION"]._serialized_end = 38131
    _globals["_DELETECHATACTION"]._serialized_start = 38133
    _globals["_DELETECHATACTION"]._serialized_end = 38204
    _globals["_CONTACTACTION"]._serialized_start = 38206
    _globals["_CONTACTACTION"]._serialized_end = 38274
    _globals["_CLEARCHATACTION"]._serialized_start = 38276
    _globals["_CLEARCHATACTION"]._serialized_end = 38346
    _globals["_CHATASSIGNMENTOPENEDSTATUSACTION"]._serialized_start = 38348
    _globals["_CHATASSIGNMENTOPENEDSTATUSACTION"]._serialized_end = 38402
    _globals["_CHATASSIGNMENTACTION"]._serialized_start = 38404
    _globals["_CHATASSIGNMENTACTION"]._serialized_end = 38449
    _globals["_ARCHIVECHATACTION"]._serialized_start = 38451
    _globals["_ARCHIVECHATACTION"]._serialized_end = 38541
    _globals["_ANDROIDUNSUPPORTEDACTIONS"]._serialized_start = 38543
    _globals["_ANDROIDUNSUPPORTEDACTIONS"]._serialized_end = 38587
    _globals["_AGENTACTION"]._serialized_start = 38589
    _globals["_AGENTACTION"]._serialized_end = 38653
    _globals["_SYNCACTIONDATA"]._serialized_start = 38655
    _globals["_SYNCACTIONDATA"]._serialized_end = 38759
    _globals["_RECENTEMOJIWEIGHT"]._serialized_start = 38761
    _globals["_RECENTEMOJIWEIGHT"]._serialized_end = 38811
    _globals["_VERIFIEDNAMECERTIFICATE"]._serialized_start = 38814
    _globals["_VERIFIEDNAMECERTIFICATE"]._serialized_end = 39031
    _globals["_VERIFIEDNAMECERTIFICATE_DETAILS"]._serialized_start = 38903
    _globals["_VERIFIEDNAMECERTIFICATE_DETAILS"]._serialized_end = 39031
    _globals["_LOCALIZEDNAME"]._serialized_start = 39033
    _globals["_LOCALIZEDNAME"]._serialized_end = 39094
    _globals["_BIZIDENTITYINFO"]._serialized_start = 39097
    _globals["_BIZIDENTITYINFO"]._serialized_end = 39571
    _globals["_BIZIDENTITYINFO_VERIFIEDLEVELVALUE"]._serialized_start = 39431
    _globals["_BIZIDENTITYINFO_VERIFIEDLEVELVALUE"]._serialized_end = 39483
    _globals["_BIZIDENTITYINFO_HOSTSTORAGETYPE"]._serialized_start = 39485
    _globals["_BIZIDENTITYINFO_HOSTSTORAGETYPE"]._serialized_end = 39532
    _globals["_BIZIDENTITYINFO_ACTUALACTORSTYPE"]._serialized_start = 39534
    _globals["_BIZIDENTITYINFO_ACTUALACTORSTYPE"]._serialized_end = 39571
    _globals["_BIZACCOUNTPAYLOAD"]._serialized_start = 39573
    _globals["_BIZACCOUNTPAYLOAD"]._serialized_end = 39668
    _globals["_BIZACCOUNTLINKINFO"]._serialized_start = 39671
    _globals["_BIZACCOUNTLINKINFO"]._serialized_end = 39971
    _globals["_BIZACCOUNTLINKINFO_HOSTSTORAGETYPE"]._serialized_start = 39485
    _globals["_BIZACCOUNTLINKINFO_HOSTSTORAGETYPE"]._serialized_end = 39532
    _globals["_BIZACCOUNTLINKINFO_ACCOUNTTYPE"]._serialized_start = 39942
    _globals["_BIZACCOUNTLINKINFO_ACCOUNTTYPE"]._serialized_end = 39971
    _globals["_HANDSHAKEMESSAGE"]._serialized_start = 39974
    _globals["_HANDSHAKEMESSAGE"]._serialized_end = 40144
    _globals["_HANDSHAKESERVERHELLO"]._serialized_start = 40146
    _globals["_HANDSHAKESERVERHELLO"]._serialized_end = 40220
    _globals["_HANDSHAKECLIENTHELLO"]._serialized_start = 40222
    _globals["_HANDSHAKECLIENTHELLO"]._serialized_end = 40296
    _globals["_HANDSHAKECLIENTFINISH"]._serialized_start = 40298
    _globals["_HANDSHAKECLIENTFINISH"]._serialized_end = 40354
    _globals["_CLIENTPAYLOAD"]._serialized_start = 40357
    _globals["_CLIENTPAYLOAD"]._serialized_end = 43897
    _globals["_CLIENTPAYLOAD_WEBINFO"]._serialized_start = 41207
    _globals["_CLIENTPAYLOAD_WEBINFO"]._serialized_end = 41789
    _globals["_CLIENTPAYLOAD_WEBINFO_WEBDPAYLOAD"]._serialized_start = 41386
    _globals["_CLIENTPAYLOAD_WEBINFO_WEBDPAYLOAD"]._serialized_end = 41701
    _globals["_CLIENTPAYLOAD_WEBINFO_WEBSUBPLATFORM"]._serialized_start = 41703
    _globals["_CLIENTPAYLOAD_WEBINFO_WEBSUBPLATFORM"]._serialized_end = 41789
    _globals["_CLIENTPAYLOAD_USERAGENT"]._serialized_start = 41792
    _globals["_CLIENTPAYLOAD_USERAGENT"]._serialized_end = 42872
    _globals["_CLIENTPAYLOAD_USERAGENT_APPVERSION"]._serialized_start = 989
    _globals["_CLIENTPAYLOAD_USERAGENT_APPVERSION"]._serialized_end = 1092
    _globals["_CLIENTPAYLOAD_USERAGENT_RELEASECHANNEL"]._serialized_start = 42315
    _globals["_CLIENTPAYLOAD_USERAGENT_RELEASECHANNEL"]._serialized_end = 42376
    _globals["_CLIENTPAYLOAD_USERAGENT_PLATFORM"]._serialized_start = 42379
    _globals["_CLIENTPAYLOAD_USERAGENT_PLATFORM"]._serialized_end = 42872
    _globals["_CLIENTPAYLOAD_INTEROPDATA"]._serialized_start = 42874
    _globals["_CLIENTPAYLOAD_INTEROPDATA"]._serialized_end = 42943
    _globals["_CLIENTPAYLOAD_DEVICEPAIRINGREGISTRATIONDATA"]._serialized_start = 42946
    _globals["_CLIENTPAYLOAD_DEVICEPAIRINGREGISTRATIONDATA"]._serialized_end = 43120
    _globals["_CLIENTPAYLOAD_DNSSOURCE"]._serialized_start = 43123
    _globals["_CLIENTPAYLOAD_DNSSOURCE"]._serialized_end = 43314
    _globals["_CLIENTPAYLOAD_DNSSOURCE_DNSRESOLUTIONMETHOD"]._serialized_start = 43226
    _globals["_CLIENTPAYLOAD_DNSSOURCE_DNSRESOLUTIONMETHOD"]._serialized_end = 43314
    _globals["_CLIENTPAYLOAD_PRODUCT"]._serialized_start = 43316
    _globals["_CLIENTPAYLOAD_PRODUCT"]._serialized_end = 43367
    _globals["_CLIENTPAYLOAD_IOSAPPEXTENSION"]._serialized_start = 43369
    _globals["_CLIENTPAYLOAD_IOSAPPEXTENSION"]._serialized_end = 43453
    _globals["_CLIENTPAYLOAD_CONNECTTYPE"]._serialized_start = 43456
    _globals["_CLIENTPAYLOAD_CONNECTTYPE"]._serialized_end = 43760
    _globals["_CLIENTPAYLOAD_CONNECTREASON"]._serialized_start = 43763
    _globals["_CLIENTPAYLOAD_CONNECTREASON"]._serialized_end = 43897
    _globals["_WEBNOTIFICATIONSINFO"]._serialized_start = 43900
    _globals["_WEBNOTIFICATIONSINFO"]._serialized_end = 44037
    _globals["_WEBMESSAGEINFO"]._serialized_start = 44040
    _globals["_WEBMESSAGEINFO"]._serialized_end = 51713
    _globals["_WEBMESSAGEINFO_STUBTYPE"]._serialized_start = 45475
    _globals["_WEBMESSAGEINFO_STUBTYPE"]._serialized_end = 51560
    _globals["_WEBMESSAGEINFO_STATUS"]._serialized_start = 51562
    _globals["_WEBMESSAGEINFO_STATUS"]._serialized_end = 51650
    _globals["_WEBMESSAGEINFO_BIZPRIVACYSTATUS"]._serialized_start = 51652
    _globals["_WEBMESSAGEINFO_BIZPRIVACYSTATUS"]._serialized_end = 51713
    _globals["_WEBFEATURES"]._serialized_start = 51716
    _globals["_WEBFEATURES"]._serialized_end = 54111
    _globals["_WEBFEATURES_FLAG"]._serialized_start = 54036
    _globals["_WEBFEATURES_FLAG"]._serialized_end = 54111
    _globals["_USERRECEIPT"]._serialized_start = 54114
    _globals["_USERRECEIPT"]._serialized_end = 54272
    _globals["_STATUSPSA"]._serialized_start = 54274
    _globals["_STATUSPSA"]._serialized_end = 54342
    _globals["_REACTION"]._serialized_start = 54344
    _globals["_REACTION"]._serialized_end = 54464
    _globals["_POLLUPDATE"]._serialized_start = 54467
    _globals["_POLLUPDATE"]._serialized_end = 54636
    _globals["_POLLADDITIONALMETADATA"]._serialized_start = 54638
    _globals["_POLLADDITIONALMETADATA"]._serialized_end = 54687
    _globals["_PININCHAT"]._serialized_start = 54690
    _globals["_PININCHAT"]._serialized_end = 54951
    _globals["_PININCHAT_TYPE"]._serialized_start = 25984
    _globals["_PININCHAT_TYPE"]._serialized_end = 26044
    _globals["_PHOTOCHANGE"]._serialized_start = 54953
    _globals["_PHOTOCHANGE"]._serialized_end = 55022
    _globals["_PAYMENTINFO"]._serialized_start = 55025
    _globals["_PAYMENTINFO"]._serialized_end = 56390
    _globals["_PAYMENTINFO_TXNSTATUS"]._serialized_start = 55475
    _globals["_PAYMENTINFO_TXNSTATUS"]._serialized_end = 56140
    _globals["_PAYMENTINFO_STATUS"]._serialized_start = 56143
    _globals["_PAYMENTINFO_STATUS"]._serialized_end = 56347
    _globals["_PAYMENTINFO_CURRENCY"]._serialized_start = 56349
    _globals["_PAYMENTINFO_CURRENCY"]._serialized_end = 56390
    _globals["_NOTIFICATIONMESSAGEINFO"]._serialized_start = 56393
    _globals["_NOTIFICATIONMESSAGEINFO"]._serialized_end = 56530
    _globals["_MESSAGEADDONCONTEXTINFO"]._serialized_start = 56532
    _globals["_MESSAGEADDONCONTEXTINFO"]._serialized_end = 56593
    _globals["_MEDIADATA"]._serialized_start = 56595
    _globals["_MEDIADATA"]._serialized_end = 56625
    _globals["_KEEPINCHAT"]._serialized_start = 56628
    _globals["_KEEPINCHAT"]._serialized_end = 56805
    _globals["_NOISECERTIFICATE"]._serialized_start = 56808
    _globals["_NOISECERTIFICATE"]._serialized_end = 56952
    _globals["_NOISECERTIFICATE_DETAILS"]._serialized_start = 56864
    _globals["_NOISECERTIFICATE_DETAILS"]._serialized_end = 56952
    _globals["_CERTCHAIN"]._serialized_start = 56955
    _globals["_CERTCHAIN"]._serialized_end = 57228
    _globals["_CERTCHAIN_NOISECERTIFICATE"]._serialized_start = 57075
    _globals["_CERTCHAIN_NOISECERTIFICATE"]._serialized_end = 57228
    _globals["_CERTCHAIN_NOISECERTIFICATE_DETAILS"]._serialized_start = 57131
    _globals["_CERTCHAIN_NOISECERTIFICATE_DETAILS"]._serialized_end = 57228
