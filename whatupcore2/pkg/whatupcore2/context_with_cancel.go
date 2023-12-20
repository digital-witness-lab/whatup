package whatupcore2

import "context"


type ContextWithCancel struct {
    ctx context.Context
    cancel context.CancelFunc
}

func NewContextWithCancel(parentCtx context.Context) *ContextWithCancel {
    ctx, cancel := context.WithCancel(parentCtx)
    return &ContextWithCancel{
        ctx: ctx,
        cancel: cancel,
    }
}

