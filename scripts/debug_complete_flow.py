#!/usr/bin/env python3
"""
Debug completo do fluxo de mensagem
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import uuid
from datetime import datetime

async def debug_flow():
    """Debug passo a passo do fluxo completo."""

    print("🔍 DEBUG COMPLETO DO FLUXO DE MENSAGEM")
    print("=" * 60)

    # 1. Teste direto do SDK
    print("\n1️⃣ TESTE DIRETO DO SDK")
    print("-" * 40)

    try:
        sdk_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sdk')
        sys.path.insert(0, sdk_dir)

        from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions

        options = ClaudeCodeOptions(
            permission_mode="bypassPermissions"
        )

        client = ClaudeSDKClient(options=options)
        print("✅ Cliente SDK criado")

        print("Conectando ao SDK...")
        await asyncio.wait_for(client.connect(), timeout=5.0)
        print("✅ Conectado")

        print("Enviando query...")
        await client.query("teste direto")

        print("Aguardando resposta...")
        response_received = False

        async for msg in client.receive_response():
            response_received = True
            if hasattr(msg, 'content'):
                for block in msg.content:
                    if hasattr(block, 'text'):
                        print(f"📨 Resposta SDK: {block.text[:100]}...")
                        break
            break

        if response_received:
            print("✅ SDK está funcionando corretamente")
        else:
            print("❌ SDK não retornou resposta")

        await client.disconnect()

    except Exception as e:
        print(f"❌ Erro no SDK: {e}")

    # 2. Teste do ClaudeHandler
    print("\n2️⃣ TESTE DO CLAUDE HANDLER")
    print("-" * 40)

    try:
        from core.claude_handler import ClaudeHandler, SessionConfig

        handler = ClaudeHandler()
        session_id = str(uuid.uuid4())

        print(f"Session ID: {session_id}")

        config = SessionConfig(
            project_id="neo4j-agent",
            temperature=0.7,
            model="claude-3-5-sonnet-20241022"
        )

        print("Criando sessão...")
        await handler.create_session(session_id, config)
        print("✅ Sessão criada")

        print("Enviando mensagem via handler...")
        response_parts = []
        chunk_count = 0

        async for chunk in handler.send_message(session_id, "teste handler"):
            chunk_count += 1
            print(f"  Chunk #{chunk_count}: tipo={chunk.get('type')}")

            if chunk.get('type') == 'content':
                content = chunk.get('content', '')
                response_parts.append(content)

            # Para após alguns chunks para debug
            if chunk_count > 10:
                break

        if response_parts:
            print(f"✅ Handler retornou resposta: {len(''.join(response_parts))} chars")
        else:
            print(f"❌ Handler não retornou conteúdo (recebeu {chunk_count} chunks)")

        await handler.destroy_session(session_id)

    except Exception as e:
        print(f"❌ Erro no Handler: {e}")
        import traceback
        traceback.print_exc()

    # 3. Verificar o pool de conexões
    print("\n3️⃣ STATUS DO POOL DE CONEXÕES")
    print("-" * 40)

    try:
        pool_status = await handler.get_pool_status()
        print(f"Pool size: {pool_status['pool_size']}")
        print(f"Healthy connections: {pool_status['healthy_connections']}")
        print(f"Max size: {pool_status['max_size']}")

    except Exception as e:
        print(f"❌ Erro ao verificar pool: {e}")

    # 4. Teste via API HTTP
    print("\n4️⃣ TESTE VIA API HTTP")
    print("-" * 40)

    try:
        import aiohttp

        session_id = str(uuid.uuid4())

        async with aiohttp.ClientSession() as session:
            # Criar sessão
            print("Criando sessão via API...")
            async with session.post(
                "http://localhost:8080/api/sessions",
                json={"session_id": session_id}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Sessão criada: {data['session_id']}")
                else:
                    print(f"❌ Erro ao criar sessão: {resp.status}")
                    return

            # Enviar mensagem
            print("Enviando mensagem via API...")
            async with session.post(
                "http://localhost:8080/api/chat",
                json={"message": "teste api", "session_id": session_id}
            ) as resp:
                if resp.status == 200:
                    print("Processando SSE...")
                    chunks_received = 0
                    content_received = False

                    async for line in resp.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            chunks_received += 1
                            try:
                                import json
                                data = json.loads(line[6:])
                                if data.get('type') == 'content':
                                    content_received = True
                                    print(f"  📨 Conteúdo recebido: {data.get('content', '')[:50]}...")
                            except:
                                pass

                        if chunks_received > 20:
                            break

                    if content_received:
                        print(f"✅ API retornou conteúdo ({chunks_received} chunks)")
                    else:
                        print(f"❌ API não retornou conteúdo ({chunks_received} chunks recebidos)")
                else:
                    print(f"❌ Erro na API: {resp.status}")

    except Exception as e:
        print(f"❌ Erro no teste da API: {e}")

    print("\n" + "=" * 60)
    print("🏁 DEBUG COMPLETO FINALIZADO")
    print("\n📊 RESUMO:")
    print("- SDK direto: Verifique acima")
    print("- Claude Handler: Verifique acima")
    print("- Pool de conexões: Verifique acima")
    print("- API HTTP: Verifique acima")

if __name__ == "__main__":
    asyncio.run(debug_flow())