// Code generated by protoc-gen-go-grpc. DO NOT EDIT.
// versions:
// - protoc-gen-go-grpc v1.2.0
// - protoc             v3.6.1
// source: whatupcore.proto

package protos

import (
	context "context"
	grpc "google.golang.org/grpc"
	codes "google.golang.org/grpc/codes"
	status "google.golang.org/grpc/status"
)

// This is a compile-time assertion to ensure that this generated file
// is compatible with the grpc package it is being compiled against.
// Requires gRPC-Go v1.32.0 or later.
const _ = grpc.SupportPackageIsVersion7

// WhatUpCoreAuthClient is the client API for WhatUpCoreAuth service.
//
// For semantics around ctx use and closing/ending streaming RPCs, please refer to https://pkg.go.dev/google.golang.org/grpc/?tab=doc#ClientConn.NewStream.
type WhatUpCoreAuthClient interface {
	Login(ctx context.Context, in *WUCredentials, opts ...grpc.CallOption) (*SessionToken, error)
	Register(ctx context.Context, in *RegisterOptions, opts ...grpc.CallOption) (WhatUpCoreAuth_RegisterClient, error)
	RenewToken(ctx context.Context, in *SessionToken, opts ...grpc.CallOption) (*SessionToken, error)
}

type whatUpCoreAuthClient struct {
	cc grpc.ClientConnInterface
}

func NewWhatUpCoreAuthClient(cc grpc.ClientConnInterface) WhatUpCoreAuthClient {
	return &whatUpCoreAuthClient{cc}
}

func (c *whatUpCoreAuthClient) Login(ctx context.Context, in *WUCredentials, opts ...grpc.CallOption) (*SessionToken, error) {
	out := new(SessionToken)
	err := c.cc.Invoke(ctx, "/protos.WhatUpCoreAuth/Login", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *whatUpCoreAuthClient) Register(ctx context.Context, in *RegisterOptions, opts ...grpc.CallOption) (WhatUpCoreAuth_RegisterClient, error) {
	stream, err := c.cc.NewStream(ctx, &WhatUpCoreAuth_ServiceDesc.Streams[0], "/protos.WhatUpCoreAuth/Register", opts...)
	if err != nil {
		return nil, err
	}
	x := &whatUpCoreAuthRegisterClient{stream}
	if err := x.ClientStream.SendMsg(in); err != nil {
		return nil, err
	}
	if err := x.ClientStream.CloseSend(); err != nil {
		return nil, err
	}
	return x, nil
}

type WhatUpCoreAuth_RegisterClient interface {
	Recv() (*RegisterMessages, error)
	grpc.ClientStream
}

type whatUpCoreAuthRegisterClient struct {
	grpc.ClientStream
}

func (x *whatUpCoreAuthRegisterClient) Recv() (*RegisterMessages, error) {
	m := new(RegisterMessages)
	if err := x.ClientStream.RecvMsg(m); err != nil {
		return nil, err
	}
	return m, nil
}

func (c *whatUpCoreAuthClient) RenewToken(ctx context.Context, in *SessionToken, opts ...grpc.CallOption) (*SessionToken, error) {
	out := new(SessionToken)
	err := c.cc.Invoke(ctx, "/protos.WhatUpCoreAuth/RenewToken", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

// WhatUpCoreAuthServer is the server API for WhatUpCoreAuth service.
// All implementations must embed UnimplementedWhatUpCoreAuthServer
// for forward compatibility
type WhatUpCoreAuthServer interface {
	Login(context.Context, *WUCredentials) (*SessionToken, error)
	Register(*RegisterOptions, WhatUpCoreAuth_RegisterServer) error
	RenewToken(context.Context, *SessionToken) (*SessionToken, error)
	mustEmbedUnimplementedWhatUpCoreAuthServer()
}

// UnimplementedWhatUpCoreAuthServer must be embedded to have forward compatible implementations.
type UnimplementedWhatUpCoreAuthServer struct {
}

func (UnimplementedWhatUpCoreAuthServer) Login(context.Context, *WUCredentials) (*SessionToken, error) {
	return nil, status.Errorf(codes.Unimplemented, "method Login not implemented")
}
func (UnimplementedWhatUpCoreAuthServer) Register(*RegisterOptions, WhatUpCoreAuth_RegisterServer) error {
	return status.Errorf(codes.Unimplemented, "method Register not implemented")
}
func (UnimplementedWhatUpCoreAuthServer) RenewToken(context.Context, *SessionToken) (*SessionToken, error) {
	return nil, status.Errorf(codes.Unimplemented, "method RenewToken not implemented")
}
func (UnimplementedWhatUpCoreAuthServer) mustEmbedUnimplementedWhatUpCoreAuthServer() {}

// UnsafeWhatUpCoreAuthServer may be embedded to opt out of forward compatibility for this service.
// Use of this interface is not recommended, as added methods to WhatUpCoreAuthServer will
// result in compilation errors.
type UnsafeWhatUpCoreAuthServer interface {
	mustEmbedUnimplementedWhatUpCoreAuthServer()
}

func RegisterWhatUpCoreAuthServer(s grpc.ServiceRegistrar, srv WhatUpCoreAuthServer) {
	s.RegisterService(&WhatUpCoreAuth_ServiceDesc, srv)
}

func _WhatUpCoreAuth_Login_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(WUCredentials)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(WhatUpCoreAuthServer).Login(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/protos.WhatUpCoreAuth/Login",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(WhatUpCoreAuthServer).Login(ctx, req.(*WUCredentials))
	}
	return interceptor(ctx, in, info, handler)
}

func _WhatUpCoreAuth_Register_Handler(srv interface{}, stream grpc.ServerStream) error {
	m := new(RegisterOptions)
	if err := stream.RecvMsg(m); err != nil {
		return err
	}
	return srv.(WhatUpCoreAuthServer).Register(m, &whatUpCoreAuthRegisterServer{stream})
}

type WhatUpCoreAuth_RegisterServer interface {
	Send(*RegisterMessages) error
	grpc.ServerStream
}

type whatUpCoreAuthRegisterServer struct {
	grpc.ServerStream
}

func (x *whatUpCoreAuthRegisterServer) Send(m *RegisterMessages) error {
	return x.ServerStream.SendMsg(m)
}

func _WhatUpCoreAuth_RenewToken_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(SessionToken)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(WhatUpCoreAuthServer).RenewToken(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/protos.WhatUpCoreAuth/RenewToken",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(WhatUpCoreAuthServer).RenewToken(ctx, req.(*SessionToken))
	}
	return interceptor(ctx, in, info, handler)
}

// WhatUpCoreAuth_ServiceDesc is the grpc.ServiceDesc for WhatUpCoreAuth service.
// It's only intended for direct use with grpc.RegisterService,
// and not to be introspected or modified (even as a copy)
var WhatUpCoreAuth_ServiceDesc = grpc.ServiceDesc{
	ServiceName: "protos.WhatUpCoreAuth",
	HandlerType: (*WhatUpCoreAuthServer)(nil),
	Methods: []grpc.MethodDesc{
		{
			MethodName: "Login",
			Handler:    _WhatUpCoreAuth_Login_Handler,
		},
		{
			MethodName: "RenewToken",
			Handler:    _WhatUpCoreAuth_RenewToken_Handler,
		},
	},
	Streams: []grpc.StreamDesc{
		{
			StreamName:    "Register",
			Handler:       _WhatUpCoreAuth_Register_Handler,
			ServerStreams: true,
		},
	},
	Metadata: "whatupcore.proto",
}

// WhatUpCoreClient is the client API for WhatUpCore service.
//
// For semantics around ctx use and closing/ending streaming RPCs, please refer to https://pkg.go.dev/google.golang.org/grpc/?tab=doc#ClientConn.NewStream.
type WhatUpCoreClient interface {
	GetConnectionStatus(ctx context.Context, in *ConnectionStatusOptions, opts ...grpc.CallOption) (*ConnectionStatus, error)
	SetACL(ctx context.Context, in *GroupACL, opts ...grpc.CallOption) (*GroupACL, error)
	GetACL(ctx context.Context, in *JID, opts ...grpc.CallOption) (*GroupACL, error)
	GetJoinedGroups(ctx context.Context, in *GetJoinedGroupsOptions, opts ...grpc.CallOption) (WhatUpCore_GetJoinedGroupsClient, error)
	GetGroupInfo(ctx context.Context, in *JID, opts ...grpc.CallOption) (*GroupInfo, error)
	GetCommunityInfo(ctx context.Context, in *JID, opts ...grpc.CallOption) (WhatUpCore_GetCommunityInfoClient, error)
	GetGroupInvite(ctx context.Context, in *JID, opts ...grpc.CallOption) (*InviteCode, error)
	GetGroupInfoInvite(ctx context.Context, in *InviteCode, opts ...grpc.CallOption) (*GroupInfo, error)
	JoinGroup(ctx context.Context, in *InviteCode, opts ...grpc.CallOption) (*GroupInfo, error)
	GetMessages(ctx context.Context, in *MessagesOptions, opts ...grpc.CallOption) (WhatUpCore_GetMessagesClient, error)
	GetPendingHistory(ctx context.Context, in *PendingHistoryOptions, opts ...grpc.CallOption) (WhatUpCore_GetPendingHistoryClient, error)
	RequestChatHistory(ctx context.Context, in *HistoryRequestOptions, opts ...grpc.CallOption) (*GroupInfo, error)
	// DownloadMedia can take in a MediaMessage since this is a subset of the proto.Message
	DownloadMedia(ctx context.Context, in *DownloadMediaOptions, opts ...grpc.CallOption) (*MediaContent, error)
	SendMessage(ctx context.Context, in *SendMessageOptions, opts ...grpc.CallOption) (*SendMessageReceipt, error)
	SetDisappearingMessageTime(ctx context.Context, in *DisappearingMessageOptions, opts ...grpc.CallOption) (*DisappearingMessageResponse, error)
	Unregister(ctx context.Context, in *UnregisterOptions, opts ...grpc.CallOption) (*ConnectionStatus, error)
}

type whatUpCoreClient struct {
	cc grpc.ClientConnInterface
}

func NewWhatUpCoreClient(cc grpc.ClientConnInterface) WhatUpCoreClient {
	return &whatUpCoreClient{cc}
}

func (c *whatUpCoreClient) GetConnectionStatus(ctx context.Context, in *ConnectionStatusOptions, opts ...grpc.CallOption) (*ConnectionStatus, error) {
	out := new(ConnectionStatus)
	err := c.cc.Invoke(ctx, "/protos.WhatUpCore/GetConnectionStatus", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *whatUpCoreClient) SetACL(ctx context.Context, in *GroupACL, opts ...grpc.CallOption) (*GroupACL, error) {
	out := new(GroupACL)
	err := c.cc.Invoke(ctx, "/protos.WhatUpCore/SetACL", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *whatUpCoreClient) GetACL(ctx context.Context, in *JID, opts ...grpc.CallOption) (*GroupACL, error) {
	out := new(GroupACL)
	err := c.cc.Invoke(ctx, "/protos.WhatUpCore/GetACL", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *whatUpCoreClient) GetJoinedGroups(ctx context.Context, in *GetJoinedGroupsOptions, opts ...grpc.CallOption) (WhatUpCore_GetJoinedGroupsClient, error) {
	stream, err := c.cc.NewStream(ctx, &WhatUpCore_ServiceDesc.Streams[0], "/protos.WhatUpCore/GetJoinedGroups", opts...)
	if err != nil {
		return nil, err
	}
	x := &whatUpCoreGetJoinedGroupsClient{stream}
	if err := x.ClientStream.SendMsg(in); err != nil {
		return nil, err
	}
	if err := x.ClientStream.CloseSend(); err != nil {
		return nil, err
	}
	return x, nil
}

type WhatUpCore_GetJoinedGroupsClient interface {
	Recv() (*JoinedGroup, error)
	grpc.ClientStream
}

type whatUpCoreGetJoinedGroupsClient struct {
	grpc.ClientStream
}

func (x *whatUpCoreGetJoinedGroupsClient) Recv() (*JoinedGroup, error) {
	m := new(JoinedGroup)
	if err := x.ClientStream.RecvMsg(m); err != nil {
		return nil, err
	}
	return m, nil
}

func (c *whatUpCoreClient) GetGroupInfo(ctx context.Context, in *JID, opts ...grpc.CallOption) (*GroupInfo, error) {
	out := new(GroupInfo)
	err := c.cc.Invoke(ctx, "/protos.WhatUpCore/GetGroupInfo", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *whatUpCoreClient) GetCommunityInfo(ctx context.Context, in *JID, opts ...grpc.CallOption) (WhatUpCore_GetCommunityInfoClient, error) {
	stream, err := c.cc.NewStream(ctx, &WhatUpCore_ServiceDesc.Streams[1], "/protos.WhatUpCore/GetCommunityInfo", opts...)
	if err != nil {
		return nil, err
	}
	x := &whatUpCoreGetCommunityInfoClient{stream}
	if err := x.ClientStream.SendMsg(in); err != nil {
		return nil, err
	}
	if err := x.ClientStream.CloseSend(); err != nil {
		return nil, err
	}
	return x, nil
}

type WhatUpCore_GetCommunityInfoClient interface {
	Recv() (*GroupInfo, error)
	grpc.ClientStream
}

type whatUpCoreGetCommunityInfoClient struct {
	grpc.ClientStream
}

func (x *whatUpCoreGetCommunityInfoClient) Recv() (*GroupInfo, error) {
	m := new(GroupInfo)
	if err := x.ClientStream.RecvMsg(m); err != nil {
		return nil, err
	}
	return m, nil
}

func (c *whatUpCoreClient) GetGroupInvite(ctx context.Context, in *JID, opts ...grpc.CallOption) (*InviteCode, error) {
	out := new(InviteCode)
	err := c.cc.Invoke(ctx, "/protos.WhatUpCore/GetGroupInvite", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *whatUpCoreClient) GetGroupInfoInvite(ctx context.Context, in *InviteCode, opts ...grpc.CallOption) (*GroupInfo, error) {
	out := new(GroupInfo)
	err := c.cc.Invoke(ctx, "/protos.WhatUpCore/GetGroupInfoInvite", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *whatUpCoreClient) JoinGroup(ctx context.Context, in *InviteCode, opts ...grpc.CallOption) (*GroupInfo, error) {
	out := new(GroupInfo)
	err := c.cc.Invoke(ctx, "/protos.WhatUpCore/JoinGroup", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *whatUpCoreClient) GetMessages(ctx context.Context, in *MessagesOptions, opts ...grpc.CallOption) (WhatUpCore_GetMessagesClient, error) {
	stream, err := c.cc.NewStream(ctx, &WhatUpCore_ServiceDesc.Streams[2], "/protos.WhatUpCore/GetMessages", opts...)
	if err != nil {
		return nil, err
	}
	x := &whatUpCoreGetMessagesClient{stream}
	if err := x.ClientStream.SendMsg(in); err != nil {
		return nil, err
	}
	if err := x.ClientStream.CloseSend(); err != nil {
		return nil, err
	}
	return x, nil
}

type WhatUpCore_GetMessagesClient interface {
	Recv() (*MessageStream, error)
	grpc.ClientStream
}

type whatUpCoreGetMessagesClient struct {
	grpc.ClientStream
}

func (x *whatUpCoreGetMessagesClient) Recv() (*MessageStream, error) {
	m := new(MessageStream)
	if err := x.ClientStream.RecvMsg(m); err != nil {
		return nil, err
	}
	return m, nil
}

func (c *whatUpCoreClient) GetPendingHistory(ctx context.Context, in *PendingHistoryOptions, opts ...grpc.CallOption) (WhatUpCore_GetPendingHistoryClient, error) {
	stream, err := c.cc.NewStream(ctx, &WhatUpCore_ServiceDesc.Streams[3], "/protos.WhatUpCore/GetPendingHistory", opts...)
	if err != nil {
		return nil, err
	}
	x := &whatUpCoreGetPendingHistoryClient{stream}
	if err := x.ClientStream.SendMsg(in); err != nil {
		return nil, err
	}
	if err := x.ClientStream.CloseSend(); err != nil {
		return nil, err
	}
	return x, nil
}

type WhatUpCore_GetPendingHistoryClient interface {
	Recv() (*MessageStream, error)
	grpc.ClientStream
}

type whatUpCoreGetPendingHistoryClient struct {
	grpc.ClientStream
}

func (x *whatUpCoreGetPendingHistoryClient) Recv() (*MessageStream, error) {
	m := new(MessageStream)
	if err := x.ClientStream.RecvMsg(m); err != nil {
		return nil, err
	}
	return m, nil
}

func (c *whatUpCoreClient) RequestChatHistory(ctx context.Context, in *HistoryRequestOptions, opts ...grpc.CallOption) (*GroupInfo, error) {
	out := new(GroupInfo)
	err := c.cc.Invoke(ctx, "/protos.WhatUpCore/RequestChatHistory", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *whatUpCoreClient) DownloadMedia(ctx context.Context, in *DownloadMediaOptions, opts ...grpc.CallOption) (*MediaContent, error) {
	out := new(MediaContent)
	err := c.cc.Invoke(ctx, "/protos.WhatUpCore/DownloadMedia", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *whatUpCoreClient) SendMessage(ctx context.Context, in *SendMessageOptions, opts ...grpc.CallOption) (*SendMessageReceipt, error) {
	out := new(SendMessageReceipt)
	err := c.cc.Invoke(ctx, "/protos.WhatUpCore/SendMessage", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *whatUpCoreClient) SetDisappearingMessageTime(ctx context.Context, in *DisappearingMessageOptions, opts ...grpc.CallOption) (*DisappearingMessageResponse, error) {
	out := new(DisappearingMessageResponse)
	err := c.cc.Invoke(ctx, "/protos.WhatUpCore/SetDisappearingMessageTime", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *whatUpCoreClient) Unregister(ctx context.Context, in *UnregisterOptions, opts ...grpc.CallOption) (*ConnectionStatus, error) {
	out := new(ConnectionStatus)
	err := c.cc.Invoke(ctx, "/protos.WhatUpCore/Unregister", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

// WhatUpCoreServer is the server API for WhatUpCore service.
// All implementations must embed UnimplementedWhatUpCoreServer
// for forward compatibility
type WhatUpCoreServer interface {
	GetConnectionStatus(context.Context, *ConnectionStatusOptions) (*ConnectionStatus, error)
	SetACL(context.Context, *GroupACL) (*GroupACL, error)
	GetACL(context.Context, *JID) (*GroupACL, error)
	GetJoinedGroups(*GetJoinedGroupsOptions, WhatUpCore_GetJoinedGroupsServer) error
	GetGroupInfo(context.Context, *JID) (*GroupInfo, error)
	GetCommunityInfo(*JID, WhatUpCore_GetCommunityInfoServer) error
	GetGroupInvite(context.Context, *JID) (*InviteCode, error)
	GetGroupInfoInvite(context.Context, *InviteCode) (*GroupInfo, error)
	JoinGroup(context.Context, *InviteCode) (*GroupInfo, error)
	GetMessages(*MessagesOptions, WhatUpCore_GetMessagesServer) error
	GetPendingHistory(*PendingHistoryOptions, WhatUpCore_GetPendingHistoryServer) error
	RequestChatHistory(context.Context, *HistoryRequestOptions) (*GroupInfo, error)
	// DownloadMedia can take in a MediaMessage since this is a subset of the proto.Message
	DownloadMedia(context.Context, *DownloadMediaOptions) (*MediaContent, error)
	SendMessage(context.Context, *SendMessageOptions) (*SendMessageReceipt, error)
	SetDisappearingMessageTime(context.Context, *DisappearingMessageOptions) (*DisappearingMessageResponse, error)
	Unregister(context.Context, *UnregisterOptions) (*ConnectionStatus, error)
	mustEmbedUnimplementedWhatUpCoreServer()
}

// UnimplementedWhatUpCoreServer must be embedded to have forward compatible implementations.
type UnimplementedWhatUpCoreServer struct {
}

func (UnimplementedWhatUpCoreServer) GetConnectionStatus(context.Context, *ConnectionStatusOptions) (*ConnectionStatus, error) {
	return nil, status.Errorf(codes.Unimplemented, "method GetConnectionStatus not implemented")
}
func (UnimplementedWhatUpCoreServer) SetACL(context.Context, *GroupACL) (*GroupACL, error) {
	return nil, status.Errorf(codes.Unimplemented, "method SetACL not implemented")
}
func (UnimplementedWhatUpCoreServer) GetACL(context.Context, *JID) (*GroupACL, error) {
	return nil, status.Errorf(codes.Unimplemented, "method GetACL not implemented")
}
func (UnimplementedWhatUpCoreServer) GetJoinedGroups(*GetJoinedGroupsOptions, WhatUpCore_GetJoinedGroupsServer) error {
	return status.Errorf(codes.Unimplemented, "method GetJoinedGroups not implemented")
}
func (UnimplementedWhatUpCoreServer) GetGroupInfo(context.Context, *JID) (*GroupInfo, error) {
	return nil, status.Errorf(codes.Unimplemented, "method GetGroupInfo not implemented")
}
func (UnimplementedWhatUpCoreServer) GetCommunityInfo(*JID, WhatUpCore_GetCommunityInfoServer) error {
	return status.Errorf(codes.Unimplemented, "method GetCommunityInfo not implemented")
}
func (UnimplementedWhatUpCoreServer) GetGroupInvite(context.Context, *JID) (*InviteCode, error) {
	return nil, status.Errorf(codes.Unimplemented, "method GetGroupInvite not implemented")
}
func (UnimplementedWhatUpCoreServer) GetGroupInfoInvite(context.Context, *InviteCode) (*GroupInfo, error) {
	return nil, status.Errorf(codes.Unimplemented, "method GetGroupInfoInvite not implemented")
}
func (UnimplementedWhatUpCoreServer) JoinGroup(context.Context, *InviteCode) (*GroupInfo, error) {
	return nil, status.Errorf(codes.Unimplemented, "method JoinGroup not implemented")
}
func (UnimplementedWhatUpCoreServer) GetMessages(*MessagesOptions, WhatUpCore_GetMessagesServer) error {
	return status.Errorf(codes.Unimplemented, "method GetMessages not implemented")
}
func (UnimplementedWhatUpCoreServer) GetPendingHistory(*PendingHistoryOptions, WhatUpCore_GetPendingHistoryServer) error {
	return status.Errorf(codes.Unimplemented, "method GetPendingHistory not implemented")
}
func (UnimplementedWhatUpCoreServer) RequestChatHistory(context.Context, *HistoryRequestOptions) (*GroupInfo, error) {
	return nil, status.Errorf(codes.Unimplemented, "method RequestChatHistory not implemented")
}
func (UnimplementedWhatUpCoreServer) DownloadMedia(context.Context, *DownloadMediaOptions) (*MediaContent, error) {
	return nil, status.Errorf(codes.Unimplemented, "method DownloadMedia not implemented")
}
func (UnimplementedWhatUpCoreServer) SendMessage(context.Context, *SendMessageOptions) (*SendMessageReceipt, error) {
	return nil, status.Errorf(codes.Unimplemented, "method SendMessage not implemented")
}
func (UnimplementedWhatUpCoreServer) SetDisappearingMessageTime(context.Context, *DisappearingMessageOptions) (*DisappearingMessageResponse, error) {
	return nil, status.Errorf(codes.Unimplemented, "method SetDisappearingMessageTime not implemented")
}
func (UnimplementedWhatUpCoreServer) Unregister(context.Context, *UnregisterOptions) (*ConnectionStatus, error) {
	return nil, status.Errorf(codes.Unimplemented, "method Unregister not implemented")
}
func (UnimplementedWhatUpCoreServer) mustEmbedUnimplementedWhatUpCoreServer() {}

// UnsafeWhatUpCoreServer may be embedded to opt out of forward compatibility for this service.
// Use of this interface is not recommended, as added methods to WhatUpCoreServer will
// result in compilation errors.
type UnsafeWhatUpCoreServer interface {
	mustEmbedUnimplementedWhatUpCoreServer()
}

func RegisterWhatUpCoreServer(s grpc.ServiceRegistrar, srv WhatUpCoreServer) {
	s.RegisterService(&WhatUpCore_ServiceDesc, srv)
}

func _WhatUpCore_GetConnectionStatus_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(ConnectionStatusOptions)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(WhatUpCoreServer).GetConnectionStatus(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/protos.WhatUpCore/GetConnectionStatus",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(WhatUpCoreServer).GetConnectionStatus(ctx, req.(*ConnectionStatusOptions))
	}
	return interceptor(ctx, in, info, handler)
}

func _WhatUpCore_SetACL_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(GroupACL)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(WhatUpCoreServer).SetACL(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/protos.WhatUpCore/SetACL",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(WhatUpCoreServer).SetACL(ctx, req.(*GroupACL))
	}
	return interceptor(ctx, in, info, handler)
}

func _WhatUpCore_GetACL_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(JID)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(WhatUpCoreServer).GetACL(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/protos.WhatUpCore/GetACL",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(WhatUpCoreServer).GetACL(ctx, req.(*JID))
	}
	return interceptor(ctx, in, info, handler)
}

func _WhatUpCore_GetJoinedGroups_Handler(srv interface{}, stream grpc.ServerStream) error {
	m := new(GetJoinedGroupsOptions)
	if err := stream.RecvMsg(m); err != nil {
		return err
	}
	return srv.(WhatUpCoreServer).GetJoinedGroups(m, &whatUpCoreGetJoinedGroupsServer{stream})
}

type WhatUpCore_GetJoinedGroupsServer interface {
	Send(*JoinedGroup) error
	grpc.ServerStream
}

type whatUpCoreGetJoinedGroupsServer struct {
	grpc.ServerStream
}

func (x *whatUpCoreGetJoinedGroupsServer) Send(m *JoinedGroup) error {
	return x.ServerStream.SendMsg(m)
}

func _WhatUpCore_GetGroupInfo_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(JID)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(WhatUpCoreServer).GetGroupInfo(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/protos.WhatUpCore/GetGroupInfo",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(WhatUpCoreServer).GetGroupInfo(ctx, req.(*JID))
	}
	return interceptor(ctx, in, info, handler)
}

func _WhatUpCore_GetCommunityInfo_Handler(srv interface{}, stream grpc.ServerStream) error {
	m := new(JID)
	if err := stream.RecvMsg(m); err != nil {
		return err
	}
	return srv.(WhatUpCoreServer).GetCommunityInfo(m, &whatUpCoreGetCommunityInfoServer{stream})
}

type WhatUpCore_GetCommunityInfoServer interface {
	Send(*GroupInfo) error
	grpc.ServerStream
}

type whatUpCoreGetCommunityInfoServer struct {
	grpc.ServerStream
}

func (x *whatUpCoreGetCommunityInfoServer) Send(m *GroupInfo) error {
	return x.ServerStream.SendMsg(m)
}

func _WhatUpCore_GetGroupInvite_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(JID)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(WhatUpCoreServer).GetGroupInvite(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/protos.WhatUpCore/GetGroupInvite",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(WhatUpCoreServer).GetGroupInvite(ctx, req.(*JID))
	}
	return interceptor(ctx, in, info, handler)
}

func _WhatUpCore_GetGroupInfoInvite_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(InviteCode)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(WhatUpCoreServer).GetGroupInfoInvite(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/protos.WhatUpCore/GetGroupInfoInvite",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(WhatUpCoreServer).GetGroupInfoInvite(ctx, req.(*InviteCode))
	}
	return interceptor(ctx, in, info, handler)
}

func _WhatUpCore_JoinGroup_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(InviteCode)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(WhatUpCoreServer).JoinGroup(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/protos.WhatUpCore/JoinGroup",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(WhatUpCoreServer).JoinGroup(ctx, req.(*InviteCode))
	}
	return interceptor(ctx, in, info, handler)
}

func _WhatUpCore_GetMessages_Handler(srv interface{}, stream grpc.ServerStream) error {
	m := new(MessagesOptions)
	if err := stream.RecvMsg(m); err != nil {
		return err
	}
	return srv.(WhatUpCoreServer).GetMessages(m, &whatUpCoreGetMessagesServer{stream})
}

type WhatUpCore_GetMessagesServer interface {
	Send(*MessageStream) error
	grpc.ServerStream
}

type whatUpCoreGetMessagesServer struct {
	grpc.ServerStream
}

func (x *whatUpCoreGetMessagesServer) Send(m *MessageStream) error {
	return x.ServerStream.SendMsg(m)
}

func _WhatUpCore_GetPendingHistory_Handler(srv interface{}, stream grpc.ServerStream) error {
	m := new(PendingHistoryOptions)
	if err := stream.RecvMsg(m); err != nil {
		return err
	}
	return srv.(WhatUpCoreServer).GetPendingHistory(m, &whatUpCoreGetPendingHistoryServer{stream})
}

type WhatUpCore_GetPendingHistoryServer interface {
	Send(*MessageStream) error
	grpc.ServerStream
}

type whatUpCoreGetPendingHistoryServer struct {
	grpc.ServerStream
}

func (x *whatUpCoreGetPendingHistoryServer) Send(m *MessageStream) error {
	return x.ServerStream.SendMsg(m)
}

func _WhatUpCore_RequestChatHistory_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(HistoryRequestOptions)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(WhatUpCoreServer).RequestChatHistory(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/protos.WhatUpCore/RequestChatHistory",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(WhatUpCoreServer).RequestChatHistory(ctx, req.(*HistoryRequestOptions))
	}
	return interceptor(ctx, in, info, handler)
}

func _WhatUpCore_DownloadMedia_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(DownloadMediaOptions)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(WhatUpCoreServer).DownloadMedia(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/protos.WhatUpCore/DownloadMedia",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(WhatUpCoreServer).DownloadMedia(ctx, req.(*DownloadMediaOptions))
	}
	return interceptor(ctx, in, info, handler)
}

func _WhatUpCore_SendMessage_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(SendMessageOptions)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(WhatUpCoreServer).SendMessage(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/protos.WhatUpCore/SendMessage",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(WhatUpCoreServer).SendMessage(ctx, req.(*SendMessageOptions))
	}
	return interceptor(ctx, in, info, handler)
}

func _WhatUpCore_SetDisappearingMessageTime_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(DisappearingMessageOptions)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(WhatUpCoreServer).SetDisappearingMessageTime(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/protos.WhatUpCore/SetDisappearingMessageTime",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(WhatUpCoreServer).SetDisappearingMessageTime(ctx, req.(*DisappearingMessageOptions))
	}
	return interceptor(ctx, in, info, handler)
}

func _WhatUpCore_Unregister_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(UnregisterOptions)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(WhatUpCoreServer).Unregister(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/protos.WhatUpCore/Unregister",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(WhatUpCoreServer).Unregister(ctx, req.(*UnregisterOptions))
	}
	return interceptor(ctx, in, info, handler)
}

// WhatUpCore_ServiceDesc is the grpc.ServiceDesc for WhatUpCore service.
// It's only intended for direct use with grpc.RegisterService,
// and not to be introspected or modified (even as a copy)
var WhatUpCore_ServiceDesc = grpc.ServiceDesc{
	ServiceName: "protos.WhatUpCore",
	HandlerType: (*WhatUpCoreServer)(nil),
	Methods: []grpc.MethodDesc{
		{
			MethodName: "GetConnectionStatus",
			Handler:    _WhatUpCore_GetConnectionStatus_Handler,
		},
		{
			MethodName: "SetACL",
			Handler:    _WhatUpCore_SetACL_Handler,
		},
		{
			MethodName: "GetACL",
			Handler:    _WhatUpCore_GetACL_Handler,
		},
		{
			MethodName: "GetGroupInfo",
			Handler:    _WhatUpCore_GetGroupInfo_Handler,
		},
		{
			MethodName: "GetGroupInvite",
			Handler:    _WhatUpCore_GetGroupInvite_Handler,
		},
		{
			MethodName: "GetGroupInfoInvite",
			Handler:    _WhatUpCore_GetGroupInfoInvite_Handler,
		},
		{
			MethodName: "JoinGroup",
			Handler:    _WhatUpCore_JoinGroup_Handler,
		},
		{
			MethodName: "RequestChatHistory",
			Handler:    _WhatUpCore_RequestChatHistory_Handler,
		},
		{
			MethodName: "DownloadMedia",
			Handler:    _WhatUpCore_DownloadMedia_Handler,
		},
		{
			MethodName: "SendMessage",
			Handler:    _WhatUpCore_SendMessage_Handler,
		},
		{
			MethodName: "SetDisappearingMessageTime",
			Handler:    _WhatUpCore_SetDisappearingMessageTime_Handler,
		},
		{
			MethodName: "Unregister",
			Handler:    _WhatUpCore_Unregister_Handler,
		},
	},
	Streams: []grpc.StreamDesc{
		{
			StreamName:    "GetJoinedGroups",
			Handler:       _WhatUpCore_GetJoinedGroups_Handler,
			ServerStreams: true,
		},
		{
			StreamName:    "GetCommunityInfo",
			Handler:       _WhatUpCore_GetCommunityInfo_Handler,
			ServerStreams: true,
		},
		{
			StreamName:    "GetMessages",
			Handler:       _WhatUpCore_GetMessages_Handler,
			ServerStreams: true,
		},
		{
			StreamName:    "GetPendingHistory",
			Handler:       _WhatUpCore_GetPendingHistory_Handler,
			ServerStreams: true,
		},
	},
	Metadata: "whatupcore.proto",
}
