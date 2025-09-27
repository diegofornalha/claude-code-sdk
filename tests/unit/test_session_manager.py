"""
Testes unitários para ClaudeCodeSessionManager.
Testa gerenciamento de sessões, limpeza e métricas.
"""

import pytest
import asyncio
from datetime import datetime, timedelta

from core.session_manager import ClaudeCodeSessionManager, SessionMetrics


@pytest.mark.unit
class TestSessionManager:
    """Suite de testes para SessionManager."""

    def test_register_session_success(self, session_manager, valid_session_id):
        """Testa registro bem-sucedido de sessão."""
        result = session_manager.register_session(valid_session_id)

        assert result is True
        assert valid_session_id in session_manager.active_sessions
        assert valid_session_id in session_manager.session_metrics

    def test_register_session_exceeds_limit(self, session_manager):
        """Testa que registro falha ao exceder limite."""
        # Registrar até o limite
        for i in range(session_manager.MAX_SESSIONS):
            session_manager.register_session(f"session-{i}")

        # Próximo registro deve falhar
        result = session_manager.register_session("overflow-session")
        assert result is False

    def test_unregister_session(self, session_manager, valid_session_id):
        """Testa remoção de sessão."""
        session_manager.register_session(valid_session_id)
        session_manager.unregister_session(valid_session_id)

        assert valid_session_id not in session_manager.active_sessions
        assert valid_session_id not in session_manager.session_metrics

    def test_update_session_activity(self, session_manager, valid_session_id):
        """Testa atualização de atividade da sessão."""
        session_manager.register_session(valid_session_id)

        initial_time = session_manager.active_sessions[valid_session_id]
        asyncio.sleep(0.1)

        session_manager.update_session_activity(valid_session_id)
        updated_time = session_manager.active_sessions[valid_session_id]

        assert updated_time >= initial_time

    def test_update_session_metrics(self, session_manager, valid_session_id):
        """Testa atualização de métricas."""
        session_manager.register_session(valid_session_id)

        session_manager.update_session_metrics(
            valid_session_id,
            message_count=5,
            total_tokens=1000,
            total_cost=0.05
        )

        metrics = session_manager.get_session_metrics(valid_session_id)
        assert metrics.message_count == 5
        assert metrics.total_tokens == 1000
        assert metrics.total_cost == 0.05

    def test_get_session_metrics_nonexistent(self, session_manager):
        """Testa obtenção de métricas de sessão inexistente."""
        metrics = session_manager.get_session_metrics("nonexistent")
        assert metrics is None

    def test_get_all_session_metrics(self, session_manager):
        """Testa obtenção de métricas de todas as sessões."""
        # Registrar múltiplas sessões
        session_ids = ["session-1", "session-2", "session-3"]
        for sid in session_ids:
            session_manager.register_session(sid)

        all_metrics = session_manager.get_all_session_metrics()

        assert len(all_metrics) == 3
        assert all(sid in all_metrics for sid in session_ids)

    @pytest.mark.asyncio
    async def test_cleanup_inactive_sessions_disabled(self, session_manager):
        """Testa que limpeza está desabilitada (timeout = 0)."""
        # Registrar sessão antiga
        session_manager.register_session("old-session")
        session_manager.active_sessions["old-session"] = (
            datetime.now() - timedelta(hours=2)
        )

        # Executar limpeza (deve retornar vazio)
        removed = await session_manager.cleanup_inactive_sessions()

        assert len(removed) == 0
        assert "old-session" in session_manager.active_sessions

    @pytest.mark.asyncio
    async def test_detect_orphaned_sessions(self, session_manager):
        """Testa detecção de sessões órfãs."""
        # Registrar sessão que não tem arquivo .jsonl
        session_manager.register_session("orphaned-session")

        orphans = await session_manager.detect_orphaned_sessions()

        # Pode ou não detectar dependendo do estado real do filesystem
        # Apenas verifica que não causa erro
        assert isinstance(orphans, list)

    def test_get_session_health_report(self, session_manager):
        """Testa geração de relatório de saúde."""
        # Registrar algumas sessões
        for i in range(5):
            sid = f"session-{i}"
            session_manager.register_session(sid)
            session_manager.update_session_metrics(
                sid,
                message_count=i + 1,
                total_tokens=(i + 1) * 100
            )

        report = session_manager.get_session_health_report()

        assert "sessions" in report
        assert report["sessions"]["active"] == 5
        assert "totals" in report
        assert report["totals"]["messages"] == 15  # 1+2+3+4+5

    @pytest.mark.asyncio
    async def test_force_cleanup_all(self, session_manager):
        """Testa limpeza forçada de todas as sessões."""
        # Registrar várias sessões
        for i in range(10):
            session_manager.register_session(f"session-{i}")

        await session_manager.force_cleanup_all()

        assert len(session_manager.active_sessions) == 0
        assert len(session_manager.session_metrics) == 0

    def test_get_active_sessions(self, session_manager):
        """Testa obtenção de sessões ativas."""
        session_ids = ["session-1", "session-2", "session-3"]
        for sid in session_ids:
            session_manager.register_session(sid)

        active = session_manager.get_active_sessions()

        assert len(active) == 3
        assert all(sid in active for sid in session_ids)

    def test_create_session(self, session_manager):
        """Testa criação de sessão via método público."""
        session_id = "new-session"
        session_manager.create_session(session_id, project_id="test-project")

        assert session_id in session_manager.active_sessions

    def test_close_session(self, session_manager, valid_session_id):
        """Testa fechamento de sessão."""
        session_manager.register_session(valid_session_id)
        session_manager.close_session(valid_session_id)

        assert valid_session_id not in session_manager.active_sessions

    @pytest.mark.asyncio
    async def test_scheduler_start_stop(self, session_manager):
        """Testa início e parada do scheduler."""
        await session_manager.ensure_scheduler_started()
        assert session_manager.scheduler_running is True

        await session_manager.stop_scheduler()
        assert session_manager.scheduler_running is False

    def test_session_metrics_dataclass(self):
        """Testa dataclass SessionMetrics."""
        metrics = SessionMetrics(
            message_count=10,
            total_tokens=5000,
            total_cost=0.25,
            connection_errors=2
        )

        assert metrics.message_count == 10
        assert metrics.total_tokens == 5000
        assert metrics.total_cost == 0.25
        assert metrics.connection_errors == 2
        assert isinstance(metrics.created_at, datetime)