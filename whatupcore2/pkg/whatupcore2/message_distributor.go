package whatupcore2

import (
	"fmt"
	"sync"
	"time"

	waLog "go.mau.fi/whatsmeow/util/log"
)

// QueueMessage represents the message structure
type QueueMessage struct {
	Content   *Message
	Timestamp time.Time
}

// QueueClient represents a connected QueueClient with a channel and a message queue
type QueueClient struct {
	ID      int
	Channel chan *Message
	queue   []*QueueMessage
	mu      sync.Mutex
	closed  bool
	log     waLog.Logger
}

// Receive returns the QueueClient's message channel for external processing
func (c *QueueClient) Receive() <-chan *Message {
	return c.Channel
}

// NewClient creates a new QueueClient
func NewClient(id int, backlog []*QueueMessage, log waLog.Logger) *QueueClient {
	log.Infof("Creating new message client with backlog: %d", len(backlog))
	return &QueueClient{
		ID:      id,
		Channel: make(chan *Message, 2048), // Buffered channel
		queue:   backlog,
		log:     log,
	}
}

func (c *QueueClient) Start() {
	go c.processQueue()
}

// EnqueueMessage adds a message to the queue if the channel is full
func (c *QueueClient) EnqueueMessage(msg *QueueMessage) {
	if c.closed {
		c.log.Warnf("Trying to enqueue message on a closed client")
		return
	}

	select {
	case c.Channel <- msg.Content:
		// QueueMessage sent successfully
	default:
		// Channel is full, add to queue
		c.log.Warnf("Channel full, adding to client queue: %d msg queued", len(c.queue))
		c.mu.Lock()
		c.queue = append(c.queue, msg)
		c.mu.Unlock()
	}
}

// processQueue delivers messages from the queue to the QueueClient
func (c *QueueClient) processQueue() {
	nextWarning := time.Now()
	for !c.closed {
		if len(c.queue) > 0 {
			msg := c.queue[0]
			select {
			case c.Channel <- msg.Content:
				// QueueMessage delivered, remove from queue
				c.mu.Lock()
				c.queue = c.queue[1:]
				c.mu.Unlock()
				if time.Now().After(nextWarning) {
					c.log.Warnf("Depleting queue: %d msg left", len(c.queue))
					nextWarning = time.Now().Add(10 * time.Second)
				}
				continue
			default:
				// Channel still full, stop processing
			}
		}
		time.Sleep(time.Second)
	}
}

// Close signals the QueueClient to close after processing all messages
func (c *QueueClient) Close() {
	c.log.Warnf("Closing QueueClient")
	c.closed = true
	c.mu.Lock()
	c.queue = nil
	c.mu.Unlock()
	close(c.Channel)
}

// MessageDistributor handles distributing messages to multiple clients
type MessageDistributor struct {
	clients map[int]*QueueClient
	counter int
	history *MessageCache
	log     waLog.Logger
}

// NewMessageDistributor creates a new message distributor
func NewMessageDistributor(messageCache *MessageCache, log waLog.Logger) *MessageDistributor {
	return &MessageDistributor{
		history: messageCache,
		clients: make(map[int]*QueueClient),
		log:     log,
	}
}

// NewClient creates and returns a new QueueClient, adding it to the distributor
func (d *MessageDistributor) NewClient() *QueueClient {
	d.counter += 1
	logName := fmt.Sprintf("c%02d", d.counter)
	QueueClient := NewClient(d.counter, d.history.GetAllMessages(), d.log.Sub(logName))
	QueueClient.Start()
	d.clients[QueueClient.ID] = QueueClient
	return QueueClient
}

// RemoveClient removes a QueueClient from the distributor
func (d *MessageDistributor) RemoveClient(queueClient *QueueClient) {
	clientID := queueClient.ID
	if QueueClient, ok := d.clients[clientID]; ok {
		QueueClient.Close()
		delete(d.clients, clientID)
	}
	d.resetCounter()
}

func (d *MessageDistributor) resetCounter() {
	maxClientID := 0
	for clientID := range d.clients {
		maxClientID = max(maxClientID, clientID)
	}
	d.counter = maxClientID
}

// SendQueueMessage sends a message to all clients
func (d *MessageDistributor) SendMessage(message *Message) {
	d.log.Debugf("Distributing new message: %s", message.Info.ID)
	queueMessage := &QueueMessage{
		Content:   message,
		Timestamp: time.Now(),
	}
	d.history.AddMessage(queueMessage)
	nPruned := 0
	for key, QueueClient := range d.clients {
		if QueueClient.closed {
			delete(d.clients, key)
			nPruned += 1
		} else {
			go QueueClient.EnqueueMessage(queueMessage)
		}
	}
	if nPruned > 0 {
		d.resetCounter()
		d.log.Debugf("Pruned closed clients: %d", nPruned)
	}
}
