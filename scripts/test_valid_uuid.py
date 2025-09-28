#!/usr/bin/env python3
"""
Teste com UUID válido
"""

import requests
import uuid
import json

def test_with_valid_uuid():
    """Testa o chat com UUID válido."""

    print("🚀 TESTE COM UUID VÁLIDO")
    print("=" * 60)

    # Gera UUID válido
    session_id = str(uuid.uuid4())
    print(f"📋 Session ID válido: {session_id}")

    # 1. Cria sessão
    print("\n1. Criando sessão...")
    session_response = requests.post(
        "http://localhost:8080/api/sessions",
        json={"session_id": session_id}
    )

    if session_response.status_code == 200:
        data = session_response.json()
        print(f"✅ Sessão criada: {data['session_id']}")
    else:
        print(f"❌ Erro ao criar sessão: {session_response.text}")
        return

    # 2. Envia mensagem
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
                print(f"Detalhes: {response.text}")
                return

            print("📨 Resposta:")
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
                print("\n✅ TESTE BEM-SUCEDIDO!")
                print(f"Resposta completa: {len(''.join(full_response))} caracteres")
            else:
                print("⚠️ Nenhuma resposta recebida")

    except requests.Timeout:
        print("⏱️ Timeout - sem resposta em 10 segundos")
    except Exception as e:
        print(f"❌ Erro: {e}")

    print("\n🎉 Teste concluído!")

if __name__ == "__main__":
    test_with_valid_uuid()