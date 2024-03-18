package whatupcore2

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"hash/fnv"
	"os"
	"path"
	"sort"
	"sync"
	"time"

	waLog "go.mau.fi/whatsmeow/util/log"
)

type CacheElement struct {
    Path string
    key string
    ExpireTime time.Time
    Size uint64
}

func (ce *CacheElement) delete() error {
    return os.Remove(ce.Path)
}

// appendSortedCacheElement appends a new CacheElement to the slice while maintaining the slice sorted by ExpireTime.
func appendSortedCacheElement(slice []CacheElement, element CacheElement) []CacheElement {
    // ensure that OLDEST items are at the end of the slice
	index := sort.Search(len(slice), func(i int) bool {
		return slice[i].ExpireTime.After(element.ExpireTime)
	})
	slice = append(slice, element)
	copy(slice[index+1:], slice[index:])
	slice[index] = element
	return slice
}

type DiskCache struct {
    Path string
    ExpireTime time.Duration
    Context ContextWithCancel
    log waLog.Logger

    MaxSize uint64
    curSize uint64
    cleanFrequency time.Duration

    elements []CacheElement
    lookup map[string]*CacheElement

    lock sync.Mutex
    salt []byte
}

func NewDiskCacheTempdir(ctx context.Context, expireTime time.Duration, maxSize uint64, cleanFrequency time.Duration, log waLog.Logger) (*DiskCache, error) {
    path, err := os.MkdirTemp("", "diskcache-*")
    log.Infof("Using path for disk cache: %s", path)
    if err != nil {
        return nil, err
    }
    dc, err := NewDiskCache(ctx, path, expireTime, maxSize, cleanFrequency, log)
    if err != nil {
        return nil, err
    }
    go func() {
        <-dc.Context.Done()
        log.Warnf("Temporary disk cache closing... removing contents")
        //os.RemoveAll(dc.Path)
    }()
    return dc, nil
}

func NewDiskCache(ctx context.Context, path string, expireTime time.Duration, maxSize uint64, cleanFrequency time.Duration, log waLog.Logger) (*DiskCache, error) {
    salt := make([]byte, 32)
    _, err := rand.Read(salt)
    if err != nil {
        return nil, err
    }
    ctxC := NewContextWithCancel(ctx)
    dc := &DiskCache{
        Path: path,
        Context: ctxC,
        ExpireTime: expireTime,
        log: log,
        cleanFrequency: cleanFrequency,
        MaxSize: maxSize,
        salt: salt,
        elements: make([]CacheElement, 0),
        lookup: make(map[string]*CacheElement),
        lock: sync.Mutex{},
    }
    go dc.periodicCleaner()
    return dc, nil
}

func (dc *DiskCache) periodicCleaner() {
    go func() {
        timer := time.NewTicker(dc.cleanFrequency)
        for {
            select {
            case <-dc.Context.Done():
                dc.log.Warnf("Context closed")
                dc.Close()
                return
            case <-timer.C:
                bytesFreed := dc.freeExpired()
                dc.log.Debugf("Cleaning expired elements from periodic clean: %d bytes freed",bytesFreed)
            }
        }
    }()
}

func (dc *DiskCache) Close() {
    dc.log.Warnf("Closing disk cache")
    dc.lock.Lock()
    for _, element := range dc.elements {
        element.delete()
    }
    dc.Context.Cancel()
    dc.lock.Unlock()
    dc = &DiskCache{}
}

func (dc *DiskCache) Add(key string, value []byte) error {
    if uint64(len(value)) > dc.MaxSize {
        return fmt.Errorf("File too big for cache: %d > %d", len(value), dc.MaxSize)
    }
    dc.freeExpired()
    neededSpace := uint64(len(value)) + dc.curSize - dc.MaxSize
    if neededSpace > 0 {
        dc.freeSpace(neededSpace)
    }
    keyPath := dc.keyPath(key)
    err := os.WriteFile(keyPath, value, 0600)
    if err != nil {
        return err
    }

    cacheElement := CacheElement{
        Path: keyPath,
        key: key,
        ExpireTime: time.Now().Add(dc.ExpireTime),
        Size: uint64(len(value)),
    }

    dc.lock.Lock()
    dc.elements = appendSortedCacheElement(dc.elements, cacheElement)
    dc.lookup[key] = &cacheElement
    dc.lock.Unlock()
    return nil
}

func (dc *DiskCache) Get(key string) ([]byte, error) {
    element, found := dc.lookup[key]
    if !found {
        return nil, nil
    }
    dc.log.Debugf("Reading from path: %s", element.Path)
    content, err := os.ReadFile(element.Path)
    if err != nil {
        return nil, err
    }
    return content, nil
}

func (dc *DiskCache) freeSpace(neededSpace uint64) uint64 {

    var freed uint64
	for i := len(dc.elements) - 1; i >= 0; i-- {
        el := dc.elements[i]
		el.delete()
        freed += el.Size
        dc.lock.Lock()
        delete(dc.lookup, el.key)
		dc.elements = append(dc.elements[:i], dc.elements[i+1:]...)
        defer dc.lock.Unlock()
        
        if freed >= neededSpace {
            return freed
        }
	}
    return freed
}

func (dc *DiskCache) freeExpired() uint64 {
    if len(dc.lookup) == 0 {
        return 0
    }

    var freed uint64
    now := time.Now()

	for i := len(dc.elements) - 1; i >= 0; i-- {
        el := dc.elements[i]
		if el.ExpireTime.Before(now) {
			el.delete()
            freed += el.Size
            dc.lock.Lock()
            delete(dc.lookup, el.key)
			dc.elements = append(dc.elements[:i], dc.elements[i+1:]...)
            defer dc.lock.Unlock()
		} else {
            break
        }
	}
    return freed
}

func (dc *DiskCache) keyPath(key string) string {
    hasher := fnv.New64()
    sum := hasher.Sum([]byte(key))
    filename := hex.EncodeToString(sum)
    return path.Join(dc.Path, filename)
}

