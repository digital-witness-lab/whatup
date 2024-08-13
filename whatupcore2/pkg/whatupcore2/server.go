package whatupcore2

import (
	"context"
	"database/sql"
	"fmt"
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"

	pb "github.com/digital-witness-lab/whatup/protos"
	"github.com/digital-witness-lab/whatup/whatupcore2/pkg/encsqlstore"
	"github.com/lib/pq"

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
	PHOTOCOP_CERT_FILE = os.Getenv("PHOTOCOP_TLS_CERT")
	TLS_CERT_FILE = mustGetEnv("WHATUP_TLS_CERT")
	TLS_KEY_FILE  = mustGetEnv("WHATUP_TLS_KEY")
	JWT_SECRET    = []byte("SECRETSECRET")
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

func getDBConnections(dbUri string, dbLog waLog.Logger) (*encsqlstore.EncContainer, *sql.DB, error) {
	dbLog.Infof("Initializing DB Connection and global Device Store")
	encsqlstore.PostgresArrayWrapper = pq.Array
	db, err := sql.Open("postgres", dbUri)
	if err != nil {
		dbLog.Errorf("Could not open database: %w", err)
		return nil, nil, fmt.Errorf("failed to open database: %w", err)
	}
	err = db.Ping()
	if err != nil {
		dbLog.Errorf("Could not ping database: %w", err)
		return nil, nil, fmt.Errorf("failed to open database: %w", err)
	}
	deviceContainer := encsqlstore.NewWithDB(db, "postgres", dbLog)
	return deviceContainer, db, nil
}

func StartRPC(port uint32, dbUri string, photoCopUri string, logLevel string) error {
	Log = waLog.Stdout("RPC", logLevel, true)

	lis, err := net.Listen("tcp", fmt.Sprintf("0.0.0.0:%d", port))
	if err != nil {
		Log.Errorf("failed to listen: %v", err)
		return err
	}

	deviceContainer, db, err := getDBConnections(dbUri, Log.Sub("db"))
	if err != nil {
		Log.Errorf("Could not create database connections: %v", err)
		return err
	}

	photoCop, err := NewPhotoCopOrEmpty(photoCopUri, PHOTOCOP_CERT_FILE, Log.Sub("photocop"))
	if err != nil {
		Log.Errorf("Could not init photo cop: %v", err)
		return err
	}
	clientOpts := &WhatsAppClientConfig{
		deviceContainer: deviceContainer,
		db:              db,
		photoCop:        photoCop,
	}
	sessionManager := NewSessionManager(JWT_SECRET, clientOpts, Log.Sub("SM"))
	sessionManager.Start()
	defer sessionManager.Close()
	authCheck := createAuthCheck(sessionManager, JWT_SECRET)
	keepAliveEnforcement := grpc.KeepaliveEnforcementPolicy(keepalive.EnforcementPolicy{
		MinTime:             5 * time.Second,
		PermitWithoutStream: true,
	})
	keepAlive := grpc.KeepaliveParams(keepalive.ServerParameters{
		Time: 10 * time.Second,
	})

	var s *grpc.Server
	creds, err := credentials.NewServerTLSFromFile(TLS_CERT_FILE, TLS_KEY_FILE)
	if err != nil {
		Log.Errorf("could not load server credentials: %v", err)
		return err
	}
	s = grpc.NewServer(
		grpc.StreamInterceptor(auth.StreamServerInterceptor(authCheck)),
		grpc.UnaryInterceptor(auth.UnaryServerInterceptor(authCheck)),
		grpc.Creds(creds),
		keepAliveEnforcement,
		keepAlive,
	)
	reflection.Register(s)

	pb.RegisterWhatUpCoreAuthServer(s, &WhatUpCoreAuthServer{
		sessionManager: sessionManager,
		log:            Log.Sub("AuthServer"),
	})
	pb.RegisterWhatUpCoreServer(s, &WhatUpCoreServer{
		sessionManager: sessionManager,
		log:            Log.Sub("CoreServer"),
	})

	go func() {
		Log.Infof("server listening at %v", lis.Addr())
		if err := s.Serve(lis); err != nil {
			Log.Errorf("failed to serve: %v", err)
		}
	}()

	Log.Infof("Registering signal listener")
	sigchan := make(chan os.Signal, 1)
	signal.Notify(sigchan, syscall.SIGTERM, syscall.SIGINT)
	sig := <-sigchan

	Log.Infof("Got signal... exiting gracefully: %v", sig)
	sessionManager.Stop()

	ctxC := NewContextWithCancel(context.Background())
	timer := time.After(10 * time.Second)
	go func() {
		s.GracefulStop()
		ctxC.Cancel()
	}()

	select {
	case <-ctxC.Done():
	case <-timer:
		Log.Infof("Forcefully shutting down")
		s.Stop()
	}
	return nil
}
