#!/usr/bin/env python3
"""
Script para aumentar o timeout do chat e prevenir timeouts com subagentes
"""

import os

def update_chat_timeout():
    """Atualiza timeout no app.js do chat."""

    app_js_path = "/Users/2a/Desktop/neo4j-agent/chat/app.js"

    print("🔧 Aumentando timeout do chat para 10 minutos...")

    # Ler arquivo
    with open(app_js_path, 'r') as f:
        content = f.read()

    # Procurar e substituir timeouts
    replacements = [
        # Timeout de 5 minutos para 10 minutos
        ("const TIMEOUT = 5 * 60 * 1000", "const TIMEOUT = 10 * 60 * 1000"),
        ("300000", "600000"),  # 5 min em ms para 10 min
        ("5 * 60", "10 * 60"),
    ]

    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            print(f"  ✅ Alterado: {old} → {new}")

    # Salvar
    with open(app_js_path, 'w') as f:
        f.write(content)

    print("\n✅ Timeout aumentado para 10 minutos!")
    print("\n📝 Outras soluções para evitar timeout com subagentes:")
    print("  1. Limite a quantidade de subagentes simultâneos")
    print("  2. Use respostas mais diretas sem spawnar muitos agentes")
    print("  3. Configure timeout maior no servidor também")
    print("  4. Use WebSocket ao invés de SSE para operações longas")

if __name__ == "__main__":
    update_chat_timeout()

    print("\n💡 DICA: Para operações com muitos subagentes, use:")
    print("  - WebSocket client: http://localhost:8080/examples/websocket_client.html")
    print("  - Ele não tem timeout e mantém conexão persistente!")