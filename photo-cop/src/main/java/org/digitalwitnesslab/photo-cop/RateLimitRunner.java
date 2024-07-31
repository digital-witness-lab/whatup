package org.digitalwitnesslab.photocop;

import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class RateLimitRunner {
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
    private final PriorityBlockingQueue<PriorityTask> taskQueue = new PriorityBlockingQueue<>();
    private final AtomicInteger currentRate = new AtomicInteger(0);
    private long requests_per_dt;
    private long dt_ms;

    public RateLimitRunner(long requests_per_dt, long dt_ms) {
        this.requests_per_dt = requests_per_dt;
        this.dt_ms = dt_ms;
        scheduler.scheduleAtFixedRate(this::resetRate, dt_ms, dt_ms, TimeUnit.MILLISECONDS);
        scheduler.scheduleAtFixedRate(this::processQueue, 0, (long) (dt_ms / requests_per_dt), TimeUnit.MILLISECONDS);
    }

    public <T> Future<T> submit(Callable<T> task, int priority) {
        PriorityTask<T> priorityTask = new PriorityTask<>(task, priority);
        if (currentRate.incrementAndGet() <= requests_per_dt) {
            currentRate.decrementAndGet(); // Decrement immediately since we will handle the task directly
            try {
                T result = task.call();
                return CompletableFuture.completedFuture(result);
            } catch (Exception e) {
                CompletableFuture<T> future = new CompletableFuture<>();
                future.completeExceptionally(e);
                return future;
            }
        } else {
            currentRate.decrementAndGet();
            taskQueue.offer(priorityTask);
            return priorityTask.getFuture();
        }
    }

    private void resetRate() {
        currentRate.set(0);
    }

    private void processQueue() {
        while (currentRate.get() < requests_per_dt && !taskQueue.isEmpty()) {
            PriorityTask<?> task = taskQueue.poll();
            if (task != null) {
                currentRate.incrementAndGet();
                scheduler.submit(() -> {
                    try {
                        task.run();
                    } finally {
                        currentRate.decrementAndGet();
                    }
                });
            }
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

        public Future<T> getFuture() {
            return future;
        }
    }
}
