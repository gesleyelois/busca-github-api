"""Cliente para interagir com a API do GitHub."""

import requests
import time
from datetime import datetime
from typing import List, Dict, Optional, Callable, Tuple

from ...domain.interfaces.github_repository import IGitHubRepository
from ...domain.entities.pull_request import PullRequest


class GitHubAPIClient(IGitHubRepository):
    """Cliente para interagir com a API do GitHub."""
    
    BASE_URL = "https://api.github.com"
    SEARCH_URL = f"{BASE_URL}/search/issues"
    
    def __init__(self, token: Optional[str] = None):
        """
        Inicializa o cliente da API.
        
        Args:
            token: Token de autenticação do GitHub (opcional, mas recomendado)
        """
        self.token = token
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
    
    def _fazer_requisicao(self, url: str, params: Dict = None) -> Dict:
        """
        Faz uma requisição à API do GitHub com tratamento de rate limiting.
        
        Args:
            url: URL da requisição
            params: Parâmetros da query string
            
        Returns:
            Resposta JSON da API
        """
        response = requests.get(url, headers=self.headers, params=params)
        
        # Verifica rate limiting
        if response.status_code == 403:
            rate_limit_remaining = response.headers.get("X-RateLimit-Remaining", "0")
            if rate_limit_remaining == "0":
                reset_time = response.headers.get("X-RateLimit-Reset")
                if reset_time:
                    reset_datetime = datetime.fromtimestamp(int(reset_time))
                    raise Exception(
                        f"Rate limit excedido. Tente novamente após {reset_datetime}"
                    )
        
        response.raise_for_status()
        return response.json()
    
    def buscar_prs_por_autor(
        self,
        repositorio: str,
        autor: str,
        data_inicio: str,
        data_fim: str,
        branch_base: str = "main",
        callback_progresso: Optional[Callable] = None
    ) -> Tuple[List[PullRequest], int]:
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
            Tupla (lista de Pull Requests encontrados, total de resultados)
        """
        prs = []
        pagina = 1
        total_resultados = None
        resultados_por_pagina = 30
        
        while True:
            # Monta a query de busca
            query = (
                f"is:pr repo:{repositorio} is:merged "
                f"base:{branch_base} merged:{data_inicio}..{data_fim} "
                f"author:{autor}"
            )
            
            params = {
                "q": query,
                "per_page": resultados_por_pagina,
                "page": pagina,
                "sort": "merged",
                "order": "desc"
            }
            
            try:
                dados = self._fazer_requisicao(self.SEARCH_URL, params)
                
                # Primeira página: captura o total
                if total_resultados is None:
                    total_resultados = dados.get("total_count", 0)
                    if callback_progresso:
                        callback_progresso(pagina, total_resultados, len(prs))
                
                items = dados.get("items", [])
                
                if not items:
                    break
                
                # Processa cada PR
                for item in items:
                    pr = self._processar_pr(item, repositorio)
                    if pr:
                        prs.append(pr)
                
                # Atualiza progresso
                if callback_progresso:
                    callback_progresso(pagina, total_resultados, len(prs))
                
                # Verifica se há mais páginas
                if len(items) < resultados_por_pagina:
                    break
                
                pagina += 1
                
                # Rate limiting: aguarda um pouco entre requisições
                time.sleep(0.5)
                
            except requests.exceptions.RequestException as e:
                if callback_progresso:
                    callback_progresso(pagina, total_resultados or 0, len(prs), erro=str(e))
                break
        
        return prs, total_resultados
    
    def _processar_pr(self, item: Dict, repositorio: str) -> Optional[PullRequest]:
        """
        Processa um item de PR retornado pela API.
        
        Args:
            item: Dados do PR da API
            repositorio: Nome do repositório
            
        Returns:
            Objeto PullRequest ou None
        """
        try:
            numero = item.get("number")
            titulo = item.get("title", "")
            link = item.get("html_url", "")
            corpo = item.get("body", "") or ""
            
            # Tenta obter data de merge do próprio item primeiro (pode ter closed_at)
            data_merge = self._extrair_data_do_item(item)
            
            # Se não encontrou no item, tenta buscar detalhes do PR
            if data_merge == "N/A":
                data_merge = self._obter_data_merge(repositorio, numero)
            
            # Gera descrição breve (primeiras 2 linhas do corpo ou título)
            descricao = self._gerar_descricao_breve(titulo, corpo)
            
            return PullRequest(
                titulo=titulo,
                link=link,
                data_merge=data_merge,
                descricao=descricao,
                numero=numero
            )
        except Exception as e:
            print(f"Erro ao processar PR #{item.get('number')}: {e}")
            return None
    
    def _extrair_data_do_item(self, item: Dict) -> str:
        """
        Tenta extrair a data de merge diretamente do item retornado pela busca.
        
        Args:
            item: Dados do PR da API de busca
            
        Returns:
            Data de merge no formato YYYY-MM-DD ou "N/A"
        """
        # A API de busca pode retornar closed_at quando o PR foi mergeado
        closed_at = item.get("closed_at")
        if closed_at:
            try:
                data_merge = datetime.fromisoformat(
                    closed_at.replace("Z", "+00:00")
                )
                return data_merge.strftime("%Y-%m-%d")
            except (ValueError, AttributeError):
                pass
        
        return "N/A"
    
    def _obter_data_merge(self, repositorio: str, numero_pr: int) -> str:
        """
        Obtém a data de merge de um PR específico fazendo uma requisição adicional.
        
        Args:
            repositorio: Nome do repositório
            numero_pr: Número do PR
            
        Returns:
            Data de merge no formato YYYY-MM-DD ou "N/A"
        """
        try:
            url = f"{self.BASE_URL}/repos/{repositorio}/pulls/{numero_pr}"
            response = requests.get(url, headers=self.headers)
            
            # Trata 404 de forma silenciosa (PR pode ter sido deletado ou não estar acessível)
            if response.status_code == 404:
                return "N/A"
            
            # Verifica outros erros
            response.raise_for_status()
            dados = response.json()
            
            if dados.get("merged_at"):
                data_merge = datetime.fromisoformat(
                    dados["merged_at"].replace("Z", "+00:00")
                )
                return data_merge.strftime("%Y-%m-%d")
            
            return "N/A"
        except requests.exceptions.RequestException:
            # Trata todos os erros de requisição de forma silenciosa
            return "N/A"
        except Exception:
            # Outros erros também são tratados silenciosamente
            return "N/A"
    
    def _gerar_descricao_breve(self, titulo: str, corpo: str) -> str:
        """
        Gera uma descrição breve (resumo inteligente) a partir do título e corpo.
        
        Args:
            titulo: Título do PR
            corpo: Corpo/descrição do PR
            
        Returns:
            Descrição breve
        """
        import re
        
        if not corpo or not corpo.strip():
            return titulo
        
        # Tenta extrair a seção "Descrição do problema" primeiro
        descricao_match = re.search(
            r'##\s*Descrição\s+do\s+problema\s*\n\s*(.+?)(?=\n\s*##|\n\s*$|$)',
            corpo,
            re.IGNORECASE | re.DOTALL
        )
        
        if descricao_match:
            texto = descricao_match.group(1).strip()
        else:
            # Se não encontrou, tenta "Solução proposta"
            solucao_match = re.search(
                r'##\s*Solução\s+proposta\s*\n\s*(.+?)(?=\n\s*##|\n\s*$|$)',
                corpo,
                re.IGNORECASE | re.DOTALL
            )
            if solucao_match:
                texto = solucao_match.group(1).strip()
            else:
                # Se não encontrou seções, pega o primeiro parágrafo relevante
                # Remove markdown headers, listas e links
                texto = corpo
        
        # Remove elementos markdown desnecessários
        # Remove imagens
        texto = re.sub(r'!\[.*?\]\(.*?\)', '', texto)
        # Remove links (mantém apenas o texto)
        texto = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', texto)
        # Remove código inline
        texto = re.sub(r'`([^`]+)`', r'\1', texto)
        # Remove blocos de código
        texto = re.sub(r'```[\s\S]*?```', '', texto)
        # Remove headers markdown
        texto = re.sub(r'^#+\s+', '', texto, flags=re.MULTILINE)
        # Remove listas markdown
        texto = re.sub(r'^\s*[-*+]\s+', '', texto, flags=re.MULTILINE)
        # Remove separadores
        texto = re.sub(r'^---+$', '', texto, flags=re.MULTILINE)
        
        # Normaliza espaços e quebras de linha
        texto = re.sub(r'\s+', ' ', texto)
        texto = texto.strip()
        
        # Pega a primeira frase ou até 150 caracteres, respeitando palavras completas
        if len(texto) <= 150:
            descricao = texto
        else:
            # Tenta encontrar o final de uma frase próximo aos 150 caracteres
            corte = 150
            # Procura por ponto final, exclamação ou interrogação
            match_ponto = re.search(r'[.!?]\s+', texto[:200])
            if match_ponto:
                corte = match_ponto.end()
            else:
                # Se não encontrou, corta na última palavra completa antes de 150
                match_palavra = re.search(r'\s+', texto[120:150])
                if match_palavra:
                    corte = 120 + match_palavra.start()
            
            descricao = texto[:corte].strip()
            if descricao and not descricao.endswith(('.', '!', '?')):
                descricao += "..."
        
        # Se ainda não tem conteúdo útil, usa o título
        if not descricao or len(descricao.strip()) < 10:
            descricao = titulo
        
        return descricao
    
    def obter_branch_e_commits(self, repositorio: str, numero_pr: int) -> Tuple[str, List[str]]:
        """
        Obtém o nome da branch e as mensagens de commit de um PR específico.
        
        Args:
            repositorio: Nome do repositório
            numero_pr: Número do PR
            
        Returns:
            Tupla (nome_branch, lista_mensagens_commit)
        """
        try:
            # Obtém detalhes do PR
            url = f"{self.BASE_URL}/repos/{repositorio}/pulls/{numero_pr}"
            dados = self._fazer_requisicao(url)
            
            branch = dados.get("head", {}).get("ref", "N/A")
            
            # Obtém commits do PR
            commits_url = f"{self.BASE_URL}/repos/{repositorio}/pulls/{numero_pr}/commits"
            commits_data = self._fazer_requisicao(commits_url)
            
            mensagens = [
                commit.get("commit", {}).get("message", "").split("\n")[0]
                for commit in commits_data
            ]
            
            return branch, mensagens
        except Exception as e:
            print(f"Erro ao obter branch e commits do PR #{numero_pr}: {e}")
            return "N/A", []

