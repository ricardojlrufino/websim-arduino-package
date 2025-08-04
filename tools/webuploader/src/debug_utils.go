package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"runtime"
	"strconv"
	"strings"
)

// ObjSourceMap represents source mapping information from object dump
type ObjSourceMap struct {
	File       string `json:"file"`
	LineNumber string `json:"lineNumber"`
	Addr       string `json:"addr"`
	LineSource string `json:"lineSource"`
}

// HandleDebugBoard processes debug information for a board
func HandleDebugBoard(hexFile, board string) error {
	fmt.Printf("[uploader] DEBUG board: %s\n", board)

	// Get source file path
	name := strings.Replace(filepath.Base(hexFile), ".hex", ".cpp", 1)
	srcFile := filepath.Join(filepath.Dir(hexFile), "sketch", name)
	fmt.Printf("Src: %s\n", srcFile)
	
	if _, err := os.Stat(srcFile); err == nil {
		fmt.Println("Exist: true")
	} else {
		fmt.Println("Exist: false")
	}

	// Get breakpoints
	breakpoints, err := GetBreakpoints(hexFile)
	if err != nil {
		return fmt.Errorf("failed to get breakpoints: %v", err)
	}

	var inoBreaks []string
	var inoSources []string

	// Filter only .ino sources
	for _, bp := range breakpoints {
		if strings.HasSuffix(bp.File, ".ino") {
			inoBreaks = append(inoBreaks, bp.Addr)
			inoSources = append(inoSources, bp.LineSource)
		}
	}

	fmt.Printf("breakpoints: %v\n", inoBreaks)

	// Create JSON message
	debugInfo := map[string]interface{}{
		"from":        "cli",
		"breakpoints": inoBreaks,
		"sources":     inoSources,
	}

	jsonData, err := json.Marshal(debugInfo)
	if err != nil {
		return fmt.Errorf("failed to marshal debug info: %v", err)
	}

	client := NewWebSocketClient(PORT)
	return client.SendDebugInfo(string(jsonData))
}

// GetBreakpoints extracts breakpoint information from a hex file
func GetBreakpoints(hexFile string) ([]ObjSourceMap, error) {
	buildFolder := filepath.Dir(hexFile)
	boardOptions := filepath.Join(buildFolder, "build.options.json")

	// Get AVR path
	avrPath, err := getAvrPath(boardOptions)
	if err != nil {
		return nil, fmt.Errorf("failed to get AVR path: %v", err)
	}

	// Generate file dump
	fileDump, err := generateFileDump(hexFile, avrPath)
	if err != nil {
		return nil, fmt.Errorf("failed to generate file dump: %v", err)
	}

	// Parse results
	dumpList, err := ParseObjDumpWL(fileDump)
	if err != nil {
		return nil, fmt.Errorf("failed to parse objdump: %v", err)
	}

	// Filter only .ino sources
	var inoBreaks []ObjSourceMap
	for _, item := range dumpList {
		if strings.HasSuffix(item.File, ".ino") {
			inoBreaks = append(inoBreaks, item)
		}
	}

	return inoBreaks, nil
}

// Helper function to get AVR path from board options
func getAvrPath(boardOptionsPath string) (string, error) {
	data, err := ioutil.ReadFile(boardOptionsPath)
	if err != nil {
		return "", err
	}

	pattern := regexp.MustCompile(`runtime\.tools\.avr-gcc\.path=(.*?),`)
	matches := pattern.FindStringSubmatch(string(data))
	if len(matches) < 2 {
		return "", fmt.Errorf("AVR path not found in build options")
	}

	return matches[1], nil
}

// Helper function to generate a file dump
func generateFileDump(hexFile, avrPath string) (string, error) {
	buildFolder := filepath.Dir(hexFile)
	name := strings.Replace(filepath.Base(hexFile), ".hex", ".elf", 1)
	elfFile := filepath.Join(buildFolder, name)

	var cmd *exec.Cmd
	var objdumpPath string

	if runtime.GOOS == "windows" {
		// Windows
		objdumpPath = filepath.Join(avrPath, "bin", "avr-objdump.exe")
		cmd = exec.Command("cmd", "/c", objdumpPath, "-WL", elfFile)
	} else {
		// Unix/Linux/macOS
		objdumpPath = filepath.Join(avrPath, "bin", "avr-objdump")
		cmd = exec.Command(objdumpPath, "-WL", elfFile)
	}

	fmt.Printf("Running: %s\n", strings.Join(cmd.Args, " "))

	output, err := cmd.Output()
	if err != nil {
		return "", fmt.Errorf("failed to run objdump: %v", err)
	}

	return string(output), nil
}

// ParseObjDumpWL parses object dump with lines information
func ParseObjDumpWL(fileDumpTxt string) ([]ObjSourceMap, error) {
	var list []ObjSourceMap
	lines := strings.Split(fileDumpTxt, "\n")

	fileRegEx := regexp.MustCompile(`(.*\.\S{1,3}):`)
	addrRegEx := regexp.MustCompile(`(\w*\.\S{1,3})\s*(\d+)\s*(0.*)`)

	var currentFile string

	for _, line := range lines {
		fileMatch := fileRegEx.FindStringSubmatch(line)
		if len(fileMatch) > 1 {
			currentFile = fileMatch[1]
			continue
		}

		addrMatch := addrRegEx.FindStringSubmatch(line)
		if len(addrMatch) > 3 {
			objMap := ObjSourceMap{
				File:       currentFile,
				LineNumber: addrMatch[2],
				Addr:       addrMatch[3],
			}
			list = append(list, objMap)
		}
	}

	// Grab line sources
	err := GrabLineSources(&list)
	if err != nil {
		log.Printf("Warning: failed to grab line sources: %v", err)
	}

	return list, nil
}

// GrabLineSources fills the LineSource field for each item in the dump list
func GrabLineSources(dumpList *[]ObjSourceMap) error {
	var currentFile string
	var lines []string

	for i := range *dumpList {
		item := &(*dumpList)[i]
		
		if strings.HasSuffix(item.File, ".ino") {
			if item.File != currentFile {
				data, err := ioutil.ReadFile(item.File)
				if err != nil {
					continue // Skip if file can't be read
				}
				lines = strings.Split(string(data), "\n")
				currentFile = item.File
			}

			lineNum, err := strconv.Atoi(item.LineNumber)
			if err != nil || lineNum < 1 || lineNum > len(lines) {
				continue
			}

			item.LineSource = lines[lineNum-1]
		}
	}

	return nil
}