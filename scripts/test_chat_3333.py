#!/usr/bin/env python3
"""
Testa o chat em http://localhost:8080/
"""

import requests
import json
import uuid
import time

def test_chat_interface():
    """Testa a interface do chat na porta 8080."""

    print("🚀 TESTE DO CHAT EM http://localhost:8080/")
    print("=" * 60)

    # Primeiro verifica se a página está acessível
    try:
        response = requests.get("http://localhost:8080/")
        if response.status_code == 200:
            print("✅ Página do chat está acessível")
        else:
            print(f"❌ Erro ao acessar página: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return

    # Gera session ID
    session_id = str(uuid.uuid4())
    print(f"\n📋 Session ID: {session_id}")

    # Cria sessão
    print("\n1. Criando sessão...")
    try:
        session_response = requests.post(
            "http://localhost:8080/api/sessions",
            json={"session_id": session_id}
        )
        if session_response.status_code == 200:
            print(f"✅ Sessão criada: {session_response.json()['session_id']}")
        else:
            print(f"❌ Erro ao criar sessão: {session_response.text}")
            return
    except Exception as e:
        print(f"❌ Erro: {e}")
        return

    # Envia mensagem
    print("\n2. Enviando mensagem 'Oi'...")
    try:
        with requests.post(
            "http://localhost:8080/api/chat",
            json={"message": "Oi", "session_id": session_id},
            stream=True,
            timeout=10
        ) as response:

            if response.status_code != 200:
                print(f"❌ Erro: Status {response.status_code}")
                return

            print("\n📨 Resposta do Claude:")
            print("-" * 60)

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

                            elif data.get('type') == 'done':
                                break

                            elif data.get('type') == 'error':
                                print(f"\n❌ Erro: {data.get('error', 'Erro desconhecido')}")
                                break

                        except json.JSONDecodeError:
                            continue

            print("\n" + "-" * 60)

            if full_response:
                print("\n✅ CHAT FUNCIONANDO PERFEITAMENTE!")
                print(f"Resposta completa: {len(''.join(full_response))} caracteres")
                print("\n🎯 Acesse http://localhost:8080/ no navegador")
                print("   e clique em 'Enviar' para testar visualmente!")
            else:
                print("⚠️ Nenhuma resposta recebida")

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_chat_interface()