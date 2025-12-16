#!/usr/bin/env python3
"""
Script para buscar Pull Requests mergeados de múltiplos autores (time).
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
from src.application.use_cases.buscar_prs_time import BuscarPRsTimeUseCase

# Carrega variáveis de ambiente
load_dotenv()


def mostrar_progresso_autor(autor: str, indice: int, total_autores: int, pagina: int, total: int, prs_encontrados: int, erro: str = None):
    """Mostra progresso da busca para um autor específico."""
    if erro:
        print(f"\r❌ [{indice}/{total_autores}] {autor}: Erro - {erro}")
    elif total is not None:
        if total > 0:
            paginas_estimadas = (total + 29) // 30
            print(f"\r🔍 [{indice}/{total_autores}] {autor}: Página {pagina}/{paginas_estimadas} | {prs_encontrados} PRs", end="", flush=True)
        else:
            print(f"\r🔍 [{indice}/{total_autores}] {autor}: Buscando... | {prs_encontrados} PRs", end="", flush=True)
    else:
        print(f"\r🔍 [{indice}/{total_autores}] {autor}: Buscando... | {prs_encontrados} PRs", end="", flush=True)


def main():
    """Função principal do script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Busca Pull Requests mergeados de múltiplos autores (time)"
    )
    parser.add_argument(
        "--repositorio",
        required=True,
        help="Repositório no formato owner/repo (ex: caelum/springnarus)"
    )
    parser.add_argument(
        "--autores",
        nargs="+",
        help="Usernames dos autores no GitHub (ex: --autores user1 user2 user3). "
             "Alternativa: use --arquivo-autores para ler de um arquivo."
    )
    parser.add_argument(
        "--arquivo-autores",
        default="config/autores.txt",
        help="Caminho para arquivo com lista de autores (um por linha). "
             "Padrão: config/autores.txt. Linhas começando com # são ignoradas."
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
             "Também pode ser definido via variável de ambiente GITHUB_TOKEN ou arquivo .env."
    )
    parser.add_argument(
        "--arquivo-saida",
        help="Arquivo para salvar o resultado (padrão: resultado_time_<data>.txt)"
    )
    
    args = parser.parse_args()
    
    # Inicializa dependências
    token = args.token or os.getenv("GITHUB_TOKEN")
    github_client = GitHubAPIClient(token=token)
    file_repository = FileRepository()
    use_case = BuscarPRsTimeUseCase(github_client, file_repository)
    
    # Determina a lista de autores
    if args.autores:
        autores = args.autores
    else:
        # Tenta ler do arquivo
        autores = file_repository.ler_autores(args.arquivo_autores)
        if not autores:
            parser.error(
                "É necessário fornecer --autores ou ter um arquivo de autores válido. "
                f"Tentou ler de: {args.arquivo_autores}"
            )
    
    print("=" * 80)
    print("ANÁLISE DE ENTREGAS DO TIME")
    print("=" * 80)
    print(f"Repositório: {args.repositorio}")
    print(f"Período: {args.data_inicio} a {args.data_fim}")
    print(f"Branch base: {args.branch_base}")
    print(f"Autores: {len(autores)} autor(es)")
    print("=" * 80)
    print()
    
    print(
        "  • Usei a API do GitHub para buscar os PRs mergeados por autor nesse intervalo. "
        "Alguns resultados da API estavam incompletos por limite de paginação "
        "(o GitHub Search retorna no máximo 30 resultados por página). "
        "Onde aplicou, marquei que os resultados são incompletos e deixei o link de busca "
        "no GitHub para ver o conjunto completo.\n"
    )
    print(
        "  • As respostas de busca trazem título do PR, link e data de merge e muitas vezes "
        "o corpo/descrição do PR. Porém a listagem de busca não inclui sempre o nome da branch "
        "nem todas as mensagens de commit. Posso buscar branch + commits para PRs específicos "
        "caso queira — solicite quais PRs quer em detalhe.\n"
    )
    print(
        "  • Vou fornecer uma breve descrição (1–2 linhas) por PR usando o título e a descrição "
        "encontrada no PR. Se quiser que eu extraia exatamente o nome da branch e todas as "
        "mensagens de commit, peço que diga quais PRs priorizar (faço isso PR-a-PR).\n"
    )
    print("=" * 80)
    print()
    
    # Executa o caso de uso
    resultado = use_case.executar(
        repositorio=args.repositorio,
        autores=autores,
        data_inicio=args.data_inicio,
        data_fim=args.data_fim,
        branch_base=args.branch_base,
        arquivo_saida=args.arquivo_saida,
        callback_progresso=mostrar_progresso_autor
    )
    
    if args.arquivo_saida:
        print(f"✅ Resultado salvo em: {args.arquivo_saida}")
        total_prs = resultado.count("  •")
        print(f"📊 Total de PRs encontrados: {total_prs}")
    else:
        data_hoje = datetime.now().strftime("%Y%m%d")
        arquivo_padrao = f"resultado_time_{data_hoje}.txt"
        if file_repository.salvar(resultado, arquivo_padrao):
            print(f"✅ Resultado salvo em: {arquivo_padrao}")
            total_prs = resultado.count("  •")
            print(f"📊 Total de PRs encontrados: {total_prs}")
        else:
            print(resultado)


if __name__ == "__main__":
    main()

