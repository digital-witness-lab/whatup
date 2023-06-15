// Code generated by protoc-gen-go-grpc. DO NOT EDIT.
// versions:
// - protoc-gen-go-grpc v1.2.0
// - protoc             v3.6.1
// source: whatupcore.proto

package protos

import (
	context "context"
	empty "github.com/golang/protobuf/ptypes/empty"
	grpc "google.golang.org/grpc"
	codes "google.golang.org/grpc/codes"
	status "google.golang.org/grpc/status"
)

// This is a compile-time assertion to ensure that this generated file
// is compatible with the grpc package it is being compiled against.
// Requires gRPC-Go v1.32.0 or later.
const _ = grpc.SupportPackageIsVersion7

// WhatUpCoreClient is the client API for WhatUpCore service.
//
// For semantics around ctx use and closing/ending streaming RPCs, please refer to https://pkg.go.dev/google.golang.org/grpc/?tab=doc#ClientConn.NewStream.
type WhatUpCoreClient interface {
	GetConnectionStatus(ctx context.Context, in *empty.Empty, opts ...grpc.CallOption) (*ConnectionStatus, error)
	GetMessage(ctx context.Context, in *empty.Empty, opts ...grpc.CallOption) (WhatUpCore_GetMessageClient, error)
	DownloadMedia(ctx context.Context, in *MediaInfo, opts ...grpc.CallOption) (*Media, error)
}

type whatUpCoreClient struct {
	cc grpc.ClientConnInterface
}

func NewWhatUpCoreClient(cc grpc.ClientConnInterface) WhatUpCoreClient {
	return &whatUpCoreClient{cc}
}

func (c *whatUpCoreClient) GetConnectionStatus(ctx context.Context, in *empty.Empty, opts ...grpc.CallOption) (*ConnectionStatus, error) {
	out := new(ConnectionStatus)
	err := c.cc.Invoke(ctx, "/protos.WhatUpCore/GetConnectionStatus", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *whatUpCoreClient) GetMessage(ctx context.Context, in *empty.Empty, opts ...grpc.CallOption) (WhatUpCore_GetMessageClient, error) {
	stream, err := c.cc.NewStream(ctx, &WhatUpCore_ServiceDesc.Streams[0], "/protos.WhatUpCore/GetMessage", opts...)
	if err != nil {
		return nil, err
	}
	x := &whatUpCoreGetMessageClient{stream}
	if err := x.ClientStream.SendMsg(in); err != nil {
		return nil, err
	}
	if err := x.ClientStream.CloseSend(); err != nil {
		return nil, err
	}
	return x, nil
}

type WhatUpCore_GetMessageClient interface {
	Recv() (*WUMessage, error)
	grpc.ClientStream
}

type whatUpCoreGetMessageClient struct {
	grpc.ClientStream
}

func (x *whatUpCoreGetMessageClient) Recv() (*WUMessage, error) {
	m := new(WUMessage)
	if err := x.ClientStream.RecvMsg(m); err != nil {
		return nil, err
	}
	return m, nil
}

func (c *whatUpCoreClient) DownloadMedia(ctx context.Context, in *MediaInfo, opts ...grpc.CallOption) (*Media, error) {
	out := new(Media)
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
	GetConnectionStatus(context.Context, *empty.Empty) (*ConnectionStatus, error)
	GetMessage(*empty.Empty, WhatUpCore_GetMessageServer) error
	DownloadMedia(context.Context, *MediaInfo) (*Media, error)
	mustEmbedUnimplementedWhatUpCoreServer()
}

// UnimplementedWhatUpCoreServer must be embedded to have forward compatible implementations.
type UnimplementedWhatUpCoreServer struct {
}

func (UnimplementedWhatUpCoreServer) GetConnectionStatus(context.Context, *empty.Empty) (*ConnectionStatus, error) {
	return nil, status.Errorf(codes.Unimplemented, "method GetConnectionStatus not implemented")
}
func (UnimplementedWhatUpCoreServer) GetMessage(*empty.Empty, WhatUpCore_GetMessageServer) error {
	return status.Errorf(codes.Unimplemented, "method GetMessage not implemented")
}
func (UnimplementedWhatUpCoreServer) DownloadMedia(context.Context, *MediaInfo) (*Media, error) {
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
	in := new(empty.Empty)
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
		return srv.(WhatUpCoreServer).GetConnectionStatus(ctx, req.(*empty.Empty))
	}
	return interceptor(ctx, in, info, handler)
}

func _WhatUpCore_GetMessage_Handler(srv interface{}, stream grpc.ServerStream) error {
	m := new(empty.Empty)
	if err := stream.RecvMsg(m); err != nil {
		return err
	}
	return srv.(WhatUpCoreServer).GetMessage(m, &whatUpCoreGetMessageServer{stream})
}

type WhatUpCore_GetMessageServer interface {
	Send(*WUMessage) error
	grpc.ServerStream
}

type whatUpCoreGetMessageServer struct {
	grpc.ServerStream
}

func (x *whatUpCoreGetMessageServer) Send(m *WUMessage) error {
	return x.ServerStream.SendMsg(m)
}

func _WhatUpCore_DownloadMedia_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(MediaInfo)
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
		return srv.(WhatUpCoreServer).DownloadMedia(ctx, req.(*MediaInfo))
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
			MethodName: "DownloadMedia",
			Handler:    _WhatUpCore_DownloadMedia_Handler,
		},
	},
	Streams: []grpc.StreamDesc{
		{
			StreamName:    "GetMessage",
			Handler:       _WhatUpCore_GetMessage_Handler,
			ServerStreams: true,
		},
	},
	Metadata: "whatupcore.proto",
}
