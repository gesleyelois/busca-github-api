# Busca de PRs no GitHub

Script Python para buscar Pull Requests mergeados e gerar relatórios em TXT e HTML.

## Instalação

```bash
pip install -r requirements.txt
```

## Configuração

### 1. Configurar Token do GitHub

1. Copie o arquivo de exemplo:
```bash
cp env.example .env
```

2. Edite o arquivo `.env` e adicione seu token:
```bash
GITHUB_TOKEN=seu_token_aqui
REPOSITORIO=caelum/springnarus
BRANCH_BASE=main
```

**📖 Como obter um token:** Acesse https://github.com/settings/tokens e crie um token com permissão `public_repo` (ou `repo` para repositórios privados).

### 2. Configurar Autores

Crie um arquivo `autores.csv` com os autores e períodos de busca:

```csv
autor,data_inicio,data_fim
felipesalmazo,2025-01-01,2025-12-31
VictorAluraDev,2025-01-01,2025-12-31
eduardofettermann,2025-01-01,2025-12-31
```

Cada autor pode ter seu próprio período de busca. As datas são obrigatórias para cada autor.

## Uso

Execute o script:

```bash
python busca_prs.py
```

O script irá:
1. Buscar PRs de cada autor no período especificado
2. Gerar `resultado.txt` com o relatório em texto
3. Gerar `docs/index.html` com o relatório em HTML

## Estrutura de Arquivos

```
busca-github-api/
├── busca_prs.py          # Script principal
├── .env                   # Configurações (não commitado)
├── env.example            # Exemplo de configuração
├── autores.csv            # Lista de autores e datas (obrigatório)
├── resultado.txt          # Relatório em texto (gerado)
├── docs/
│   └── index.html         # Relatório em HTML (gerado)
└── requirements.txt       # Dependências Python
```

## GitHub Pages

Para publicar o HTML no GitHub Pages:

1. Faça commit do arquivo `docs/index.html`:
```bash
git add docs/index.html
git commit -m "Atualiza relatório de PRs"
git push
```

2. Configure o GitHub Pages no repositório:
   - Vá em Settings > Pages
   - Source: Deploy from a branch
   - Branch: `main` / `docs`

3. Acesse: `https://seu-usuario.github.io/busca-github-api/`

## Exemplo de Saída

### resultado.txt
```
================================================================================
ANÁLISE DE ENTREGAS DO TIME
================================================================================

Repositório: caelum/springnarus
Período: 2025-01-01 a 2025-12-31
Branch Base: main

================================================================================

felipesalmazo
--------------------------------------------------------------------------------
PRs (48 encontrados):
  • [Conversão] Adiciona merchant id para subscriptions — https://github.com/... — merged: 2025-09-12 — ...
  • [Conversão] Altera data de criacão acquirement na renovacao da recorrência — https://github.com/... — merged: 2025-07-30 — ...
  ...
```

### docs/index.html
Página HTML visual com cards para cada PR, estatísticas e design responsivo.

## Requisitos

- Python 3.7+
- Token do GitHub com permissão `public_repo` (ou `repo` para privados)

## Dependências

- `requests` - Para requisições HTTP à API do GitHub
- `python-dotenv` - Para carregar variáveis de ambiente do `.env`

## Limitações

- A API do GitHub Search retorna no máximo 30 resultados por página
- Rate limiting: 30 requisições por minuto (com token autenticado)
- Descrições de PR são limitadas a ~150 caracteres

## Troubleshooting

### Erro: "GITHUB_TOKEN não encontrado"
- Verifique se o arquivo `.env` existe e contém `GITHUB_TOKEN=seu_token`

### Erro: "Rate limit excedido"
- Aguarde alguns minutos e tente novamente
- Use um token autenticado para aumentar o limite

### Nenhum PR encontrado
- Verifique se as datas estão corretas
- Confirme que os autores estão corretos
- Verifique se o repositório e branch estão corretos
