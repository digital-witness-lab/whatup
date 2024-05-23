package main

import (
	"bufio"
	"context"
	"fmt"
	"io"
	"os"
	"os/exec"
	"os/signal"
	"sync"
	"syscall"
)

var (
	VERSION            = "v0.2.0"
	STREAM_BUFFER_SIZE = 5 * 1024 * 1024 // 5MB in bytes
	CLEANERS           = []CleanerFunc{
		phoneNumberCleaner(),
		notifyAttribCleaner(),
		notifyBodyCleaner(),
		pushNameCleaner(),
	}
)

func filter(line string, cleaners []CleanerFunc) (ret string) {
	defer func() {
		if err := recover(); err != nil {
			fmt.Printf("log-cleaner: Recovered from panic: %v\n", err)
			ret = line
		}
	}()
	ret = line
	for _, clean := range cleaners {
		ret = clean(ret)
	}
	return ret
}

func filterStream(input io.Reader, output io.StringWriter, cleaners []CleanerFunc) {
	scanner := bufio.NewScanner(input)
	buffer := make([]byte, STREAM_BUFFER_SIZE)
	scanner.Buffer(buffer, STREAM_BUFFER_SIZE)
	for scanner.Scan() {
		line := scanner.Text()
		line = filter(line, cleaners)
		output.WriteString(line)
		output.WriteString("\n")
	}
	if err := scanner.Err(); err != nil && err != io.EOF {
		fmt.Printf("log-cleaner: Error scanning: %v\n", err)
	}
}

func runWgCancel(wg *sync.WaitGroup, cancel context.CancelFunc, f func()) {
	wg.Add(1)
	f()
	cancel()
	wg.Done()
}

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintf(os.Stderr, "Usage: %s <sub-command> [arguments...]\n", os.Args[0])
		os.Exit(1)
	}
	ctx, cancel := context.WithCancel(context.Background())
	fmt.Fprintf(os.Stdout, "log-cleaner: Running version %s\n", VERSION)

	cmd := exec.CommandContext(ctx, os.Args[1], os.Args[2:]...)

	// Connect cmd.Stdin directly to os.Stdin.
	cmd.Stdin = os.Stdin

	// Creating pipes for stdout and stderr of the child process.
	stdoutPipe, err := cmd.StdoutPipe()
	if err != nil {
		fmt.Fprintf(os.Stderr, "log-cleaner: Failed to create stdout pipe: %v\n", err)
		os.Exit(1)
	}

	stderrPipe, err := cmd.StderrPipe()
	if err != nil {
		fmt.Fprintf(os.Stderr, "log-cleaner: Failed to create stderr pipe: %v\n", err)
		os.Exit(1)
	}

	// Start the command.
	if err := cmd.Start(); err != nil {
		fmt.Fprintf(os.Stderr, "log-cleaner: Failed to start command: %v\n", err)
		os.Exit(1)
	}

	// Forward signals to the child process.
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
	go func() {
		for sig := range sigChan {
			fmt.Fprintf(os.Stderr, "log-cleaner: Got signal... killing child: %v\n", sig)
			if cmd.Process != nil {
				cmd.Process.Signal(sig)
			}
		}
	}()

	var wg sync.WaitGroup

	// Filter and forward stdout and stderr
	go func() {
		wg.Add(1)
		filterStream(stdoutPipe, os.Stdout, CLEANERS)
		cancel()
		wg.Done()
	}()
	go func() {
		wg.Add(1)
		filterStream(stderrPipe, os.Stderr, CLEANERS)
		cancel()
		wg.Done()
	}()

	// Wait for the command to finish.
	if err := cmd.Wait(); err != nil {
		fmt.Fprintf(os.Stderr, "log-cleaner: Command finished with error: %v\n", err)
	}
	stdoutPipe.Close()
	stderrPipe.Close()
	wg.Wait()
}
