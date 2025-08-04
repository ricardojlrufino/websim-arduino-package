package main

import (
	"fmt"
	"log"
	"net"
	"os"
	"os/exec"
	"time"
)

const PORT = 8887

func isServerRunning() bool {
	// Try to connect to see if server is already running
	listener, err := net.Listen("tcp", fmt.Sprintf(":%d", PORT))
	if err != nil {
		// Port is already in use, server is probably running
		return true
	}

	// Close the listener if we were able to bind to the port
	listener.Close()
	return false
}

func startServerInBackground() {
	// Get the executable path
	execPath, err := os.Executable()
	if err != nil {
		log.Fatalf("Failed to get executable path: %v", err)
	}

	// Start a new process in background
	cmd := exec.Command(execPath, "--daemon")
	cmd.Stdout = nil
	cmd.Stderr = nil

	// Start the process
	err = cmd.Start()
	if err != nil {
		log.Fatalf("Failed to start daemon process: %v", err)
	}

	fmt.Println("[uploader] Server started in background")
}

func main() {
	args := os.Args[1:]

	// Check if we're being started as a daemon
	if len(args) > 0 && args[0] == "--daemon" {
		RunServer(PORT)
		return
	}

	// Check if server is already running
	serverRunning := isServerRunning()

	// If server is not running, start it in background
	if !serverRunning {
		fmt.Println("[uploader] Starting server in background...")
		startServerInBackground()

		// Wait a moment for server to start
		time.Sleep(2 * time.Second)
	}

	// Parse arguments and handle client operations
	filePath, board := ParseArguments(args)

	// If file path provided, try to send file
	if filePath != "" {
		client := NewWebSocketClient(PORT)
		err := client.SendFile(filePath, board)
		if err != nil {
			fmt.Printf("Error sending file: %v\n", err)
			// If this failed and we just started the server, give it a bit more time
			if !serverRunning {
				fmt.Println("Waiting for server to fully start...")
				time.Sleep(3 * time.Second)
				err = client.SendFile(filePath, board)
				if err != nil {
					fmt.Printf("Second attempt failed: %v\n", err)
				}
			}
		} else {
			// Handle legacy debug board functionality
			err := client.HandleLegacyDebugBoard(args, filePath)
			if err != nil {
				log.Printf("Debug handling failed: %v", err)
			}
		}
	}
}
