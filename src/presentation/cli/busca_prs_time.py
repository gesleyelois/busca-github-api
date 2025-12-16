#!/usr/bin/env python3
"""
Script para buscar Pull Requests mergeados de múltiplos autores (time).
Analisa entregas de todos os colaboradores do time em um intervalo de datas.
"""

import sys
import os
from typing import List
from dotenv import load_dotenv
from busca_prs_github import (
    GitHubAPIClient,
    gerar_link_busca_github,
    formatar_resultados
)

# Carrega variáveis de ambiente do arquivo .env
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


def salvar_resultado(resultado: str, arquivo: str):
    """Salva o resultado em um arquivo."""
    try:
        with open(arquivo, "w", encoding="utf-8") as f:
            f.write(resultado)
        return True
    except Exception as e:
        print(f"\n❌ Erro ao salvar resultado: {e}")
        return False


def ler_autores_do_arquivo(caminho_arquivo: str = "autores.txt") -> List[str]:
    """
    Lê a lista de autores de um arquivo de texto.
    
    Args:
        caminho_arquivo: Caminho para o arquivo com a lista de autores
        
    Returns:
        Lista de autores (sem linhas vazias e comentários)
    """
    autores = []
    
    if not os.path.exists(caminho_arquivo):
        return autores
    
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                # Ignora linhas vazias e comentários
                if linha and not linha.startswith("#"):
                    autores.append(linha)
    except Exception as e:
        print(f"Erro ao ler arquivo de autores {caminho_arquivo}: {e}")
    
    return autores


def buscar_prs_time(
    repositorio: str,
    autores: List[str],
    data_inicio: str,
    data_fim: str,
    branch_base: str = "main",
    token: str = None,
    arquivo_saida: str = None
) -> None:
    """
    Busca PRs mergeados para múltiplos autores.
    
    Args:
        repositorio: Nome do repositório (formato: owner/repo)
        autores: Lista de usernames dos autores
        data_inicio: Data de início (formato: YYYY-MM-DD)
        data_fim: Data de fim (formato: YYYY-MM-DD)
        branch_base: Branch base dos PRs (padrão: main)
        token: Token de autenticação do GitHub (opcional)
        arquivo_saida: Arquivo para salvar o resultado
    """
    client = GitHubAPIClient(token=token)
    
    print("=" * 80)
    print("ANÁLISE DE ENTREGAS DO TIME")
    print("=" * 80)
    print(f"Repositório: {repositorio}")
    print(f"Período: {data_inicio} a {data_fim}")
    print(f"Branch base: {branch_base}")
    print(f"Autores: {len(autores)} autor(es)")
    print("=" * 80)
    print()
    
    # Prepara resultado completo (não imprime no terminal)
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
            mostrar_progresso_autor(autor, indice, total_autores, pagina, total, prs_encontrados, erro)
        
        prs, total_resultados = client.buscar_prs_por_autor(
            repositorio=repositorio,
            autor=autor,
            data_inicio=data_inicio,
            data_fim=data_fim,
            branch_base=branch_base,
            callback_progresso=callback
        )
        
        print()  # Nova linha após progresso
        
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
    
    # Salva resultado em arquivo
    if arquivo_saida:
        if salvar_resultado(resultado_completo, arquivo_saida):
            print(f"✅ Resultado salvo em: {arquivo_saida}")
            print(f"📊 Total de PRs encontrados: {total_prs_encontrados}")
        else:
            print(resultado_completo)
    else:
        from datetime import datetime
        data_hoje = datetime.now().strftime("%Y%m%d")
        arquivo_padrao = f"resultado_time_{data_hoje}.txt"
        if salvar_resultado(resultado_completo, arquivo_padrao):
            print(f"✅ Resultado salvo em: {arquivo_padrao}")
            print(f"📊 Total de PRs encontrados: {total_prs_encontrados}")
        else:
            print(resultado_completo)


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
        default="autores.txt",
        help="Caminho para arquivo com lista de autores (um por linha). "
             "Padrão: autores.txt. Linhas começando com # são ignoradas."
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
    
    # Determina a lista de autores
    if args.autores:
        autores = args.autores
    else:
        # Tenta ler do arquivo
        autores = ler_autores_do_arquivo(args.arquivo_autores)
        if not autores:
            parser.error(
                "É necessário fornecer --autores ou ter um arquivo de autores válido. "
                f"Tentou ler de: {args.arquivo_autores}"
            )
    
    # Tenta obter token do argumento, variável de ambiente ou arquivo .env
    token = args.token or os.getenv("GITHUB_TOKEN")
    
    buscar_prs_time(
        repositorio=args.repositorio,
        autores=autores,
        data_inicio=args.data_inicio,
        data_fim=args.data_fim,
        branch_base=args.branch_base,
        token=token,
        arquivo_saida=args.arquivo_saida
    )


if __name__ == "__main__":
    main()

