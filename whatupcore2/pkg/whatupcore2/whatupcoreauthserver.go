package whatupcore2

import (
	"context"
	"fmt"

	pb "github.com/digital-witness-lab/whatup/protos"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

type WhatUpCoreAuthServer struct {
    sessionManager *SessionManager
    pb.UnimplementedWhatUpCoreAuthServer
}

func (s *WhatUpCoreAuthServer) AuthFuncOverride(ctx context.Context, fullMethodName string) (context.Context, error) {
    // Override authentication on auth server since this is the service that
    // gives out authentication tokens
	return ctx, nil
}

func (s *WhatUpCoreAuthServer) Login(ctx context.Context, credentials *pb.WUCredentials) (*pb.SessionToken, error) {
    if (len(credentials.Passphrase) < 8) {
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

func (s *WhatUpCoreAuthServer) Register(credentials *pb.WUCredentials, qrStream pb.WhatUpCoreAuth_RegisterServer) error {
    if (len(credentials.Passphrase) < 8) {
        return status.Error(codes.InvalidArgument, "Passphrase too short. Must be >= 8 characters")
    }
    ctx := context.Background()
    ctx, cancel := context.WithCancel(ctx)
    defer cancel()

    session, regState, err := s.sessionManager.AddRegistration(ctx, credentials.Username, credentials.Passphrase)
    if err != nil {
        return err
    }

    for !regState.Completed {
        select {
        case qrCode, open := <- regState.QRCodes:
            if !open {
                break
            }
            clientErr := qrStream.Send(&pb.RegisterMessages{
                Qrcode: qrCode,
            })
            if clientErr != nil {
                return fmt.Errorf("Client Disconnected")
            }
        case err, open := <- regState.Errors:
            if !open {
                break
            }
            fmt.Printf("Recieved error while logging in: %+v\n", err)
            return err
        case <- ctx.Done():
            fmt.Println("WhatsAppServe login context marked done")
            return context.Cause(ctx)
        }
    }

    if regState.Success {
        qrStream.Send(&pb.RegisterMessages{
            LoggedIn: true,
            Token: session.ToProto(),
        })
        return nil
    }
    return fmt.Errorf("Unknown error. Registration completed but not successful")
}
