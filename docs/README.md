# Pasta docs/

Esta pasta contém os arquivos HTML gerados para publicação no GitHub Pages.

O arquivo `index.html` é gerado automaticamente pelo workflow do GitHub Actions quando você executa a busca de PRs.

Para gerar manualmente:

```bash
python busca_prs_time.py \
  --repositorio owner/repo \
  --data-inicio 2025-01-01 \
  --data-fim 2025-12-31 \
  --arquivo-saida resultado.txt

python gerar_html.py resultado.txt docs/index.html
```

