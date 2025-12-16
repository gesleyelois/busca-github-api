"""Implementação de repositório de arquivos."""

import os
from typing import List

from ...domain.interfaces.file_repository import IFileRepository


class FileRepository(IFileRepository):
    """Implementação de repositório de arquivos."""
    
    def salvar(self, conteudo: str, caminho: str) -> bool:
        """Salva conteúdo em um arquivo."""
        try:
            # Garante que o diretório existe
            dir_path = os.path.dirname(caminho)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(conteudo)
            return True
        except Exception as e:
            print(f"\n❌ Erro ao salvar resultado: {e}")
            return False
    
    def ler(self, caminho: str) -> str:
        """Lê conteúdo de um arquivo."""
        with open(caminho, "r", encoding="utf-8") as f:
            return f.read()
    
    def ler_autores(self, caminho: str) -> List[str]:
        """
        Lê lista de autores de um arquivo.
        
        Args:
            caminho: Caminho para o arquivo com a lista de autores
            
        Returns:
            Lista de autores (sem linhas vazias e comentários)
        """
        autores = []
        
        if not os.path.exists(caminho):
            return autores
        
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                for linha in f:
                    linha = linha.strip()
                    # Ignora linhas vazias e comentários
                    if linha and not linha.startswith("#"):
                        autores.append(linha)
        except Exception as e:
            print(f"Erro ao ler arquivo de autores {caminho}: {e}")
        
        return autores
    
    def existe(self, caminho: str) -> bool:
        """Verifica se um arquivo existe."""
        return os.path.exists(caminho)

