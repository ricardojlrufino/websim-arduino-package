# Arduino Uploader Makefile
# Facilita a compilação e gerenciamento do projeto

# Variáveis
BINARY_NAME=webuploader
SOURCE_PATH=src/*.go
BIN_PATH=bin
DIST_PATH=dist
VERSION="1.2.0"
LDFLAGS=-s -w -X main.version=$(VERSION)

# Detectar OS
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
    DETECTED_OS=linux
endif
ifeq ($(UNAME_S),Darwin)
    DETECTED_OS=darwin
endif

# Cores para output
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[1;33m
BLUE=\033[0;34m
NC=\033[0m # No Color

.PHONY: all build clean test run help install deps linux windows macos current

# Target padrão
all: deps build

# Mostrar ajuda
help:
	@echo "$(BLUE)Arduino Uploader - Comandos disponíveis:$(NC)"
	@echo ""
	@echo "$(YELLOW)Build Commands:$(NC)"
	@echo "  make build      - Build para todas as plataformas"
	@echo "  make current    - Build apenas para o sistema atual"
	@echo "  make linux      - Build apenas para Linux"
	@echo "  make windows    - Build apenas para Windows"
	@echo "  make macos      - Build apenas para macOS"
	@echo ""
	@echo "$(YELLOW)Development Commands:$(NC)"
	@echo "  make run        - Executar aplicação"
	@echo "  make test       - Executar testes"
	@echo "  make clean      - Limpar arquivos de build"
	@echo "  make deps       - Instalar dependências"
	@echo "  make install    - Instalar no sistema"
	@echo ""
	@echo "$(YELLOW)Examples:$(NC)"
	@echo "  make run ARGS='sketch.hex'"
	@echo "  make run ARGS='sketch.hex -b BOARD_DBG'"

# Instalar dependências
deps:
	@echo "$(BLUE)📦 Instalando dependências...$(NC)"
	@go mod tidy
	@go mod download

# Build para todas as plataformas
build: deps
	@echo "$(BLUE)🏗️  Building for all platforms...$(NC)"
	@mkdir -p $(BIN_PATH)
	@$(MAKE) linux
	@$(MAKE) windows
	@$(MAKE) macos
	@$(MAKE) current
	@echo "$(GREEN)✅ Build completed for all platforms!$(NC)"
	@ls -la $(BIN_PATH)/

# Build para Linux
linux: deps
	@echo "$(YELLOW)🐧 Building for Linux...$(NC)"
	@mkdir -p $(BIN_PATH)
	@GOOS=linux GOARCH=amd64 go build -ldflags="$(LDFLAGS)" -o $(BIN_PATH)/$(BINARY_NAME)-linux $(SOURCE_PATH)

# Build para Windows
windows: deps
	@echo "$(YELLOW)🪟 Building for Windows...$(NC)"
	@mkdir -p $(BIN_PATH)
	@GOOS=windows GOARCH=amd64 go build -ldflags="$(LDFLAGS)" -o $(BIN_PATH)/$(BINARY_NAME).exe $(SOURCE_PATH)

# Build para macOS
macos: deps
	@echo "$(YELLOW)🍎 Building for macOS...$(NC)"
	@mkdir -p $(BIN_PATH)
	@GOOS=darwin GOARCH=amd64 go build -ldflags="$(LDFLAGS)" -o $(BIN_PATH)/$(BINARY_NAME)-macos-intel $(SOURCE_PATH)
	@GOOS=darwin GOARCH=arm64 go build -ldflags="$(LDFLAGS)" -o $(BIN_PATH)/$(BINARY_NAME)-macos-arm64 $(SOURCE_PATH)

# Executar aplicação
run: current
	@echo "$(BLUE)🚀 Running application...$(NC)"
	@./$(BIN_PATH)/$(BINARY_NAME) $(ARGS)

# Executar testes
test:
	@echo "$(BLUE)🧪 Running tests...$(NC)"
	@go test -v ./...

# Limpar arquivos de build
clean:
	@echo "$(YELLOW)🧹 Cleaning build files...$(NC)"
	@rm -rf $(BIN_PATH)
	@rm -rf $(DIST_PATH)
	@go clean
	@echo "$(GREEN)✅ Clean completed!$(NC)"

# Instalar no sistema (apenas Unix/Linux/macOS)
install: current
	@echo "$(BLUE)📥 Installing to system...$(NC)"
ifeq ($(DETECTED_OS),linux)
	@sudo cp $(BIN_PATH)/$(BINARY_NAME) /usr/local/bin/
	@echo "$(GREEN)✅ Installed to /usr/local/bin/$(NC)"
endif
ifeq ($(DETECTED_OS),darwin)
	@sudo cp $(BIN_PATH)/$(BINARY_NAME) /usr/local/bin/
	@echo "$(GREEN)✅ Installed to /usr/local/bin/$(NC)"
endif
ifneq ($(DETECTED_OS),linux)
ifneq ($(DETECTED_OS),darwin)
	@echo "$(RED)❌ Install not supported on this OS$(NC)"
	@echo "$(YELLOW)💡 Copy $(BIN_PATH)/$(BINARY_NAME) manually to your PATH$(NC)"
endif
endif

# Target para desenvolvimento rápido
dev: current
	@echo "$(GREEN)🔧 Development build ready!$(NC)"
	@echo "$(YELLOW)Usage:$(NC)"
	@echo "  ./$(BIN_PATH)/$(BINARY_NAME)                    # Start server"
	@echo "  ./$(BIN_PATH)/$(BINARY_NAME) sketch.hex         # Upload file"
	@echo "  ./$(BIN_PATH)/$(BINARY_NAME) sketch.hex -b DBG  # Debug mode"

# Verificar dependências do sistema
check:
	@echo "$(BLUE)🔍 Checking system dependencies...$(NC)"
	@command -v go >/dev/null 2>&1 || { echo "$(RED)❌ Go is not installed$(NC)"; exit 1; }
	@echo "$(GREEN)✅ Go: $(shell go version)$(NC)"
	@command -v git >/dev/null 2>&1 || { echo "$(YELLOW)⚠️  Git not found (optional)$(NC)"; }
	@git --version 2>/dev/null && echo "$(GREEN)✅ Git: $(shell git --version)$(NC)" || true

# Mostrar informações do projeto
info:
	@echo "$(BLUE)📋 Project Information:$(NC)"
	@echo "  Name: Arduino Uploader (Go Implementation)"
	@echo "  Version: $(VERSION)"
	@echo "  Source: $(SOURCE_PATH)"
	@echo "  Binary: $(BIN_PATH)/$(BINARY_NAME)"
	@echo "  LDFLAGS: $(LDFLAGS)"
	@echo ""
	@echo "$(BLUE)📁 Project Structure:$(NC)"
	@find . -type f -name "*.go" -o -name "*.md" -o -name "Makefile" -o -name "*.mod" | head -10

# Release build (otimizado)
release: clean
	@echo "$(BLUE)🚀 Building release version...$(NC)"
	@mkdir -p $(BIN_PATH)
	@echo "$(YELLOW)Building optimized binaries...$(NC)"
	@GOOS=linux GOARCH=amd64 go build -ldflags="$(LDFLAGS) -X main.buildType=release" -o $(BIN_PATH)/$(BINARY_NAME)-linux $(SOURCE_PATH)
	@GOOS=windows GOARCH=amd64 go build -ldflags="$(LDFLAGS) -X main.buildType=release" -o $(BIN_PATH)/$(BINARY_NAME).exe $(SOURCE_PATH)
	@GOOS=darwin GOARCH=amd64 go build -ldflags="$(LDFLAGS) -X main.buildType=release" -o $(BIN_PATH)/$(BINARY_NAME)-macos-intel $(SOURCE_PATH)
	@GOOS=darwin GOARCH=arm64 go build -ldflags="$(LDFLAGS) -X main.buildType=release" -o $(BIN_PATH)/$(BINARY_NAME)-macos-arm64 $(SOURCE_PATH)
	@echo "$(GREEN)✅ Release build completed!$(NC)"

# Criar arquivo de distribuição
dist: release
	@echo "$(BLUE)📦 Creating distribution package...$(NC)"
	@mkdir -p $(DIST_PATH)/$(BINARY_NAME)
	@cp README.md $(DIST_PATH)/$(BINARY_NAME)
	@cp scripts/* $(DIST_PATH)/$(BINARY_NAME)
	@cp $(BIN_PATH)/$(BINARY_NAME)-linux $(DIST_PATH)/$(BINARY_NAME)
	@cp $(BIN_PATH)/$(BINARY_NAME).exe $(DIST_PATH)/$(BINARY_NAME)
	@cp $(BIN_PATH)/$(BINARY_NAME)-macos-intel $(DIST_PATH)/$(BINARY_NAME)
	@cp $(BIN_PATH)/$(BINARY_NAME)-macos-arm64 $(DIST_PATH)/$(BINARY_NAME)
	@echo "$(BLUE)📦 Release files:$(NC)"
	@ls -lah $(DIST_PATH)/$(BINARY_NAME)
	@tar -czf $(BINARY_NAME)-$(VERSION).tar.gz -C $(DIST_PATH) .
	@sync
	@echo "$(GREEN)✅ Distribution package created: $(BINARY_NAME)-$(VERSION).tar.gz$(NC)"
	@echo "📦 Package Size:"
	@du -b $(BINARY_NAME)-$(VERSION).tar.gz | cut -f1
	@echo "📦 Package Checksum:"
	@sha256sum $(BINARY_NAME)-$(VERSION).tar.gz | cut -f1
	@python3 ./scripts/update_package.py ../../package_websim_arduino_index_local.json --from-file $(BINARY_NAME)-$(VERSION).tar.gz

# Benchmark (se houver testes de benchmark)
bench:
	@echo "$(BLUE)⚡ Running benchmarks...$(NC)"
	@go test -bench=. -benchmem ./... || echo "$(YELLOW)⚠️  No benchmarks found$(NC)"

# Verificar qualidade do código
lint:
	@echo "$(BLUE)🔍 Checking code quality...$(NC)"
	@command -v golint >/dev/null 2>&1 && golint ./... || echo "$(YELLOW)⚠️  golint not installed$(NC)"
	@go vet ./...
	@gofmt -l . | grep -v '^$' && echo "$(RED)❌ Code formatting issues found$(NC)" || echo "$(GREEN)✅ Code formatting OK$(NC)"

# Formatar código
fmt:
	@echo "$(BLUE)✨ Formatting code...$(NC)"
	@go fmt ./...
	@echo "$(GREEN)✅ Code formatted!$(NC)"

# Mostrar estatísticas do projeto
stats:
	@echo "$(BLUE)📊 Project Statistics:$(NC)"
	@echo "  Go files: $(shell find . -name '*.go' | wc -l)"
	@echo "  Lines of code: $(shell find . -name '*.go' -exec wc -l {} + | tail -1 | awk '{print $1}')"
	@echo "  Total files: $(shell find . -type f | wc -l)"
	@echo ""
	@echo "$(BLUE)📈 Dependencies:$(NC)"
	@go list -m all

# Target para CI/CD
ci: check deps test lint build
	@echo "$(GREEN)✅ CI pipeline completed successfully!$(NC)"