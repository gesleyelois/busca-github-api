#!/bin/bash
# Script de setup inicial

echo "🔧 Configurando busca-github-api..."

# Cria arquivo .env se não existir
if [ ! -f .env ]; then
    echo "📝 Criando arquivo .env..."
    cp env.example .env
    echo "✅ Arquivo .env criado!"
    echo "⚠️  Não esqueça de editar o arquivo .env e adicionar seu token do GitHub"
else
    echo "ℹ️  Arquivo .env já existe"
fi

# Verifica se o arquivo de autores existe
if [ ! -f autores.txt ]; then
    echo "📝 Arquivo autores.txt não encontrado, mas não é obrigatório"
fi

echo ""
echo "✅ Setup concluído!"
echo ""
echo "Próximos passos:"
echo "1. Edite o arquivo .env e adicione seu token do GitHub"
echo "2. (Opcional) Edite o arquivo autores.txt com a lista de autores"
echo "3. Execute: pip install -r requirements.txt"
echo "4. Use os scripts conforme documentado no README.md"

