#!/usr/bin/env python3
"""
Script para buscar Pull Requests mergeados na API do GitHub por autor.
Analisa entregas dos colaboradores do time em um intervalo de datas.
"""

import requests
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
import time
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()


@dataclass
class PullRequest:
    """Representa um Pull Request mergeado."""
    titulo: str
    link: str
    data_merge: str
    descricao: str
    numero: int
    branch: Optional[str] = None
    commits: Optional[List[str]] = None


class GitHubAPIClient:
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
        callback_progresso = None
    ) -> List[PullRequest]:
        """
        Busca PRs mergeados por autor em um intervalo de datas.
        
        Args:
            repositorio: Nome do repositório (formato: owner/repo)
            autor: Username do autor no GitHub
            data_inicio: Data de início (formato: YYYY-MM-DD)
            data_fim: Data de fim (formato: YYYY-MM-DD)
            branch_base: Branch base dos PRs (padrão: main)
            callback_progresso: Função callback para atualizar progresso (pagina, total, prs_encontrados)
            
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
        Gera uma descrição breve (1-2 linhas) a partir do título e corpo.
        
        Args:
            titulo: Título do PR
            corpo: Corpo/descrição do PR
            
        Returns:
            Descrição breve
        """
        # Remove markdown e quebras de linha excessivas
        corpo_limpo = corpo.replace("\r\n", " ").replace("\n", " ")
        
        # Pega as primeiras 200 caracteres
        if corpo_limpo:
            descricao = corpo_limpo[:200].strip()
            if len(corpo_limpo) > 200:
                descricao += "..."
        else:
            descricao = titulo
        
        return descricao
    
    def obter_branch_e_commits(self, repositorio: str, numero_pr: int) -> tuple:
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
    total_resultados: int,
    link_busca: str
) -> str:
    """
    Formata os resultados para exibição.
    
    Args:
        autor: Username do autor
        prs: Lista de PRs encontrados
        total_resultados: Total de resultados encontrados
        link_busca: Link de busca no GitHub
        
    Returns:
        String formatada com os resultados
    """
    resultado = f"\n{autor}\n"
    resultado += "=" * 80 + "\n\n"
    
    # Verifica se há resultados incompletos
    if total_resultados > len(prs):
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


def mostrar_progresso(autor: str, pagina: int, total: int, prs_encontrados: int, erro: str = None):
    """Mostra progresso da busca."""
    if erro:
        print(f"\r❌ Erro ao buscar PRs de {autor}: {erro}")
    elif total is not None:
        if total > 0:
            # Calcula estimativa de páginas
            paginas_estimadas = (total + 29) // 30
            print(f"\r🔍 {autor}: Página {pagina}/{paginas_estimadas} | {prs_encontrados} PRs encontrados", end="", flush=True)
        else:
            print(f"\r🔍 {autor}: Buscando... | {prs_encontrados} PRs encontrados", end="", flush=True)
    else:
        print(f"\r🔍 {autor}: Buscando... | {prs_encontrados} PRs encontrados", end="", flush=True)


def salvar_resultado(resultado: str, arquivo: str):
    """Salva o resultado em um arquivo."""
    try:
        with open(arquivo, "w", encoding="utf-8") as f:
            f.write(resultado)
        return True
    except Exception as e:
        print(f"\n❌ Erro ao salvar resultado: {e}")
        return False


def main():
    """Função principal do script."""
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(
        description="Busca Pull Requests mergeados na API do GitHub por autor"
    )
    parser.add_argument(
        "--repositorio",
        required=True,
        help="Repositório no formato owner/repo (ex: caelum/springnarus)"
    )
    parser.add_argument(
        "--autor",
        required=True,
        help="Username do autor no GitHub"
    )
    parser.add_argument(
        "--data-inicio",
        required=True,
        help="Data de início no formato YYYY-MM-DD"
    )
    parser.add_argument(
        "--data-fim",
        required=True,
        help="Data de fim no formato YYYY-MM-DD"
    )
    parser.add_argument(
        "--branch-base",
        default="main",
        help="Branch base dos PRs (padrão: main)"
    )
    parser.add_argument(
        "--token",
        help="Token de autenticação do GitHub (opcional, mas recomendado). "
             "Também pode ser definido via variável de ambiente GITHUB_TOKEN."
    )
    parser.add_argument(
        "--detalhes",
        nargs="+",
        type=int,
        help="Números dos PRs para obter detalhes (branch e commits)"
    )
    parser.add_argument(
        "--arquivo-saida",
        help="Arquivo para salvar o resultado (padrão: resultado_<autor>_<data>.txt)"
    )
    
    args = parser.parse_args()
    
    # Tenta obter token do argumento ou da variável de ambiente
    token = args.token or os.getenv("GITHUB_TOKEN")
    
    # Inicializa cliente
    client = GitHubAPIClient(token=token)
    
    # Define arquivo de saída
    if args.arquivo_saida:
        arquivo_saida = args.arquivo_saida
    else:
        data_hoje = datetime.now().strftime("%Y%m%d")
        arquivo_saida = f"resultado_{args.autor}_{data_hoje}.txt"
    
    # Busca PRs com callback de progresso
    print(f"🔍 Buscando PRs de {args.autor} em {args.repositorio}...")
    
    def callback(pagina, total, prs_encontrados, erro=None):
        mostrar_progresso(args.autor, pagina, total, prs_encontrados, erro)
    
    prs, total_resultados = client.buscar_prs_por_autor(
        repositorio=args.repositorio,
        autor=args.autor,
        data_inicio=args.data_inicio,
        data_fim=args.data_fim,
        branch_base=args.branch_base,
        callback_progresso=callback
    )
    
    print()  # Nova linha após progresso
    
    # Gera link de busca
    link_busca = gerar_link_busca_github(
        repositorio=args.repositorio,
        autor=args.autor,
        data_inicio=args.data_inicio,
        data_fim=args.data_fim,
        branch_base=args.branch_base
    )
    
    # Formata resultados
    resultado = formatar_resultados(args.autor, prs, total_resultados, link_busca)
    
    # Adiciona detalhes se solicitado
    detalhes_texto = ""
    if args.detalhes:
        detalhes_texto = "\n" + "=" * 80 + "\n"
        detalhes_texto += "DETALHES DE PRs ESPECÍFICOS\n"
        detalhes_texto += "=" * 80 + "\n\n"
        
        for numero_pr in args.detalhes:
            branch, commits = client.obter_branch_e_commits(
                args.repositorio, numero_pr
            )
            detalhes_texto += f"PR #{numero_pr}:\n"
            detalhes_texto += f"  Branch: {branch}\n"
            detalhes_texto += f"  Commits ({len(commits)}):\n"
            for commit in commits:
                detalhes_texto += f"    - {commit}\n"
            detalhes_texto += "\n"
    
    resultado_completo = resultado + detalhes_texto
    
    # Salva resultado em arquivo
    if salvar_resultado(resultado_completo, arquivo_saida):
        print(f"✅ Resultado salvo em: {arquivo_saida}")
        print(f"📊 Total de PRs encontrados: {len(prs)}")
        if total_resultados and total_resultados > len(prs):
            print(f"⚠️  Resultados incompletos: {len(prs)} de {total_resultados}")
    else:
        # Se não conseguiu salvar, mostra no terminal
        print(resultado_completo)


if __name__ == "__main__":
    main()

