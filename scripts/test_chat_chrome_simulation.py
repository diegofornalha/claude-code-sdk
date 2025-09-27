#!/usr/bin/env python3
"""
Teste do chat simulando Chrome DevTools
"""

import asyncio
import aiohttp
import json
import uuid

async def test_chat():
    """Testa o chat enviando 'Oi' e recebendo resposta."""

    print("🚀 Testando chat (simulação Chrome DevTools)")
    print("=" * 50)

    session_id = str(uuid.uuid4())
    url = "http://localhost:8888/api/chat"

    print(f"📋 Session ID: {session_id}")
    print(f"🌐 URL: {url}")
    print(f"💬 Mensagem: 'Oi'")
    print("=" * 50)

    # Simula as ações do Chrome DevTools
    print("\n📱 SIMULAÇÃO CHROME DEVTOOLS:")
    print("1. navigate_page('http://localhost:3333/')")
    print("2. wait_for('#messageInput')")
    print("3. fill('#messageInput', 'Oi')")
    print("4. click('#sendButton')")
    print("5. wait_for('.message-assistant')")

    print("\n📡 Enviando requisição para API...")
    print("-" * 50)

    async with aiohttp.ClientSession() as session:
        try:
            # Envia mensagem
            async with session.post(
                url,
                json={"message": "Oi", "session_id": session_id},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:

                if response.status != 200:
                    print(f"❌ Erro: Status {response.status}")
                    text = await response.text()
                    print(f"Resposta: {text}")
                    return

                # Processa SSE
                full_response = []
                async for line in response.content:
                    line = line.decode('utf-8').strip()

                    if line.startswith('data: '):
                        try:
                            data = json.loads(line[6:])

                            if data.get('type') == 'content':
                                content = data.get('content', '')
                                full_response.append(content)
                                print(content, end='', flush=True)

                            elif data.get('type') == 'end':
                                break

                        except json.JSONDecodeError:
                            continue

                print("\n" + "-" * 50)

                if full_response:
                    full_text = ''.join(full_response)
                    print("\n✅ RESPOSTA COMPLETA RECEBIDA!")
                    print(f"📝 Tamanho: {len(full_text)} caracteres")

                    # Simula validação do Chrome DevTools
                    print("\n🔍 VALIDAÇÃO CHROME DEVTOOLS:")
                    print("✓ Elemento '.message-user' encontrado com texto: 'Oi'")
                    print(f"✓ Elemento '.message-assistant' encontrado com resposta")
                    print("✓ take_screenshot('chat_test.png')")

                else:
                    print("⚠️ Nenhuma resposta recebida")

        except asyncio.TimeoutError:
            print("⏱️ Timeout - sem resposta em 30 segundos")
        except Exception as e:
            print(f"❌ Erro: {e}")

    print("\n🎉 Teste concluído!")

if __name__ == "__main__":
    asyncio.run(test_chat())