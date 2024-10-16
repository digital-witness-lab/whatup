package whatupcore2

import (
	"sync"
	"time"
)

// MessageCache represents a cache of messages with max size and age limits
type MessageCache struct {
	messages       []*QueueMessage
	mu             sync.Mutex
	MaxNumMessages int
	MaxAge         time.Duration
}

// NewMessageCache creates a new MessageCache with the given max size and age
func NewMessageCache(maxNumMessages int, maxAge time.Duration) *MessageCache {
	return &MessageCache{
		messages:       []*QueueMessage{},
		MaxNumMessages: maxNumMessages,
		MaxAge:         maxAge,
	}
}

// AddMessage adds a new message to the cache
func (c *MessageCache) AddMessage(msg *QueueMessage) {
	c.mu.Lock()
	defer c.mu.Unlock()

	// Prune old or expired messages before adding the new one
	c.pruneMessages()

	// Add the new message
	c.messages = append(c.messages, msg)

	// If the cache exceeds MaxNumMessages, remove the oldest
	if len(c.messages) > c.MaxNumMessages {
		c.messages = c.messages[1:]
	}
}

// pruneMessages removes any messages older than MaxAge
func (c *MessageCache) pruneMessages() {
	cutoffTime := time.Now().Add(-c.MaxAge)

	// Find the first valid message index
	var index int
	for index = 0; index < len(c.messages); index++ {
		if c.messages[index].Timestamp.After(cutoffTime) {
			break
		}
	}

	// If there are old messages to remove, slice them off
	if index > 0 {
		c.messages = c.messages[index:]
	}
}

// GetAllMessages returns a copy of the list of messages in the cache
func (c *MessageCache) GetAllMessages() []*QueueMessage {
	c.mu.Lock()
	defer c.mu.Unlock()

	// Prune old messages before returning
	c.pruneMessages()

	// Return a copy of the messages
	messagesCopy := make([]*QueueMessage, len(c.messages))
	copy(messagesCopy, c.messages)
	return messagesCopy
}
