package whatupcore2

import (
	"context"

	pb "github.com/digital-witness-lab/whatup/protos"
	waLog "go.mau.fi/whatsmeow/util/log"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials"
)

type PhotoCopInterface interface {
	Decide(context.Context, []byte) (*pb.PhotoCopDecision, error)
	DecidePriority(context.Context, []byte, int32) (*pb.PhotoCopDecision, error)
}

type PhotoCopMedia struct {
	Body     *[]byte
	Decision *pb.PhotoCopDecision
}

func NewPhotoCopMedia() *PhotoCopMedia {
	return &PhotoCopMedia{
		Body:     &[]byte{},
		Decision: &pb.PhotoCopDecision{},
	}
}

type PhotoCop struct {
	host   string
	client pb.PhotoCopClient
	conn   *grpc.ClientConn
	log    waLog.Logger
}

func NewPhotoCopOrEmpty(host string, cert string, log waLog.Logger) (PhotoCopInterface, error) {
	if host != "" {
        log.Infof("Creating PhotoCop instance connected to: %s", host)
		return NewPhotoCop(host, cert, log)
	}
    log.Infof("Creating empty PhotoCop")
	return &EmptyPhotoCop{log: log}, nil
}

func NewPhotoCop(host string, cert string, log waLog.Logger) (*PhotoCop, error) {
	creds, err := credentials.NewClientTLSFromFile(cert, "")
	if err != nil {
		return nil, err
	}
	conn, err := grpc.NewClient(
		host,
		grpc.WithTransportCredentials(creds),
	)
	if err != nil {
		return nil, err
	}
	client := pb.NewPhotoCopClient(conn)
	return &PhotoCop{
		host:   host,
		client: client,
		log:    log,
	}, nil
}

func (pc *PhotoCop) DecidePriority(ctx context.Context, data []byte, priority int32) (*pb.PhotoCopDecision, error) {
	pc.log.Debugf("Request to PhotoCop DecidePriority()")
	return pc.client.CheckPhoto(ctx, &pb.CheckPhotoRequest{
		Photo:    data,
		Priority: priority,
	})
}

func (pc *PhotoCop) Decide(ctx context.Context, data []byte) (*pb.PhotoCopDecision, error) {
	return pc.DecidePriority(ctx, data, 0)
}

type EmptyPhotoCop struct {
	log waLog.Logger
}

func (pc *EmptyPhotoCop) DecidePriority(ctx context.Context, data []byte, priority int32) (*pb.PhotoCopDecision, error) {
	pc.log.Debugf("Request to empty PhotoCop DecidePriority()")
	return &pb.PhotoCopDecision{}, nil
}

func (pc *EmptyPhotoCop) Decide(ctx context.Context, data []byte) (*pb.PhotoCopDecision, error) {
	pc.log.Debugf("Request to empty PhotoCop Decide()")
	return &pb.PhotoCopDecision{}, nil
}
