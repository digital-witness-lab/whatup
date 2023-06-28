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
	err := c.cc.Invoke(ctx, "/protos.WhatUpCoreAuth/Login", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *whatUpCoreAuthClient) Register(ctx context.Context, in *WUCredentials, opts ...grpc.CallOption) (WhatUpCoreAuth_RegisterClient, error) {
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
		FullMethod: "/protos.WhatUpCoreAuth/Login",
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
	GetMessages(ctx context.Context, in *MessagesOptions, opts ...grpc.CallOption) (WhatUpCore_GetMessagesClient, error)
	GetGroupInfo(ctx context.Context, in *JID, opts ...grpc.CallOption) (*GroupInfo, error)
	DownloadMedia(ctx context.Context, in *MediaMessage, opts ...grpc.CallOption) (*MediaContent, error)
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

func (c *whatUpCoreClient) GetMessages(ctx context.Context, in *MessagesOptions, opts ...grpc.CallOption) (WhatUpCore_GetMessagesClient, error) {
	stream, err := c.cc.NewStream(ctx, &WhatUpCore_ServiceDesc.Streams[0], "/protos.WhatUpCore/GetMessages", opts...)
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

func (c *whatUpCoreClient) GetGroupInfo(ctx context.Context, in *JID, opts ...grpc.CallOption) (*GroupInfo, error) {
	out := new(GroupInfo)
	err := c.cc.Invoke(ctx, "/protos.WhatUpCore/GetGroupInfo", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *whatUpCoreClient) DownloadMedia(ctx context.Context, in *MediaMessage, opts ...grpc.CallOption) (*MediaContent, error) {
	out := new(MediaContent)
	err := c.cc.Invoke(ctx, "/protos.WhatUpCore/DownloadMedia", in, out, opts...)
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
	GetMessages(*MessagesOptions, WhatUpCore_GetMessagesServer) error
	GetGroupInfo(context.Context, *JID) (*GroupInfo, error)
	DownloadMedia(context.Context, *MediaMessage) (*MediaContent, error)
	mustEmbedUnimplementedWhatUpCoreServer()
}

// UnimplementedWhatUpCoreServer must be embedded to have forward compatible implementations.
type UnimplementedWhatUpCoreServer struct {
}

func (UnimplementedWhatUpCoreServer) GetConnectionStatus(context.Context, *ConnectionStatusOptions) (*ConnectionStatus, error) {
	return nil, status.Errorf(codes.Unimplemented, "method GetConnectionStatus not implemented")
}
func (UnimplementedWhatUpCoreServer) GetMessages(*MessagesOptions, WhatUpCore_GetMessagesServer) error {
	return status.Errorf(codes.Unimplemented, "method GetMessages not implemented")
}
func (UnimplementedWhatUpCoreServer) GetGroupInfo(context.Context, *JID) (*GroupInfo, error) {
	return nil, status.Errorf(codes.Unimplemented, "method GetGroupInfo not implemented")
}
func (UnimplementedWhatUpCoreServer) DownloadMedia(context.Context, *MediaMessage) (*MediaContent, error) {
	return nil, status.Errorf(codes.Unimplemented, "method DownloadMedia not implemented")
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

func _WhatUpCore_DownloadMedia_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(MediaMessage)
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
		return srv.(WhatUpCoreServer).DownloadMedia(ctx, req.(*MediaMessage))
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
			MethodName: "DownloadMedia",
			Handler:    _WhatUpCore_DownloadMedia_Handler,
		},
	},
	Streams: []grpc.StreamDesc{
		{
			StreamName:    "GetMessages",
			Handler:       _WhatUpCore_GetMessages_Handler,
			ServerStreams: true,
		},
	},
	Metadata: "whatupcore.proto",
}
