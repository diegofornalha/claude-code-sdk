"""
Configuração global de testes pytest.
Fixtures compartilhadas entre todos os testes.
"""

import pytest
import asyncio
import sys
import os
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock, MagicMock
from datetime import datetime

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from httpx import AsyncClient

# Importar módulos da API
from server import app
from core.claude_handler import ClaudeHandler, SessionConfig
from core.session_manager import ClaudeCodeSessionManager
from core.input_validator import InputValidator


# ============================================
# FIXTURES DE CONFIGURAÇÃO
# ============================================

@pytest.fixture(scope="session")
def event_loop():
    """Cria event loop para testes async."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    """Cliente de teste para FastAPI."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Cliente async para testes de integração."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# ============================================
# FIXTURES DE MOCK
# ============================================

@pytest.fixture
def mock_claude_client():
    """Mock do ClaudeSDKClient."""
    mock = AsyncMock()
    mock.connect = AsyncMock()
    mock.disconnect = AsyncMock()
    mock.query = AsyncMock()
    mock.receive_response = AsyncMock()
    mock.interrupt = AsyncMock()
    return mock


@pytest.fixture
def mock_neo4j_driver():
    """Mock do driver Neo4j."""
    mock = MagicMock()
    session_mock = MagicMock()
    mock.session.return_value = session_mock
    session_mock.__enter__ = MagicMock(return_value=session_mock)
    session_mock.__exit__ = MagicMock(return_value=None)
    return mock


@pytest.fixture
def mock_session_manager():
    """Mock do SessionManager."""
    manager = Mock(spec=ClaudeCodeSessionManager)
    manager.register_session = Mock(return_value=True)
    manager.unregister_session = Mock()
    manager.update_session_activity = Mock()
    manager.get_active_sessions = Mock(return_value={})
    manager.get_session_metrics = Mock(return_value=None)
    manager.update_session_metrics = Mock()
    return manager


# ============================================
# FIXTURES DE INSTÂNCIAS
# ============================================

@pytest.fixture
async def claude_handler(mock_session_manager):
    """Instância de ClaudeHandler para testes."""
    handler = ClaudeHandler()
    handler.session_manager = mock_session_manager
    yield handler
    # Cleanup
    await handler.shutdown_pool()


@pytest.fixture
def session_manager():
    """Instância de SessionManager para testes."""
    return ClaudeCodeSessionManager()


@pytest.fixture
def input_validator():
    """Instância de InputValidator para testes."""
    return InputValidator()


# ============================================
# FIXTURES DE DADOS DE TESTE
# ============================================

@pytest.fixture
def valid_session_id() -> str:
    """ID de sessão válido para testes."""
    return "12345678-1234-1234-1234-123456789abc"


@pytest.fixture
def valid_project_id() -> str:
    """ID de projeto válido."""
    return "neo4j-agent"


@pytest.fixture
def sample_chat_message() -> dict:
    """Mensagem de chat válida."""
    return {
        "message": "Olá, como você está?",
        "session_id": "12345678-1234-1234-1234-123456789abc",
        "project_id": "neo4j-agent"
    }


@pytest.fixture
def sample_session_config() -> SessionConfig:
    """Configuração de sessão de exemplo."""
    return SessionConfig(
        project_id="neo4j-agent",
        temperature=0.7,
        model="claude-3-5-sonnet-20241022",
        permission_mode="bypassPermissions"
    )


@pytest.fixture
def malicious_inputs() -> list:
    """Lista de entradas maliciosas para testes de segurança."""
    return [
        "<script>alert('XSS')</script>",
        "'; DROP TABLE users; --",
        "../../../etc/passwd",
        "javascript:alert(1)",
        "<iframe src='evil.com'></iframe>",
        "' OR '1'='1",
        "%00null byte",
        "{{7*7}}",  # Template injection
        "${7*7}",   # Template injection
        "../../sensitive.env"
    ]


# ============================================
# FIXTURES DE CLEANUP
# ============================================

@pytest.fixture(autouse=True)
async def cleanup_sessions(claude_handler):
    """Limpa sessões após cada teste."""
    yield
    # Cleanup após teste
    for session_id in list(claude_handler.clients.keys()):
        try:
            await claude_handler.destroy_session(session_id)
        except:
            pass


# ============================================
# HELPERS
# ============================================

@pytest.fixture
def assert_async_call():
    """Helper para verificar chamadas async."""
    def _assert(mock, *args, **kwargs):
        mock.assert_called_once()
        if args or kwargs:
            mock.assert_called_with(*args, **kwargs)
    return _assert


@pytest.fixture
def wait_for_condition():
    """Helper para esperar condição async."""
    async def _wait(condition_func, timeout=5.0, interval=0.1):
        elapsed = 0
        while elapsed < timeout:
            if await condition_func():
                return True
            await asyncio.sleep(interval)
            elapsed += interval
        return False
    return _wait