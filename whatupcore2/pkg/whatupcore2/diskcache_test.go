package whatupcore2

import (
	"context"
	"testing"
	"time"

	waLog "go.mau.fi/whatsmeow/util/log"
)

func TestDiskCacheLifecycle(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Create a new disk cache
	dc, err := NewDiskCacheTempdir(ctx, 1*time.Second, 1024*1024, 10*time.Second, waLog.Stdout("diskCache", "ERROR", true))
	if err != nil {
		t.Fatalf("Failed to create disk cache: %v", err)
	}
	defer dc.Close()

	// Add an item to the cache
	key := "testKey"
	value := []byte("testData")
	err = dc.Add(key, value)
	if err != nil {
		t.Errorf("Failed to add item to cache: %v", err)
	}

	// Retrieve the item from the cache
	retrievedValue, err := dc.Get(key)
	if err != nil {
		t.Errorf("Failed to retrieve item from cache: %v", err)
	}
    if retrievedValue == nil {
		t.Errorf("Could not find value in cache")
    } else if string(retrievedValue) != string(value) {
		t.Errorf("Retrieved value does not match added value: got %v, want %v", string(retrievedValue), string(value))
	}

	// Wait for the item to expire
	time.Sleep(2 * time.Second)

	// Try to retrieve the expired item
    dc.freeExpired()
	retrievedValue, err = dc.Get(key)
	if err != nil {
		t.Errorf("Failed to retrieve item from cache after expiration: %v", err)
	}
	if retrievedValue != nil {
		t.Errorf("Expected nil value for expired item, got: %v", string(retrievedValue))
	}
}

func TestDiskCacheOrder(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Create a new disk cache
	dc, err := NewDiskCacheTempdir(ctx, 5*time.Second, 1024*1024, 1*time.Second, waLog.Stdout("diskCache", "ERROR", true))
	if err != nil {
		t.Fatalf("Failed to create disk cache: %v", err)
	}
	defer dc.Close()

    dc.Add("key1", []byte("234asdf"))
    time.Sleep(500 * time.Millisecond)
    dc.Add("key2", []byte("sadfsd"))

    if dc.elements[0].key != "key2" {
        t.Fatalf("Elements is out of order. Older elements should be last")
    }
}
