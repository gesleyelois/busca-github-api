"""Caso de uso: Buscar PRs por autor."""

from typing import List, Optional, Callable
from ...domain.interfaces.github_repository import IGitHubRepository
from ...domain.entities.pull_request import PullRequest


def gerar_link_busca_github(
    repositorio: str,
    autor: str,
    data_inicio: str,
    data_fim: str,
    branch_base: str = "main"
) -> str:
    """
    Gera o link de busca no GitHub para ver todos os resultados.
    
    Args:
        repositorio: Nome do repositório
        autor: Username do autor
        data_inicio: Data de início
        data_fim: Data de fim
        branch_base: Branch base
        
    Returns:
        URL de busca no GitHub
    """
    query = (
        f"is:pr+repo:{repositorio}+is:merged+base:{branch_base}+"
        f"merged:{data_inicio}..{data_fim}+author:{autor}"
    )
    return f"https://github.com/search?q={query}"


def formatar_resultados(
    autor: str,
    prs: List[PullRequest],
    total_resultados: Optional[int],
    link_busca: str
) -> str:
    """
    Formata os resultados para exibição.
    
    Args:
        autor: Username do autor
        prs: Lista de PRs encontrados
        total_resultados: Total de resultados encontrados (pode ser None em caso de erro)
        link_busca: Link de busca no GitHub
        
    Returns:
        String formatada com os resultados
    """
    resultado = f"\n{autor}\n"
    resultado += "=" * 80 + "\n\n"
    
    # Verifica se há resultados incompletos (só se total_resultados não for None)
    if total_resultados is not None and total_resultados > len(prs):
        resultado += (
            f"Observação: a busca retornou {total_resultados} resultados no total, "
            f"a API trouxe {len(prs)}; os resultados estão incompletos. "
            f"Ver todos no GitHub: {link_busca}\n\n"
        )
    
    if not prs:
        resultado += "Nenhum PR encontrado no período.\n"
        return resultado
    
    resultado += (
        f"PRs ({len(prs)} encontrados — cada linha = título — link — "
        f"data do merge — breve descrição):\n\n"
    )
    
    for pr in prs:
        resultado += (
            f"  • {pr.titulo} — {pr.link} — "
            f"merged: {pr.data_merge} — {pr.descricao}\n"
        )
    
    return resultado


class BuscarPRsPorAutorUseCase:
    """Caso de uso para buscar PRs por autor."""
    
    def __init__(self, github_repository: IGitHubRepository):
        """
        Inicializa o caso de uso.
        
        Args:
            github_repository: Repositório do GitHub
        """
        self.github_repository = github_repository
    
    def executar(
        self,
        repositorio: str,
        autor: str,
        data_inicio: str,
        data_fim: str,
        branch_base: str = "main",
        callback_progresso: Optional[Callable] = None
    ) -> tuple[List[PullRequest], Optional[int], str]:
        """
        Executa a busca de PRs por autor.
        
        Args:
            repositorio: Nome do repositório (formato: owner/repo)
            autor: Username do autor no GitHub
            data_inicio: Data de início (formato: YYYY-MM-DD)
            data_fim: Data de fim (formato: YYYY-MM-DD)
            branch_base: Branch base dos PRs (padrão: main)
            callback_progresso: Função callback para atualizar progresso
            
        Returns:
            Tupla (lista de PRs, total de resultados ou None em caso de erro, link de busca)
        """
        prs, total_resultados = self.github_repository.buscar_prs_por_autor(
            repositorio=repositorio,
            autor=autor,
            data_inicio=data_inicio,
            data_fim=data_fim,
            branch_base=branch_base,
            callback_progresso=callback_progresso
        )
        
        link_busca = gerar_link_busca_github(
            repositorio=repositorio,
            autor=autor,
            data_inicio=data_inicio,
            data_fim=data_fim,
            branch_base=branch_base
        )
        
        return prs, total_resultados, link_busca

