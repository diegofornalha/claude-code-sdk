#!/usr/bin/env python3
"""
Debug do problema no chat
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import uuid
from core.claude_handler import ClaudeHandler, SessionConfig

async def test_claude_handler():
    """Testa o ClaudeHandler diretamente."""

    print("🔍 DEBUG DO CHAT")
    print("=" * 60)

    # Cria handler
    handler = ClaudeHandler()
    session_id = str(uuid.uuid4())

    print(f"1. Criando sessão: {session_id}")

    try:
        # Cria configuração
        config = SessionConfig(
            project_id="neo4j-agent",
            temperature=0.7,
            model="claude-3-5-sonnet-20241022"
        )

        # Cria sessão
        await handler.create_session(session_id, config)
        print("✅ Sessão criada com sucesso")

    except Exception as e:
        print(f"❌ Erro ao criar sessão: {e}")
        print(f"   Tipo: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return

    print("\n2. Enviando mensagem 'Oi'")

    try:
        # Envia mensagem
        response_parts = []
        async for chunk in handler.send_message(session_id, "Oi"):
            if chunk.get('type') == 'content':
                content = chunk.get('content', '')
                response_parts.append(content)
                print(content, end='', flush=True)

        print("\n" + "-" * 60)

        if response_parts:
            print("✅ Resposta recebida com sucesso!")
            print(f"   Tamanho: {len(''.join(response_parts))} caracteres")
        else:
            print("⚠️ Nenhuma resposta recebida")

    except Exception as e:
        print(f"\n❌ Erro ao enviar mensagem: {e}")
        print(f"   Tipo: {type(e).__name__}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        try:
            await handler.destroy_session(session_id)
            print("\n✅ Sessão limpa")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_claude_handler())