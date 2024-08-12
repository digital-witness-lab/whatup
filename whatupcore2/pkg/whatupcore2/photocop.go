package whatupcore2

import (
	"context"

	pb "github.com/digital-witness-lab/whatup/protos"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type PhotoCopInterface interface {
	Decide(context.Context, []byte) (*pb.PhotoCopDecision, error)
	DecidePriority(context.Context, []byte, int32) (*pb.PhotoCopDecision, error)
}

type PhotoCopMedia struct {
	Body     []byte
	Decision *pb.PhotoCopDecision
}

func NewPhotoCopMedia() *PhotoCopMedia {
	return &PhotoCopMedia{
		Body:     []byte{},
		Decision: &pb.PhotoCopDecision{},
	}
}

type PhotoCop struct {
	host   string
	client pb.PhotoCopClient
	conn   *grpc.ClientConn
}

func NewPhotoCopOrEmpty(host string) (PhotoCopInterface, error) {
	if host != "" {
		return NewPhotoCop(host)
	}
	return &EmptyPhotoCop{}, nil
}

func NewPhotoCop(host string) (*PhotoCop, error) {
    // TODO: change insecure.NewCredentials() to correponding photo-cop credentials
	conn, err := grpc.NewClient(
        host, 
        grpc.WithTransportCredentials(insecure.NewCredentials()),
    )
	if err != nil {
		return nil, err
	}
	client := pb.NewPhotoCopClient(conn)
	return &PhotoCop{
		host:   host,
		client: client,
	}, nil
}

func (pc *PhotoCop) DecidePriority(ctx context.Context, data []byte, priority int32) (*pb.PhotoCopDecision, error) {
	return pc.client.CheckPhoto(ctx, &pb.CheckPhotoRequest{
		Photo:    data,
		Priority: priority,
	})
}

func (pc *PhotoCop) Decide(ctx context.Context, data []byte) (*pb.PhotoCopDecision, error) {
	return pc.DecidePriority(ctx, data, 0)
}

type EmptyPhotoCop struct {
}

func (pc *EmptyPhotoCop) DecidePriority(ctx context.Context, data []byte, priority int32) (*pb.PhotoCopDecision, error) {
	return &pb.PhotoCopDecision{}, nil
}

func (pc *EmptyPhotoCop) Decide(ctx context.Context, data []byte) (*pb.PhotoCopDecision, error) {
	return &pb.PhotoCopDecision{}, nil
}
