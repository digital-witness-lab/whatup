package whatupcore2

import (
	"container/list"
	"context"
	"errors"
	"fmt"
	"math/rand"
	"sync"
	"time"

	waLog "go.mau.fi/whatsmeow/util/log"
)

var nowFunc func() time.Time = time.Now

type QueueMessage struct {
	addedAt time.Time
	message *Message
}

type MessageClient struct {
	position *list.Element
	queue    *MessageQueue
	valid    bool

	newMessageAlert chan bool
	ctxC            ContextWithCancel
	log             waLog.Logger
}

func NewMessageClient(queue *MessageQueue) *MessageClient {
	ctxC := NewContextWithCancel(queue.ctxC)
	log := queue.log.Sub(fmt.Sprintf("c-%0.3d", rand.Intn(999)))
	return &MessageClient{
		position: queue.getFront(),
		queue:    queue,
		valid:    true,

		ctxC: ctxC,
		log:  log,
	}
}

func (mc *MessageClient) MessageChan() (chan *QueueMessage, error) {
	if mc.newMessageAlert != nil {
		return nil, errors.New("Can only have one message chan per client")
	}
	mc.log.Debugf("creating channel")
	mc.newMessageAlert = make(chan bool, 128)
	msgChan := make(chan *QueueMessage)
	go func() {
		defer func() { mc.newMessageAlert = nil }()
		mc.newMessageAlert <- true
		for {
			mc.log.Debugf("waiting for new message or done")
			select {
			case <-mc.ctxC.Done():
				mc.log.Debugf("done by context")
				mc.Close()
				return
            case alert := <-mc.newMessageAlert:
                if alert == false {
				    mc.log.Debugf("newMessageAlert channel is closed. Closing context and exiting")
                    mc.Close()
                    return
                }
				mc.log.Debugf("saw new message alert")
				ok := mc.depleteQueueToChan(msgChan)
				if !ok {
					mc.log.Debugf("!ok from deplete")
					mc.Close()
					return
				}
			}
		}
	}()
	return msgChan, nil
}

func (mc *MessageClient) depleteQueueToChan(msgChan chan *QueueMessage) bool {
	for {
		msg, ok := mc.ReadMessage()
		if !ok {
			mc.log.Debugf("depletion found queue closed")
			return ok
		} else if msg == nil {
			mc.log.Debugf("depletion found nil message")
			return ok
		}
		mc.log.Debugf("depleting queue saw message: %s: %s", msg.addedAt, msg.message.DebugString())
		msgChan <- msg
	}
}

func (mc *MessageClient) ReadMessage() (*QueueMessage, bool) {
	if !mc.valid {
		return nil, false
	}
	var cursor *list.Element
	if mc.position == nil || mc.position.Value == nil {
		mc.log.Debugf("client resetting queue position")
		mc.position = mc.queue.getFront()
		cursor = mc.position
	} else {
		cursor = mc.position.Next()
		if cursor != nil {
			mc.position = cursor
		} else {
			mc.log.Debugf("could not advance position")
		}
	}
	var msg *QueueMessage
	if cursor != nil {
		msg = cursor.Value.(*QueueMessage)
	}
	mc.log.Debugf("reading from queue: (msg == nil) = %t: (position == nil) = %t: len(q) = %d", msg == nil, mc.position == nil, mc.queue.messages.Len())
	return msg, true
}

func (mc *MessageClient) Close() {
	mc.log.Debugf("Client closing")
	mc.valid = false
	mc.position = nil
	mc.queue = nil
	mc.ctxC.Cancel()
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

	ctxC ContextWithCancel

	log waLog.Logger
}

func NewMessageQueue(ctx context.Context, pruneTime time.Duration, maxNumElements int, maxMessageAge time.Duration, log waLog.Logger) *MessageQueue {
	clients := make([]*MessageClient, 0)
	ctxC := NewContextWithCancel(ctx)
	return &MessageQueue{
		maxNumElements: maxNumElements,
		maxMessageAge:  maxMessageAge,
		messages:       list.New(),
		clients:        clients,
		valid:          true,

		pruneTime: pruneTime,

		ctxC: ctxC,
		log:  log,
	}
}

func (mq *MessageQueue) NewClient() *MessageClient {
	if !mq.valid {
		return nil
	}
	mq.log.Debugf("Creating new client")
	client := NewMessageClient(mq)
	mq.clients = append(mq.clients, client)
	return client
}

func (mq *MessageQueue) Start() {
	go func() {
		ticker := time.NewTicker(mq.pruneTime)
		select {
		case <-ticker.C:
			mq.log.Debugf("Pruning")
			mq.PruneAll()
		case <-mq.ctxC.Done():
			mq.log.Debugf("Closing")
			mq.Close()
			return
		}
	}()
}

func (mq *MessageQueue) Stop() {
	mq.log.Debugf("Stop")
	mq.ctxC.Cancel()
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
	N := mq.messages.Len()
	n := 0
	var next *list.Element
	for e := mq.messages.Front(); e != nil; e = next {
		next = e.Next()
		if mq.maxNumElements > 0 && mq.messages.Len() > mq.maxNumElements {
			e.Value = nil
			mq.messages.Remove(e)
			n++
		} else if mq.maxMessageAge > 0 && now.Sub(e.Value.(*QueueMessage).addedAt) > mq.maxMessageAge {
			e.Value = nil
			mq.messages.Remove(e)
			n++
		} else {
			break
		}
	}
	mq.log.Debugf("Prune messages: %d / %d messages removed", n, N)
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
	if n > 0 {
		mq.log.Debugf("Pruning clients: %d", n)
		mq.clients = mq.clients[:n]
	}
	mq.log.Debugf("After prune, remaining clients: %d", len(mq.clients))
}

func (mq *MessageQueue) SendMessageTimestamp(msg *Message, now time.Time) {
	if !mq.valid {
		return
	}

	mq.lock.Lock()
	newElement := &QueueMessage{addedAt: now, message: msg}
	e := mq.messages.Back()
	if e == nil {
		mq.log.Debugf("Message queue empty. Adding message to front: %s", now)
		mq.messages.PushFront(newElement)
	} else {
		var prev *list.Element
		for ; e != nil; e = prev {
			if newElement.addedAt.After(e.Value.(*QueueMessage).addedAt) {
				mq.log.Debugf("Adding message after: %d: %s (goes after) %s", mq.messages.Len(), now, e.Value.(*QueueMessage).addedAt)
				mq.messages.InsertAfter(newElement, e)
				break
			}
			prev = e.Prev()
			if prev == nil {
				mq.log.Debugf("Adding message to front: %d: %s", mq.messages.Len(), now)
				mq.messages.PushFront(newElement)
				break
			}
		}
	}
	mq.lock.Unlock()

	for _, client := range mq.clients {
		if client.newMessageAlert != nil {
			client.log.Debugf("Queue notifying client of message")
			client.newMessageAlert <- true
		}
	}
	mq.PruneMessages()
}

func (mq *MessageQueue) SendMessage(msg *Message) {
	mq.SendMessageTimestamp(msg, nowFunc())
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
	mq.log.Warnf("Closing message queue")
	mq.lock.Lock()
	defer mq.lock.Unlock()
	mq.ctxC.Cancel()
	for _, client := range mq.clients {
		client.Close()
	}
	mq.messages.Init()
	mq.valid = false
}

func (mq *MessageQueue) Clear() {
	mq.log.Debugf("Clearing queue")
	mq.lock.Lock()
	defer mq.lock.Unlock()
	mq.messages.Init()
}
