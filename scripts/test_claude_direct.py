#!/usr/bin/env python3
"""
Teste direto do Claude SDK
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Adiciona o diretório do SDK ao path
sdk_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sdk')
sys.path.insert(0, sdk_dir)

import asyncio

async def test_claude_sdk():
    """Testa o Claude SDK diretamente."""

    print("🔍 TESTE DIRETO DO CLAUDE SDK")
    print("=" * 60)

    try:
        from claude_code_sdk import (
            ClaudeSDKClient,
            UserMessage,
            ClaudeCodeOptions
        )

        print("✅ SDK importado com sucesso")

        # Cria opções
        options = ClaudeCodeOptions(
            permission_mode="bypassPermissions"
        )

        # Cria cliente
        client = ClaudeSDKClient(options=options)
        print("✅ Cliente criado")

        # Conecta
        print("Conectando...")
        await asyncio.wait_for(client.connect(), timeout=10.0)
        print("✅ Conectado ao SDK")

        # Envia mensagem
        print("\nEnviando mensagem: 'Oi'")
        await client.query("Oi")

        # Recebe resposta
        print("Aguardando resposta...")
        response_parts = []

        async for msg in client.receive_response():
            if hasattr(msg, 'content'):
                for block in msg.content:
                    if hasattr(block, 'text'):
                        response_parts.append(block.text)
                        print(block.text, end='', flush=True)

        print("\n" + "=" * 60)

        if response_parts:
            print("✅ RESPOSTA RECEBIDA COM SUCESSO!")
        else:
            print("⚠️ Nenhuma resposta recebida")

        # Desconecta
        await client.disconnect()
        print("✅ Desconectado")

    except ImportError as e:
        print(f"❌ Erro ao importar SDK: {e}")
    except asyncio.TimeoutError:
        print("❌ Timeout ao conectar com SDK")
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_claude_sdk())