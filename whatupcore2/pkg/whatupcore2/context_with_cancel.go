package whatupcore2

import "context"

type ContextWithCancel struct {
	context.Context
	cancel      context.CancelFunc
	HasCanceled bool
}

func NewContextWithCancel(parentCtx context.Context) ContextWithCancel {
	ctx, cancel := context.WithCancel(parentCtx)
	return ContextWithCancel{
		Context:     ctx,
		cancel:      cancel,
		HasCanceled: false,
	}
}

func (c ContextWithCancel) Cancel() {
	c.cancel()
	c.HasCanceled = true
}

func (c ContextWithCancel) IsZero() bool {
	return c.cancel == nil
}
