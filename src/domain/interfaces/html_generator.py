"""Interface para gerador de HTML."""

from abc import ABC, abstractmethod
from typing import Dict, List
from ..entities.pull_request import PullRequest


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
    
    @abstractmethod
    def preparar_dados_para_html(
        self,
        repositorio: str,
        periodo: str,
        branch: str,
        autores_prs: Dict[str, List[PullRequest]],
        observacoes: List[str] = None
    ) -> Dict:
        """Prepara dados estruturados para geração de HTML a partir de PRs."""
        pass

