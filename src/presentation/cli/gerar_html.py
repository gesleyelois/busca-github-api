#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from html import escape

def parse_resultado_txt(file_path):
    """Parseia o arquivo resultado.txt e retorna os dados estruturados"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extrair informações do cabeçalho
    repo_match = re.search(r'Repositório: (.+)', content)
    periodo_match = re.search(r'Período: (.+)', content)
    branch_match = re.search(r'Branch base: (.+)', content)
    
    repo = repo_match.group(1) if repo_match else ''
    periodo = periodo_match.group(1) if periodo_match else ''
    branch = branch_match.group(1) if branch_match else ''
    
    # Extrair observações
    obs_section = re.search(r'Observações importantes antes das listas:(.*?)================================================================================', content, re.DOTALL)
    observacoes = []
    if obs_section:
        obs_text = obs_section.group(1)
        obs_items = re.findall(r'  • (.+?)(?=\n  • |\n\n|$)', obs_text, re.DOTALL)
        observacoes = [item.strip() for item in obs_items]
    
    # Extrair PRs por autor
    authors = {}
    
    # Dividir por seções de autores
    author_pattern = r'Buscando PRs de (.+?)\.\.\.\s*\n\s*\n(.+?)(?=\n\nBuscando PRs de |\Z)'
    matches = re.finditer(author_pattern, content, re.DOTALL)
    
    for match in matches:
        author = match.group(1).strip()
        section = match.group(2)
        
        # Verificar se não há PRs
        if 'Nenhum PR encontrado' in section:
            authors[author] = {
                'count': 0,
                'prs': []
            }
            continue
        
        # Extrair contagem de PRs
        count_match = re.search(r'PRs \((\d+) encontrados', section)
        pr_count = int(count_match.group(1)) if count_match else 0
        
        # Extrair PRs - padrão: "  • título — url — merged: data — descrição"
        pr_lines = re.findall(r'  • (.+?) — (https://[^\s]+) — merged: (\d{4}-\d{2}-\d{2}) — (.+?)(?=\n  • |\n\n|$)', section, re.DOTALL)
        
        prs = []
        for title, url, date, desc in pr_lines:
            # Limpar a descrição
            desc_clean = desc.strip()
            if len(desc_clean) > 200:
                desc_clean = desc_clean[:200] + '...'
            
            prs.append({
                'title': title.strip(),
                'url': url.strip(),
                'date': date.strip(),
                'description': desc_clean
            })
        
        authors[author] = {
            'count': pr_count,
            'prs': prs
        }
    
    return {
        'repo': repo,
        'periodo': periodo,
        'branch': branch,
        'observacoes': observacoes,
        'authors': authors
    }

def generate_html(data):
    """Gera o HTML a partir dos dados parseados"""
    
    html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Análise de Entregas do Time - Springnarus</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        }}

        .header-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 30px;
            text-align: left;
        }}

        .info-item {{
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }}

        .info-item strong {{
            display: block;
            margin-bottom: 5px;
            font-size: 0.9em;
            opacity: 0.9;
        }}

        .info-item span {{
            font-size: 1.1em;
        }}

        .observations {{
            background: #f8f9fa;
            padding: 30px 40px;
            border-bottom: 3px solid #667eea;
        }}

        .observations h2 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.5em;
        }}

        .observations ul {{
            list-style: none;
            padding-left: 0;
        }}

        .observations li {{
            padding: 10px 0;
            padding-left: 25px;
            position: relative;
        }}

        .observations li:before {{
            content: "•";
            color: #667eea;
            font-weight: bold;
            position: absolute;
            left: 0;
            font-size: 1.5em;
        }}

        .author-section {{
            padding: 40px;
            border-bottom: 2px solid #e9ecef;
        }}

        .author-section:last-child {{
            border-bottom: none;
        }}

        .author-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
        }}

        .author-name {{
            font-size: 2em;
            color: #667eea;
            font-weight: bold;
        }}

        .pr-count {{
            background: #667eea;
            color: white;
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 1em;
            font-weight: bold;
        }}

        .prs-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }}

        .pr-card {{
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            padding: 20px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}

        .pr-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
            border-color: #667eea;
        }}

        .pr-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 5px;
            height: 100%;
            background: #667eea;
            transform: scaleY(0);
            transition: transform 0.3s ease;
        }}

        .pr-card:hover::before {{
            transform: scaleY(1);
        }}

        .pr-title {{
            font-size: 1.1em;
            font-weight: bold;
            color: #333;
            margin-bottom: 12px;
            line-height: 1.4;
        }}

        .pr-link {{
            color: #667eea;
            text-decoration: none;
            font-size: 0.9em;
            display: inline-block;
            margin-bottom: 10px;
            word-break: break-all;
        }}

        .pr-link:hover {{
            text-decoration: underline;
        }}

        .pr-date {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85em;
            margin-bottom: 10px;
        }}

        .pr-description {{
            color: #666;
            font-size: 0.9em;
            line-height: 1.5;
            margin-top: 10px;
        }}

        .no-prs {{
            text-align: center;
            padding: 40px;
            color: #999;
            font-size: 1.2em;
        }}

        .stats {{
            display: flex;
            justify-content: space-around;
            padding: 30px;
            background: #f8f9fa;
            border-top: 3px solid #667eea;
        }}

        .stat-item {{
            text-align: center;
        }}

        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}

        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}

        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8em;
            }}

            .header-info {{
                grid-template-columns: 1fr;
            }}

            .prs-grid {{
                grid-template-columns: 1fr;
            }}

            .author-header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }}

            .stats {{
                flex-direction: column;
                gap: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Análise de Entregas do Time</h1>
            <div class="header-info">
                <div class="info-item">
                    <strong>Repositório</strong>
                    <span>{escape(data['repo'])}</span>
                </div>
                <div class="info-item">
                    <strong>Período</strong>
                    <span>{escape(data['periodo'])}</span>
                </div>
                <div class="info-item">
                    <strong>Branch Base</strong>
                    <span>{escape(data['branch'])}</span>
                </div>
            </div>
        </div>

        <div class="observations">
            <h2>📝 Observações Importantes</h2>
            <ul>
'''
    
    for obs in data['observacoes']:
        html += f'                <li>{escape(obs)}</li>\n'
    
    html += '''            </ul>
        </div>
'''
    
    # Calcular estatísticas
    total_prs = sum(author['count'] for author in data['authors'].values())
    total_authors = len(data['authors'])
    
    # Gerar seções de autores
    for author, author_data in sorted(data['authors'].items()):
        html += f'''        <div class="author-section">
            <div class="author-header">
                <div class="author-name">{escape(author)}</div>
                <div class="pr-count">{author_data['count']} PRs</div>
            </div>
'''
        
        if author_data['count'] == 0:
            html += '''            <div class="no-prs">
                Nenhum PR encontrado no período.
            </div>
'''
        else:
            html += '            <div class="prs-grid">\n'
            for pr in author_data['prs']:
                pr_num = pr['url'].split('/')[-1] if '/' in pr['url'] else ''
                html += f'''                <div class="pr-card">
                    <div class="pr-title">{escape(pr['title'])}</div>
                    <a href="{escape(pr['url'])}" class="pr-link" target="_blank">#{pr_num}</a>
                    <div class="pr-date">merged: {escape(pr['date'])}</div>
                    <div class="pr-description">{escape(pr['description'])}</div>
                </div>
'''
            html += '            </div>\n'
        
        html += '        </div>\n'
    
    html += f'''        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{total_authors}</div>
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

if __name__ == '__main__':
    import sys
    import os
    
    # Determina arquivo de entrada e saída
    arquivo_entrada = sys.argv[1] if len(sys.argv) > 1 else 'resultado.txt'
    arquivo_saida = sys.argv[2] if len(sys.argv) > 2 else 'resultado.html'
    
    # Se não especificado e existe resultado.txt, usa docs/index.html para GitHub Pages
    if arquivo_entrada == 'resultado.txt' and arquivo_saida == 'resultado.html':
        if os.path.exists('resultado.txt'):
            # Cria diretório docs se não existir
            os.makedirs('docs', exist_ok=True)
            arquivo_saida = 'docs/index.html'
    
    # Parsear o arquivo
    if not os.path.exists(arquivo_entrada):
        print(f"❌ Arquivo não encontrado: {arquivo_entrada}")
        sys.exit(1)
    
    data = parse_resultado_txt(arquivo_entrada)
    
    # Gerar HTML
    html = generate_html(data)
    
    # Salvar HTML
    # Garante que o diretório existe
    dir_saida = os.path.dirname(arquivo_saida)
    if dir_saida:
        os.makedirs(dir_saida, exist_ok=True)
    
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ HTML gerado com sucesso!")
    print(f"   - {len(data['authors'])} autores processados")
    print(f"   - {sum(a['count'] for a in data['authors'].values())} PRs no total")
    print(f"   - Arquivo salvo: {arquivo_saida}")

