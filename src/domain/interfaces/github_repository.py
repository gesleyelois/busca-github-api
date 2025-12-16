"""Interface para repositório do GitHub."""

from abc import ABC, abstractmethod
from typing import List, Optional, Callable
from ..entities.pull_request import PullRequest


class IGitHubRepository(ABC):
    """Interface para acessar a API do GitHub."""
    
    @abstractmethod
    def buscar_prs_por_autor(
        self,
        repositorio: str,
        autor: str,
        data_inicio: str,
        data_fim: str,
        branch_base: str = "main",
        callback_progresso: Optional[Callable] = None
    ) -> tuple[List[PullRequest], Optional[int]]:
        """
        Busca PRs mergeados por autor em um intervalo de datas.
        
        Args:
            repositorio: Nome do repositório (formato: owner/repo)
            autor: Username do autor no GitHub
            data_inicio: Data de início (formato: YYYY-MM-DD)
            data_fim: Data de fim (formato: YYYY-MM-DD)
            branch_base: Branch base dos PRs (padrão: main)
            callback_progresso: Função callback para atualizar progresso
            
        Returns:
            Tupla (lista de Pull Requests encontrados, total de resultados ou None em caso de erro)
        """
        pass
    
    @abstractmethod
    def obter_branch_e_commits(self, repositorio: str, numero_pr: int) -> tuple[str, List[str]]:
        """
        Obtém o nome da branch e as mensagens de commit de um PR específico.
        
        Args:
            repositorio: Nome do repositório
            numero_pr: Número do PR
            
        Returns:
            Tupla (nome_branch, lista_mensagens_commit)
        """
        pass

