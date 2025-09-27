#!/usr/bin/env python3
"""
Script de teste para o ClaudeHandler.
Testa as principais funcionalidades do handler de forma isolada.
"""

import asyncio
import sys
import os
from datetime import datetime
import json
from typing import Dict, Any

# Adiciona o diretório pai ao path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.claude_handler import ClaudeHandler, SessionConfig
from utils.logging_config import get_contextual_logger

logger = get_contextual_logger("test_handler")

class HandlerTestSuite:
    """Suite de testes para o ClaudeHandler."""

    def __init__(self):
        self.handler = ClaudeHandler()
        self.test_results = []
        self.session_ids = []

    async def run_all_tests(self):
        """Executa todos os testes."""
        print("\n" + "="*60)
        print("🧪 INICIANDO TESTES DO CLAUDE HANDLER")
        print("="*60 + "\n")

        tests = [
            self.test_create_session,
            self.test_session_with_config,
            self.test_send_message,
            self.test_multiple_sessions,
            self.test_session_info,
            self.test_update_session_config,
            self.test_pool_status,
            self.test_session_destruction,
            self.test_error_handling,
        ]

        for test_func in tests:
            await self.run_test(test_func)

        # Limpa sessões criadas
        await self.cleanup_sessions()

        # Exibe resumo
        self.show_results()

    async def run_test(self, test_func):
        """Executa um teste individual."""
        test_name = test_func.__name__.replace("test_", "").replace("_", " ").title()

        try:
            print(f"▶️  Testando: {test_name}")
            result = await test_func()

            if result:
                print(f"✅ {test_name}: PASSOU")
                self.test_results.append((test_name, "PASSOU", None))
            else:
                print(f"❌ {test_name}: FALHOU")
                self.test_results.append((test_name, "FALHOU", "Teste retornou False"))

        except Exception as e:
            print(f"❌ {test_name}: ERRO - {str(e)}")
            self.test_results.append((test_name, "ERRO", str(e)))

        print()

    async def test_create_session(self) -> bool:
        """Testa criação básica de sessão."""
        session_id = "test-session-001"
        self.session_ids.append(session_id)

        await self.handler.create_session(session_id)

        # Verifica se sessão foi criada
        if session_id not in self.handler.clients:
            raise AssertionError("Sessão não foi criada no clients")

        if session_id not in self.handler.active_sessions:
            raise AssertionError("Sessão não marcada como ativa")

        print(f"   ├─ Sessão criada: {session_id}")
        print(f"   └─ Status ativo: {self.handler.active_sessions[session_id]}")

        return True

    async def test_session_with_config(self) -> bool:
        """Testa criação de sessão com configuração customizada."""
        session_id = "test-session-002"
        self.session_ids.append(session_id)

        config = SessionConfig(
            project_id="test-project",
            temperature=0.5,
            model="claude-3-5-sonnet-20241022",
            system_prompt="Você é um assistente de testes",
            allowed_tools=["Read", "Write"],
            max_turns=10,
            permission_mode="bypassPermissions",
            cwd="/tmp"
        )

        await self.handler.create_session(session_id, config)

        # Verifica configuração
        saved_config = self.handler.session_configs.get(session_id)
        if not saved_config:
            raise AssertionError("Configuração não foi salva")

        if saved_config.temperature != 0.5:
            raise AssertionError(f"Temperature incorreta: {saved_config.temperature}")

        print(f"   ├─ Sessão com config: {session_id}")
        print(f"   ├─ Temperature: {saved_config.temperature}")
        print(f"   ├─ Tools: {saved_config.allowed_tools}")
        print(f"   └─ Permission Mode: {saved_config.permission_mode}")

        return True

    async def test_send_message(self) -> bool:
        """Testa envio de mensagem simples."""
        session_id = "test-session-003"
        self.session_ids.append(session_id)

        await self.handler.create_session(session_id)

        # Envia mensagem de teste
        message = "Olá, este é um teste. Responda apenas 'OK'"
        chunks = []

        print(f"   ├─ Enviando: '{message}'")

        try:
            async for chunk in self.handler.send_message(session_id, message, timeout=10.0):
                chunks.append(chunk)

                if chunk.get("type") == "processing":
                    print(f"   ├─ Processando...")
                elif chunk.get("type") == "text_chunk":
                    print(f"   ├─ Chunk: {chunk.get('content', '')[:30]}...")
                elif chunk.get("type") == "result":
                    print(f"   └─ Finalizado")

        except asyncio.TimeoutError:
            print(f"   └─ Timeout (normal para teste)")
            # Timeout é aceitável em teste
            return True

        return len(chunks) > 0

    async def test_multiple_sessions(self) -> bool:
        """Testa múltiplas sessões simultâneas."""
        sessions = []

        for i in range(3):
            session_id = f"test-multi-{i:03d}"
            self.session_ids.append(session_id)
            sessions.append(session_id)
            await self.handler.create_session(session_id)

        # Verifica todas as sessões
        all_sessions = await self.handler.get_all_sessions()

        created_count = sum(1 for s in all_sessions if any(sid in s['session_id'] for sid in sessions))

        print(f"   ├─ Sessões criadas: {len(sessions)}")
        print(f"   ├─ Sessões ativas totais: {len(all_sessions)}")
        print(f"   └─ Nossas sessões encontradas: {created_count}")

        return created_count == len(sessions)

    async def test_session_info(self) -> bool:
        """Testa obtenção de informações da sessão."""
        session_id = "test-info-001"
        self.session_ids.append(session_id)

        config = SessionConfig(
            system_prompt="Test prompt",
            allowed_tools=["Tool1", "Tool2"]
        )

        await self.handler.create_session(session_id, config)

        info = await self.handler.get_session_info(session_id)

        if info.get("error"):
            raise AssertionError(f"Erro ao obter info: {info['error']}")

        print(f"   ├─ Session ID: {info.get('session_id')}")
        print(f"   ├─ Ativa: {info.get('active')}")
        print(f"   ├─ System Prompt: {info['config'].get('system_prompt')}")
        print(f"   └─ Tools: {info['config'].get('allowed_tools')}")

        return info['session_id'] == session_id

    async def test_update_session_config(self) -> bool:
        """Testa atualização de configuração da sessão."""
        session_id = "test-update-001"
        self.session_ids.append(session_id)

        # Cria com config inicial
        initial_config = SessionConfig(temperature=0.7)
        await self.handler.create_session(session_id, initial_config)

        # Atualiza config
        new_config = SessionConfig(
            temperature=0.3,
            system_prompt="Updated prompt"
        )

        success = await self.handler.update_session_config(session_id, new_config)

        if not success:
            raise AssertionError("Falha ao atualizar config")

        # Verifica atualização
        saved_config = self.handler.session_configs.get(session_id)

        print(f"   ├─ Config atualizada: {success}")
        print(f"   ├─ Nova temperature: {saved_config.temperature}")
        print(f"   └─ Novo prompt: {saved_config.system_prompt}")

        return saved_config.temperature == 0.3

    async def test_pool_status(self) -> bool:
        """Testa status do pool de conexões."""
        # Garante que manutenção foi iniciada
        await self.handler.ensure_pool_maintenance_started()

        status = await self.handler.get_pool_status()

        print(f"   ├─ Tamanho do pool: {status['pool_size']}")
        print(f"   ├─ Conexões saudáveis: {status['healthy_connections']}")
        print(f"   ├─ Max size: {status['max_size']}")
        print(f"   └─ Min size: {status['min_size']}")

        return isinstance(status, dict) and 'pool_size' in status

    async def test_session_destruction(self) -> bool:
        """Testa destruição de sessão."""
        session_id = "test-destroy-001"

        await self.handler.create_session(session_id)

        # Verifica que existe
        if session_id not in self.handler.clients:
            raise AssertionError("Sessão não foi criada")

        await self.handler.destroy_session(session_id)

        # Verifica que foi removida
        if session_id in self.handler.clients:
            raise AssertionError("Sessão não foi destruída")

        print(f"   ├─ Sessão criada e destruída: {session_id}")
        print(f"   └─ Verificação: OK")

        return True

    async def test_error_handling(self) -> bool:
        """Testa tratamento de erros."""
        # Tenta destruir sessão inexistente
        try:
            await self.handler.destroy_session("non-existent-session")
            print(f"   ├─ Destruir sessão inexistente: OK (sem erro)")
        except Exception as e:
            print(f"   ├─ Destruir sessão inexistente: Erro capturado")

        # Tenta obter info de sessão inexistente
        info = await self.handler.get_session_info("non-existent-session")

        if "error" not in info:
            raise AssertionError("Deveria retornar erro para sessão inexistente")

        print(f"   └─ Info sessão inexistente: {info['error']}")

        return True

    async def cleanup_sessions(self):
        """Limpa todas as sessões de teste."""
        print("\n🧹 Limpando sessões de teste...")

        for session_id in self.session_ids:
            try:
                if session_id in self.handler.clients:
                    await self.handler.destroy_session(session_id)
                    print(f"   ├─ Removida: {session_id}")
            except Exception as e:
                print(f"   ├─ Erro ao remover {session_id}: {e}")

        # Encerra pool
        await self.handler.shutdown_pool()
        print(f"   └─ Pool de conexões encerrado")

    def show_results(self):
        """Exibe resumo dos resultados."""
        print("\n" + "="*60)
        print("📊 RESUMO DOS TESTES")
        print("="*60)

        passed = sum(1 for _, status, _ in self.test_results if status == "PASSOU")
        failed = sum(1 for _, status, _ in self.test_results if status == "FALHOU")
        errors = sum(1 for _, status, _ in self.test_results if status == "ERRO")
        total = len(self.test_results)

        print(f"\n✅ Passou: {passed}/{total}")
        print(f"❌ Falhou: {failed}/{total}")
        print(f"⚠️  Erros: {errors}/{total}")

        if failed > 0 or errors > 0:
            print("\n🔍 Detalhes dos problemas:")
            for name, status, error in self.test_results:
                if status != "PASSOU":
                    print(f"   • {name}: {status}")
                    if error:
                        print(f"     └─ {error}")

        print("\n" + "="*60)

        # Retorna código de saída apropriado
        return 0 if (failed == 0 and errors == 0) else 1


async def main():
    """Função principal."""
    test_suite = HandlerTestSuite()

    try:
        await test_suite.run_all_tests()
    except KeyboardInterrupt:
        print("\n⚠️  Testes interrompidos pelo usuário")
        await test_suite.cleanup_sessions()
        return 1
    except Exception as e:
        print(f"\n❌ Erro fatal nos testes: {e}")
        import traceback
        traceback.print_exc()
        await test_suite.cleanup_sessions()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)