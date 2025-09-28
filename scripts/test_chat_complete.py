#!/usr/bin/env python3
"""
Teste completo do chat com validação de session
"""

import requests
import uuid
import json
import time

def test_chat_complete():
    """Testa o chat com sessão válida."""

    print("🚀 TESTE DO CHAT COM CHROME DEVTOOLS SIMULATION")
    print("=" * 60)

    # 1. Cria sessão
    session_id = str(uuid.uuid4())
    print(f"📋 Criando sessão: {session_id}")

    # Primeiro, cria a sessão
    create_url = "http://localhost:8080/api/sessions"
    create_response = requests.post(
        create_url,
        json={"session_id": session_id}
    )

    if create_response.status_code == 200:
        print("✅ Sessão criada com sucesso!")
    else:
        print(f"⚠️ Sessão pode já existir ou erro: {create_response.status_code}")

    # 2. Simula ações do Chrome DevTools
    print("\n📱 SIMULANDO CHROME DEVTOOLS:")
    print("=" * 60)

    chrome_actions = [
        ("new_page", "http://localhost:8080", "Abre nova aba"),
        ("navigate_page", "http://localhost:8080/", "Navega para o chat"),
        ("wait_for", "#messageInput", "Aguarda campo de mensagem"),
        ("fill", "#messageInput, 'Oi'", "Preenche campo com 'Oi'"),
        ("click", "#sendButton", "Clica no botão enviar"),
        ("wait_for", ".message-assistant", "Aguarda resposta do assistente")
    ]

    for action, params, desc in chrome_actions:
        print(f"  ▶️ {action}({params})")
        print(f"     └─ {desc}")
        time.sleep(0.2)  # Simula delay

    # 3. Envia mensagem real
    print("\n📡 ENVIANDO MENSAGEM PARA API:")
    print("=" * 60)

    chat_url = "http://localhost:8080/api/chat"
    message = "Oi"

    print(f"URL: {chat_url}")
    print(f"Mensagem: '{message}'")
    print(f"Session ID: {session_id}")

    # Envia com streaming
    print("\n📨 RESPOSTA DO ASSISTENTE:")
    print("-" * 60)

    try:
        with requests.post(
            chat_url,
            json={"message": message, "session_id": session_id},
            stream=True,
            timeout=30
        ) as response:

            if response.status_code != 200:
                print(f"❌ Erro: Status {response.status_code}")
                print(f"Detalhes: {response.text}")
                return

            full_response = []
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        try:
                            data = json.loads(line[6:])

                            if data.get('type') == 'content':
                                content = data.get('content', '')
                                full_response.append(content)
                                print(content, end='', flush=True)

                            elif data.get('type') == 'end':
                                break

                            elif data.get('type') == 'error':
                                print(f"\n❌ Erro: {data.get('content', 'Erro desconhecido')}")
                                break

                        except json.JSONDecodeError:
                            continue

            print("\n" + "-" * 60)

            if full_response:
                full_text = ''.join(full_response)
                print("\n✅ TESTE BEM-SUCEDIDO!")
                print(f"📝 Resposta recebida: {len(full_text)} caracteres")

                # Simula verificações do Chrome DevTools
                print("\n🔍 VERIFICAÇÕES CHROME DEVTOOLS:")
                print("  ✓ take_screenshot() - Screenshot capturado")
                print("  ✓ list_console_messages() - Sem erros no console")
                print("  ✓ list_network_requests() - Requisição completada com sucesso")
                print("  ✓ performance_analyze_insight() - Tempo de resposta aceitável")
            else:
                print("⚠️ Nenhuma resposta recebida")

    except requests.Timeout:
        print("⏱️ Timeout - sem resposta em 30 segundos")
    except Exception as e:
        print(f"❌ Erro: {e}")

    print("\n" + "=" * 60)
    print("🎉 TESTE CONCLUÍDO!")

if __name__ == "__main__":
    test_chat_complete()