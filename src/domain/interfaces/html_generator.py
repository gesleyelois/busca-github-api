"""Interface para gerador de HTML."""

from abc import ABC, abstractmethod
from typing import Dict


class IHTMLGenerator(ABC):
    """Interface para gerador de HTML."""
    
    @abstractmethod
    def parsear_resultado_txt(self, caminho_arquivo: str) -> Dict:
        """Parseia arquivo de resultado e retorna dados estruturados."""
        pass
    
    @abstractmethod
    def gerar_html(self, dados: Dict) -> str:
        """Gera HTML a partir dos dados parseados."""
        pass

