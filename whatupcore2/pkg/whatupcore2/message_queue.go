package whatupcore2

import (
	"container/list"
	"context"
	"errors"
	"sync"
	"time"
)

var nowFunc func() time.Time = time.Now

type MessageClient struct {
	position *list.Element
	queue    *MessageQueue
	valid    bool

	newMessageAlert chan bool
	ctx             context.Context
	ctxCancel       context.CancelFunc
}

func NewMessageClient(queue *MessageQueue) *MessageClient {
	ctx, ctxCancel := context.WithCancel(queue.ctx)
	return &MessageClient{
		position: queue.getFront(),
		queue:    queue,
		valid:    true,

		ctx:       ctx,
		ctxCancel: ctxCancel,
	}
}

func (mc *MessageClient) MessageChan() (chan *Message, error) {
	if mc.newMessageAlert != nil {
		return nil, errors.New("Can only have one message chan per client")
	}
	mc.newMessageAlert = make(chan bool)
	msgChan := make(chan *Message)
	go func() {
		defer func() { mc.newMessageAlert = nil }()
		for {
			ok := mc.depleteQueueToChan(msgChan)
			if !ok {
				return
			}
			select {
			case <-mc.ctx.Done():
				mc.Close()
				return
			case <-mc.newMessageAlert:
				ok := mc.depleteQueueToChan(msgChan)
				if !ok {
					return
				}
			}
		}
	}()
	return msgChan, nil
}

func (mc *MessageClient) depleteQueueToChan(msgChan chan *Message) bool {
	for {
		msg, ok := mc.ReadMessage()
		if !ok {
			return ok
		} else if msg == nil {
			return ok
		}
		msgChan <- msg
	}
}

func (mc *MessageClient) ReadMessage() (*Message, bool) {
	if !mc.valid {
		return nil, false
	}
	var cursor *list.Element
	if mc.position == nil {
		mc.position = mc.queue.getFront()
		cursor = mc.position
	} else {
		cursor = mc.position.Next()
		if cursor != nil {
			mc.position = cursor
		}
	}
	var msg *Message
	if cursor != nil {
		msg = cursor.Value.(*Message)
	}
	return msg, true
}

func (mc *MessageClient) Close() {
	mc.ctxCancel()
	mc.valid = false
	mc.position = nil
	mc.queue = nil
}

func (mc *MessageClient) IsOpen() bool {
	return mc.valid
}

type MessageQueue struct {
	maxNumElements int
	maxMessageAge  time.Duration

	messages *list.List
	clients  []*MessageClient
	lock     sync.Mutex
	valid    bool

	pruneTime time.Duration

	ctx       context.Context
	ctxCancel context.CancelFunc
}

func NewMessageQueue(ctx context.Context, pruneTime time.Duration, maxNumElements int, maxMessageAge time.Duration) *MessageQueue {
	clients := make([]*MessageClient, 0)
	ctx, ctxCancel := context.WithCancel(ctx)
	return &MessageQueue{
		maxNumElements: maxNumElements,
		maxMessageAge:  maxMessageAge,
		messages:       list.New(),
		clients:        clients,
		valid:          true,

		pruneTime: pruneTime,

		ctx:       ctx,
		ctxCancel: ctxCancel,
	}
}

func (mq *MessageQueue) NewClient() *MessageClient {
	if !mq.valid {
		return nil
	}
	client := NewMessageClient(mq)
	mq.clients = append(mq.clients, client)
	return client
}

func (mq *MessageQueue) Start() {
	go func() {
		ticker := time.NewTicker(mq.pruneTime)
		select {
		case <-ticker.C:
			mq.PruneAll()
		case <-mq.ctx.Done():
			mq.Close()
			return
		}
	}()
}

func (mq *MessageQueue) Stop() {
	mq.ctxCancel()
	mq.valid = false
	mq.messages.Init()
}

func (mq *MessageQueue) IsOpen() bool {
	return mq.valid
}

func (mq *MessageQueue) PruneAll() {
	mq.PruneClients()
	mq.PruneMessages()
}

func (mq *MessageQueue) PruneMessages() {
	mq.lock.Lock()
	defer mq.lock.Unlock()

	now := nowFunc()
	var next *list.Element
	for e := mq.messages.Front(); e != nil; e = next {
		next = e.Next()
		if mq.maxNumElements > 0 && mq.messages.Len() > mq.maxNumElements {
			mq.messages.Remove(e)
		} else if mq.maxMessageAge > 0 && now.Sub(e.Value.(*Message).Info.Timestamp) > mq.maxMessageAge {
			mq.messages.Remove(e)
		} else {
			break
		}
	}
}

func (mq *MessageQueue) PruneClients() {
	mq.lock.Lock()
	defer mq.lock.Unlock()
	n := 0
	for _, client := range mq.clients {
		if client.IsOpen() {
			mq.clients[n] = client
			n++
		}
	}
	mq.clients = mq.clients[:n]
}

func (mq *MessageQueue) SendMessage(msg *Message) {
	if !mq.valid {
		return
	}

	mq.lock.Lock()
	var prev *list.Element
	msgTimestamp := msg.Info.Timestamp
	e := mq.messages.Back()
	if e == nil {
		mq.messages.PushFront(msg)
	} else {
		for ; e != nil; e = prev {
			if msgTimestamp.Compare(e.Value.(*Message).Info.Timestamp) > 0 {
				mq.messages.InsertAfter(msg, e)
				break
			}
			prev = e.Prev()
			if prev == nil {
				mq.messages.PushFront(msg)
				break
			}
		}
	}
	mq.lock.Unlock()

	for _, client := range mq.clients {
		if client.newMessageAlert != nil {
			client.newMessageAlert <- true
		}
	}
	mq.PruneMessages()
}

func (mq *MessageQueue) getFront() *list.Element {
	if !mq.valid {
		return nil
	}
	mq.lock.Lock()
	defer mq.lock.Unlock()
	return mq.messages.Front()
}

func (mq *MessageQueue) Close() {
	mq.lock.Lock()
	defer mq.lock.Unlock()
	mq.ctxCancel()
	for _, client := range mq.clients {
		client.Close()
	}
	mq.messages.Init()
	mq.valid = false
}
