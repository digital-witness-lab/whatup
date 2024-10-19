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
	wg      sync.WaitGroup
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
		Channel: make(chan *Message, 10), // Buffered channel
		queue:   backlog,
		log:     log,
	}
}

// EnqueueMessage adds a message to the queue if the channel is full
func (c *QueueClient) EnqueueMessage(msg *QueueMessage) {
	c.mu.Lock()
	defer c.mu.Unlock()

	select {
	case c.Channel <- msg.Content:
		// QueueMessage sent successfully
	default:
		// Channel is full, add to queue
		c.log.Warnf("Channel full, adding to client queue: %d", len(c.queue))
		c.queue = append(c.queue, msg)
	}
}

// processQueue delivers messages from the queue to the QueueClient
func (c *QueueClient) processQueue() {
	c.mu.Lock()
	defer c.mu.Unlock()

	for len(c.queue) > 0 {
		msg := c.queue[0]
		select {
		case c.Channel <- msg.Content:
			// QueueMessage delivered, remove from queue
			c.log.Warnf("Depleting queue: %d", len(c.queue))
			c.queue = c.queue[1:]
		default:
			// Channel still full, stop processing
			return
		}
	}
}

// Close signals the QueueClient to close after processing all messages
func (c *QueueClient) Close() {
	c.log.Debugf("Closing QueueClient")
	c.mu.Lock()
	c.closed = true
	c.mu.Unlock()
	close(c.Channel)
	c.wg.Wait()
}

// MessageDistributor handles distributing messages to multiple clients
type MessageDistributor struct {
	clients map[int]*QueueClient
	mu      sync.Mutex
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
	d.mu.Lock()
	defer d.mu.Unlock()

	d.counter++
	logName := fmt.Sprintf("c%02d", d.counter)
	QueueClient := NewClient(d.counter, d.history.GetAllMessages(), d.log.Sub(logName))
	QueueClient.wg.Add(1)
	go func() {
		defer QueueClient.wg.Done()
		for {
			select {
			case _, ok := <-QueueClient.Channel:
				if !ok {
					// Channel is closed, ensure queue is processed
					QueueClient.processQueue()
					return
				}
			default:
				// Process queued messages
				QueueClient.processQueue()
			}
		}
	}()
	d.clients[QueueClient.ID] = QueueClient
	return QueueClient
}

// RemoveClient removes a QueueClient from the distributor
func (d *MessageDistributor) RemoveClient(queueClient *QueueClient) {
	d.mu.Lock()
	defer d.mu.Unlock()

	clientID := queueClient.ID
	if QueueClient, ok := d.clients[clientID]; ok {
		QueueClient.Close()
		delete(d.clients, clientID)
	}
	maxClientID := 0
	for clientID := range d.clients {
		maxClientID = max(maxClientID, clientID)
	}
	d.counter = maxClientID
}

// SendQueueMessage sends a message to all clients
func (d *MessageDistributor) SendMessage(message *Message) {
	d.mu.Lock()
	defer d.mu.Unlock()

	d.log.Debugf("Distributing new message: %s", message.Info.ID)
	queueMessage := &QueueMessage{
		Content:   message,
		Timestamp: time.Now(),
	}
	d.history.AddMessage(queueMessage)
	for _, QueueClient := range d.clients {
		QueueClient.EnqueueMessage(queueMessage)
	}
}
