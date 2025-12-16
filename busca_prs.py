#!/usr/bin/env python3
"""
Script simples para buscar PRs do GitHub e gerar relatórios em TXT e HTML.
"""

import os
import csv
import time
import requests
from datetime import datetime
from typing import List, Dict, Optional
from html import escape
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configurações do .env
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPOSITORIO = os.getenv("REPOSITORIO", "caelum/springnarus")
BRANCH_BASE = os.getenv("BRANCH_BASE", "main")

# URLs da API
BASE_URL = "https://api.github.com"
SEARCH_URL = f"{BASE_URL}/search/issues"


def buscar_prs_por_autor(
    autor: str,
    data_inicio: str,
    data_fim: str,
    repositorio: str = REPOSITORIO,
    branch_base: str = BRANCH_BASE,
    token: str = GITHUB_TOKEN
) -> List[Dict]:
    """
    Busca PRs mergeados de um autor no período especificado.
    
    Returns:
        Lista de PRs encontrados
    """
    prs = []
    pagina = 1
    resultados_por_pagina = 30
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    if token:
        headers["Authorization"] = f"token {token}"
    
    while True:
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
            response = requests.get(SEARCH_URL, headers=headers, params=params)
            
            if response.status_code == 403:
                rate_limit_remaining = response.headers.get("X-RateLimit-Remaining", "0")
                if rate_limit_remaining == "0":
                    reset_time = response.headers.get("X-RateLimit-Reset")
                    if reset_time:
                        reset_datetime = datetime.fromtimestamp(int(reset_time))
                        print(f"⚠️  Rate limit excedido. Tente novamente após {reset_datetime}")
                    break
            
            response.raise_for_status()
            dados = response.json()
            
            items = dados.get("items", [])
            if not items:
                break
            
            for item in items:
                pr = {
                    "titulo": item.get("title", ""),
                    "url": item.get("html_url", ""),
                    "data_merge": item.get("pull_request", {}).get("merged_at", "")
                }
                
                # Extrai data de merge
                if pr["data_merge"]:
                    pr["data_merge"] = pr["data_merge"][:10]  # YYYY-MM-DD
                
                prs.append(pr)
            
            if len(items) < resultados_por_pagina:
                break
            
            pagina += 1
            time.sleep(0.5)  # Rate limiting
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao buscar PRs de {autor}: {e}")
            break
    
    return prs


def ler_autores_csv(arquivo: str = "autores.csv") -> List[Dict]:
    """
    Lê autores e configurações de um arquivo CSV.
    
    Formato esperado:
    autor,data_inicio,data_fim
    felipesalmazo,2025-01-01,2025-12-31
    """
    autores = []
    
    if not os.path.exists(arquivo):
        print(f"❌ Erro: Arquivo {arquivo} não encontrado.")
        print(f"   Crie um arquivo CSV com as colunas: autor,data_inicio,data_fim")
        return []
    
    with open(arquivo, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            autor = row.get("autor", "").strip()
            data_inicio = row.get("data_inicio", "").strip()
            data_fim = row.get("data_fim", "").strip()
            
            if not autor:
                continue
            
            if not data_inicio or not data_fim:
                print(f"⚠️  Aviso: Autor {autor} sem data_inicio ou data_fim. Pulando...")
                continue
            
            autores.append({
                "autor": autor,
                "data_inicio": data_inicio,
                "data_fim": data_fim
            })
    
    return autores


def gerar_txt(autores_prs: Dict[str, List[Dict]], repositorio: str, periodo: str, branch: str) -> str:
    """Gera relatório em formato TXT."""
    resultado = []
    resultado.append("=" * 80)
    resultado.append("ANÁLISE DE ENTREGAS DO TIME")
    resultado.append("=" * 80)
    resultado.append(f"\nRepositório: {repositorio}")
    resultado.append(f"Período: {periodo}")
    resultado.append(f"Branch Base: {branch}\n")
    resultado.append("=" * 80)
    resultado.append("")
    
    total_prs = 0
    
    for autor, prs in sorted(autores_prs.items()):
        resultado.append(f"\n{autor}")
        resultado.append("-" * 80)
        
        if not prs:
            resultado.append("Nenhum PR encontrado no período.")
        else:
            resultado.append(f"PRs ({len(prs)} encontrados):")
            for pr in prs:
                resultado.append(f"  • {pr['titulo']} — {pr['url']} — merged: {pr['data_merge']}")
            total_prs += len(prs)
        
        resultado.append("")
    
    resultado.append("=" * 80)
    resultado.append(f"Total: {total_prs} PRs de {len(autores_prs)} autores")
    resultado.append("=" * 80)
    
    return "\n".join(resultado)


def gerar_html(autores_prs: Dict[str, List[Dict]], repositorio: str, periodo: str, branch: str) -> str:
    """Gera relatório em formato HTML."""
    total_prs = sum(len(prs) for prs in autores_prs.values())
    total_autores = len(autores_prs)
    
    html = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Entregas do Time</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        }

        .header-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 30px;
            text-align: left;
        }

        .info-item {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }

        .info-item strong {
            display: block;
            margin-bottom: 5px;
            font-size: 0.9em;
            opacity: 0.9;
        }

        .info-item span {
            font-size: 1.1em;
        }

        .author-section {
            padding: 40px;
            border-bottom: 2px solid #e9ecef;
        }

        .author-section:last-child {
            border-bottom: none;
        }

        .author-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
        }

        .author-name {
            font-size: 2em;
            color: #667eea;
            font-weight: bold;
        }

        .pr-count {
            background: #667eea;
            color: white;
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 1em;
            font-weight: bold;
        }

        .prs-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }

        .pr-card {
            background: #ffffff;
            border: 2px solid #e9ecef;
            border-radius: 16px;
            padding: 24px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            cursor: pointer;
            text-decoration: none;
            color: inherit;
            display: block;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }

        .pr-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 40px rgba(102, 126, 234, 0.25);
            border-color: #667eea;
            background: #f8f9ff;
        }

        .pr-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 6px;
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            transform: scaleY(0);
            transition: transform 0.3s ease;
        }

        .pr-card:hover::before {
            transform: scaleY(1);
        }

        .pr-title {
            font-size: 1.15em;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 16px;
            line-height: 1.5;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .pr-card:hover .pr-title {
            color: #667eea;
        }

        .pr-meta {
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 16px;
        }

        .pr-link {
            color: #667eea;
            text-decoration: none;
            font-size: 0.9em;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            pointer-events: none;
        }

        .pr-card:hover .pr-link {
            color: #764ba2;
        }

        .pr-date {
            display: inline-flex;
            align-items: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
            box-shadow: 0 2px 6px rgba(102, 126, 234, 0.3);
        }

        .pr-icon {
            display: inline-block;
            margin-right: 4px;
        }

        .pr-description {
            color: #666;
            font-size: 0.9em;
            line-height: 1.5;
            margin-top: 10px;
        }

        .no-prs {
            text-align: center;
            padding: 40px;
            color: #999;
            font-size: 1.2em;
        }

        .stats {
            display: flex;
            justify-content: space-around;
            padding: 30px;
            background: #f8f9fa;
            border-top: 3px solid #667eea;
        }

        .stat-item {
            text-align: center;
        }

        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }

        .stat-label {
            color: #666;
            margin-top: 5px;
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8em;
            }

            .header-info {
                grid-template-columns: 1fr;
            }

            .prs-grid {
                grid-template-columns: 1fr;
            }

            .author-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }

            .stats {
                flex-direction: column;
                gap: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Entregas do Time</h1>
            <div class="header-info">
                <div class="info-item">
                    <strong>Repositório</strong>
                    <span>''' + escape(repositorio) + '''</span>
                </div>
                <div class="info-item">
                    <strong>Período</strong>
                    <span>''' + escape(periodo) + '''</span>
                </div>
                <div class="info-item">
                    <strong>Branch Base</strong>
                    <span>''' + escape(branch) + '''</span>
                </div>
            </div>
        </div>'''
    
    for autor, prs in sorted(autores_prs.items()):
        html += f'''
        <div class="author-section">
            <div class="author-header">
                <div class="author-name">{escape(autor)}</div>
                <div class="pr-count">{len(prs)} PRs</div>
            </div>'''
        
        if not prs:
            html += '''
            <div class="no-prs">
                Nenhum PR encontrado no período.
            </div>'''
        else:
            html += '''
            <div class="prs-grid">'''
            
            for pr in prs:
                pr_num = pr["url"].split("/")[-1] if "/" in pr["url"] else ""
                
                html += f'''
                <a href="{escape(pr["url"])}" class="pr-card" target="_blank" rel="noopener noreferrer">
                    <div class="pr-title">{escape(pr["titulo"])}</div>
                    <div class="pr-meta">
                        <span class="pr-link">
                            <span class="pr-icon">🔗</span>
                            #{pr_num}
                        </span>
                        <span class="pr-date">
                            <span class="pr-icon">📅</span>
                            merged: {escape(pr["data_merge"])}
                        </span>
                    </div>
                </a>'''
            
            html += '''
            </div>'''
        
        html += '''
        </div>'''
    
    html += f'''
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{total_autores}</div>
                <div class="stat-label">Autores</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{total_prs}</div>
                <div class="stat-label">Total de PRs</div>
            </div>
        </div>
    </div>
</body>
</html>'''
    
    return html


def main():
    """Função principal."""
    if not GITHUB_TOKEN:
        print("❌ Erro: GITHUB_TOKEN não encontrado no .env")
        print("   Crie um arquivo .env com: GITHUB_TOKEN=seu_token_aqui")
        return
    
    # Lê autores do CSV
    autores_config = ler_autores_csv()
    
    if not autores_config:
        print("❌ Erro: Nenhum autor encontrado.")
        print("   Crie um arquivo autores.csv com as colunas: autor,data_inicio,data_fim")
        return
    
    print(f"🔍 Buscando PRs para {len(autores_config)} autor(es)...")
    print(f"   Repositório: {REPOSITORIO}")
    print(f"   Branch: {BRANCH_BASE}\n")
    
    autores_prs = {}
    periodo_inicio = None
    periodo_fim = None
    
    for config in autores_config:
        autor = config["autor"]
        data_inicio = config["data_inicio"]
        data_fim = config["data_fim"]
        
        if periodo_inicio is None:
            periodo_inicio = data_inicio
            periodo_fim = data_fim
        
        print(f"📋 Buscando PRs de {autor}...")
        prs = buscar_prs_por_autor(autor, data_inicio, data_fim)
        
        autores_prs[autor] = prs
        print(f"   ✅ {len(prs)} PRs encontrados\n")
    
    periodo = f"{periodo_inicio} a {periodo_fim}"
    
    # Gera TXT
    print("📝 Gerando resultado.txt...")
    resultado_txt = gerar_txt(autores_prs, REPOSITORIO, periodo, BRANCH_BASE)
    with open("resultado.txt", "w", encoding="utf-8") as f:
        f.write(resultado_txt)
    print("   ✅ resultado.txt gerado\n")
    
    # Gera HTML
    print("🌐 Gerando docs/index.html...")
    os.makedirs("docs", exist_ok=True)
    resultado_html = gerar_html(autores_prs, REPOSITORIO, periodo, BRANCH_BASE)
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(resultado_html)
    print("   ✅ docs/index.html gerado\n")
    
    total_prs = sum(len(prs) for prs in autores_prs.values())
    print("=" * 80)
    print(f"✅ Concluído! {total_prs} PRs de {len(autores_prs)} autores")
    print("=" * 80)


if __name__ == "__main__":
    main()

