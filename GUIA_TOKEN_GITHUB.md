# Como Obter um Token do GitHub

Este guia explica como criar um Personal Access Token (PAT) no GitHub para usar com os scripts de busca de PRs.

## Passo a Passo

### 1. Acesse as Configurações do GitHub

1. Faça login no GitHub
2. Clique no seu avatar (canto superior direito)
3. Selecione **Settings** (Configurações)

### 2. Acesse a Seção de Tokens

1. No menu lateral esquerdo, role até o final
2. Clique em **Developer settings** (Configurações do desenvolvedor)
3. No menu lateral esquerdo, clique em **Personal access tokens**
4. Selecione **Tokens (classic)** ou **Fine-grained tokens**

**Recomendação:** Use **Tokens (classic)** para maior compatibilidade.

### 3. Crie um Novo Token

1. Clique em **Generate new token** (Gerar novo token)
2. Se estiver usando tokens classic, clique em **Generate new token (classic)**

### 4. Configure o Token

#### Para Tokens Classic:

1. **Note** (Nota): Dê um nome descritivo, ex: "Busca PRs - Script Python"
2. **Expiration** (Expiração): Escolha o período de validade:
   - **30 days** (30 dias)
   - **60 days** (60 dias)
   - **90 days** (90 dias)
   - **No expiration** (Sem expiração) - ⚠️ Menos seguro, mas mais conveniente
3. **Select scopes** (Selecionar permissões): Marque as seguintes permissões:
   - ✅ **`public_repo`** - Acesso a repositórios públicos (necessário para buscar PRs em repositórios públicos)
   - ✅ **`repo`** - ⚠️ **OBRIGATÓRIO para repositórios privados** - Acesso completo a repositórios (inclui privados)

#### Para Fine-grained Tokens:

1. **Token name**: Dê um nome descritivo
2. **Expiration**: Escolha o período de validade
3. **Repository access**: 
   - **All repositories** (Todos os repositórios) ou
   - **Only select repositories** (Apenas repositórios selecionados)
4. **Repository permissions**: Selecione:
   - **Contents**: Read-only (Leitura)
   - **Metadata**: Read-only (Leitura)
   - **Pull requests**: Read-only (Leitura)

### 5. Gere e Copie o Token

1. Role até o final da página
2. Clique em **Generate token** (Gerar token)
3. **⚠️ IMPORTANTE:** Copie o token imediatamente! Você não poderá vê-lo novamente depois de sair desta página.
4. Guarde o token em um local seguro (gerenciador de senhas, variável de ambiente, etc.)

## Como Usar o Token nos Scripts

### Opção 1: Passar como Argumento (Menos Seguro)

```bash
python busca_prs_github.py \
  --repositorio caelum/springnarus \
  --autor felipesalmazo \
  --data-inicio 2025-01-01 \
  --data-fim 2025-12-12 \
  --token ghp_seu_token_aqui
```

### Opção 2: Variável de Ambiente (Recomendado)

1. Configure a variável de ambiente:

```bash
# Linux/Mac
export GITHUB_TOKEN="ghp_seu_token_aqui"

# Windows (PowerShell)
$env:GITHUB_TOKEN="ghp_seu_token_aqui"

# Windows (CMD)
set GITHUB_TOKEN=ghp_seu_token_aqui
```

2. Use nos scripts (os scripts podem ser modificados para ler automaticamente):

```bash
python busca_prs_github.py \
  --repositorio caelum/springnarus \
  --autor felipesalmazo \
  --data-inicio 2025-01-01 \
  --data-fim 2025-12-12 \
  --token $GITHUB_TOKEN
```

### Opção 3: Arquivo de Configuração (Mais Seguro)

Você pode criar um arquivo `.env` (não versionado) ou um arquivo de configuração local.

## Links Úteis

- **Criar token classic:** https://github.com/settings/tokens/new
- **Gerenciar tokens:** https://github.com/settings/tokens
- **Documentação oficial:** https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token

## Segurança

⚠️ **IMPORTANTE:**

- **NUNCA** compartilhe seu token publicamente
- **NUNCA** faça commit do token no Git
- Adicione arquivos com tokens ao `.gitignore`
- Use tokens com expiração quando possível
- Revogue tokens que não estão mais em uso
- Use permissões mínimas necessárias (princípio do menor privilégio)

## Acessando Repositórios Privados

Para acessar repositórios privados via API, você precisa:

### 1. Token com Permissão `repo`

⚠️ **IMPORTANTE:** Para repositórios privados, você **DEVE** usar a permissão `repo` (não apenas `public_repo`).

#### Tokens Classic:
- Marque a permissão **`repo`** (isso inclui acesso a repositórios privados)
- A permissão `public_repo` **NÃO** é suficiente para repositórios privados

#### Fine-grained Tokens:
- Em **Repository access**, selecione:
  - **All repositories** (se quiser acesso a todos), ou
  - **Only select repositories** (e escolha os repositórios privados específicos)
- Em **Repository permissions**, selecione:
  - **Contents**: Read-only
  - **Metadata**: Read-only
  - **Pull requests**: Read-only

### 2. Acesso ao Repositório

Certifique-se de que:
- Você tem acesso ao repositório privado (é membro da organização ou tem acesso direto)
- O token foi criado com a conta que tem acesso ao repositório
- Se o repositório pertence a uma organização, verifique se a organização permite tokens pessoais

### 3. Verificar Acesso

Para testar se seu token tem acesso a um repositório privado:

```bash
# Teste de acesso (substitua owner/repo pelo repositório privado)
curl -H "Authorization: token ghp_seu_token" \
     https://api.github.com/repos/owner/repo
```

Se retornar os dados do repositório, o acesso está funcionando. Se retornar 404, verifique:
- Se o token tem a permissão `repo`
- Se você tem acesso ao repositório
- Se o nome do repositório está correto

### 4. Usar nos Scripts

Os scripts funcionam da mesma forma para repositórios privados, desde que o token tenha a permissão `repo`:

```bash
# O token será lido automaticamente do arquivo .env
python busca_prs_github.py \
  --repositorio organizacao/repositorio-privado \
  --autor username \
  --data-inicio 2025-01-01 \
  --data-fim 2025-12-12
```

## Limites de Rate Limiting

- **Sem token:** 60 requisições por hora
- **Com token:** 5.000 requisições por hora

Usar um token é altamente recomendado para evitar bloqueios durante buscas extensas!

