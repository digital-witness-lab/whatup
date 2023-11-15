package whatupcore2

import (
	"context"
	"sync"
	"testing"
	"time"

	"go.mau.fi/whatsmeow/types"
	"go.mau.fi/whatsmeow/types/events"
)

func MessageFromTime(t time.Time) *Message {
	return &Message{
		MessageEvent: &events.Message{
			Info: types.MessageInfo{
				Timestamp: t,
			},
		},
	}
}

func MessageFromUnix(timestamp int64) *Message {
	return MessageFromTime(time.Unix(timestamp, 0))
}

func MessageNow() *Message {
	return MessageFromTime(time.Now())
}

func CheckMsgReadInOrder(t *testing.T, client *MessageClient, low, high int) {
	for i := low; i < high; i++ {
		msg, _ := client.ReadMessage()
		if msg == nil {
			t.Fatalf("Should be able to read message")
		}
		if msg.Info.Timestamp.Unix() != int64(i) {
			t.Fatalf("Message order invalid: %d: %d", msg.Info.Timestamp.Unix(), i)
		}
	}
}

func TestMessageQueueOrder(t *testing.T) {
	ctx := context.Background()
	mq := NewMessageQueue(ctx, 0, 0, 0)

	for i := 50; i < 0; i-- {
		mq.SendMessage(MessageFromUnix(int64(i)))
	}
	prev := int64(0)
	for e := mq.messages.Front(); e != nil; e = e.Next() {
		n := e.Value.(*Message).Info.Timestamp.Unix()
		if n > prev {
			t.Fatalf("Invalid message ordering: %d > %d", n, prev)
		}
		prev = n
	}
}

func TestMessageQueueMaxLen(t *testing.T) {
	ctx := context.Background()
	mq := NewMessageQueue(ctx, 0, 10, 0)

	for i := 1; i < 100; i++ {
		mq.SendMessage(MessageNow())
		if mq.messages.Len() != min(i, 10) {
			t.Fatalf("Queue should be capped at 10 messages: %d messages", mq.messages.Len())
		}
	}
}

func TestMessageQueueMaxAge(t *testing.T) {
	ctx := context.Background()
	mq := NewMessageQueue(ctx, 0, 0, 50*time.Second)

	// fix the queue's time
	now := time.Now()
	nowFunc = func() time.Time { return now }
	defer func() { nowFunc = time.Now }()

	for i := 1; i < 100; i++ {
		mq.SendMessage(MessageFromTime(now.Add(-time.Duration(i) * time.Second)))
		if mq.messages.Len() != min(i, 50) {
			t.Fatalf("Queue should be capped at 50 from the time restriction: %d messages", mq.messages.Len())
		}
	}
}

func TestMessageMultiClient(t *testing.T) {
	ctx := context.Background()
	mq := NewMessageQueue(ctx, 0, 50, 0)
	client := mq.NewClient()
	clientSlow := mq.NewClient()

	for i := 1; i < 100; i++ {
		mq.SendMessage(MessageFromUnix(int64(i)))
		if mq.messages.Len() != min(i, 50) {
			t.Fatalf("Queue should be capped at 50 from the time restriction: %d messages", mq.messages.Len())
		}
	}

	CheckMsgReadInOrder(t, client, 50, 100)
	msg, ok := client.ReadMessage()
	if msg != nil {
		t.Fatalf("There should be no messages left to read: %v: %t", msg, ok)
	}

	CheckMsgReadInOrder(t, clientSlow, 50, 100)
	msg, ok = clientSlow.ReadMessage()
	if msg != nil {
		t.Fatalf("There should be no messages left to read: %v: %t", msg, ok)
	}
}

func TestMessageSingleClient(t *testing.T) {
	ctx := context.Background()
	mq := NewMessageQueue(ctx, 0, 50, 0)
	client := mq.NewClient()

	for i := 1; i < 100; i++ {
		mq.SendMessage(MessageFromUnix(int64(i)))
		if mq.messages.Len() != min(i, 50) {
			t.Fatalf("Queue should be capped at 50 from the time restriction: %d messages", mq.messages.Len())
		}
	}

	for i := 50; i < 100; i++ {
		msg, _ := client.ReadMessage()
		if msg == nil {
			t.Fatalf("Should be able to read message")
		}
		if msg.Info.Timestamp.Unix() != int64(i) {
			t.Fatalf("Message order invalid: %d: %d", msg.Info.Timestamp.Unix(), i)
		}
	}

	mq.SendMessage(MessageFromUnix(100))
	msg, _ := client.ReadMessage()
	if msg == nil {
		t.Fatalf("Failed to read additional message")
	}
	if msg.Info.Timestamp.Unix() != 100 {
		t.Fatalf("Message order invalid: %d: %d", msg.Info.Timestamp.Unix(), 100)
	}
}

func TestMessageBackgroundPrune(t *testing.T) {
	ctx := context.Background()
	mq := NewMessageQueue(ctx, 200*time.Millisecond, 0, 60*time.Second)
	mq.Start()
	defer mq.Stop()

	// fix the queue's time
	now := time.Now()
	timeOffset := time.Duration(0)
	nowFunc = func() time.Time { return now.Add(timeOffset) }
	defer func() { nowFunc = time.Now }()

	for i := 0; i < 10; i++ {
		mq.SendMessage(MessageFromTime(now))
	}

	if mq.messages.Len() != 10 {
		t.Fatalf("Expected 10 messages in queue: %d", mq.messages.Len())
	}

	// advance time by 2min
	timeOffset = 120 * time.Second
	time.Sleep(400 * time.Millisecond) // let the ticker tick
	if mq.messages.Len() != 0 {
		t.Fatalf("Expected 0 messages in queue: %d", mq.messages.Len())
	}
}

func TestMessagePruneClients(t *testing.T) {
	ctx := context.Background()
	mq := NewMessageQueue(ctx, 0, 50, 0)

	clients := []*MessageClient{
		mq.NewClient(),
		mq.NewClient(),
		mq.NewClient(),
	}

	if len(mq.clients) != 3 {
		t.Fatalf("Not the right number of clients: %d", len(mq.clients))
	}

	clients[0].Close()
	if clients[0].IsOpen() {
		t.Fatalf("Client should be closed")
	}
	mq.SendMessage(MessageFromUnix(int64(1)))

	if msg, ok := clients[0].ReadMessage(); ok {
		t.Fatalf("Trying to read from a closed client shouldn't be ok: %v: %t", msg, ok)
	}

	mq.PruneClients()
	if len(mq.clients) != 2 {
		t.Fatalf("Not the right number of clients: %d", len(mq.clients))
	}
	mq.SendMessage(MessageFromUnix(int64(2)))

	for _, client := range clients[1:] {
		CheckMsgReadInOrder(t, client, 1, 3)
	}

	mq.Close()
	for _, client := range clients[1:] {
		if client.IsOpen() {
			t.Fatalf("Client should be closed")
		}
	}
}

func TestMessageMsgChan(t *testing.T) {
	ctx := context.Background()
	mq := NewMessageQueue(ctx, 0, 50, 0)
	client := mq.NewClient()

	for i := 1; i < 100; i++ {
		mq.SendMessage(MessageFromUnix(int64(i)))
		if mq.messages.Len() != min(i, 50) {
			t.Fatalf("Queue should be capped at 50 from the time restriction: %d messages", mq.messages.Len())
		}
	}

	c, err := client.MessageChan()
	if err != nil {
		t.Fatalf("Should be able to create message chan")
	}

	_, err = client.MessageChan()
	if err == nil {
		t.Fatalf("Should not be able to create second chan")
	}

	for i := 50; i < 100; i++ {
		msg := <-c
		if msg == nil {
			t.Fatalf("Should be able to read message")
		}
		if msg.Info.Timestamp.Unix() != int64(i) {
			t.Fatalf("Message order invalid: %d: %d", msg.Info.Timestamp.Unix(), i)
		}
	}

	var wg sync.WaitGroup
	go func() {
		wg.Add(1)
		msg := <-c
		if msg == nil {
			t.Fatalf("Should be able to read message")
		}
		if msg.Info.Timestamp.Unix() != int64(100) {
			t.Fatalf("Message order invalid: %d: %d", msg.Info.Timestamp.Unix(), 100)
		}
		wg.Done()
	}()

	mq.SendMessage(MessageFromUnix(100))
	wg.Wait()
}
