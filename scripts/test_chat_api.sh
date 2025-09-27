#!/bin/bash

# Script para testar o chat via API
echo "🚀 Testando chat API..."
echo ""

# Gera um session_id único
SESSION_ID=$(uuidgen)
echo "📋 Session ID: $SESSION_ID"
echo ""

# Envia mensagem "Oi" para o chat
echo "📤 Enviando mensagem: 'Oi'"
echo ""

# Faz a requisição SSE
echo "📨 Resposta do assistente:"
echo "----------------------------------------"

curl -N -X POST http://localhost:8888/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Oi\", \"session_id\": \"$SESSION_ID\"}" \
  2>/dev/null | while IFS= read -r line; do
    if [[ $line == data:* ]]; then
        # Remove o prefixo "data: " e processa o JSON
        json="${line#data: }"
        if [[ $json != "" && $json != " " ]]; then
            # Extrai o tipo e conteúdo
            type=$(echo "$json" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('type', ''))" 2>/dev/null)

            if [[ $type == "content" ]]; then
                content=$(echo "$json" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('content', ''))" 2>/dev/null)
                echo -n "$content"
            elif [[ $type == "end" ]]; then
                echo ""
                echo "----------------------------------------"
                echo "✅ Resposta completa recebida!"
                break
            fi
        fi
    fi
done

echo ""
echo "🎉 Teste concluído!"