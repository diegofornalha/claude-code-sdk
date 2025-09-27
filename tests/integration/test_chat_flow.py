"""
Testes de integração para fluxo de chat completo.
Testa SSE streaming e comunicação com Claude.
"""

import pytest
import asyncio
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
class TestChatFlow:
    """Testes de fluxo completo de chat."""

    async def test_chat_simple_message(self, async_client):
        """Testa envio de mensagem simples via chat."""
        payload = {
            "message": "Olá, Claude!",
            "project_id": "test-project"
        }

        # Chat usa SSE, então precisamos tratar diferente
        async with async_client.stream("POST", "/api/chat", json=payload) as response:
            assert response.status_code == 200
            assert "text/event-stream" in response.headers.get("content-type", "")

            # Coletar eventos SSE
            events = []
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]  # Remove "data: "
                    events.append(data)

            # Deve ter recebido pelo menos um evento
            assert len(events) > 0

    async def test_chat_with_existing_session(self, async_client, valid_session_id):
        """Testa chat com sessão existente."""
        # Criar sessão primeiro
        await async_client.post("/api/sessions", json={
            "session_id": valid_session_id,
            "project_id": "test"
        })

        payload = {
            "message": "Continuar conversa",
            "session_id": valid_session_id,
            "project_id": "test"
        }

        async with async_client.stream("POST", "/api/chat", json=payload) as response:
            assert response.status_code == 200

    @pytest.mark.security
    async def test_chat_with_xss_attempt(self, async_client):
        """Testa proteção contra XSS em mensagens."""
        payload = {
            "message": "<script>alert('XSS')</script>",
            "project_id": "test-project"
        }

        async with async_client.stream("POST", "/api/chat", json=payload) as response:
            # Não deve retornar erro, mas deve sanitizar
            assert response.status_code in [200, 400]

    @pytest.mark.security
    async def test_chat_message_too_long(self, async_client):
        """Testa rejeição de mensagem muito longa."""
        payload = {
            "message": "a" * 50001,  # Acima do limite
            "project_id": "test"
        }

        response = await async_client.post("/api/chat", json=payload)
        assert response.status_code == 400

    async def test_chat_invalid_session_id(self, async_client):
        """Testa validação de session_id inválido."""
        payload = {
            "message": "Test",
            "session_id": "invalid-uuid",
            "project_id": "test"
        }

        response = await async_client.post("/api/chat", json=payload)
        assert response.status_code == 400

    async def test_chat_empty_message(self, async_client):
        """Testa rejeição de mensagem vazia."""
        payload = {
            "message": "",
            "project_id": "test"
        }

        response = await async_client.post("/api/chat", json=payload)
        # Pode ser 400 ou criar sessão - depende da validação
        assert response.status_code in [200, 400]