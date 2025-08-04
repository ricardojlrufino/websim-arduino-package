#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para atualizar valores específicos em JSON do WebSim Arduino
Foco: Atualizar size e checksum das plataformas (packages.platforms)
python platform_updater.py arquivo.json --platform "WebSim AVR Boards" --from-file websim-avr-1.0.zip
"""

import json
import os
import hashlib
import argparse
import sys
from typing import Dict, Any, Optional

class WebSimPlatformUpdater:
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
    
    def update_platform_values(self, platform_name: str, new_size: str, new_checksum: str) -> bool:
        """
        Atualiza os valores de size e checksum de uma plataforma específica
        
        Args:
            platform_name (str): Nome da plataforma a ser atualizada
            new_size (str): Novo valor para size
            new_checksum (str): Novo valor para checksum
            
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
                for platform in package.get('platforms', []):
                    if platform.get('name') == platform_name:
                        # Atualizar valores
                        old_size = platform.get('size', 'N/A')
                        old_checksum = platform.get('checksum', 'N/A')
                        
                        platform['size'] = new_size
                        platform['checksum'] = new_checksum
                        
                        print(f"Plataforma: {platform_name}")
                        print(f"  Versão: {platform.get('version', 'N/A')}")
                        print(f"  Arquitetura: {platform.get('architecture', 'N/A')}")
                        print(f"  Size: {old_size} → {new_size}")
                        print(f"  Checksum: {old_checksum} → {new_checksum}")
                        print(f"  URL: {platform.get('url', 'N/A')}")
                        print()
                        
                        updated_count += 1
            
            if updated_count > 0:
                print(f"✅ {updated_count} plataforma(s) '{platform_name}' atualizada(s) com sucesso!")
                return True
            else:
                print(f"⚠️ Nenhuma plataforma '{platform_name}' encontrada para atualizar.")
                return False
                
        except Exception as e:
            print(f"Erro ao atualizar valores: {e}")
            return False
    
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
    
    def update_from_file(self, file_path: str, platform_name: str) -> bool:
        """
        Atualiza size e checksum baseado em um arquivo local
        
        Args:
            file_path (str): Caminho do arquivo para calcular size/checksum
            platform_name (str): Nome da plataforma a ser atualizada
            
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
        
        return self.update_platform_values(platform_name, new_size, formatted_checksum)
    
    def display_current_values(self, platform_name: Optional[str] = None):
        """
        Exibe os valores atuais das plataformas
        
        Args:
            platform_name (str, optional): Nome específico da plataforma, se None mostra todas
        """
        if not self.data:
            print("Erro: JSON não carregado. Execute load_json() primeiro.")
            return
        
        if platform_name:
            print(f"=== Valores Atuais da Plataforma: {platform_name} ===")
        else:
            print("=== Valores Atuais de Todas as Plataformas ===")
        
        found = False
        
        for package in self.data.get('packages', []):
            print(f"Package: {package.get('name', 'N/A')}")
            for platform in package.get('platforms', []):
                # Filtrar por plataforma específica se solicitado
                if platform_name and platform.get('name') != platform_name:
                    continue
                    
                found = True
                print(f"  Plataforma: {platform.get('name')}")
                print(f"    Versão: {platform.get('version')}")
                print(f"    Arquitetura: {platform.get('architecture')}")
                print(f"    Categoria: {platform.get('category')}")
                print(f"    Size: {platform.get('size')}")
                print(f"    Checksum: {platform.get('checksum')}")
                print(f"    URL: {platform.get('url')}")
                print(f"    Archive: {platform.get('archiveFileName')}")
                
                # Mostrar boards se existirem
                boards = platform.get('boards', [])
                if boards:
                    print(f"    Boards: {', '.join(board.get('name', 'N/A') for board in boards)}")
                
                print()
            print()
        
        if not found:
            if platform_name:
                print(f"⚠️ Plataforma '{platform_name}' não encontrada no JSON.")
            else:
                print("⚠️ Nenhuma plataforma encontrada no JSON.")
    
    def list_platforms(self):
        """
        Lista todas as plataformas disponíveis no JSON
        """
        if not self.data:
            print("Erro: JSON não carregado. Execute load_json() primeiro.")
            return
        
        print("=== Plataformas Disponíveis ===")
        platforms_found = []
        
        for package in self.data.get('packages', []):
            package_name = package.get('name', 'N/A')
            for platform in package.get('platforms', []):
                platform_info = {
                    'package': package_name,
                    'name': platform.get('name'),
                    'version': platform.get('version'),
                    'architecture': platform.get('architecture')
                }
                platforms_found.append(platform_info)
        
        if platforms_found:
            for platform in platforms_found:
                print(f"  • {platform['name']} (v{platform['version']}) - {platform['architecture']} - Package: {platform['package']}")
        else:
            print("⚠️ Nenhuma plataforma encontrada no JSON.")
        
        print(f"\nTotal: {len(platforms_found)} plataforma(s)")


# Função principal com argumentos da linha de comando
def main():
    """
    Função principal com argumentos da linha de comando
    """
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(
        description='Atualiza valores específicos de plataformas no JSON do WebSim Arduino',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  %(prog)s arquivo.json --show                                             # Mostra todas as plataformas
  %(prog)s arquivo.json --show --platform "WebSim AVR Boards"             # Mostra plataforma específica
  %(prog)s arquivo.json --list                                             # Lista plataformas disponíveis
  %(prog)s arquivo.json --platform "WebSim AVR Boards" --size 5588 --checksum abc123    # Atualiza plataforma específica
  %(prog)s arquivo.json --platform "WebSim AVR Boards" --from-file websim-avr-1.0.zip  # Calcula de arquivo local
        """
    )
    
    # Argumentos obrigatórios
    parser.add_argument('json_file', 
                       help='Caminho para o arquivo JSON a ser atualizado')
    
    # Argumentos opcionais para atualização
    parser.add_argument('--platform', '-p',
                       default='WebSim AVR Boards',
                       help='Nome da plataforma a ser atualizada (padrão: "WebSim AVR Boards")')
    
    parser.add_argument('--size', '-s',
                       help='Novo valor para o campo size')
    
    parser.add_argument('--checksum', '-c',
                       help='Novo valor para o campo checksum (sem prefixo SHA-256:)')
    
    parser.add_argument('--from-file', '-f',
                       help='Calcular size e checksum de um arquivo local')
    
    parser.add_argument('--show', '-v',
                       action='store_true',
                       help='Apenas exibir valores atuais sem modificar')
    
    parser.add_argument('--list', '-l',
                       action='store_true',
                       help='Listar todas as plataformas disponíveis')
    
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
    updater = WebSimPlatformUpdater(args.json_file)
    
    # Carregar JSON
    if not updater.load_json():
        sys.exit(1)
    
    # Listar plataformas se solicitado
    if args.list:
        updater.list_platforms()
        return
    
    # Exibir valores atuais
    if args.show:
        updater.display_current_values(args.platform)
        return
    else:
        updater.display_current_values(args.platform)
    
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
        print(f"\n=== Atualizando plataforma '{args.platform}' baseado no arquivo: {args.from_file} ===")
        success = updater.update_from_file(args.from_file, args.platform)
    
    # Atualização com valores específicos
    elif args.size and args.checksum:
        print(f"\n=== Atualizando plataforma '{args.platform}' com valores específicos ===")
        # Adicionar prefixo SHA-256 se não estiver presente
        checksum = args.checksum
        if not checksum.startswith('SHA-256:'):
            checksum = f"SHA-256:{checksum}"
        
        success = updater.update_platform_values(args.platform, args.size, checksum)
    
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