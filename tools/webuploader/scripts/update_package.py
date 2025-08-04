#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para atualizar valores específicos em JSON do WebSim Arduino
Foco: Atualizar size e checksum da ferramenta webuploader
"""

import json
import os
import hashlib
import argparse
import sys
from typing import Dict, Any, Optional

class WebSimJSONUpdater:
    def __init__(self, json_file_path: str):
        """
        Inicializa o atualizador com o caminho do arquivo JSON
        
        Args:
            json_file_path (str): Caminho para o arquivo JSON
        """
        self.json_file_path = json_file_path
        self.data = None
        
    def load_json(self) -> bool:
        """
        Carrega o arquivo JSON
        
        Returns:
            bool: True se carregado com sucesso, False caso contrário
        """
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as file:
                self.data = json.load(file)
            return True
        except FileNotFoundError:
            print(f"Erro: Arquivo {self.json_file_path} não encontrado.")
            return False
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON: {e}")
            return False
        except Exception as e:
            print(f"Erro inesperado ao carregar JSON: {e}")
            return False
    
    def save_json(self, backup: bool = True) -> bool:
        """
        Salva o arquivo JSON
        
        Args:
            backup (bool): Se deve criar backup antes de salvar
            
        Returns:
            bool: True se salvo com sucesso, False caso contrário
        """
        try:
            # Criar backup se solicitado
            if backup and os.path.exists(self.json_file_path):
                backup_path = f"{self.json_file_path}.backup"
                with open(self.json_file_path, 'r', encoding='utf-8') as original:
                    with open(backup_path, 'w', encoding='utf-8') as backup_file:
                        backup_file.write(original.read())
                print(f"Backup criado: {backup_path}")
            
            # Salvar arquivo atualizado
            with open(self.json_file_path, 'w', encoding='utf-8') as file:
                json.dump(self.data, file, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao salvar JSON: {e}")
            return False
    
    def update_tool_values(self, tool_name: str, new_size: str, new_checksum: str, 
                          host_filter: Optional[str] = None) -> bool:
        """
        Atualiza os valores de size e checksum de uma ferramenta específica
        
        Args:
            tool_name (str): Nome da ferramenta a ser atualizada
            new_size (str): Novo valor para size
            new_checksum (str): Novo valor para checksum
            host_filter (str, optional): Filtrar por host específico
            
        Returns:
            bool: True se atualizado com sucesso, False caso contrário
        """
        if not self.data:
            print("Erro: JSON não carregado. Execute load_json() primeiro.")
            return False
        
        updated_count = 0
        
        try:
            # Navegar pela estrutura JSON
            for package in self.data.get('packages', []):
                for tool in package.get('tools', []):
                    if tool.get('name') == tool_name:
                        for system in tool.get('systems', []):
                            # Aplicar filtro de host se especificado
                            if host_filter and system.get('host') != host_filter:
                                continue
                                
                            # Atualizar valores
                            old_size = system.get('size', 'N/A')
                            old_checksum = system.get('checksum', 'N/A')
                            
                            system['size'] = new_size
                            system['checksum'] = new_checksum
                            
                            print(f"Tool: {tool_name}")
                            print(f"Host: {system.get('host')}")
                            print(f"  Size: {old_size} → {new_size}")
                            print(f"  Checksum: {old_checksum} → {new_checksum}")
                            print()
                            
                            updated_count += 1
            
            if updated_count > 0:
                print(f"✅ {updated_count} sistema(s) da ferramenta '{tool_name}' atualizado(s) com sucesso!")
                return True
            else:
                print(f"⚠️ Nenhum sistema da ferramenta '{tool_name}' encontrado para atualizar.")
                return False
                
        except Exception as e:
            print(f"Erro ao atualizar valores: {e}")
            return False
    
    def update_webuploader_values(self, new_size: str, new_checksum: str, 
                                 host_filter: Optional[str] = None) -> bool:
        """
        Atualiza os valores de size e checksum da ferramenta webuploader (método de compatibilidade)
        
        Args:
            new_size (str): Novo valor para size
            new_checksum (str): Novo valor para checksum
            host_filter (str, optional): Filtrar por host específico
            
        Returns:
            bool: True se atualizado com sucesso, False caso contrário
        """
        return self.update_tool_values('webuploader', new_size, new_checksum, host_filter)
    
    def calculate_file_checksum(self, file_path: str, algorithm: str = 'sha256') -> Optional[str]:
        """
        Calcula o checksum de um arquivo
        
        Args:
            file_path (str): Caminho do arquivo
            algorithm (str): Algoritmo de hash (sha256, md5, etc.)
            
        Returns:
            str: Checksum calculado ou None se erro
        """
        try:
            hash_obj = hashlib.new(algorithm)
            with open(file_path, 'rb') as file:
                for chunk in iter(lambda: file.read(4096), b""):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except FileNotFoundError:
            print(f"Erro: Arquivo {file_path} não encontrado.")
            return None
        except Exception as e:
            print(f"Erro ao calcular checksum: {e}")
            return None
    
    def get_file_size(self, file_path: str) -> Optional[str]:
        """
        Obtém o tamanho de um arquivo
        
        Args:
            file_path (str): Caminho do arquivo
            
        Returns:
            str: Tamanho do arquivo em bytes como string ou None se erro
        """
        try:
            size = os.path.getsize(file_path)
            return str(size)
        except FileNotFoundError:
            print(f"Erro: Arquivo {file_path} não encontrado.")
            return None
        except Exception as e:
            print(f"Erro ao obter tamanho do arquivo: {e}")
            return None
    
    def update_from_file(self, file_path: str, tool_name: str = 'webuploader', 
                        host_filter: Optional[str] = None) -> bool:
        """
        Atualiza size e checksum baseado em um arquivo local
        
        Args:
            file_path (str): Caminho do arquivo para calcular size/checksum
            tool_name (str): Nome da ferramenta a ser atualizada
            host_filter (str, optional): Filtrar por host específico
            
        Returns:
            bool: True se atualizado com sucesso, False caso contrário
        """
        # Calcular size e checksum do arquivo
        new_size = self.get_file_size(file_path)
        if not new_size:
            return False
            
        new_checksum = self.calculate_file_checksum(file_path)
        if not new_checksum:
            return False
        
        # Formatar checksum no padrão esperado (SHA-256:hash)
        formatted_checksum = f"SHA-256:{new_checksum}"
        
        print(f"Arquivo: {file_path}")
        print(f"Size calculado: {new_size}")
        print(f"Checksum calculado: {formatted_checksum}")
        print()
        
        return self.update_tool_values(tool_name, new_size, formatted_checksum, host_filter)
    
    def display_current_values(self, tool_name: Optional[str] = None):
        """
        Exibe os valores atuais das ferramentas
        
        Args:
            tool_name (str, optional): Nome específico da ferramenta, se None mostra todas
        """
        if not self.data:
            print("Erro: JSON não carregado. Execute load_json() primeiro.")
            return
        
        if tool_name:
            print(f"=== Valores Atuais da Ferramenta: {tool_name} ===")
        else:
            print("=== Valores Atuais de Todas as Ferramentas ===")
        
        found = False
        
        for package in self.data.get('packages', []):
            for tool in package.get('tools', []):
                # Filtrar por ferramenta específica se solicitado
                if tool_name and tool.get('name') != tool_name:
                    continue
                    
                found = True
                print(f"Ferramenta: {tool.get('name')} v{tool.get('version')}")
                for system in tool.get('systems', []):
                    print(f"  Host: {system.get('host')}")
                    print(f"  Size: {system.get('size')}")
                    print(f"  Checksum: {system.get('checksum')}")
                    print(f"  URL: {system.get('url')}")
                    print()
        
        if not found:
            if tool_name:
                print(f"⚠️ Ferramenta '{tool_name}' não encontrada no JSON.")
            else:
                print("⚠️ Nenhuma ferramenta encontrada no JSON.")

# Função de exemplo de uso
def main():
    """
    Função principal com argumentos da linha de comando
    """
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(
        description='Atualiza valores específicos no JSON do WebSim Arduino',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  %(prog)s arquivo.json --show                                           # Mostra todas as ferramentas
  %(prog)s arquivo.json --show --tool webuploader                       # Mostra ferramenta específica
  %(prog)s arquivo.json --tool webuploader --size 2507992 --checksum abc123    # Atualiza ferramenta específica
  %(prog)s arquivo.json --tool webuploader --from-file webuploader.tar.gz      # Calcula de arquivo local
  %(prog)s arquivo.json --tool webuploader --size 2507992 --checksum abc123 --host x86_64-linux-gnu  # Host específico
        """
    )
    
    # Argumentos obrigatórios
    parser.add_argument('json_file', 
                       help='Caminho para o arquivo JSON a ser atualizado')
    
    # Argumentos opcionais para atualização
    parser.add_argument('--tool', '-t',
                       default='webuploader',
                       help='Nome da ferramenta a ser atualizada (padrão: webuploader)')
    
    parser.add_argument('--size', '-s',
                       help='Novo valor para o campo size')
    
    parser.add_argument('--checksum', '-c',
                       help='Novo valor para o campo checksum (sem prefixo SHA-256:)')
    
    parser.add_argument('--from-file', '-f',
                       help='Calcular size e checksum de um arquivo local')
    
    parser.add_argument('--host',
                       help='Filtrar por host específico (ex: x86_64-linux-gnu)')
    
    parser.add_argument('--show', '-v',
                       action='store_true',
                       help='Apenas exibir valores atuais sem modificar')
    
    parser.add_argument('--no-backup',
                       action='store_true',
                       help='Não criar backup antes de salvar')
    
    # Parse dos argumentos
    args = parser.parse_args()
    
    # Verificar se arquivo JSON existe
    if not os.path.exists(args.json_file):
        print(f"❌ Erro: Arquivo '{args.json_file}' não encontrado.")
        sys.exit(1)
    
    # Criar instância do atualizador
    updater = WebSimJSONUpdater(args.json_file)
    
    # Carregar JSON
    if not updater.load_json():
        sys.exit(1)
    
    # Exibir valores atuais
    updater.display_current_values(args.tool if not args.show else None)
    
    # Se apenas mostrar, sair
    if args.show:
        return
    
    # Verificar se foram fornecidos parâmetros de atualização
    if not (args.size and args.checksum) and not args.from_file:
        print("\n⚠️ Para atualizar, forneça:")
        print("  - --size e --checksum juntos, OU")
        print("  - --from-file com caminho do arquivo")
        print("\nUse --help para ver exemplos.")
        return
    
    success = False
    
    # Atualização baseada em arquivo
    if args.from_file:
        print(f"\n=== Atualizando ferramenta '{args.tool}' baseado no arquivo: {args.from_file} ===")
        success = updater.update_from_file(args.from_file, args.tool, args.host)
    
    # Atualização com valores específicos
    elif args.size and args.checksum:
        print(f"\n=== Atualizando ferramenta '{args.tool}' com valores específicos ===")
        # Adicionar prefixo SHA-256 se não estiver presente
        checksum = args.checksum
        if not checksum.startswith('SHA-256:'):
            checksum = f"SHA-256:{checksum}"
        
        success = updater.update_tool_values(args.tool, args.size, checksum, args.host)
    
    # Salvar se houve sucesso
    if success:
        backup = not args.no_backup
        if updater.save_json(backup=backup):
            print(f"✅ Arquivo '{args.json_file}' atualizado com sucesso!")
        else:
            print("❌ Erro ao salvar arquivo.")
            sys.exit(1)
    else:
        print("❌ Nenhuma atualização foi realizada.")
        sys.exit(1)


if __name__ == "__main__":
    main()