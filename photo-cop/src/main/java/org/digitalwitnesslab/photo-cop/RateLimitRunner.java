package org.digitalwitnesslab.photocop;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class RateLimitRunner {
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
    private final PriorityBlockingQueue<PriorityTask> taskQueue = new PriorityBlockingQueue<>();
    private final AtomicInteger currentRate = new AtomicInteger(0);
    private long requests_per_dt;
    private long dt_ms;
    private int cacheSize;

    private final Map<ByteArrayWrapper, Future<?>> cache = new LinkedHashMap<ByteArrayWrapper, Future<?>>() {
        @Override
        protected boolean removeEldestEntry(Map.Entry<ByteArrayWrapper, Future<?>> eldest) {
            return size() > cacheSize;
        }
    };

    public RateLimitRunner(int cacheSize, long requests_per_dt, long dt_ms) {
        this.requests_per_dt = requests_per_dt;
        this.dt_ms = dt_ms;
        this.cacheSize = cacheSize;
        scheduler.scheduleAtFixedRate(this::resetRate, dt_ms, dt_ms, TimeUnit.MILLISECONDS);
        scheduler.scheduleAtFixedRate(this::processQueue, 0, (long) (dt_ms / requests_per_dt), TimeUnit.MILLISECONDS);
    }

    public <T> Future<T> submit(Callable<T> task, byte[] cacheKey, int priority) {
        ByteArrayWrapper keyWrapper = new ByteArrayWrapper(cacheKey);
        PriorityTask<T> priorityTask = new PriorityTask<>(task, priority);
    
        synchronized (cache) {
            System.err.println("Cache key:");
            System.err.println(keyWrapper.hashCode());
            if (cache.containsKey(keyWrapper)) {
                System.err.println("Found request in cache");
                return (Future<T>) cache.get(keyWrapper);
            }
            cache.put(keyWrapper, priorityTask.getFuture());
        }
    
        if (currentRate.get() <= this.requests_per_dt) {
            scheduler.submit(() -> {
                try {
                    currentRate.incrementAndGet();
                    T result = task.call();
                    priorityTask.getFuture().complete(result);
                } catch (Exception e) {
                    priorityTask.getFuture().completeExceptionally(e);
                }
            });
        } else {
            System.err.println("Rate-limiting request.");
            taskQueue.offer(priorityTask);
        }
        return priorityTask.getFuture();
    }

    private void resetRate() {
        currentRate.set(0);
    }

    private void processQueue() {
        while (currentRate.get() < requests_per_dt && !taskQueue.isEmpty()) {
            PriorityTask<?> task = taskQueue.poll();
            if (task != null) {
                scheduler.submit(() -> {
                    currentRate.incrementAndGet();
                    task.run();
                });
            }
        }
    }

    private static class ByteArrayWrapper {
        private final byte[] data;
        private final int hashCode;

        public ByteArrayWrapper(byte[] data) {
            this.data = data;
            this.hashCode = Arrays.hashCode(data);
        }

        @Override
        public boolean equals(Object obj) {
            if (this == obj) {
                return true;
            }
            if (obj == null || getClass() != obj.getClass()) {
                return false;
            }
            ByteArrayWrapper other = (ByteArrayWrapper) obj;
            return Arrays.equals(data, other.data);
        }

        @Override
        public int hashCode() {
            return hashCode;
        }
    }

    private static class PriorityTask<T> implements Comparable<PriorityTask<T>>, Runnable {
        private final Callable<T> task;
        private final int priority;
        private final CompletableFuture<T> future = new CompletableFuture<>();
    
        public PriorityTask(Callable<T> task, int priority) {
            this.task = task;
            this.priority = priority;
        }
    
        @Override
        public int compareTo(PriorityTask<T> other) {
            return Integer.compare(other.priority, this.priority); // Higher priority first
        }
    
        @Override
        public void run() {
            try {
                T result = task.call();
                future.complete(result);
            } catch (Exception e) {
                future.completeExceptionally(e);
            }
        }
    
        public CompletableFuture<T> getFuture() {
            return future;
        }
    }
}
