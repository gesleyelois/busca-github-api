#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para gerar HTML a partir de resultado.txt.
Refatorado para usar Clean Architecture.
"""

import sys
import os

# Adiciona o diretório raiz ao path para permitir imports relativos
raiz_projeto = os.path.dirname(__file__)
sys.path.insert(0, raiz_projeto)

from src.infrastructure.repositories.file_repository import FileRepository
from src.infrastructure.repositories.html_generator import HTMLGenerator
from src.application.use_cases.gerar_html import GerarHTMLUseCase


def main():
    """Função principal."""
    # Determina arquivo de entrada e saída
    arquivo_entrada = sys.argv[1] if len(sys.argv) > 1 else 'resultado.txt'
    arquivo_saida = sys.argv[2] if len(sys.argv) > 2 else 'resultado.html'
    
    # Se não especificado e existe resultado.txt, usa docs/index.html para GitHub Pages
    if arquivo_entrada == 'resultado.txt' and arquivo_saida == 'resultado.html':
        if os.path.exists('resultado.txt'):
            # Cria diretório docs se não existir
            os.makedirs('docs', exist_ok=True)
            arquivo_saida = 'docs/index.html'
    
    # Inicializa dependências
    file_repository = FileRepository()
    html_generator = HTMLGenerator()
    use_case = GerarHTMLUseCase(html_generator, file_repository)
    
    # Executa o caso de uso
    use_case.executar(arquivo_entrada, arquivo_saida)


if __name__ == '__main__':
    main()

