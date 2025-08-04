package main

import (
	"encoding/json"
	"fmt"
	"net/url"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/gorilla/websocket"
)

type WebSocketClient struct {
	serverPort int
}

func NewWebSocketClient(port int) *WebSocketClient {
	return &WebSocketClient{
		serverPort: port,
	}
}

func (c *WebSocketClient) SendFile(filePath string, board string) error {
	// Check if file exists
	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		return fmt.Errorf("file does not exist: %s", filePath)
	}

	// Read file
	fileData, err := os.ReadFile(filePath)
	if err != nil {
		return fmt.Errorf("failed to read file: %v", err)
	}

	// Create WebSocket connection
	u := url.URL{Scheme: "ws", Host: fmt.Sprintf("localhost:%d", c.serverPort), Path: "/", RawQuery: "from=cli"}
	conn, _, err := websocket.DefaultDialer.Dial(u.String(), nil)
	if err != nil {
		return fmt.Errorf("failed to connect: %v", err)
	}
	defer conn.Close()

	// Send board change command if board is specified
	if board != "" {
		boardCmd := fmt.Sprintf(`{"action":"change-board", "board": "%s"}`, board)
		err = conn.WriteMessage(websocket.TextMessage, []byte(boardCmd))
		if err != nil {
			return fmt.Errorf("failed to send board command: %v", err)
		}
		fmt.Printf("[ide] Board changed to: %s\n", board)
	}

	// Send websim.json if it exists
	c.sendWebsimJson(filePath, conn)

	// Send file data
	err = conn.WriteMessage(websocket.BinaryMessage, fileData)
	if err != nil {
		return fmt.Errorf("failed to send file: %v", err)
	}

	fmt.Printf("[ide] board: (%s)\n", board)
	fmt.Printf("[ide] Send File (%s)\n", filePath)
	fmt.Printf("[ide] hex size (%d)\n", len(fileData))
	fmt.Println("[ide] upload finish !")

	// Wait for server response or close
	for {
		_, message, err := conn.ReadMessage()
		if err != nil {
			break
		}
		fmt.Printf("[ide] received: %s\n", string(message))
	}

	return nil
}

func (c *WebSocketClient) SendDebugInfo(message string) error {
	// Create WebSocket connection
	u := url.URL{Scheme: "ws", Host: fmt.Sprintf("localhost:%d", c.serverPort), Path: "/", RawQuery: "from=cli"}
	conn, _, err := websocket.DefaultDialer.Dial(u.String(), nil)
	if err != nil {
		return fmt.Errorf("failed to connect: %v", err)
	}
	defer conn.Close()

	// Send debug message
	err = conn.WriteMessage(websocket.TextMessage, []byte(message))
	if err != nil {
		return fmt.Errorf("failed to send debug info: %v", err)
	}

	time.Sleep(500 * time.Millisecond)
	return nil
}

func (c *WebSocketClient) HandleDebugBoard(hexFile string, board string) error {
	// Create debug message
	message := fmt.Sprintf("Debug mode activated for board: %s with hex file: %s", board, hexFile)

	// Send debug information to server
	return c.SendDebugInfo(message)
}

// ParseArguments parses command line arguments and returns filePath and board
func ParseArguments(args []string) (string, string) {
	var filePath string
	var board string

	for i := 0; i < len(args); i++ {
		if args[i] == "--board" && i+1 < len(args) {
			board = args[i+1]
			i++ // Skip the next argument as it's the board name
		} else if !strings.HasPrefix(args[i], "--") && filePath == "" {
			filePath = args[i]
		}
	}

	return filePath, board
}

// HandleLegacyDebugBoard handles legacy debug board functionality
func (c *WebSocketClient) HandleLegacyDebugBoard(args []string, filePath string) error {
	// Check for debug board flag (legacy support)
	if len(args) > 2 && args[1] == "-b" {
		debugBoard := args[2]
		if strings.Contains(debugBoard, "_DBG") {
			return c.HandleDebugBoard(filePath, debugBoard)
		}
	}
	return nil
}

// getSketchLocationFromBuildOptions extracts sketchLocation from build.options.json
func getSketchLocationFromBuildOptions(filePath string) (string, error) {
	buildFolder := filepath.Dir(filePath)
	buildOptionsPath := filepath.Join(buildFolder, "build.options.json")

	fmt.Printf("[ide] buildOptionsPath from: %s\n", buildOptionsPath)

	// Check if build.options.json exists
	if _, err := os.Stat(buildOptionsPath); os.IsNotExist(err) {
		return "", nil // Return empty string, not an error
	}

	// Read the file
	data, err := os.ReadFile(buildOptionsPath)
	if err != nil {
		return "", nil // Return empty string, not an error
	}

	// Parse JSON into map
	var buildOptions map[string]interface{}
	err = json.Unmarshal(data, &buildOptions)
	if err != nil {
		return "", nil // Return empty string, not an error
	}

	// Get sketchLocation from map
	if sketchLocation, ok := buildOptions["sketchLocation"].(string); ok {
		return sketchLocation, nil
	}

	return "", nil
}

// sendWebsimJson checks for websim.json in sketch location and sends it (optional, no errors)
func (c *WebSocketClient) sendWebsimJson(filePath string, conn *websocket.Conn) {
	// Get sketch location from build.options.json
	sketchLocation, err := getSketchLocationFromBuildOptions(filePath)

	fmt.Printf("[ide] sketchLocation: %s\n", sketchLocation)

	if err != nil || sketchLocation == "" {
		return // Silently skip if no sketch location
	}

	// Check if websim.json exists in sketch location
	websimJsonPath := filepath.Join(sketchLocation, "websim.json")
	if _, err := os.Stat(websimJsonPath); os.IsNotExist(err) {
		return // Silently skip if websim.json doesn't exist
	}

	// Read websim.json
	websimData, err := os.ReadFile(websimJsonPath)
	if err != nil {
		return // Silently skip if can't read file
	}

	// Create the message with the required format
	message := map[string]interface{}{
		"action": "load-circuit-json",
		"data":   string(websimData),
	}

	messageJson, err := json.Marshal(message)
	if err != nil {
		return // Silently skip if can't marshal
	}

	// Send the message
	err = conn.WriteMessage(websocket.TextMessage, messageJson)
	if err != nil {
		return // Silently skip if can't send
	}

	fmt.Printf("[ide] Sent websim.json from: %s\n", websimJsonPath)
}
