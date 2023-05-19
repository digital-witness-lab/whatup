// Code generated by protoc-gen-go. DO NOT EDIT.
// versions:
// 	protoc-gen-go v1.28.1
// 	protoc        v3.6.1
// source: whatupcore.proto

package whatupcore

import (
	whatsappweb "github.com/digital-witness-lab/whatup/protos/whatsappweb"
	empty "github.com/golang/protobuf/ptypes/empty"
	timestamp "github.com/golang/protobuf/ptypes/timestamp"
	protoreflect "google.golang.org/protobuf/reflect/protoreflect"
	protoimpl "google.golang.org/protobuf/runtime/protoimpl"
	reflect "reflect"
	sync "sync"
)

const (
	// Verify that this generated code is sufficiently up-to-date.
	_ = protoimpl.EnforceVersion(20 - protoimpl.MinVersion)
	// Verify that runtime/protoimpl is sufficiently up-to-date.
	_ = protoimpl.EnforceVersion(protoimpl.MaxVersion - 20)
)

type MediaInfo_MediaType int32

const (
	MediaInfo_NONE  MediaInfo_MediaType = 0
	MediaInfo_IMAGE MediaInfo_MediaType = 1
	MediaInfo_VIDEO MediaInfo_MediaType = 2
)

// Enum value maps for MediaInfo_MediaType.
var (
	MediaInfo_MediaType_name = map[int32]string{
		0: "NONE",
		1: "IMAGE",
		2: "VIDEO",
	}
	MediaInfo_MediaType_value = map[string]int32{
		"NONE":  0,
		"IMAGE": 1,
		"VIDEO": 2,
	}
)

func (x MediaInfo_MediaType) Enum() *MediaInfo_MediaType {
	p := new(MediaInfo_MediaType)
	*p = x
	return p
}

func (x MediaInfo_MediaType) String() string {
	return protoimpl.X.EnumStringOf(x.Descriptor(), protoreflect.EnumNumber(x))
}

func (MediaInfo_MediaType) Descriptor() protoreflect.EnumDescriptor {
	return file_whatupcore_proto_enumTypes[0].Descriptor()
}

func (MediaInfo_MediaType) Type() protoreflect.EnumType {
	return &file_whatupcore_proto_enumTypes[0]
}

func (x MediaInfo_MediaType) Number() protoreflect.EnumNumber {
	return protoreflect.EnumNumber(x)
}

// Deprecated: Use MediaInfo_MediaType.Descriptor instead.
func (MediaInfo_MediaType) EnumDescriptor() ([]byte, []int) {
	return file_whatupcore_proto_rawDescGZIP(), []int{7, 0}
}

type JID struct {
	state         protoimpl.MessageState
	sizeCache     protoimpl.SizeCache
	unknownFields protoimpl.UnknownFields

	User   string `protobuf:"bytes,1,opt,name=user,proto3" json:"user,omitempty"`
	Agent  uint32 `protobuf:"varint,2,opt,name=agent,proto3" json:"agent,omitempty"`
	Device uint32 `protobuf:"varint,3,opt,name=device,proto3" json:"device,omitempty"`
	Server uint32 `protobuf:"varint,4,opt,name=server,proto3" json:"server,omitempty"`
	Ad     uint32 `protobuf:"varint,5,opt,name=ad,proto3" json:"ad,omitempty"`
}

func (x *JID) Reset() {
	*x = JID{}
	if protoimpl.UnsafeEnabled {
		mi := &file_whatupcore_proto_msgTypes[0]
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		ms.StoreMessageInfo(mi)
	}
}

func (x *JID) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*JID) ProtoMessage() {}

func (x *JID) ProtoReflect() protoreflect.Message {
	mi := &file_whatupcore_proto_msgTypes[0]
	if protoimpl.UnsafeEnabled && x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use JID.ProtoReflect.Descriptor instead.
func (*JID) Descriptor() ([]byte, []int) {
	return file_whatupcore_proto_rawDescGZIP(), []int{0}
}

func (x *JID) GetUser() string {
	if x != nil {
		return x.User
	}
	return ""
}

func (x *JID) GetAgent() uint32 {
	if x != nil {
		return x.Agent
	}
	return 0
}

func (x *JID) GetDevice() uint32 {
	if x != nil {
		return x.Device
	}
	return 0
}

func (x *JID) GetServer() uint32 {
	if x != nil {
		return x.Server
	}
	return 0
}

func (x *JID) GetAd() uint32 {
	if x != nil {
		return x.Ad
	}
	return 0
}

type ConnectionStatus struct {
	state         protoimpl.MessageState
	sizeCache     protoimpl.SizeCache
	unknownFields protoimpl.UnknownFields

	IsConnected bool                 `protobuf:"varint,1,opt,name=isConnected,proto3" json:"isConnected,omitempty"`
	IsLoggedIn  bool                 `protobuf:"varint,2,opt,name=isLoggedIn,proto3" json:"isLoggedIn,omitempty"`
	Timestamp   *timestamp.Timestamp `protobuf:"bytes,3,opt,name=timestamp,proto3" json:"timestamp,omitempty"`
}

func (x *ConnectionStatus) Reset() {
	*x = ConnectionStatus{}
	if protoimpl.UnsafeEnabled {
		mi := &file_whatupcore_proto_msgTypes[1]
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		ms.StoreMessageInfo(mi)
	}
}

func (x *ConnectionStatus) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*ConnectionStatus) ProtoMessage() {}

func (x *ConnectionStatus) ProtoReflect() protoreflect.Message {
	mi := &file_whatupcore_proto_msgTypes[1]
	if protoimpl.UnsafeEnabled && x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use ConnectionStatus.ProtoReflect.Descriptor instead.
func (*ConnectionStatus) Descriptor() ([]byte, []int) {
	return file_whatupcore_proto_rawDescGZIP(), []int{1}
}

func (x *ConnectionStatus) GetIsConnected() bool {
	if x != nil {
		return x.IsConnected
	}
	return false
}

func (x *ConnectionStatus) GetIsLoggedIn() bool {
	if x != nil {
		return x.IsLoggedIn
	}
	return false
}

func (x *ConnectionStatus) GetTimestamp() *timestamp.Timestamp {
	if x != nil {
		return x.Timestamp
	}
	return nil
}

type Message struct {
	state         protoimpl.MessageState
	sizeCache     protoimpl.SizeCache
	unknownFields protoimpl.UnknownFields

	Info              *MessageInfo         `protobuf:"bytes,1,opt,name=info,proto3" json:"info,omitempty"`
	Content           *MessageContent      `protobuf:"bytes,2,opt,name=content,proto3" json:"content,omitempty"`
	MessageProperties *MessageProperties   `protobuf:"bytes,3,opt,name=messageProperties,proto3" json:"messageProperties,omitempty"`
	OriginalMessage   *whatsappweb.Message `protobuf:"bytes,4,opt,name=originalMessage,proto3" json:"originalMessage,omitempty"`
}

func (x *Message) Reset() {
	*x = Message{}
	if protoimpl.UnsafeEnabled {
		mi := &file_whatupcore_proto_msgTypes[2]
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		ms.StoreMessageInfo(mi)
	}
}

func (x *Message) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*Message) ProtoMessage() {}

func (x *Message) ProtoReflect() protoreflect.Message {
	mi := &file_whatupcore_proto_msgTypes[2]
	if protoimpl.UnsafeEnabled && x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use Message.ProtoReflect.Descriptor instead.
func (*Message) Descriptor() ([]byte, []int) {
	return file_whatupcore_proto_rawDescGZIP(), []int{2}
}

func (x *Message) GetInfo() *MessageInfo {
	if x != nil {
		return x.Info
	}
	return nil
}

func (x *Message) GetContent() *MessageContent {
	if x != nil {
		return x.Content
	}
	return nil
}

func (x *Message) GetMessageProperties() *MessageProperties {
	if x != nil {
		return x.MessageProperties
	}
	return nil
}

func (x *Message) GetOriginalMessage() *whatsappweb.Message {
	if x != nil {
		return x.OriginalMessage
	}
	return nil
}

type MessageSource struct {
	state         protoimpl.MessageState
	sizeCache     protoimpl.SizeCache
	unknownFields protoimpl.UnknownFields

	Chat               *JID `protobuf:"bytes,1,opt,name=chat,proto3" json:"chat,omitempty"`
	Sender             *JID `protobuf:"bytes,2,opt,name=sender,proto3" json:"sender,omitempty"`
	BroadcastListOwner *JID `protobuf:"bytes,3,opt,name=broadcastListOwner,proto3" json:"broadcastListOwner,omitempty"`
	IsFromMe           bool `protobuf:"varint,4,opt,name=isFromMe,proto3" json:"isFromMe,omitempty"`
	IsGroup            bool `protobuf:"varint,5,opt,name=isGroup,proto3" json:"isGroup,omitempty"`
}

func (x *MessageSource) Reset() {
	*x = MessageSource{}
	if protoimpl.UnsafeEnabled {
		mi := &file_whatupcore_proto_msgTypes[3]
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		ms.StoreMessageInfo(mi)
	}
}

func (x *MessageSource) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*MessageSource) ProtoMessage() {}

func (x *MessageSource) ProtoReflect() protoreflect.Message {
	mi := &file_whatupcore_proto_msgTypes[3]
	if protoimpl.UnsafeEnabled && x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use MessageSource.ProtoReflect.Descriptor instead.
func (*MessageSource) Descriptor() ([]byte, []int) {
	return file_whatupcore_proto_rawDescGZIP(), []int{3}
}

func (x *MessageSource) GetChat() *JID {
	if x != nil {
		return x.Chat
	}
	return nil
}

func (x *MessageSource) GetSender() *JID {
	if x != nil {
		return x.Sender
	}
	return nil
}

func (x *MessageSource) GetBroadcastListOwner() *JID {
	if x != nil {
		return x.BroadcastListOwner
	}
	return nil
}

func (x *MessageSource) GetIsFromMe() bool {
	if x != nil {
		return x.IsFromMe
	}
	return false
}

func (x *MessageSource) GetIsGroup() bool {
	if x != nil {
		return x.IsGroup
	}
	return false
}

type MessageInfo struct {
	state         protoimpl.MessageState
	sizeCache     protoimpl.SizeCache
	unknownFields protoimpl.UnknownFields

	Source    *MessageSource       `protobuf:"bytes,1,opt,name=source,proto3" json:"source,omitempty"`
	Timestamp *timestamp.Timestamp `protobuf:"bytes,2,opt,name=timestamp,proto3" json:"timestamp,omitempty"`
	Id        string               `protobuf:"bytes,3,opt,name=id,proto3" json:"id,omitempty"`
	PushName  string               `protobuf:"bytes,4,opt,name=pushName,proto3" json:"pushName,omitempty"`
	Type      string               `protobuf:"bytes,5,opt,name=type,proto3" json:"type,omitempty"`         // TODO: turn into enum!
	Category  string               `protobuf:"bytes,6,opt,name=category,proto3" json:"category,omitempty"` // TODO: turn into enum!
	Multicast bool                 `protobuf:"varint,7,opt,name=multicast,proto3" json:"multicast,omitempty"`
}

func (x *MessageInfo) Reset() {
	*x = MessageInfo{}
	if protoimpl.UnsafeEnabled {
		mi := &file_whatupcore_proto_msgTypes[4]
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		ms.StoreMessageInfo(mi)
	}
}

func (x *MessageInfo) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*MessageInfo) ProtoMessage() {}

func (x *MessageInfo) ProtoReflect() protoreflect.Message {
	mi := &file_whatupcore_proto_msgTypes[4]
	if protoimpl.UnsafeEnabled && x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use MessageInfo.ProtoReflect.Descriptor instead.
func (*MessageInfo) Descriptor() ([]byte, []int) {
	return file_whatupcore_proto_rawDescGZIP(), []int{4}
}

func (x *MessageInfo) GetSource() *MessageSource {
	if x != nil {
		return x.Source
	}
	return nil
}

func (x *MessageInfo) GetTimestamp() *timestamp.Timestamp {
	if x != nil {
		return x.Timestamp
	}
	return nil
}

func (x *MessageInfo) GetId() string {
	if x != nil {
		return x.Id
	}
	return ""
}

func (x *MessageInfo) GetPushName() string {
	if x != nil {
		return x.PushName
	}
	return ""
}

func (x *MessageInfo) GetType() string {
	if x != nil {
		return x.Type
	}
	return ""
}

func (x *MessageInfo) GetCategory() string {
	if x != nil {
		return x.Category
	}
	return ""
}

func (x *MessageInfo) GetMulticast() bool {
	if x != nil {
		return x.Multicast
	}
	return false
}

type MessageContent struct {
	state         protoimpl.MessageState
	sizeCache     protoimpl.SizeCache
	unknownFields protoimpl.UnknownFields

	Title      string            `protobuf:"bytes,1,opt,name=title,proto3" json:"title,omitempty"`
	Text       string            `protobuf:"bytes,2,opt,name=text,proto3" json:"text,omitempty"`
	Properties map[string]string `protobuf:"bytes,3,rep,name=properties,proto3" json:"properties,omitempty" protobuf_key:"bytes,1,opt,name=key,proto3" protobuf_val:"bytes,2,opt,name=value,proto3"`
	Thumbnail  []byte            `protobuf:"bytes,4,opt,name=thumbnail,proto3" json:"thumbnail,omitempty"`
	MediaInfo  *MediaInfo        `protobuf:"bytes,5,opt,name=mediaInfo,proto3" json:"mediaInfo,omitempty"`
}

func (x *MessageContent) Reset() {
	*x = MessageContent{}
	if protoimpl.UnsafeEnabled {
		mi := &file_whatupcore_proto_msgTypes[5]
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		ms.StoreMessageInfo(mi)
	}
}

func (x *MessageContent) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*MessageContent) ProtoMessage() {}

func (x *MessageContent) ProtoReflect() protoreflect.Message {
	mi := &file_whatupcore_proto_msgTypes[5]
	if protoimpl.UnsafeEnabled && x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use MessageContent.ProtoReflect.Descriptor instead.
func (*MessageContent) Descriptor() ([]byte, []int) {
	return file_whatupcore_proto_rawDescGZIP(), []int{5}
}

func (x *MessageContent) GetTitle() string {
	if x != nil {
		return x.Title
	}
	return ""
}

func (x *MessageContent) GetText() string {
	if x != nil {
		return x.Text
	}
	return ""
}

func (x *MessageContent) GetProperties() map[string]string {
	if x != nil {
		return x.Properties
	}
	return nil
}

func (x *MessageContent) GetThumbnail() []byte {
	if x != nil {
		return x.Thumbnail
	}
	return nil
}

func (x *MessageContent) GetMediaInfo() *MediaInfo {
	if x != nil {
		return x.MediaInfo
	}
	return nil
}

type MessageProperties struct {
	state         protoimpl.MessageState
	sizeCache     protoimpl.SizeCache
	unknownFields protoimpl.UnknownFields

	IsEphemeral           bool   `protobuf:"varint,1,opt,name=isEphemeral,proto3" json:"isEphemeral,omitempty"`
	IsViewOnce            bool   `protobuf:"varint,2,opt,name=isViewOnce,proto3" json:"isViewOnce,omitempty"`
	IsDocumentWithCaption bool   `protobuf:"varint,3,opt,name=isDocumentWithCaption,proto3" json:"isDocumentWithCaption,omitempty"`
	IsEdit                bool   `protobuf:"varint,4,opt,name=isEdit,proto3" json:"isEdit,omitempty"`
	ForwardedScore        uint32 `protobuf:"varint,5,opt,name=forwardedScore,proto3" json:"forwardedScore,omitempty"`
}

func (x *MessageProperties) Reset() {
	*x = MessageProperties{}
	if protoimpl.UnsafeEnabled {
		mi := &file_whatupcore_proto_msgTypes[6]
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		ms.StoreMessageInfo(mi)
	}
}

func (x *MessageProperties) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*MessageProperties) ProtoMessage() {}

func (x *MessageProperties) ProtoReflect() protoreflect.Message {
	mi := &file_whatupcore_proto_msgTypes[6]
	if protoimpl.UnsafeEnabled && x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use MessageProperties.ProtoReflect.Descriptor instead.
func (*MessageProperties) Descriptor() ([]byte, []int) {
	return file_whatupcore_proto_rawDescGZIP(), []int{6}
}

func (x *MessageProperties) GetIsEphemeral() bool {
	if x != nil {
		return x.IsEphemeral
	}
	return false
}

func (x *MessageProperties) GetIsViewOnce() bool {
	if x != nil {
		return x.IsViewOnce
	}
	return false
}

func (x *MessageProperties) GetIsDocumentWithCaption() bool {
	if x != nil {
		return x.IsDocumentWithCaption
	}
	return false
}

func (x *MessageProperties) GetIsEdit() bool {
	if x != nil {
		return x.IsEdit
	}
	return false
}

func (x *MessageProperties) GetForwardedScore() uint32 {
	if x != nil {
		return x.ForwardedScore
	}
	return 0
}

type MediaInfo struct {
	state         protoimpl.MessageState
	sizeCache     protoimpl.SizeCache
	unknownFields protoimpl.UnknownFields

	Locator   map[string][]byte   `protobuf:"bytes,1,rep,name=locator,proto3" json:"locator,omitempty" protobuf_key:"bytes,1,opt,name=key,proto3" protobuf_val:"bytes,2,opt,name=value,proto3"`
	MediaType MediaInfo_MediaType `protobuf:"varint,3,opt,name=mediaType,proto3,enum=whatup.MediaInfo_MediaType" json:"mediaType,omitempty"`
	MimeType  string              `protobuf:"bytes,4,opt,name=mimeType,proto3" json:"mimeType,omitempty"`
}

func (x *MediaInfo) Reset() {
	*x = MediaInfo{}
	if protoimpl.UnsafeEnabled {
		mi := &file_whatupcore_proto_msgTypes[7]
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		ms.StoreMessageInfo(mi)
	}
}

func (x *MediaInfo) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*MediaInfo) ProtoMessage() {}

func (x *MediaInfo) ProtoReflect() protoreflect.Message {
	mi := &file_whatupcore_proto_msgTypes[7]
	if protoimpl.UnsafeEnabled && x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use MediaInfo.ProtoReflect.Descriptor instead.
func (*MediaInfo) Descriptor() ([]byte, []int) {
	return file_whatupcore_proto_rawDescGZIP(), []int{7}
}

func (x *MediaInfo) GetLocator() map[string][]byte {
	if x != nil {
		return x.Locator
	}
	return nil
}

func (x *MediaInfo) GetMediaType() MediaInfo_MediaType {
	if x != nil {
		return x.MediaType
	}
	return MediaInfo_NONE
}

func (x *MediaInfo) GetMimeType() string {
	if x != nil {
		return x.MimeType
	}
	return ""
}

type Media struct {
	state         protoimpl.MessageState
	sizeCache     protoimpl.SizeCache
	unknownFields protoimpl.UnknownFields

	Contents []byte `protobuf:"bytes,1,opt,name=Contents,proto3" json:"Contents,omitempty"`
}

func (x *Media) Reset() {
	*x = Media{}
	if protoimpl.UnsafeEnabled {
		mi := &file_whatupcore_proto_msgTypes[8]
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		ms.StoreMessageInfo(mi)
	}
}

func (x *Media) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*Media) ProtoMessage() {}

func (x *Media) ProtoReflect() protoreflect.Message {
	mi := &file_whatupcore_proto_msgTypes[8]
	if protoimpl.UnsafeEnabled && x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use Media.ProtoReflect.Descriptor instead.
func (*Media) Descriptor() ([]byte, []int) {
	return file_whatupcore_proto_rawDescGZIP(), []int{8}
}

func (x *Media) GetContents() []byte {
	if x != nil {
		return x.Contents
	}
	return nil
}

var File_whatupcore_proto protoreflect.FileDescriptor

var file_whatupcore_proto_rawDesc = []byte{
	0x0a, 0x10, 0x77, 0x68, 0x61, 0x74, 0x75, 0x70, 0x63, 0x6f, 0x72, 0x65, 0x2e, 0x70, 0x72, 0x6f,
	0x74, 0x6f, 0x12, 0x06, 0x77, 0x68, 0x61, 0x74, 0x75, 0x70, 0x1a, 0x1f, 0x67, 0x6f, 0x6f, 0x67,
	0x6c, 0x65, 0x2f, 0x70, 0x72, 0x6f, 0x74, 0x6f, 0x62, 0x75, 0x66, 0x2f, 0x74, 0x69, 0x6d, 0x65,
	0x73, 0x74, 0x61, 0x6d, 0x70, 0x2e, 0x70, 0x72, 0x6f, 0x74, 0x6f, 0x1a, 0x1b, 0x67, 0x6f, 0x6f,
	0x67, 0x6c, 0x65, 0x2f, 0x70, 0x72, 0x6f, 0x74, 0x6f, 0x62, 0x75, 0x66, 0x2f, 0x65, 0x6d, 0x70,
	0x74, 0x79, 0x2e, 0x70, 0x72, 0x6f, 0x74, 0x6f, 0x1a, 0x11, 0x77, 0x68, 0x61, 0x74, 0x73, 0x61,
	0x70, 0x70, 0x77, 0x65, 0x62, 0x2e, 0x70, 0x72, 0x6f, 0x74, 0x6f, 0x22, 0x6f, 0x0a, 0x03, 0x4a,
	0x49, 0x44, 0x12, 0x12, 0x0a, 0x04, 0x75, 0x73, 0x65, 0x72, 0x18, 0x01, 0x20, 0x01, 0x28, 0x09,
	0x52, 0x04, 0x75, 0x73, 0x65, 0x72, 0x12, 0x14, 0x0a, 0x05, 0x61, 0x67, 0x65, 0x6e, 0x74, 0x18,
	0x02, 0x20, 0x01, 0x28, 0x0d, 0x52, 0x05, 0x61, 0x67, 0x65, 0x6e, 0x74, 0x12, 0x16, 0x0a, 0x06,
	0x64, 0x65, 0x76, 0x69, 0x63, 0x65, 0x18, 0x03, 0x20, 0x01, 0x28, 0x0d, 0x52, 0x06, 0x64, 0x65,
	0x76, 0x69, 0x63, 0x65, 0x12, 0x16, 0x0a, 0x06, 0x73, 0x65, 0x72, 0x76, 0x65, 0x72, 0x18, 0x04,
	0x20, 0x01, 0x28, 0x0d, 0x52, 0x06, 0x73, 0x65, 0x72, 0x76, 0x65, 0x72, 0x12, 0x0e, 0x0a, 0x02,
	0x61, 0x64, 0x18, 0x05, 0x20, 0x01, 0x28, 0x0d, 0x52, 0x02, 0x61, 0x64, 0x22, 0x8e, 0x01, 0x0a,
	0x10, 0x43, 0x6f, 0x6e, 0x6e, 0x65, 0x63, 0x74, 0x69, 0x6f, 0x6e, 0x53, 0x74, 0x61, 0x74, 0x75,
	0x73, 0x12, 0x20, 0x0a, 0x0b, 0x69, 0x73, 0x43, 0x6f, 0x6e, 0x6e, 0x65, 0x63, 0x74, 0x65, 0x64,
	0x18, 0x01, 0x20, 0x01, 0x28, 0x08, 0x52, 0x0b, 0x69, 0x73, 0x43, 0x6f, 0x6e, 0x6e, 0x65, 0x63,
	0x74, 0x65, 0x64, 0x12, 0x1e, 0x0a, 0x0a, 0x69, 0x73, 0x4c, 0x6f, 0x67, 0x67, 0x65, 0x64, 0x49,
	0x6e, 0x18, 0x02, 0x20, 0x01, 0x28, 0x08, 0x52, 0x0a, 0x69, 0x73, 0x4c, 0x6f, 0x67, 0x67, 0x65,
	0x64, 0x49, 0x6e, 0x12, 0x38, 0x0a, 0x09, 0x74, 0x69, 0x6d, 0x65, 0x73, 0x74, 0x61, 0x6d, 0x70,
	0x18, 0x03, 0x20, 0x01, 0x28, 0x0b, 0x32, 0x1a, 0x2e, 0x67, 0x6f, 0x6f, 0x67, 0x6c, 0x65, 0x2e,
	0x70, 0x72, 0x6f, 0x74, 0x6f, 0x62, 0x75, 0x66, 0x2e, 0x54, 0x69, 0x6d, 0x65, 0x73, 0x74, 0x61,
	0x6d, 0x70, 0x52, 0x09, 0x74, 0x69, 0x6d, 0x65, 0x73, 0x74, 0x61, 0x6d, 0x70, 0x22, 0xed, 0x01,
	0x0a, 0x07, 0x4d, 0x65, 0x73, 0x73, 0x61, 0x67, 0x65, 0x12, 0x27, 0x0a, 0x04, 0x69, 0x6e, 0x66,
	0x6f, 0x18, 0x01, 0x20, 0x01, 0x28, 0x0b, 0x32, 0x13, 0x2e, 0x77, 0x68, 0x61, 0x74, 0x75, 0x70,
	0x2e, 0x4d, 0x65, 0x73, 0x73, 0x61, 0x67, 0x65, 0x49, 0x6e, 0x66, 0x6f, 0x52, 0x04, 0x69, 0x6e,
	0x66, 0x6f, 0x12, 0x30, 0x0a, 0x07, 0x63, 0x6f, 0x6e, 0x74, 0x65, 0x6e, 0x74, 0x18, 0x02, 0x20,
	0x01, 0x28, 0x0b, 0x32, 0x16, 0x2e, 0x77, 0x68, 0x61, 0x74, 0x75, 0x70, 0x2e, 0x4d, 0x65, 0x73,
	0x73, 0x61, 0x67, 0x65, 0x43, 0x6f, 0x6e, 0x74, 0x65, 0x6e, 0x74, 0x52, 0x07, 0x63, 0x6f, 0x6e,
	0x74, 0x65, 0x6e, 0x74, 0x12, 0x47, 0x0a, 0x11, 0x6d, 0x65, 0x73, 0x73, 0x61, 0x67, 0x65, 0x50,
	0x72, 0x6f, 0x70, 0x65, 0x72, 0x74, 0x69, 0x65, 0x73, 0x18, 0x03, 0x20, 0x01, 0x28, 0x0b, 0x32,
	0x19, 0x2e, 0x77, 0x68, 0x61, 0x74, 0x75, 0x70, 0x2e, 0x4d, 0x65, 0x73, 0x73, 0x61, 0x67, 0x65,
	0x50, 0x72, 0x6f, 0x70, 0x65, 0x72, 0x74, 0x69, 0x65, 0x73, 0x52, 0x11, 0x6d, 0x65, 0x73, 0x73,
	0x61, 0x67, 0x65, 0x50, 0x72, 0x6f, 0x70, 0x65, 0x72, 0x74, 0x69, 0x65, 0x73, 0x12, 0x3e, 0x0a,
	0x0f, 0x6f, 0x72, 0x69, 0x67, 0x69, 0x6e, 0x61, 0x6c, 0x4d, 0x65, 0x73, 0x73, 0x61, 0x67, 0x65,
	0x18, 0x04, 0x20, 0x01, 0x28, 0x0b, 0x32, 0x14, 0x2e, 0x77, 0x68, 0x61, 0x74, 0x73, 0x61, 0x70,
	0x70, 0x77, 0x65, 0x62, 0x2e, 0x4d, 0x65, 0x73, 0x73, 0x61, 0x67, 0x65, 0x52, 0x0f, 0x6f, 0x72,
	0x69, 0x67, 0x69, 0x6e, 0x61, 0x6c, 0x4d, 0x65, 0x73, 0x73, 0x61, 0x67, 0x65, 0x22, 0xc8, 0x01,
	0x0a, 0x0d, 0x4d, 0x65, 0x73, 0x73, 0x61, 0x67, 0x65, 0x53, 0x6f, 0x75, 0x72, 0x63, 0x65, 0x12,
	0x1f, 0x0a, 0x04, 0x63, 0x68, 0x61, 0x74, 0x18, 0x01, 0x20, 0x01, 0x28, 0x0b, 0x32, 0x0b, 0x2e,
	0x77, 0x68, 0x61, 0x74, 0x75, 0x70, 0x2e, 0x4a, 0x49, 0x44, 0x52, 0x04, 0x63, 0x68, 0x61, 0x74,
	0x12, 0x23, 0x0a, 0x06, 0x73, 0x65, 0x6e, 0x64, 0x65, 0x72, 0x18, 0x02, 0x20, 0x01, 0x28, 0x0b,
	0x32, 0x0b, 0x2e, 0x77, 0x68, 0x61, 0x74, 0x75, 0x70, 0x2e, 0x4a, 0x49, 0x44, 0x52, 0x06, 0x73,
	0x65, 0x6e, 0x64, 0x65, 0x72, 0x12, 0x3b, 0x0a, 0x12, 0x62, 0x72, 0x6f, 0x61, 0x64, 0x63, 0x61,
	0x73, 0x74, 0x4c, 0x69, 0x73, 0x74, 0x4f, 0x77, 0x6e, 0x65, 0x72, 0x18, 0x03, 0x20, 0x01, 0x28,
	0x0b, 0x32, 0x0b, 0x2e, 0x77, 0x68, 0x61, 0x74, 0x75, 0x70, 0x2e, 0x4a, 0x49, 0x44, 0x52, 0x12,
	0x62, 0x72, 0x6f, 0x61, 0x64, 0x63, 0x61, 0x73, 0x74, 0x4c, 0x69, 0x73, 0x74, 0x4f, 0x77, 0x6e,
	0x65, 0x72, 0x12, 0x1a, 0x0a, 0x08, 0x69, 0x73, 0x46, 0x72, 0x6f, 0x6d, 0x4d, 0x65, 0x18, 0x04,
	0x20, 0x01, 0x28, 0x08, 0x52, 0x08, 0x69, 0x73, 0x46, 0x72, 0x6f, 0x6d, 0x4d, 0x65, 0x12, 0x18,
	0x0a, 0x07, 0x69, 0x73, 0x47, 0x72, 0x6f, 0x75, 0x70, 0x18, 0x05, 0x20, 0x01, 0x28, 0x08, 0x52,
	0x07, 0x69, 0x73, 0x47, 0x72, 0x6f, 0x75, 0x70, 0x22, 0xf0, 0x01, 0x0a, 0x0b, 0x4d, 0x65, 0x73,
	0x73, 0x61, 0x67, 0x65, 0x49, 0x6e, 0x66, 0x6f, 0x12, 0x2d, 0x0a, 0x06, 0x73, 0x6f, 0x75, 0x72,
	0x63, 0x65, 0x18, 0x01, 0x20, 0x01, 0x28, 0x0b, 0x32, 0x15, 0x2e, 0x77, 0x68, 0x61, 0x74, 0x75,
	0x70, 0x2e, 0x4d, 0x65, 0x73, 0x73, 0x61, 0x67, 0x65, 0x53, 0x6f, 0x75, 0x72, 0x63, 0x65, 0x52,
	0x06, 0x73, 0x6f, 0x75, 0x72, 0x63, 0x65, 0x12, 0x38, 0x0a, 0x09, 0x74, 0x69, 0x6d, 0x65, 0x73,
	0x74, 0x61, 0x6d, 0x70, 0x18, 0x02, 0x20, 0x01, 0x28, 0x0b, 0x32, 0x1a, 0x2e, 0x67, 0x6f, 0x6f,
	0x67, 0x6c, 0x65, 0x2e, 0x70, 0x72, 0x6f, 0x74, 0x6f, 0x62, 0x75, 0x66, 0x2e, 0x54, 0x69, 0x6d,
	0x65, 0x73, 0x74, 0x61, 0x6d, 0x70, 0x52, 0x09, 0x74, 0x69, 0x6d, 0x65, 0x73, 0x74, 0x61, 0x6d,
	0x70, 0x12, 0x0e, 0x0a, 0x02, 0x69, 0x64, 0x18, 0x03, 0x20, 0x01, 0x28, 0x09, 0x52, 0x02, 0x69,
	0x64, 0x12, 0x1a, 0x0a, 0x08, 0x70, 0x75, 0x73, 0x68, 0x4e, 0x61, 0x6d, 0x65, 0x18, 0x04, 0x20,
	0x01, 0x28, 0x09, 0x52, 0x08, 0x70, 0x75, 0x73, 0x68, 0x4e, 0x61, 0x6d, 0x65, 0x12, 0x12, 0x0a,
	0x04, 0x74, 0x79, 0x70, 0x65, 0x18, 0x05, 0x20, 0x01, 0x28, 0x09, 0x52, 0x04, 0x74, 0x79, 0x70,
	0x65, 0x12, 0x1a, 0x0a, 0x08, 0x63, 0x61, 0x74, 0x65, 0x67, 0x6f, 0x72, 0x79, 0x18, 0x06, 0x20,
	0x01, 0x28, 0x09, 0x52, 0x08, 0x63, 0x61, 0x74, 0x65, 0x67, 0x6f, 0x72, 0x79, 0x12, 0x1c, 0x0a,
	0x09, 0x6d, 0x75, 0x6c, 0x74, 0x69, 0x63, 0x61, 0x73, 0x74, 0x18, 0x07, 0x20, 0x01, 0x28, 0x08,
	0x52, 0x09, 0x6d, 0x75, 0x6c, 0x74, 0x69, 0x63, 0x61, 0x73, 0x74, 0x22, 0x90, 0x02, 0x0a, 0x0e,
	0x4d, 0x65, 0x73, 0x73, 0x61, 0x67, 0x65, 0x43, 0x6f, 0x6e, 0x74, 0x65, 0x6e, 0x74, 0x12, 0x14,
	0x0a, 0x05, 0x74, 0x69, 0x74, 0x6c, 0x65, 0x18, 0x01, 0x20, 0x01, 0x28, 0x09, 0x52, 0x05, 0x74,
	0x69, 0x74, 0x6c, 0x65, 0x12, 0x12, 0x0a, 0x04, 0x74, 0x65, 0x78, 0x74, 0x18, 0x02, 0x20, 0x01,
	0x28, 0x09, 0x52, 0x04, 0x74, 0x65, 0x78, 0x74, 0x12, 0x46, 0x0a, 0x0a, 0x70, 0x72, 0x6f, 0x70,
	0x65, 0x72, 0x74, 0x69, 0x65, 0x73, 0x18, 0x03, 0x20, 0x03, 0x28, 0x0b, 0x32, 0x26, 0x2e, 0x77,
	0x68, 0x61, 0x74, 0x75, 0x70, 0x2e, 0x4d, 0x65, 0x73, 0x73, 0x61, 0x67, 0x65, 0x43, 0x6f, 0x6e,
	0x74, 0x65, 0x6e, 0x74, 0x2e, 0x50, 0x72, 0x6f, 0x70, 0x65, 0x72, 0x74, 0x69, 0x65, 0x73, 0x45,
	0x6e, 0x74, 0x72, 0x79, 0x52, 0x0a, 0x70, 0x72, 0x6f, 0x70, 0x65, 0x72, 0x74, 0x69, 0x65, 0x73,
	0x12, 0x1c, 0x0a, 0x09, 0x74, 0x68, 0x75, 0x6d, 0x62, 0x6e, 0x61, 0x69, 0x6c, 0x18, 0x04, 0x20,
	0x01, 0x28, 0x0c, 0x52, 0x09, 0x74, 0x68, 0x75, 0x6d, 0x62, 0x6e, 0x61, 0x69, 0x6c, 0x12, 0x2f,
	0x0a, 0x09, 0x6d, 0x65, 0x64, 0x69, 0x61, 0x49, 0x6e, 0x66, 0x6f, 0x18, 0x05, 0x20, 0x01, 0x28,
	0x0b, 0x32, 0x11, 0x2e, 0x77, 0x68, 0x61, 0x74, 0x75, 0x70, 0x2e, 0x4d, 0x65, 0x64, 0x69, 0x61,
	0x49, 0x6e, 0x66, 0x6f, 0x52, 0x09, 0x6d, 0x65, 0x64, 0x69, 0x61, 0x49, 0x6e, 0x66, 0x6f, 0x1a,
	0x3d, 0x0a, 0x0f, 0x50, 0x72, 0x6f, 0x70, 0x65, 0x72, 0x74, 0x69, 0x65, 0x73, 0x45, 0x6e, 0x74,
	0x72, 0x79, 0x12, 0x10, 0x0a, 0x03, 0x6b, 0x65, 0x79, 0x18, 0x01, 0x20, 0x01, 0x28, 0x09, 0x52,
	0x03, 0x6b, 0x65, 0x79, 0x12, 0x14, 0x0a, 0x05, 0x76, 0x61, 0x6c, 0x75, 0x65, 0x18, 0x02, 0x20,
	0x01, 0x28, 0x09, 0x52, 0x05, 0x76, 0x61, 0x6c, 0x75, 0x65, 0x3a, 0x02, 0x38, 0x01, 0x22, 0xcb,
	0x01, 0x0a, 0x11, 0x4d, 0x65, 0x73, 0x73, 0x61, 0x67, 0x65, 0x50, 0x72, 0x6f, 0x70, 0x65, 0x72,
	0x74, 0x69, 0x65, 0x73, 0x12, 0x20, 0x0a, 0x0b, 0x69, 0x73, 0x45, 0x70, 0x68, 0x65, 0x6d, 0x65,
	0x72, 0x61, 0x6c, 0x18, 0x01, 0x20, 0x01, 0x28, 0x08, 0x52, 0x0b, 0x69, 0x73, 0x45, 0x70, 0x68,
	0x65, 0x6d, 0x65, 0x72, 0x61, 0x6c, 0x12, 0x1e, 0x0a, 0x0a, 0x69, 0x73, 0x56, 0x69, 0x65, 0x77,
	0x4f, 0x6e, 0x63, 0x65, 0x18, 0x02, 0x20, 0x01, 0x28, 0x08, 0x52, 0x0a, 0x69, 0x73, 0x56, 0x69,
	0x65, 0x77, 0x4f, 0x6e, 0x63, 0x65, 0x12, 0x34, 0x0a, 0x15, 0x69, 0x73, 0x44, 0x6f, 0x63, 0x75,
	0x6d, 0x65, 0x6e, 0x74, 0x57, 0x69, 0x74, 0x68, 0x43, 0x61, 0x70, 0x74, 0x69, 0x6f, 0x6e, 0x18,
	0x03, 0x20, 0x01, 0x28, 0x08, 0x52, 0x15, 0x69, 0x73, 0x44, 0x6f, 0x63, 0x75, 0x6d, 0x65, 0x6e,
	0x74, 0x57, 0x69, 0x74, 0x68, 0x43, 0x61, 0x70, 0x74, 0x69, 0x6f, 0x6e, 0x12, 0x16, 0x0a, 0x06,
	0x69, 0x73, 0x45, 0x64, 0x69, 0x74, 0x18, 0x04, 0x20, 0x01, 0x28, 0x08, 0x52, 0x06, 0x69, 0x73,
	0x45, 0x64, 0x69, 0x74, 0x12, 0x26, 0x0a, 0x0e, 0x66, 0x6f, 0x72, 0x77, 0x61, 0x72, 0x64, 0x65,
	0x64, 0x53, 0x63, 0x6f, 0x72, 0x65, 0x18, 0x05, 0x20, 0x01, 0x28, 0x0d, 0x52, 0x0e, 0x66, 0x6f,
	0x72, 0x77, 0x61, 0x72, 0x64, 0x65, 0x64, 0x53, 0x63, 0x6f, 0x72, 0x65, 0x22, 0x85, 0x02, 0x0a,
	0x09, 0x4d, 0x65, 0x64, 0x69, 0x61, 0x49, 0x6e, 0x66, 0x6f, 0x12, 0x38, 0x0a, 0x07, 0x6c, 0x6f,
	0x63, 0x61, 0x74, 0x6f, 0x72, 0x18, 0x01, 0x20, 0x03, 0x28, 0x0b, 0x32, 0x1e, 0x2e, 0x77, 0x68,
	0x61, 0x74, 0x75, 0x70, 0x2e, 0x4d, 0x65, 0x64, 0x69, 0x61, 0x49, 0x6e, 0x66, 0x6f, 0x2e, 0x4c,
	0x6f, 0x63, 0x61, 0x74, 0x6f, 0x72, 0x45, 0x6e, 0x74, 0x72, 0x79, 0x52, 0x07, 0x6c, 0x6f, 0x63,
	0x61, 0x74, 0x6f, 0x72, 0x12, 0x39, 0x0a, 0x09, 0x6d, 0x65, 0x64, 0x69, 0x61, 0x54, 0x79, 0x70,
	0x65, 0x18, 0x03, 0x20, 0x01, 0x28, 0x0e, 0x32, 0x1b, 0x2e, 0x77, 0x68, 0x61, 0x74, 0x75, 0x70,
	0x2e, 0x4d, 0x65, 0x64, 0x69, 0x61, 0x49, 0x6e, 0x66, 0x6f, 0x2e, 0x4d, 0x65, 0x64, 0x69, 0x61,
	0x54, 0x79, 0x70, 0x65, 0x52, 0x09, 0x6d, 0x65, 0x64, 0x69, 0x61, 0x54, 0x79, 0x70, 0x65, 0x12,
	0x1a, 0x0a, 0x08, 0x6d, 0x69, 0x6d, 0x65, 0x54, 0x79, 0x70, 0x65, 0x18, 0x04, 0x20, 0x01, 0x28,
	0x09, 0x52, 0x08, 0x6d, 0x69, 0x6d, 0x65, 0x54, 0x79, 0x70, 0x65, 0x1a, 0x3a, 0x0a, 0x0c, 0x4c,
	0x6f, 0x63, 0x61, 0x74, 0x6f, 0x72, 0x45, 0x6e, 0x74, 0x72, 0x79, 0x12, 0x10, 0x0a, 0x03, 0x6b,
	0x65, 0x79, 0x18, 0x01, 0x20, 0x01, 0x28, 0x09, 0x52, 0x03, 0x6b, 0x65, 0x79, 0x12, 0x14, 0x0a,
	0x05, 0x76, 0x61, 0x6c, 0x75, 0x65, 0x18, 0x02, 0x20, 0x01, 0x28, 0x0c, 0x52, 0x05, 0x76, 0x61,
	0x6c, 0x75, 0x65, 0x3a, 0x02, 0x38, 0x01, 0x22, 0x2b, 0x0a, 0x09, 0x4d, 0x65, 0x64, 0x69, 0x61,
	0x54, 0x79, 0x70, 0x65, 0x12, 0x08, 0x0a, 0x04, 0x4e, 0x4f, 0x4e, 0x45, 0x10, 0x00, 0x12, 0x09,
	0x0a, 0x05, 0x49, 0x4d, 0x41, 0x47, 0x45, 0x10, 0x01, 0x12, 0x09, 0x0a, 0x05, 0x56, 0x49, 0x44,
	0x45, 0x4f, 0x10, 0x02, 0x22, 0x23, 0x0a, 0x05, 0x4d, 0x65, 0x64, 0x69, 0x61, 0x12, 0x1a, 0x0a,
	0x08, 0x43, 0x6f, 0x6e, 0x74, 0x65, 0x6e, 0x74, 0x73, 0x18, 0x01, 0x20, 0x01, 0x28, 0x0c, 0x52,
	0x08, 0x43, 0x6f, 0x6e, 0x74, 0x65, 0x6e, 0x74, 0x73, 0x32, 0xc7, 0x01, 0x0a, 0x0a, 0x57, 0x68,
	0x61, 0x74, 0x55, 0x70, 0x43, 0x6f, 0x72, 0x65, 0x12, 0x49, 0x0a, 0x13, 0x47, 0x65, 0x74, 0x43,
	0x6f, 0x6e, 0x6e, 0x65, 0x63, 0x74, 0x69, 0x6f, 0x6e, 0x53, 0x74, 0x61, 0x74, 0x75, 0x73, 0x12,
	0x16, 0x2e, 0x67, 0x6f, 0x6f, 0x67, 0x6c, 0x65, 0x2e, 0x70, 0x72, 0x6f, 0x74, 0x6f, 0x62, 0x75,
	0x66, 0x2e, 0x45, 0x6d, 0x70, 0x74, 0x79, 0x1a, 0x18, 0x2e, 0x77, 0x68, 0x61, 0x74, 0x75, 0x70,
	0x2e, 0x43, 0x6f, 0x6e, 0x6e, 0x65, 0x63, 0x74, 0x69, 0x6f, 0x6e, 0x53, 0x74, 0x61, 0x74, 0x75,
	0x73, 0x22, 0x00, 0x12, 0x39, 0x0a, 0x0a, 0x47, 0x65, 0x74, 0x4d, 0x65, 0x73, 0x73, 0x61, 0x67,
	0x65, 0x12, 0x16, 0x2e, 0x67, 0x6f, 0x6f, 0x67, 0x6c, 0x65, 0x2e, 0x70, 0x72, 0x6f, 0x74, 0x6f,
	0x62, 0x75, 0x66, 0x2e, 0x45, 0x6d, 0x70, 0x74, 0x79, 0x1a, 0x0f, 0x2e, 0x77, 0x68, 0x61, 0x74,
	0x75, 0x70, 0x2e, 0x4d, 0x65, 0x73, 0x73, 0x61, 0x67, 0x65, 0x22, 0x00, 0x30, 0x01, 0x12, 0x33,
	0x0a, 0x0d, 0x44, 0x6f, 0x77, 0x6e, 0x6c, 0x6f, 0x61, 0x64, 0x4d, 0x65, 0x64, 0x69, 0x61, 0x12,
	0x11, 0x2e, 0x77, 0x68, 0x61, 0x74, 0x75, 0x70, 0x2e, 0x4d, 0x65, 0x64, 0x69, 0x61, 0x49, 0x6e,
	0x66, 0x6f, 0x1a, 0x0d, 0x2e, 0x77, 0x68, 0x61, 0x74, 0x75, 0x70, 0x2e, 0x4d, 0x65, 0x64, 0x69,
	0x61, 0x22, 0x00, 0x42, 0x39, 0x5a, 0x37, 0x67, 0x69, 0x74, 0x68, 0x75, 0x62, 0x2e, 0x63, 0x6f,
	0x6d, 0x2f, 0x64, 0x69, 0x67, 0x69, 0x74, 0x61, 0x6c, 0x2d, 0x77, 0x69, 0x74, 0x6e, 0x65, 0x73,
	0x73, 0x2d, 0x6c, 0x61, 0x62, 0x2f, 0x77, 0x68, 0x61, 0x74, 0x75, 0x70, 0x2f, 0x70, 0x72, 0x6f,
	0x74, 0x6f, 0x73, 0x2f, 0x77, 0x68, 0x61, 0x74, 0x75, 0x70, 0x63, 0x6f, 0x72, 0x65, 0x62, 0x06,
	0x70, 0x72, 0x6f, 0x74, 0x6f, 0x33,
}

var (
	file_whatupcore_proto_rawDescOnce sync.Once
	file_whatupcore_proto_rawDescData = file_whatupcore_proto_rawDesc
)

func file_whatupcore_proto_rawDescGZIP() []byte {
	file_whatupcore_proto_rawDescOnce.Do(func() {
		file_whatupcore_proto_rawDescData = protoimpl.X.CompressGZIP(file_whatupcore_proto_rawDescData)
	})
	return file_whatupcore_proto_rawDescData
}

var file_whatupcore_proto_enumTypes = make([]protoimpl.EnumInfo, 1)
var file_whatupcore_proto_msgTypes = make([]protoimpl.MessageInfo, 11)
var file_whatupcore_proto_goTypes = []interface{}{
	(MediaInfo_MediaType)(0),    // 0: whatup.MediaInfo.MediaType
	(*JID)(nil),                 // 1: whatup.JID
	(*ConnectionStatus)(nil),    // 2: whatup.ConnectionStatus
	(*Message)(nil),             // 3: whatup.Message
	(*MessageSource)(nil),       // 4: whatup.MessageSource
	(*MessageInfo)(nil),         // 5: whatup.MessageInfo
	(*MessageContent)(nil),      // 6: whatup.MessageContent
	(*MessageProperties)(nil),   // 7: whatup.MessageProperties
	(*MediaInfo)(nil),           // 8: whatup.MediaInfo
	(*Media)(nil),               // 9: whatup.Media
	nil,                         // 10: whatup.MessageContent.PropertiesEntry
	nil,                         // 11: whatup.MediaInfo.LocatorEntry
	(*timestamp.Timestamp)(nil), // 12: google.protobuf.Timestamp
	(*whatsappweb.Message)(nil), // 13: whatsappweb.Message
	(*empty.Empty)(nil),         // 14: google.protobuf.Empty
}
var file_whatupcore_proto_depIdxs = []int32{
	12, // 0: whatup.ConnectionStatus.timestamp:type_name -> google.protobuf.Timestamp
	5,  // 1: whatup.Message.info:type_name -> whatup.MessageInfo
	6,  // 2: whatup.Message.content:type_name -> whatup.MessageContent
	7,  // 3: whatup.Message.messageProperties:type_name -> whatup.MessageProperties
	13, // 4: whatup.Message.originalMessage:type_name -> whatsappweb.Message
	1,  // 5: whatup.MessageSource.chat:type_name -> whatup.JID
	1,  // 6: whatup.MessageSource.sender:type_name -> whatup.JID
	1,  // 7: whatup.MessageSource.broadcastListOwner:type_name -> whatup.JID
	4,  // 8: whatup.MessageInfo.source:type_name -> whatup.MessageSource
	12, // 9: whatup.MessageInfo.timestamp:type_name -> google.protobuf.Timestamp
	10, // 10: whatup.MessageContent.properties:type_name -> whatup.MessageContent.PropertiesEntry
	8,  // 11: whatup.MessageContent.mediaInfo:type_name -> whatup.MediaInfo
	11, // 12: whatup.MediaInfo.locator:type_name -> whatup.MediaInfo.LocatorEntry
	0,  // 13: whatup.MediaInfo.mediaType:type_name -> whatup.MediaInfo.MediaType
	14, // 14: whatup.WhatUpCore.GetConnectionStatus:input_type -> google.protobuf.Empty
	14, // 15: whatup.WhatUpCore.GetMessage:input_type -> google.protobuf.Empty
	8,  // 16: whatup.WhatUpCore.DownloadMedia:input_type -> whatup.MediaInfo
	2,  // 17: whatup.WhatUpCore.GetConnectionStatus:output_type -> whatup.ConnectionStatus
	3,  // 18: whatup.WhatUpCore.GetMessage:output_type -> whatup.Message
	9,  // 19: whatup.WhatUpCore.DownloadMedia:output_type -> whatup.Media
	17, // [17:20] is the sub-list for method output_type
	14, // [14:17] is the sub-list for method input_type
	14, // [14:14] is the sub-list for extension type_name
	14, // [14:14] is the sub-list for extension extendee
	0,  // [0:14] is the sub-list for field type_name
}

func init() { file_whatupcore_proto_init() }
func file_whatupcore_proto_init() {
	if File_whatupcore_proto != nil {
		return
	}
	if !protoimpl.UnsafeEnabled {
		file_whatupcore_proto_msgTypes[0].Exporter = func(v interface{}, i int) interface{} {
			switch v := v.(*JID); i {
			case 0:
				return &v.state
			case 1:
				return &v.sizeCache
			case 2:
				return &v.unknownFields
			default:
				return nil
			}
		}
		file_whatupcore_proto_msgTypes[1].Exporter = func(v interface{}, i int) interface{} {
			switch v := v.(*ConnectionStatus); i {
			case 0:
				return &v.state
			case 1:
				return &v.sizeCache
			case 2:
				return &v.unknownFields
			default:
				return nil
			}
		}
		file_whatupcore_proto_msgTypes[2].Exporter = func(v interface{}, i int) interface{} {
			switch v := v.(*Message); i {
			case 0:
				return &v.state
			case 1:
				return &v.sizeCache
			case 2:
				return &v.unknownFields
			default:
				return nil
			}
		}
		file_whatupcore_proto_msgTypes[3].Exporter = func(v interface{}, i int) interface{} {
			switch v := v.(*MessageSource); i {
			case 0:
				return &v.state
			case 1:
				return &v.sizeCache
			case 2:
				return &v.unknownFields
			default:
				return nil
			}
		}
		file_whatupcore_proto_msgTypes[4].Exporter = func(v interface{}, i int) interface{} {
			switch v := v.(*MessageInfo); i {
			case 0:
				return &v.state
			case 1:
				return &v.sizeCache
			case 2:
				return &v.unknownFields
			default:
				return nil
			}
		}
		file_whatupcore_proto_msgTypes[5].Exporter = func(v interface{}, i int) interface{} {
			switch v := v.(*MessageContent); i {
			case 0:
				return &v.state
			case 1:
				return &v.sizeCache
			case 2:
				return &v.unknownFields
			default:
				return nil
			}
		}
		file_whatupcore_proto_msgTypes[6].Exporter = func(v interface{}, i int) interface{} {
			switch v := v.(*MessageProperties); i {
			case 0:
				return &v.state
			case 1:
				return &v.sizeCache
			case 2:
				return &v.unknownFields
			default:
				return nil
			}
		}
		file_whatupcore_proto_msgTypes[7].Exporter = func(v interface{}, i int) interface{} {
			switch v := v.(*MediaInfo); i {
			case 0:
				return &v.state
			case 1:
				return &v.sizeCache
			case 2:
				return &v.unknownFields
			default:
				return nil
			}
		}
		file_whatupcore_proto_msgTypes[8].Exporter = func(v interface{}, i int) interface{} {
			switch v := v.(*Media); i {
			case 0:
				return &v.state
			case 1:
				return &v.sizeCache
			case 2:
				return &v.unknownFields
			default:
				return nil
			}
		}
	}
	type x struct{}
	out := protoimpl.TypeBuilder{
		File: protoimpl.DescBuilder{
			GoPackagePath: reflect.TypeOf(x{}).PkgPath(),
			RawDescriptor: file_whatupcore_proto_rawDesc,
			NumEnums:      1,
			NumMessages:   11,
			NumExtensions: 0,
			NumServices:   1,
		},
		GoTypes:           file_whatupcore_proto_goTypes,
		DependencyIndexes: file_whatupcore_proto_depIdxs,
		EnumInfos:         file_whatupcore_proto_enumTypes,
		MessageInfos:      file_whatupcore_proto_msgTypes,
	}.Build()
	File_whatupcore_proto = out.File
	file_whatupcore_proto_rawDesc = nil
	file_whatupcore_proto_goTypes = nil
	file_whatupcore_proto_depIdxs = nil
}
