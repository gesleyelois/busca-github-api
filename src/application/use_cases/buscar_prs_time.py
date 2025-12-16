"""Caso de uso: Buscar PRs do time."""

from typing import List
from ...domain.interfaces.github_repository import IGitHubRepository
from ...domain.interfaces.file_repository import IFileRepository
from .buscar_prs_por_autor import formatar_resultados, gerar_link_busca_github


class BuscarPRsTimeUseCase:
    """Caso de uso para buscar PRs de múltiplos autores (time)."""
    
    def __init__(
        self,
        github_repository: IGitHubRepository,
        file_repository: IFileRepository
    ):
        """
        Inicializa o caso de uso.
        
        Args:
            github_repository: Repositório do GitHub
            file_repository: Repositório de arquivos
        """
        self.github_repository = github_repository
        self.file_repository = file_repository
    
    def executar(
        self,
        repositorio: str,
        autores: List[str],
        data_inicio: str,
        data_fim: str,
        branch_base: str = "main",
        arquivo_saida: str = None,
        callback_progresso: callable = None
    ) -> str:
        """
        Executa a busca de PRs para múltiplos autores.
        
        Args:
            repositorio: Nome do repositório (formato: owner/repo)
            autores: Lista de usernames dos autores
            data_inicio: Data de início (formato: YYYY-MM-DD)
            data_fim: Data de fim (formato: YYYY-MM-DD)
            branch_base: Branch base dos PRs (padrão: main)
            arquivo_saida: Arquivo para salvar o resultado
            callback_progresso: Função callback para atualizar progresso
            
        Returns:
            Resultado formatado como string
        """
        resultado_completo = "Observações importantes antes das listas:\n\n"
        resultado_completo += (
            "  • Usei a API do GitHub para buscar os PRs mergeados por autor nesse intervalo. "
            "Alguns resultados da API estavam incompletos por limite de paginação "
            "(o GitHub Search retorna no máximo 30 resultados por página). "
            "Onde aplicou, marquei que os resultados estão incompletos e deixei o link de busca "
            "no GitHub para ver o conjunto completo.\n\n"
        )
        resultado_completo += (
            "  • As respostas de busca trazem título do PR, link e data de merge e muitas vezes "
            "o corpo/descrição do PR. Porém a listagem de busca não inclui sempre o nome da branch "
            "nem todas as mensagens de commit. Posso buscar branch + commits para PRs específicos "
            "caso queira — solicite quais PRs quer em detalhe.\n\n"
        )
        resultado_completo += (
            "  • Vou fornecer uma breve descrição (1–2 linhas) por PR usando o título e a descrição "
            "encontrada no PR. Se quiser que eu extraia exatamente o nome da branch e todas as "
            "mensagens de commit, peço que diga quais PRs priorizar (faço isso PR-a-PR).\n\n"
        )
        resultado_completo += "=" * 80 + "\n\n"
        
        total_autores = len(autores)
        total_prs_encontrados = 0
        
        # Busca PRs para cada autor
        for indice, autor in enumerate(autores, 1):
            def callback(pagina, total, prs_encontrados, erro=None):
                if callback_progresso:
                    callback_progresso(autor, indice, total_autores, pagina, total, prs_encontrados, erro)
            
            prs, total_resultados = self.github_repository.buscar_prs_por_autor(
                repositorio=repositorio,
                autor=autor,
                data_inicio=data_inicio,
                data_fim=data_fim,
                branch_base=branch_base,
                callback_progresso=callback
            )
            
            link_busca = gerar_link_busca_github(
                repositorio=repositorio,
                autor=autor,
                data_inicio=data_inicio,
                data_fim=data_fim,
                branch_base=branch_base
            )
            
            resultado_autor = formatar_resultados(autor, prs, total_resultados, link_busca)
            resultado_completo += resultado_autor + "\n"
            
            total_prs_encontrados += len(prs)
        
        # Salva resultado se especificado
        if arquivo_saida:
            self.file_repository.salvar(resultado_completo, arquivo_saida)
        
        return resultado_completo

