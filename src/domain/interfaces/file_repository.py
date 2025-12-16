"""Interface para repositório de arquivos."""

from abc import ABC, abstractmethod
from typing import List


class IFileRepository(ABC):
    """Interface para operações com arquivos."""
    
    @abstractmethod
    def salvar(self, conteudo: str, caminho: str) -> bool:
        """Salva conteúdo em um arquivo."""
        pass
    
    @abstractmethod
    def ler(self, caminho: str) -> str:
        """Lê conteúdo de um arquivo."""
        pass
    
    @abstractmethod
    def ler_autores(self, caminho: str) -> List[str]:
        """Lê lista de autores de um arquivo."""
        pass
    
    @abstractmethod
    def existe(self, caminho: str) -> bool:
        """Verifica se um arquivo existe."""
        pass

