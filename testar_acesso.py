#!/usr/bin/env python3
"""
Script para testar se o token do GitHub tem acesso a um repositório (público ou privado).
"""

import requests
import os
import sys
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()


def testar_acesso_repositorio(repositorio: str, token: str = None) -> bool:
    """
    Testa se o token tem acesso ao repositório.
    
    Args:
        repositorio: Nome do repositório no formato owner/repo
        token: Token de autenticação (opcional, tenta ler do .env)
        
    Returns:
        True se tem acesso, False caso contrário
    """
    if not token:
        token = os.getenv("GITHUB_TOKEN")
    
    if not token:
        print("❌ Erro: Token não encontrado!")
        print("   Configure o token no arquivo .env ou passe como argumento.")
        return False
    
    url = f"https://api.github.com/repos/{repositorio}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}"
    }
    
    print(f"🔍 Testando acesso ao repositório: {repositorio}")
    print(f"   URL: {url}")
    print()
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            dados = response.json()
            print("✅ Acesso confirmado!")
            print()
            print(f"   Nome: {dados.get('full_name')}")
            print(f"   Privado: {'Sim' if dados.get('private') else 'Não'}")
            print(f"   Descrição: {dados.get('description') or 'N/A'}")
            print(f"   Estrelas: {dados.get('stargazers_count', 0)}")
            print()
            
            if dados.get('private'):
                print("   ⚠️  Este é um repositório PRIVADO.")
                print("   ✅ Seu token tem acesso a repositórios privados!")
            else:
                print("   ℹ️  Este é um repositório PÚBLICO.")
            
            return True
            
        elif response.status_code == 404:
            print("❌ Repositório não encontrado (404)")
            print()
            print("   Possíveis causas:")
            print("   • O repositório não existe")
            print("   • O nome do repositório está incorreto")
            print("   • Você não tem acesso ao repositório (se for privado)")
            print("   • O token não tem permissão 'repo' (necessário para privados)")
            return False
            
        elif response.status_code == 403:
            print("❌ Acesso negado (403)")
            print()
            print("   Possíveis causas:")
            print("   • O token não tem permissão 'repo' (necessário para privados)")
            print("   • Rate limit excedido")
            print("   • A organização bloqueia tokens pessoais")
            
            # Verifica rate limit
            rate_limit_remaining = response.headers.get("X-RateLimit-Remaining", "0")
            if rate_limit_remaining == "0":
                reset_time = response.headers.get("X-RateLimit-Reset")
                if reset_time:
                    from datetime import datetime
                    reset_datetime = datetime.fromtimestamp(int(reset_time))
                    print(f"   • Rate limit resetará em: {reset_datetime}")
            
            return False
            
        else:
            print(f"❌ Erro inesperado: {response.status_code}")
            print(f"   Resposta: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return False


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Testa se o token do GitHub tem acesso a um repositório"
    )
    parser.add_argument(
        "repositorio",
        help="Repositório no formato owner/repo (ex: caelum/springnarus)"
    )
    parser.add_argument(
        "--token",
        help="Token de autenticação (opcional, tenta ler do .env)"
    )
    
    args = parser.parse_args()
    
    sucesso = testar_acesso_repositorio(args.repositorio, args.token)
    
    if sucesso:
        print("✅ Teste concluído com sucesso!")
        sys.exit(0)
    else:
        print()
        print("💡 Dicas:")
        print("   • Verifique se o token tem a permissão 'repo' para repositórios privados")
        print("   • Veja o guia: GUIA_TOKEN_GITHUB.md")
        sys.exit(1)


if __name__ == "__main__":
    main()

