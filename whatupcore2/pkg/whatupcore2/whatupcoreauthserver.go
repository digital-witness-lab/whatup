package whatupcore2

import (
	"context"
	"fmt"

	pb "github.com/digital-witness-lab/whatup/protos"
	waLog "go.mau.fi/whatsmeow/util/log"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

type WhatUpCoreAuthServer struct {
	sessionManager *SessionManager
	log            waLog.Logger
	pb.UnimplementedWhatUpCoreAuthServer
}

func (s *WhatUpCoreAuthServer) AuthFuncOverride(ctx context.Context, fullMethodName string) (context.Context, error) {
	// Override authentication on auth server since this is the service that
	// gives out authentication tokens
	return ctx, nil
}

func (s *WhatUpCoreAuthServer) Login(ctx context.Context, credentials *pb.WUCredentials) (*pb.SessionToken, error) {
	if len(credentials.Passphrase) < 8 {
		return nil, status.Error(codes.InvalidArgument, "Passphrase too short. Must be >= 8 characters")
	}
	session, err := s.sessionManager.AddLogin(credentials.Username, credentials.Passphrase)
	if err != nil {
		return nil, err
	}
	return session.ToProto(), nil
}

func (s *WhatUpCoreAuthServer) RenewToken(ctx context.Context, token *pb.SessionToken) (*pb.SessionToken, error) {
	sessionId, err := s.sessionManager.TokenToSessionId(token.Token)
	if err != nil {
		return nil, status.Errorf(codes.Unauthenticated, "Invalid token: %v", err)
	}

	session, err := s.sessionManager.RenewSessionToken(sessionId)
	if err != nil {
		return nil, err
	}
	return session.ToProto(), nil
}

func (s *WhatUpCoreAuthServer) Register(registerOptions *pb.RegisterOptions, qrStream pb.WhatUpCoreAuth_RegisterServer) error {
	credentials := registerOptions.Credentials
	if len(credentials.Passphrase) < 8 {
		return status.Error(codes.InvalidArgument, "Passphrase too short. Must be >= 8 characters")
	}
	ctx := context.Background()
	ctxC := NewContextWithCancel(ctx)
	defer ctxC.Cancel()

	session, regState, err := s.sessionManager.AddRegistration(ctx, credentials.Username, credentials.Passphrase, registerOptions)
	if err != nil {
		return err
	} else if regState == nil && session != nil {
		qrStream.Send(&pb.RegisterMessages{
			LoggedIn: true,
			Token:    session.ToProto(),
		})
		return nil
	}

	for !regState.Completed {
		select {
		case qrCode, open := <-regState.QRCodes:
			if !open || regState.Success {
				break
			}
			clientErr := qrStream.Send(&pb.RegisterMessages{
				Qrcode: qrCode,
			})
			if clientErr != nil {
				return fmt.Errorf("Client Disconnected")
			}
		case err, open := <-regState.Errors:
			if !open || regState.Success {
				break
			}
			fmt.Printf("Recieved error while logging in: %+v\n", err)
			return err
		case <-ctx.Done():
			fmt.Println("WhatsAppServe login context marked done")
			return context.Cause(ctx)
		}
	}

	if regState.Success {
		qrStream.Send(&pb.RegisterMessages{
			LoggedIn: true,
			Token:    session.ToProto(),
		})
		return nil
	}
	return fmt.Errorf("Unknown error. Registration completed but not successful")
}
