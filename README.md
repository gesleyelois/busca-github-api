# Busca de PRs no GitHub

Script Python para buscar e analisar Pull Requests mergeados na API do GitHub por autor.

## Instalação

```bash
pip install -r requirements.txt
```

## Configuração Rápida

Execute o script de setup:

```bash
./setup.sh
```

Ou configure manualmente:

### 1. Configurar Token do GitHub (Arquivo .env)

1. Copie o arquivo de exemplo:
```bash
cp env.example .env
```

2. Edite o arquivo `.env` e adicione seu token:
```bash
GITHUB_TOKEN=ghp_seu_token_aqui
```

**📖 Não tem token?** Veja o guia completo: [GUIA_TOKEN_GITHUB.md](GUIA_TOKEN_GITHUB.md)

**🔒 Repositórios Privados:** Para acessar repositórios privados, o token precisa ter a permissão `repo` (não apenas `public_repo`). Veja a seção "Acessando Repositórios Privados" no guia.

### 2. Configurar Lista de Autores (Opcional)

Edite o arquivo `autores.txt` e adicione um autor por linha:

```
felipesalmazo
user2
user3
```

Linhas começando com `#` são ignoradas (comentários).

## Uso

### Busca básica

```bash
python busca_prs_github.py \
  --repositorio caelum/springnarus \
  --autor felipesalmazo \
  --data-inicio 2025-01-01 \
  --data-fim 2025-12-12
```

### Com token de autenticação (recomendado)

Para evitar limites de rate limiting, é recomendado usar um token de autenticação do GitHub.

**📖 Veja o guia completo:** [GUIA_TOKEN_GITHUB.md](GUIA_TOKEN_GITHUB.md)

#### Opção 1: Arquivo .env (Recomendado - Mais Seguro)

Configure o token no arquivo `.env` (veja seção de Configuração acima) e use normalmente:

```bash
python busca_prs_github.py \
  --repositorio caelum/springnarus \
  --autor felipesalmazo \
  --data-inicio 2025-01-01 \
  --data-fim 2025-12-12
```

#### Opção 2: Variável de ambiente

```bash
# Configure a variável de ambiente
export GITHUB_TOKEN="ghp_seu_token_aqui"

# Use o script normalmente (o token será lido automaticamente)
python busca_prs_github.py \
  --repositorio caelum/springnarus \
  --autor felipesalmazo \
  --data-inicio 2025-01-01 \
  --data-fim 2025-12-12
```

#### Opção 3: Passar como argumento

```bash
python busca_prs_github.py \
  --repositorio caelum/springnarus \
  --autor felipesalmazo \
  --data-inicio 2025-01-01 \
  --data-fim 2025-12-12 \
  --token seu_token_aqui
```

### Buscar detalhes de PRs específicos

Para obter o nome da branch e todas as mensagens de commit de PRs específicos:

```bash
python busca_prs_github.py \
  --repositorio caelum/springnarus \
  --autor felipesalmazo \
  --data-inicio 2025-01-01 \
  --data-fim 2025-12-12 \
  --detalhes 10035 10036 10037
```

### Especificar branch base

Por padrão, o script busca PRs mergeados na branch `main`. Para usar outra branch:

```bash
python busca_prs_github.py \
  --repositorio caelum/springnarus \
  --autor felipesalmazo \
  --data-inicio 2025-01-01 \
  --data-fim 2025-12-12 \
  --branch-base develop
```

## Scripts Disponíveis

### 1. `busca_prs_github.py` - Busca por autor único

Busca PRs de um único autor.

### 0. `testar_acesso.py` - Testar acesso a repositório

Testa se seu token tem acesso a um repositório (útil para verificar acesso a repositórios privados):

```bash
python testar_acesso.py owner/repositorio
```

Exemplo:
```bash
python testar_acesso.py caelum/springnarus
```

### 2. `busca_prs_time.py` - Busca por múltiplos autores (time)

Busca PRs de múltiplos autores de uma vez, útil para analisar todo o time.

#### Usando arquivo de autores (Recomendado)

Se você configurou o arquivo `autores.txt`:

```bash
python busca_prs_time.py \
  --repositorio caelum/springnarus \
  --data-inicio 2025-01-01 \
  --data-fim 2025-12-12
```

O script lerá automaticamente os autores do arquivo `autores.txt`.

#### Passando autores como argumento

```bash
python busca_prs_time.py \
  --repositorio caelum/springnarus \
  --autores felipesalmazo user2 user3 \
  --data-inicio 2025-01-01 \
  --data-fim 2025-12-12
```

#### Usando arquivo de autores customizado

```bash
python busca_prs_time.py \
  --repositorio caelum/springnarus \
  --arquivo-autores meu_arquivo_autores.txt \
  --data-inicio 2025-01-01 \
  --data-fim 2025-12-12
```

## GitHub Pages

Este projeto está configurado para publicar automaticamente os resultados em HTML no GitHub Pages.

### Configuração Inicial

1. **Habilite o GitHub Pages no repositório:**
   - Vá em Settings → Pages
   - Em "Source", selecione "GitHub Actions"

2. **Configure o token do GitHub (se necessário):**
   - O workflow usa automaticamente o token padrão do GitHub Actions (`secrets.GITHUB_TOKEN`)
   - Para repositórios privados ou se precisar de mais permissões, você pode criar um Personal Access Token:
     - Vá em Settings → Secrets and variables → Actions
     - Adicione um secret chamado `GH_PERSONAL_TOKEN` (⚠️ não pode começar com `GITHUB_`)
     - O workflow usará automaticamente se disponível, senão usa o token padrão

### Uso do GitHub Pages

#### Opção 1: Execução Manual (Recomendado)

1. Vá em **Actions** no seu repositório
2. Selecione o workflow **"Publicar no GitHub Pages"**
3. Clique em **"Run workflow"**
4. Preencha os parâmetros:
   - **Repositório**: Formato `owner/repo` (ex: `caelum/springnarus`)
   - **Data início**: Data inicial no formato `YYYY-MM-DD`
   - **Data fim**: Data final no formato `YYYY-MM-DD`
   - **Branch base**: Branch base dos PRs (padrão: `main`)
5. Clique em **"Run workflow"**

O workflow irá:
- Buscar os PRs usando o arquivo `autores.txt`
- Gerar o HTML com os resultados
- Publicar automaticamente no GitHub Pages

#### Opção 2: Execução Automática (Schedule)

O workflow está configurado para executar automaticamente toda segunda-feira às 8h UTC (5h horário de Brasília). Você pode ajustar o schedule no arquivo `.github/workflows/publish-pages.yml`.

#### Opção 3: Execução Local

Você também pode gerar o HTML localmente e fazer commit:

```bash
# 1. Buscar PRs do time
python busca_prs_time.py \
  --repositorio caelum/springnarus \
  --data-inicio 2025-01-01 \
  --data-fim 2025-12-31 \
  --arquivo-saida resultado.txt

# 2. Gerar HTML para GitHub Pages
python gerar_html.py resultado.txt docs/index.html

# 3. Fazer commit e push
git add docs/index.html
git commit -m "Atualiza análise de PRs"
git push
```

### Acessando o Resultado

Após a publicação, o resultado estará disponível em:
```
https://<seu-usuario>.github.io/<nome-do-repositorio>/
```

Por exemplo:
```
https://gesleyelois.github.io/busca-github-api/
```

## Funcionalidades

- ✅ Busca PRs mergeados por autor em um intervalo de datas
- ✅ Suporta múltiplos autores (script separado)
- ✅ **Arquivo de configuração `.env` para token** (mais seguro)
- ✅ **Arquivo de lista de autores** (`autores.txt`) para busca em lote
- ✅ Suporta paginação (busca todos os resultados, não apenas os primeiros 30)
- ✅ Gera link de busca no GitHub para ver todos os resultados
- ✅ Extrai título, link, data de merge e descrição breve de cada PR
- ✅ Opção para obter detalhes (branch e commits) de PRs específicos
- ✅ Tratamento de rate limiting da API
- ✅ Formatação organizada dos resultados
- ✅ **Publicação automática no GitHub Pages** com visualização HTML moderna

## Observações

- A API do GitHub Search retorna no máximo 30 resultados por página. O script faz paginação automática para buscar todos os resultados.
- Sem token de autenticação, você tem limite de 60 requisições por hora. Com token, o limite é de 5000 requisições por hora.
- O script indica quando os resultados estão incompletos e fornece o link para ver todos no GitHub.
- **Repositórios privados:** Requer token com permissão `repo`. Veja [GUIA_TOKEN_GITHUB.md](GUIA_TOKEN_GITHUB.md) para mais detalhes.

## Exemplo de Saída

```
felipesalmazo
================================================================================

Observação: a busca retornou 48 resultados no total, a API trouxe 30; os resultados estão incompletos. Ver todos no GitHub: https://github.com/search?q=...

PRs (30 encontrados — cada linha = título — link — data do merge — breve descrição):

  • Manda url do video de onboarding para as tags e substitui o método — https://github.com/caelum/springnarus/pull/10035 — merged: 2025-12-02 — envia/usa URL do vídeo de onboarding para tags; substitui método relacionado.
  • ...
```

