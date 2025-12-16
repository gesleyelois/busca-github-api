#!/bin/bash
# Script para configurar remote e fazer push para GitHub

echo "🚀 Configurando repositório Git para GitHub..."
echo ""

# Verifica se já existe remote
if git remote -v | grep -q origin; then
    echo "✅ Remote 'origin' já configurado:"
    git remote -v
    echo ""
    read -p "Deseja fazer push agora? (s/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        git push -u origin main
    fi
else
    echo "📝 Para adicionar o remote e fazer push:"
    echo ""
    echo "1. Crie um repositório no GitHub (se ainda não criou)"
    echo "2. Execute:"
    echo "   git remote add origin https://github.com/SEU_USUARIO/busca-github-api.git"
    echo "   git push -u origin main"
    echo ""
    echo "Ou se preferir usar SSH:"
    echo "   git remote add origin git@github.com:SEU_USUARIO/busca-github-api.git"
    echo "   git push -u origin main"
    echo ""
    read -p "Deseja adicionar o remote agora? (s/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        read -p "Digite seu usuário do GitHub: " usuario
        read -p "Digite o nome do repositório (padrão: busca-github-api): " repo
        repo=${repo:-busca-github-api}
        
        echo ""
        echo "Escolha o protocolo:"
        echo "1) HTTPS"
        echo "2) SSH"
        read -p "Opção (1 ou 2): " protocolo
        
        if [ "$protocolo" = "1" ]; then
            git remote add origin "https://github.com/$usuario/$repo.git"
        else
            git remote add origin "git@github.com:$usuario/$repo.git"
        fi
        
        echo "✅ Remote adicionado!"
        echo ""
        read -p "Deseja fazer push agora? (s/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            git push -u origin main
        fi
    fi
fi

