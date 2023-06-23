package whatupcore2

import (
	"context"
	"fmt"
	"log"
	"net"
	"time"

	pb "github.com/digital-witness-lab/whatup/protos"
	"github.com/grpc-ecosystem/go-grpc-middleware/v2/interceptors/auth"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/credentials"
	"google.golang.org/grpc/keepalive"
	"google.golang.org/grpc/reflection"
	"google.golang.org/grpc/status"
)

var (
    TLS_CERT_FILE = "../data/keys/cert.pem"
    TLS_KEY_FILE = "../data/keys/key.pem"
    JWT_SECRET = []byte("SECRETSECRET")
)

func createAuthCheck(sessionManager *SessionManager, secretKey []byte) func(context.Context) (context.Context, error) {
    return func(ctx context.Context) (context.Context, error) {
	    token, err := auth.AuthFromMD(ctx, "bearer")
	    if err != nil {
	    	return nil, err
	    }
        sessionId, err := sessionManager.TokenToSessionId(token)
        if err != nil {
            return nil, status.Errorf(codes.Unauthenticated, "Invalid auth token: %v", err)
        }

        session, ok := sessionManager.GetSession(sessionId)
	    if !ok {
	    	return nil, status.Errorf(codes.Unauthenticated, "Unregistered auth token")
	    }

	    return context.WithValue(ctx, "session", session), nil
    }
}

func StartRPC(port uint32) error {
	lis, err := net.Listen("tcp", fmt.Sprintf("0.0.0.0:%d", port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
        return err
	}

    sessionManager := NewSessionManager(JWT_SECRET)
    sessionManager.Start()
    authCheck := createAuthCheck(sessionManager, JWT_SECRET)
    keepAlive := grpc.KeepaliveParams(keepalive.ServerParameters{
        Time: 10 * time.Second,
    })

    var s *grpc.Server
    if false {
        creds, err := credentials.NewServerTLSFromFile(TLS_CERT_FILE, TLS_KEY_FILE)
        if err != nil {
	    	log.Fatalf("could not load server credentials: %v", err)
            return err
        }
	    s = grpc.NewServer(grpc.Creds(creds), keepAlive)
    } else {
	    s = grpc.NewServer(
		    grpc.StreamInterceptor(auth.StreamServerInterceptor(authCheck)),
		    grpc.UnaryInterceptor(auth.UnaryServerInterceptor(authCheck)),
            keepAlive,
        )
    }
    reflection.Register(s)

    pb.RegisterWhatUpCoreAuthServer(s, &WhatUpCoreAuthServer{
        sessionManager:sessionManager,
    })
    pb.RegisterWhatUpCoreServer(s, &WhatUpCoreServer{
        sessionManager:sessionManager,
    })

	log.Printf("server listening at %v", lis.Addr())
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
    return nil
}
