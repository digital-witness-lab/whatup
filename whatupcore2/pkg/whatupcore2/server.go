package whatupcore2

import (
	"context"
	"fmt"
	"net"
	"os"
	"time"

	pb "github.com/digital-witness-lab/whatup/protos"
	"github.com/grpc-ecosystem/go-grpc-middleware/v2/interceptors/auth"
	waLog "go.mau.fi/whatsmeow/util/log"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/credentials"
	"google.golang.org/grpc/keepalive"
	"google.golang.org/grpc/reflection"
	"google.golang.org/grpc/status"
)

var (
	TLS_CERT_FILE = "/run/secrets/ssl-cert"
	TLS_KEY_FILE  = "/run/secrets/ssl-key"
	JWT_SECRET    = []byte("SECRETSECRET")
	USE_SSL       = getEnvAsBoolean(os.Getenv("USE_SSL"))
	Log           waLog.Logger
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

		go session.UpdateLastAccessWhileAlive(ctx)

		return context.WithValue(ctx, "session", session), nil
	}
}

func StartRPC(port uint32, logLevel string) error {
	Log = waLog.Stdout("RPC", logLevel, true)

	lis, err := net.Listen("tcp", fmt.Sprintf("0.0.0.0:%d", port))
	if err != nil {
		Log.Errorf("failed to listen: %v", err)
		return err
	}

	sessionManager := NewSessionManager(JWT_SECRET, Log.Sub("SessionManager"))
	sessionManager.Start()
	authCheck := createAuthCheck(sessionManager, JWT_SECRET)
	keepAlive := grpc.KeepaliveParams(keepalive.ServerParameters{
		Time: 10 * time.Second,
	})

	var s *grpc.Server
	if USE_SSL {
		creds, err := credentials.NewServerTLSFromFile(TLS_CERT_FILE, TLS_KEY_FILE)
		if err != nil {
			Log.Errorf("could not load server credentials: %v", err)
			return err
		}
		s = grpc.NewServer(
			grpc.StreamInterceptor(auth.StreamServerInterceptor(authCheck)),
			grpc.UnaryInterceptor(auth.UnaryServerInterceptor(authCheck)),
			grpc.Creds(creds),
			keepAlive,
		)
	} else {
		s = grpc.NewServer(
			grpc.StreamInterceptor(auth.StreamServerInterceptor(authCheck)),
			grpc.UnaryInterceptor(auth.UnaryServerInterceptor(authCheck)),
			keepAlive,
		)
	}
	reflection.Register(s)

	pb.RegisterWhatUpCoreAuthServer(s, &WhatUpCoreAuthServer{
		sessionManager: sessionManager,
		log:            Log.Sub("AuthServer"),
	})
	pb.RegisterWhatUpCoreServer(s, &WhatUpCoreServer{
		sessionManager: sessionManager,
		log:            Log.Sub("CoreServer"),
	})

	Log.Infof("server listening at %v", lis.Addr())
	if err := s.Serve(lis); err != nil {
		Log.Errorf("failed to serve: %v", err)
	}
	return nil
}
