#!/bin/bash

# Script para capturar screenshot da janela do navegador

echo "🎯 Tentando capturar janela do navegador..."

# Tenta ativar e capturar cada navegador
for browser in "Google Chrome" "Safari" "Firefox" "Arc" "Brave Browser" "Microsoft Edge"; do
    echo "Verificando $browser..."

    # Verifica se o navegador está rodando
    if osascript -e "tell application \"System Events\" to (name of processes) contains \"$browser\"" 2>/dev/null | grep -q "true"; then
        echo "✅ $browser está rodando"

        # Ativa o navegador
        osascript -e "tell application \"$browser\" to activate" 2>/dev/null

        # Aguarda a janela ficar ativa
        sleep 2

        # Tenta capturar a janela ativa
        echo "📸 Capturando janela..."

        # Usa screencapture com modo de janela interativo
        # O usuário precisa clicar na janela desejada
        echo "👆 Clique na janela do navegador com o chat para capturar"
        screencapture -W -x /tmp/browser_window.png

        if [ -f "/tmp/browser_window.png" ]; then
            echo "✅ Screenshot salvo em /tmp/browser_window.png"
            exit 0
        fi
    fi
done

echo "❌ Nenhum navegador encontrado ou não foi possível capturar"
echo ""
echo "📱 Alternativa: Use os atalhos do macOS:"
echo "  • Cmd + Shift + 4 e depois Espaço - Clique na janela"
echo "  • Cmd + Shift + 5 - Escolha 'Capturar Janela Selecionada'"