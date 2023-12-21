package whatupcore2

import "context"

type ContextWithCancel struct {
	context.Context
	Cancel context.CancelFunc
}

func NewContextWithCancel(parentCtx context.Context) ContextWithCancel {
	ctx, cancel := context.WithCancel(parentCtx)
	return ContextWithCancel{
		Context: ctx,
		Cancel:  cancel,
	}
}

func (c ContextWithCancel) IsZero() bool {
	return c.Cancel == nil
}
