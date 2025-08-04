# Arduino Web Uploader - Go Implementation

Esta é uma implementação em Go da aplicação Java original que permite fazer upload de código Arduino através de WebSockets para uma interface web.

## Estrutura do Projeto

```
arduino-uploader/
├── go.mod
├── go.sum
├── README.md
├── src/
│   └── main.go
└── bin/ (criado após compilação)
    ├── arduino-uploader      (Linux/macOS)
    └── arduino-uploader.exe  (Windows)
```

## Funcionalidades

- **Server WebSocket**: Recebe arquivos `.hex` e os retransmite para clientes web conectados
- **Cliente CLI**: Envia arquivos para o servidor WebSocket
- **Debug Support**: Suporte para placas com modo debug (`_DBG`)
- **Cross-platform**: Compatível com Linux, Windows e macOS
- **Auto-start**: Se o servidor não estiver rodando, ele é iniciado automaticamente

## Instalação

### Pré-requisitos

- Go 1.19 ou superior
- Git (para baixar dependências)
- Make (opcional, para usar Makefile)

### Estrutura de diretórios

Crie a seguinte estrutura:

```bash
mkdir arduino-uploader
cd arduino-uploader
mkdir src bin
```

### Métodos de Compilação

#### Método 1: Usando Makefile (Recomendado para Linux/macOS)

```bash
# Verificar dependências
make check

# Build completo para todas as plataformas
make build

# Build apenas para sistema atual
make current

# Build específico por plataforma
make linux     # Para Linux
make windows   # Para Windows  
make macos     # Para macOS

# Build otimizado para release
make release

# Ver todas as opções
make help
```

#### Método 2: Usando Scripts de Build

**Linux/macOS:**
```bash
chmod +x build.sh
./build.sh
```

**Windows PowerShell:**
```powershell
.\build.ps1
# ou com limpeza
.\build.ps1 -Clean
```

#### Método 3: Build Manual

1. Coloque o `go.mod` na raiz do projeto
2. Coloque o `main.go` na pasta `src/`
3. Instale as dependências:

```bash
go mod tidy
```

4. Compile o projeto:

```bash
# Para o sistema atual
go build -o bin/arduino-uploader src/main.go

# Para Linux (64-bit)
GOOS=linux GOARCH=amd64 go build -o bin/arduino-uploader-linux src/main.go

# Para Windows (64-bit)
GOOS=windows GOARCH=amd64 go build -o bin/arduino-uploader.exe src/main.go

# Para macOS (64-bit)
GOOS=darwin GOARCH=amd64 go build -o bin/arduino-uploader-macos src/main.go
```

### Instalação no Sistema

**Linux/macOS com Makefile:**
```bash
make install
```

**Manual:**
```bash
# Linux/macOS
sudo cp bin/arduino-uploader /usr/local/bin/

# Windows - copie para um diretório no PATH
copy bin\arduino-uploader.exe C:\Windows\System32\
```

## Uso

### Iniciar apenas o servidor

```bash
./bin/arduino-uploader
```

O servidor será iniciado na porta `8887` e ficará aguardando conexões.

### Fazer upload de um arquivo

```bash
./bin/arduino-uploader /path/to/sketch.hex
```

### Upload com suporte a debug

```bash
./bin/arduino-uploader /path/to/sketch.hex -b BOARD_NAME_DBG
```

## Como funciona

1. **Auto-detecção**: O programa primeiro tenta se conectar a um servidor existente
2. **Envio direto**: Se conseguir conectar, envia o arquivo e termina
3. **Iniciar servidor**: Se não conseguir conectar, inicia o servidor
4. **Segunda tentativa**: Após iniciar o servidor, tenta enviar o arquivo novamente
5. **Servidor persistente**: O servidor fica rodando para futuras conexões

## Arquitetura

### Componentes principais

- **WSServer**: Gerencia conexões WebSocket e roteamento de mensagens
- **Client CLI**: Envia arquivos para o servidor
- **Debug Handler**: Processa informações de debug para placas especiais
- **File Parser**: Analisa arquivos `.elf` para extrair breakpoints

### Fluxo de dados

1. Cliente CLI lê arquivo `.hex`
2. Conecta via WebSocket ao servidor
3. Envia dados binários do arquivo
4. Servidor retransmite para cliente web conectado
5. Cliente web recebe o arquivo para processamento

## Diferenças da versão Java

### Melhorias

- **Código mais limpo**: Menos verbosidade, mais legível
- **Melhor tratamento de erros**: Erros mais informativos
- **Cross-platform nativo**: Não requer JVM
- **Menor footprint**: Executável menor e menor uso de memória
- **Compilação estática**: Um único executável sem dependências

### Compatibilidade

- Mantém a mesma porta (8887)
- Mesmo protocolo WebSocket
- Mesma estrutura de mensagens JSON
- Compatível com o frontend web existente

## Configuração

### Variáveis importantes

- `PORT`: Porta do servidor WebSocket (padrão: 8887)
- `WEB_SIGNATURE`: Assinatura para identificar clientes web

### Arquivos necessários para debug

- `build.options.json`: Contém caminhos para ferramentas AVR
- `sketch.elf`: Arquivo ELF para análise de debug
- Arquivos fonte `.ino`: Para extração de código fonte

## Troubleshooting

### Servidor não inicia

- Verifique se a porta 8887 está disponível
- Execute com privilégios adequados se necessário

### Falha no upload

- Certifique-se de que o arquivo `.hex` existe
- Verifique se há clientes web conectados

### Debug não funciona

- Verifique se o arquivo `build.options.json` existe
- Confirme se as ferramentas AVR estão instaladas
- Verifique os caminhos no arquivo de configuração

### Problemas de conexão

- Confirme se não há firewall bloqueando a porta
- Tente reiniciar o servidor
- Verifique se o cliente web está acessível

### Dependências

- `github.com/gorilla/websocket`: Biblioteca WebSocket
- Bibliotecas padrão do Go para HTTP, JSON, regexp, etc.

## Licença

Este projeto mantém compatibilidade com a aplicação Java original.