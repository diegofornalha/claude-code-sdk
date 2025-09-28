#!/usr/bin/env python3
"""
Teste do WebSocket endpoint
"""

import asyncio
import websockets
import json
import uuid

async def test_websocket():
    """Testa conexão WebSocket com o servidor."""

    session_id = str(uuid.uuid4())
    uri = f"ws://localhost:8080/ws/advanced/{session_id}"

    print(f"🚀 Conectando ao WebSocket: {uri}")
    print("=" * 60)

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Conectado com sucesso!")

            # Enviar mensagem de teste
            message = {
                "type": "query",
                "message": "Olá! Este é um teste do WebSocket."
            }

            print(f"\n📤 Enviando: {message['message']}")
            await websocket.send(json.dumps(message))

            # Receber respostas
            print("\n📥 Respostas:")
            print("-" * 40)

            response_count = 0
            full_response = []

            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(response)
                    response_count += 1

                    if data.get("type") == "processing":
                        print("⏳ Processando...")
                    elif data.get("type") == "content":
                        content = data.get("content", "")
                        full_response.append(content)
                        print(content, end="", flush=True)
                    elif data.get("type") == "done":
                        print("\n" + "-" * 40)
                        print("✅ Resposta completa!")
                        break
                    elif data.get("type") == "error":
                        print(f"\n❌ Erro: {data.get('error')}")
                        break

                except asyncio.TimeoutError:
                    print("\n⏱️ Timeout - sem mais respostas")
                    break

            if full_response:
                print(f"\n📊 Estatísticas:")
                print(f"  - Chunks recebidos: {response_count}")
                print(f"  - Resposta total: {len(''.join(full_response))} caracteres")
                print("\n✅ TESTE BEM-SUCEDIDO!")
            else:
                print("\n⚠️ Nenhuma resposta de conteúdo recebida")

            # Testar comando
            print("\n🎮 Testando comando 'get_stats'...")
            command = {
                "type": "command",
                "command": "get_stats"
            }
            await websocket.send(json.dumps(command))

            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                print(f"📊 Resposta do comando: {data}")
            except:
                pass

    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        print("\n💡 Verifique se:")
        print("  1. O servidor está rodando em http://localhost:8080")
        print("  2. Os endpoints WebSocket estão configurados")
        print("  3. O handler WebSocket está importado corretamente")

if __name__ == "__main__":
    print("🧪 TESTE DO WEBSOCKET ENDPOINT")
    print()
    asyncio.run(test_websocket())