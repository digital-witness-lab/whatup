// Code generated by protoc-gen-go-grpc. DO NOT EDIT.
// versions:
// - protoc-gen-go-grpc v1.3.0
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

const (
	WhatUpCoreAuth_Login_FullMethodName      = "/protos.WhatUpCoreAuth/Login"
	WhatUpCoreAuth_Register_FullMethodName   = "/protos.WhatUpCoreAuth/Register"
	WhatUpCoreAuth_RenewToken_FullMethodName = "/protos.WhatUpCoreAuth/RenewToken"
)

// WhatUpCoreAuthClient is the client API for WhatUpCoreAuth service.
//
// For semantics around ctx use and closing/ending streaming RPCs, please refer to https://pkg.go.dev/google.golang.org/grpc/?tab=doc#ClientConn.NewStream.
type WhatUpCoreAuthClient interface {
	Login(ctx context.Context, in *WUCredentials, opts ...grpc.CallOption) (*SessionToken, error)
	Register(ctx context.Context, in *WUCredentials, opts ...grpc.CallOption) (WhatUpCoreAuth_RegisterClient, error)
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
	err := c.cc.Invoke(ctx, WhatUpCoreAuth_Login_FullMethodName, in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *whatUpCoreAuthClient) Register(ctx context.Context, in *WUCredentials, opts ...grpc.CallOption) (WhatUpCoreAuth_RegisterClient, error) {
	stream, err := c.cc.NewStream(ctx, &WhatUpCoreAuth_ServiceDesc.Streams[0], WhatUpCoreAuth_Register_FullMethodName, opts...)
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
	err := c.cc.Invoke(ctx, WhatUpCoreAuth_RenewToken_FullMethodName, in, out, opts...)
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
	Register(*WUCredentials, WhatUpCoreAuth_RegisterServer) error
	RenewToken(context.Context, *SessionToken) (*SessionToken, error)
	mustEmbedUnimplementedWhatUpCoreAuthServer()
}

// UnimplementedWhatUpCoreAuthServer must be embedded to have forward compatible implementations.
type UnimplementedWhatUpCoreAuthServer struct {
}

func (UnimplementedWhatUpCoreAuthServer) Login(context.Context, *WUCredentials) (*SessionToken, error) {
	return nil, status.Errorf(codes.Unimplemented, "method Login not implemented")
}
func (UnimplementedWhatUpCoreAuthServer) Register(*WUCredentials, WhatUpCoreAuth_RegisterServer) error {
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
		FullMethod: WhatUpCoreAuth_Login_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(WhatUpCoreAuthServer).Login(ctx, req.(*WUCredentials))
	}
	return interceptor(ctx, in, info, handler)
}

func _WhatUpCoreAuth_Register_Handler(srv interface{}, stream grpc.ServerStream) error {
	m := new(WUCredentials)
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
		FullMethod: WhatUpCoreAuth_RenewToken_FullMethodName,
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

const (
	WhatUpCore_GetConnectionStatus_FullMethodName        = "/protos.WhatUpCore/GetConnectionStatus"
	WhatUpCore_GetGroupInfo_FullMethodName               = "/protos.WhatUpCore/GetGroupInfo"
	WhatUpCore_GetGroupInfoInvite_FullMethodName         = "/protos.WhatUpCore/GetGroupInfoInvite"
	WhatUpCore_JoinGroup_FullMethodName                  = "/protos.WhatUpCore/JoinGroup"
	WhatUpCore_GetMessages_FullMethodName                = "/protos.WhatUpCore/GetMessages"
	WhatUpCore_GetPendingHistory_FullMethodName          = "/protos.WhatUpCore/GetPendingHistory"
	WhatUpCore_DownloadMedia_FullMethodName              = "/protos.WhatUpCore/DownloadMedia"
	WhatUpCore_SendMessage_FullMethodName                = "/protos.WhatUpCore/SendMessage"
	WhatUpCore_SetDisappearingMessageTime_FullMethodName = "/protos.WhatUpCore/SetDisappearingMessageTime"
)

// WhatUpCoreClient is the client API for WhatUpCore service.
//
// For semantics around ctx use and closing/ending streaming RPCs, please refer to https://pkg.go.dev/google.golang.org/grpc/?tab=doc#ClientConn.NewStream.
type WhatUpCoreClient interface {
	GetConnectionStatus(ctx context.Context, in *ConnectionStatusOptions, opts ...grpc.CallOption) (*ConnectionStatus, error)
	GetGroupInfo(ctx context.Context, in *JID, opts ...grpc.CallOption) (*GroupInfo, error)
	GetGroupInfoInvite(ctx context.Context, in *InviteCode, opts ...grpc.CallOption) (*GroupInfo, error)
	JoinGroup(ctx context.Context, in *InviteCode, opts ...grpc.CallOption) (*GroupInfo, error)
	GetMessages(ctx context.Context, in *MessagesOptions, opts ...grpc.CallOption) (WhatUpCore_GetMessagesClient, error)
	GetPendingHistory(ctx context.Context, in *PendingHistoryOptions, opts ...grpc.CallOption) (WhatUpCore_GetPendingHistoryClient, error)
	// DownloadMedia can take in a MediaMessage since this is a subset of the proto.Message
	DownloadMedia(ctx context.Context, in *DownloadMediaOptions, opts ...grpc.CallOption) (*MediaContent, error)
	SendMessage(ctx context.Context, in *SendMessageOptions, opts ...grpc.CallOption) (*SendMessageReceipt, error)
	SetDisappearingMessageTime(ctx context.Context, in *DisappearingMessageOptions, opts ...grpc.CallOption) (*DisappearingMessageResponse, error)
}

type whatUpCoreClient struct {
	cc grpc.ClientConnInterface
}

func NewWhatUpCoreClient(cc grpc.ClientConnInterface) WhatUpCoreClient {
	return &whatUpCoreClient{cc}
}

func (c *whatUpCoreClient) GetConnectionStatus(ctx context.Context, in *ConnectionStatusOptions, opts ...grpc.CallOption) (*ConnectionStatus, error) {
	out := new(ConnectionStatus)
	err := c.cc.Invoke(ctx, WhatUpCore_GetConnectionStatus_FullMethodName, in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *whatUpCoreClient) GetGroupInfo(ctx context.Context, in *JID, opts ...grpc.CallOption) (*GroupInfo, error) {
	out := new(GroupInfo)
	err := c.cc.Invoke(ctx, WhatUpCore_GetGroupInfo_FullMethodName, in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *whatUpCoreClient) GetGroupInfoInvite(ctx context.Context, in *InviteCode, opts ...grpc.CallOption) (*GroupInfo, error) {
	out := new(GroupInfo)
	err := c.cc.Invoke(ctx, WhatUpCore_GetGroupInfoInvite_FullMethodName, in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *whatUpCoreClient) JoinGroup(ctx context.Context, in *InviteCode, opts ...grpc.CallOption) (*GroupInfo, error) {
	out := new(GroupInfo)
	err := c.cc.Invoke(ctx, WhatUpCore_JoinGroup_FullMethodName, in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *whatUpCoreClient) GetMessages(ctx context.Context, in *MessagesOptions, opts ...grpc.CallOption) (WhatUpCore_GetMessagesClient, error) {
	stream, err := c.cc.NewStream(ctx, &WhatUpCore_ServiceDesc.Streams[0], WhatUpCore_GetMessages_FullMethodName, opts...)
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
	Recv() (*WUMessage, error)
	grpc.ClientStream
}

type whatUpCoreGetMessagesClient struct {
	grpc.ClientStream
}

func (x *whatUpCoreGetMessagesClient) Recv() (*WUMessage, error) {
	m := new(WUMessage)
	if err := x.ClientStream.RecvMsg(m); err != nil {
		return nil, err
	}
	return m, nil
}

func (c *whatUpCoreClient) GetPendingHistory(ctx context.Context, in *PendingHistoryOptions, opts ...grpc.CallOption) (WhatUpCore_GetPendingHistoryClient, error) {
	stream, err := c.cc.NewStream(ctx, &WhatUpCore_ServiceDesc.Streams[1], WhatUpCore_GetPendingHistory_FullMethodName, opts...)
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
	Recv() (*WUMessage, error)
	grpc.ClientStream
}

type whatUpCoreGetPendingHistoryClient struct {
	grpc.ClientStream
}

func (x *whatUpCoreGetPendingHistoryClient) Recv() (*WUMessage, error) {
	m := new(WUMessage)
	if err := x.ClientStream.RecvMsg(m); err != nil {
		return nil, err
	}
	return m, nil
}

func (c *whatUpCoreClient) DownloadMedia(ctx context.Context, in *DownloadMediaOptions, opts ...grpc.CallOption) (*MediaContent, error) {
	out := new(MediaContent)
	err := c.cc.Invoke(ctx, WhatUpCore_DownloadMedia_FullMethodName, in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *whatUpCoreClient) SendMessage(ctx context.Context, in *SendMessageOptions, opts ...grpc.CallOption) (*SendMessageReceipt, error) {
	out := new(SendMessageReceipt)
	err := c.cc.Invoke(ctx, WhatUpCore_SendMessage_FullMethodName, in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *whatUpCoreClient) SetDisappearingMessageTime(ctx context.Context, in *DisappearingMessageOptions, opts ...grpc.CallOption) (*DisappearingMessageResponse, error) {
	out := new(DisappearingMessageResponse)
	err := c.cc.Invoke(ctx, WhatUpCore_SetDisappearingMessageTime_FullMethodName, in, out, opts...)
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
	GetGroupInfo(context.Context, *JID) (*GroupInfo, error)
	GetGroupInfoInvite(context.Context, *InviteCode) (*GroupInfo, error)
	JoinGroup(context.Context, *InviteCode) (*GroupInfo, error)
	GetMessages(*MessagesOptions, WhatUpCore_GetMessagesServer) error
	GetPendingHistory(*PendingHistoryOptions, WhatUpCore_GetPendingHistoryServer) error
	// DownloadMedia can take in a MediaMessage since this is a subset of the proto.Message
	DownloadMedia(context.Context, *DownloadMediaOptions) (*MediaContent, error)
	SendMessage(context.Context, *SendMessageOptions) (*SendMessageReceipt, error)
	SetDisappearingMessageTime(context.Context, *DisappearingMessageOptions) (*DisappearingMessageResponse, error)
	mustEmbedUnimplementedWhatUpCoreServer()
}

// UnimplementedWhatUpCoreServer must be embedded to have forward compatible implementations.
type UnimplementedWhatUpCoreServer struct {
}

func (UnimplementedWhatUpCoreServer) GetConnectionStatus(context.Context, *ConnectionStatusOptions) (*ConnectionStatus, error) {
	return nil, status.Errorf(codes.Unimplemented, "method GetConnectionStatus not implemented")
}
func (UnimplementedWhatUpCoreServer) GetGroupInfo(context.Context, *JID) (*GroupInfo, error) {
	return nil, status.Errorf(codes.Unimplemented, "method GetGroupInfo not implemented")
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
func (UnimplementedWhatUpCoreServer) DownloadMedia(context.Context, *DownloadMediaOptions) (*MediaContent, error) {
	return nil, status.Errorf(codes.Unimplemented, "method DownloadMedia not implemented")
}
func (UnimplementedWhatUpCoreServer) SendMessage(context.Context, *SendMessageOptions) (*SendMessageReceipt, error) {
	return nil, status.Errorf(codes.Unimplemented, "method SendMessage not implemented")
}
func (UnimplementedWhatUpCoreServer) SetDisappearingMessageTime(context.Context, *DisappearingMessageOptions) (*DisappearingMessageResponse, error) {
	return nil, status.Errorf(codes.Unimplemented, "method SetDisappearingMessageTime not implemented")
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
		FullMethod: WhatUpCore_GetConnectionStatus_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(WhatUpCoreServer).GetConnectionStatus(ctx, req.(*ConnectionStatusOptions))
	}
	return interceptor(ctx, in, info, handler)
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
		FullMethod: WhatUpCore_GetGroupInfo_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(WhatUpCoreServer).GetGroupInfo(ctx, req.(*JID))
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
		FullMethod: WhatUpCore_GetGroupInfoInvite_FullMethodName,
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
		FullMethod: WhatUpCore_JoinGroup_FullMethodName,
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
	Send(*WUMessage) error
	grpc.ServerStream
}

type whatUpCoreGetMessagesServer struct {
	grpc.ServerStream
}

func (x *whatUpCoreGetMessagesServer) Send(m *WUMessage) error {
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
	Send(*WUMessage) error
	grpc.ServerStream
}

type whatUpCoreGetPendingHistoryServer struct {
	grpc.ServerStream
}

func (x *whatUpCoreGetPendingHistoryServer) Send(m *WUMessage) error {
	return x.ServerStream.SendMsg(m)
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
		FullMethod: WhatUpCore_DownloadMedia_FullMethodName,
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
		FullMethod: WhatUpCore_SendMessage_FullMethodName,
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
		FullMethod: WhatUpCore_SetDisappearingMessageTime_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(WhatUpCoreServer).SetDisappearingMessageTime(ctx, req.(*DisappearingMessageOptions))
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
			MethodName: "GetGroupInfo",
			Handler:    _WhatUpCore_GetGroupInfo_Handler,
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
	},
	Streams: []grpc.StreamDesc{
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
