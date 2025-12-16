#!/usr/bin/env python3
"""
Script para buscar Pull Requests mergeados na API do GitHub por autor.
Refatorado para usar Clean Architecture.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Adiciona o diretório raiz ao path para permitir imports relativos
raiz_projeto = os.path.dirname(__file__)
sys.path.insert(0, raiz_projeto)

from src.infrastructure.clients.github_api_client import GitHubAPIClient
from src.infrastructure.repositories.file_repository import FileRepository
from src.application.use_cases.buscar_prs_por_autor import (
    BuscarPRsPorAutorUseCase,
    formatar_resultados
)

# Carrega variáveis de ambiente
load_dotenv()


def mostrar_progresso(autor: str, pagina: int, total: int, prs_encontrados: int, erro: str = None):
    """Mostra progresso da busca."""
    if erro:
        print(f"\r❌ Erro ao buscar PRs de {autor}: {erro}")
    elif total is not None:
        if total > 0:
            paginas_estimadas = (total + 29) // 30
            print(f"\r🔍 {autor}: Página {pagina}/{paginas_estimadas} | {prs_encontrados} PRs encontrados", end="", flush=True)
        else:
            print(f"\r🔍 {autor}: Buscando... | {prs_encontrados} PRs encontrados", end="", flush=True)
    else:
        print(f"\r🔍 {autor}: Buscando... | {prs_encontrados} PRs encontrados", end="", flush=True)


def main():
    """Função principal do script."""
    import argparse
    
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
    
    # Inicializa dependências
    github_client = GitHubAPIClient(token=token)
    file_repository = FileRepository()
    use_case = BuscarPRsPorAutorUseCase(github_client)
    
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
    
    prs, total_resultados, link_busca = use_case.executar(
        repositorio=args.repositorio,
        autor=args.autor,
        data_inicio=args.data_inicio,
        data_fim=args.data_fim,
        branch_base=args.branch_base,
        callback_progresso=callback
    )
    
    print()  # Nova linha após progresso
    
    # Formata resultados
    resultado = formatar_resultados(args.autor, prs, total_resultados, link_busca)
    
    # Adiciona detalhes se solicitado
    detalhes_texto = ""
    if args.detalhes:
        detalhes_texto = "\n" + "=" * 80 + "\n"
        detalhes_texto += "DETALHES DE PRs ESPECÍFICOS\n"
        detalhes_texto += "=" * 80 + "\n\n"
        
        for numero_pr in args.detalhes:
            branch, commits = github_client.obter_branch_e_commits(
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
    if file_repository.salvar(resultado_completo, arquivo_saida):
        print(f"✅ Resultado salvo em: {arquivo_saida}")
        print(f"📊 Total de PRs encontrados: {len(prs)}")
        if total_resultados and total_resultados > len(prs):
            print(f"⚠️  Resultados incompletos: {len(prs)} de {total_resultados}")
    else:
        # Se não conseguiu salvar, mostra no terminal
        print(resultado_completo)


if __name__ == "__main__":
    main()

