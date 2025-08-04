package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"
	"webuploader/src/utils"

	"github.com/gorilla/websocket"
)

const (
	WEB_SIGNATURE = `{"from":"web"`
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true // Allow connections from any origin
	},
}

type WSServer struct {
	webClient *websocket.Conn
	clients   map[*websocket.Conn]bool
}

func NewWSServer() *WSServer {
	return &WSServer{
		clients: make(map[*websocket.Conn]bool),
	}
}

// handleWebSocket manages WebSocket connections from both web and CLI clients.
// It upgrades HTTP connections to WebSocket protocol, maintains client connections,
// and routes messages between clients. The function:
// - Adds new connections to the clients map
// - Identifies web clients vs CLI clients based on URL parameters
// - Launches the web interface if a CLI client connects without a web client present
// - Processes incoming text and binary messages
// - Cleans up connections when they're closed
func (ws *WSServer) handleWebSocket(w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Printf("Failed to upgrade connection: %v", err)
		return
	}
	defer conn.Close()

	ws.clients[conn] = true
	defer delete(ws.clients, conn)

	// Send welcome message
	conn.WriteMessage(websocket.TextMessage, []byte("Welcome to the WebSIM server!"))

	// Check if this is a web client connection
	uri := r.URL.String()
	if strings.Contains(uri, "from=web") {
		ws.webClient = conn
		log.Printf("Web client connected from %s", conn.RemoteAddr())
	} else {
		// CLI connection
		if ws.webClient == nil {
			conn.WriteMessage(websocket.TextMessage, []byte("###### WARN: NO WEB Client connected !! opening https://websim-arduino.web.app"))
			err := utils.OpenURL("https://websim-arduino.web.app")
			if err != nil {
				fmt.Print("[uploader] Error openning browser")
				fmt.Print("[uploader] Please open 'https://websim-arduino.web.app' on browser")
			}
		}
		log.Printf("CLI client connected from %s", conn.RemoteAddr())
	}

	for {
		messageType, message, err := conn.ReadMessage()
		if err != nil {
			log.Printf("Error reading message: %v", err)
			break
		}

		switch messageType {
		case websocket.TextMessage:
			ws.handleTextMessage(conn, string(message))
		case websocket.BinaryMessage:
			ws.handleBinaryMessage(conn, message)
		}
	}

	// Clean up web client reference if this was the web client
	if conn == ws.webClient {
		ws.webClient = nil
	}
}

func (ws *WSServer) handleTextMessage(sender *websocket.Conn, message string) {
	log.Printf("Received text message: %s", message)

	// Broadcast to all clients except sender
	ws.broadcast(message, sender)

	// Check if this establishes the web client connection
	if strings.Contains(message, WEB_SIGNATURE) {
		ws.webClient = sender
	}
}

func (ws *WSServer) handleBinaryMessage(sender *websocket.Conn, message []byte) {
	log.Printf("Received binary message of size: %d bytes", len(message))

	// Wait for web client connection for up to 10 seconds
	if ws.webClient == nil {
		sender.WriteMessage(websocket.TextMessage, []byte("Waiting for web browser to connect (timeout: 10s)..."))

		timeout := time.After(30 * time.Second)
		ticker := time.NewTicker(500 * time.Millisecond)
		defer ticker.Stop()

		for ws.webClient == nil {
			select {
			case <-ticker.C:
				// Check if web client connected
				if ws.webClient != nil {
					sender.WriteMessage(websocket.TextMessage, []byte("Web browser client connected !"))
					break
				}
			case <-timeout:
				sender.WriteMessage(websocket.TextMessage, []byte("###### ERROR: Timed out waiting for web browser client"))
				return
			}
		}
	}

	// Send to web browser if connected
	if ws.webClient != nil {
		err := ws.webClient.WriteMessage(websocket.BinaryMessage, message)
		if err != nil {
			log.Printf("Error sending to web client: %v", err)
			sender.WriteMessage(websocket.TextMessage, []byte("###### WARN: Failed to send to web client"))
		}
	}

	// Close CLI connection after sending file
	sender.Close()
}

func (ws *WSServer) broadcast(message string, except *websocket.Conn) {
	for client := range ws.clients {
		if client != except {
			err := client.WriteMessage(websocket.TextMessage, []byte(message))
			if err != nil {
				log.Printf("Error broadcasting to client: %v", err)
				client.Close()
				delete(ws.clients, client)
			}
		}
	}
}

func RunServer(port int) {
	server := NewWSServer()

	http.HandleFunc("/", server.handleWebSocket)

	fmt.Printf("[uploader] Server started on port: %d\n", port)
	fmt.Println("[uploader] Open: https://websim-arduino.web.app")

	// Set up signal handling for graceful shutdown
	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt, syscall.SIGTERM)

	go func() {
		<-c
		fmt.Println("\nShutting down server...")
		os.Exit(0)
	}()

	log.Fatal(http.ListenAndServe(fmt.Sprintf(":%d", port), nil))
}
