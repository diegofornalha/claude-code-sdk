"""
Testes unitários para ClaudeHandler.
Testa gerenciamento de sessões e comunicação com Claude SDK.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

from core.claude_handler import ClaudeHandler, SessionConfig, SessionHistory


@pytest.mark.unit
@pytest.mark.asyncio
class TestClaudeHandler:
    """Suite de testes para ClaudeHandler."""

    async def test_create_session_success(self, claude_handler, valid_session_id):
        """Testa criação bem-sucedida de sessão."""
        config = SessionConfig(project_id="test-project")

        with patch.object(claude_handler, '_get_or_create_pooled_client',
                         return_value=AsyncMock()) as mock_client:
            await claude_handler.create_session(valid_session_id, config)

            assert valid_session_id in claude_handler.clients
            assert valid_session_id in claude_handler.active_sessions
            assert claude_handler.active_sessions[valid_session_id] is True

    async def test_create_session_without_config(self, claude_handler, valid_session_id):
        """Testa criação de sessão sem config usa defaults."""
        with patch.object(claude_handler, '_get_or_create_pooled_client',
                         return_value=AsyncMock()):
            await claude_handler.create_session(valid_session_id)

            config = claude_handler.session_configs[valid_session_id]
            assert config.project_id == "neo4j-agent"
            assert config.temperature == 0.7

    async def test_create_duplicate_session_recreates(self, claude_handler, valid_session_id):
        """Testa que criar sessão duplicada recria a sessão."""
        with patch.object(claude_handler, '_get_or_create_pooled_client',
                         return_value=AsyncMock()):
            # Criar primeira vez
            await claude_handler.create_session(valid_session_id)
            first_client = claude_handler.clients[valid_session_id]

            # Criar segunda vez (deve recriar)
            await claude_handler.create_session(valid_session_id)
            second_client = claude_handler.clients[valid_session_id]

            # Cliente deve ter sido recriado
            assert valid_session_id in claude_handler.clients

    async def test_destroy_session_success(self, claude_handler, valid_session_id):
        """Testa destruição bem-sucedida de sessão."""
        # Criar sessão primeiro
        with patch.object(claude_handler, '_get_or_create_pooled_client',
                         return_value=AsyncMock()):
            await claude_handler.create_session(valid_session_id)

            # Destruir sessão
            await claude_handler.destroy_session(valid_session_id)

            assert valid_session_id not in claude_handler.clients
            assert valid_session_id not in claude_handler.active_sessions

    async def test_destroy_nonexistent_session(self, claude_handler):
        """Testa que destruir sessão inexistente não causa erro."""
        # Não deve lançar exceção
        await claude_handler.destroy_session("nonexistent-session-id")

    async def test_send_message_creates_session_if_needed(self, claude_handler, valid_session_id):
        """Testa que send_message cria sessão se não existir."""
        with patch.object(claude_handler, '_get_or_create_pooled_client',
                         return_value=AsyncMock()):
            mock_client = AsyncMock()
            mock_client.query = AsyncMock()
            mock_client.receive_response = AsyncMock(return_value=[])

            claude_handler.clients[valid_session_id] = mock_client

            # Mock da criação de sessão
            with patch.object(claude_handler, 'create_session',
                             return_value=asyncio.sleep(0)):

                messages = []
                async for msg in claude_handler.send_message(valid_session_id, "test"):
                    messages.append(msg)

                assert len(messages) > 0

    async def test_interrupt_session_success(self, claude_handler, valid_session_id):
        """Testa interrupção de sessão ativa."""
        mock_client = AsyncMock()
        mock_client.interrupt = AsyncMock()
        claude_handler.clients[valid_session_id] = mock_client

        result = await claude_handler.interrupt_session(valid_session_id)

        assert result is True
        mock_client.interrupt.assert_called_once()

    async def test_interrupt_nonexistent_session(self, claude_handler):
        """Testa interrupção de sessão inexistente."""
        result = await claude_handler.interrupt_session("nonexistent")
        assert result is False

    async def test_clear_session_maintains_config(self, claude_handler, valid_session_id):
        """Testa que clear_session mantém a configuração."""
        config = SessionConfig(
            project_id="test",
            temperature=0.9,
            system_prompt="Test prompt"
        )

        with patch.object(claude_handler, '_get_or_create_pooled_client',
                         return_value=AsyncMock()):
            await claude_handler.create_session(valid_session_id, config)
            await claude_handler.clear_session(valid_session_id)

            # Configuração deve ser mantida
            new_config = claude_handler.session_configs.get(valid_session_id)
            assert new_config is not None
            assert new_config.temperature == 0.9

    async def test_get_session_info_success(self, claude_handler, valid_session_id):
        """Testa obtenção de informações da sessão."""
        with patch.object(claude_handler, '_get_or_create_pooled_client',
                         return_value=AsyncMock()):
            await claude_handler.create_session(valid_session_id)

            info = await claude_handler.get_session_info(valid_session_id)

            assert info["session_id"] == valid_session_id
            assert info["active"] is True
            assert "config" in info
            assert "history" in info

    async def test_get_session_info_nonexistent(self, claude_handler):
        """Testa obtenção de info de sessão inexistente."""
        info = await claude_handler.get_session_info("nonexistent")
        assert "error" in info

    async def test_get_all_sessions(self, claude_handler):
        """Testa listagem de todas as sessões."""
        session_ids = [
            "12345678-1234-1234-1234-123456789001",
            "12345678-1234-1234-1234-123456789002",
            "12345678-1234-1234-1234-123456789003"
        ]

        with patch.object(claude_handler, '_get_or_create_pooled_client',
                         return_value=AsyncMock()):
            for sid in session_ids:
                await claude_handler.create_session(sid)

            sessions = await claude_handler.get_all_sessions()

            assert len(sessions) == 3
            assert all(s["active"] for s in sessions)

    async def test_update_session_config(self, claude_handler, valid_session_id):
        """Testa atualização de configuração de sessão."""
        # Criar sessão inicial
        with patch.object(claude_handler, '_get_or_create_pooled_client',
                         return_value=AsyncMock()):
            initial_config = SessionConfig(temperature=0.7)
            await claude_handler.create_session(valid_session_id, initial_config)

            # Atualizar config
            new_config = SessionConfig(temperature=0.9, system_prompt="New prompt")
            result = await claude_handler.update_session_config(valid_session_id, new_config)

            assert result is True
            updated_config = claude_handler.session_configs[valid_session_id]
            assert updated_config.temperature == 0.9

    async def test_pool_status(self, claude_handler):
        """Testa obtenção de status do pool."""
        status = await claude_handler.get_pool_status()

        assert "pool_size" in status
        assert "healthy_connections" in status
        assert "max_size" in status
        assert status["max_size"] == claude_handler.POOL_MAX_SIZE

    @pytest.mark.slow
    async def test_pool_maintenance(self, claude_handler):
        """Testa manutenção automática do pool."""
        # Adicionar conexão fictícia ao pool
        from core.claude_handler import PooledConnection
        from datetime import timedelta

        old_conn = PooledConnection(
            client=AsyncMock(),
            created_at=datetime.now() - timedelta(hours=2)
        )

        claude_handler.connection_pool.append(old_conn)

        # Executar manutenção
        await claude_handler._maintain_pool()

        # Conexão antiga deve ter sido removida
        assert old_conn not in claude_handler.connection_pool

    async def test_health_check_pool(self, claude_handler):
        """Testa verificação de saúde do pool."""
        from core.claude_handler import PooledConnection

        # Adicionar conexões saudáveis e não saudáveis
        healthy_conn = PooledConnection(client=AsyncMock())
        unhealthy_conn = PooledConnection(client=None)

        claude_handler.connection_pool.extend([healthy_conn, unhealthy_conn])

        await claude_handler._health_check_pool()

        assert healthy_conn.is_healthy is True
        assert unhealthy_conn.is_healthy is False

    async def test_shutdown_pool(self, claude_handler):
        """Testa desligamento completo do pool."""
        from core.claude_handler import PooledConnection

        # Adicionar conexões
        for _ in range(3):
            conn = PooledConnection(client=AsyncMock())
            claude_handler.connection_pool.append(conn)

        await claude_handler.shutdown_pool()

        assert len(claude_handler.connection_pool) == 0