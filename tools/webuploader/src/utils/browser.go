package utils

import (
	"fmt"
	"os/exec"
	"runtime"
)

// OpenURL abre a URL fornecida no navegador padrão do sistema.
// Suporta Windows, macOS e Linux.
func OpenURL(url string) error {
	var cmd *exec.Cmd

	switch runtime.GOOS {
	case "windows":
		cmd = exec.Command("rundll32", "url.dll,FileProtocolHandler", url)
	case "darwin": // macOS
		cmd = exec.Command("open", url)
	default: // Linux e outros
		// Tenta vários comandos comuns em sistemas Linux
		cmd = exec.Command("xdg-open", url)
	}

	err := cmd.Start()
	if err != nil {
		return fmt.Errorf("falha ao abrir URL no navegador: %v", err)
	}

	return nil
}
