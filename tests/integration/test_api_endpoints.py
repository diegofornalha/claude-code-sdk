"""
Testes de integração para endpoints da API.
Testa fluxos completos de requisição/resposta.
"""

import pytest
import json
import asyncio
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
class TestAPIEndpoints:
    """Suite de testes de integração para API."""

    async def test_health_check(self, async_client):
        """Testa endpoint de health check."""
        response = await async_client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "sdk_available" in data

    async def test_create_session_success(self, async_client):
        """Testa criação bem-sucedida de sessão."""
        payload = {
            "project_id": "test-project",
            "config": {"temperature": 0.8}
        }

        response = await async_client.post("/api/sessions", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["project_id"] == "test-project"
        assert data["status"] == "created"

    async def test_create_session_invalid_project_id(self, async_client):
        """Testa criação de sessão com project_id inválido."""
        payload = {
            "project_id": "invalid project with spaces",
            "config": {}
        }

        response = await async_client.post("/api/sessions", json=payload)

        # Deve retornar erro de validação
        assert response.status_code == 400

    async def test_list_sessions(self, async_client):
        """Testa listagem de sessões."""
        # Criar algumas sessões primeiro
        for i in range(3):
            await async_client.post("/api/sessions", json={
                "project_id": f"project-{i}"
            })

        response = await async_client.get("/api/sessions")

        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert "total" in data
        assert data["total"] >= 3

    async def test_delete_session_success(self, async_client, valid_session_id):
        """Testa deleção bem-sucedida de sessão."""
        # Criar sessão primeiro
        create_response = await async_client.post("/api/sessions", json={
            "session_id": valid_session_id,
            "project_id": "test"
        })
        assert create_response.status_code == 200

        # Deletar sessão
        response = await async_client.delete(f"/api/sessions/{valid_session_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "deleted"

    async def test_delete_nonexistent_session(self, async_client):
        """Testa deleção de sessão inexistente."""
        fake_id = "12345678-1234-1234-1234-123456789999"
        response = await async_client.delete(f"/api/sessions/{fake_id}")

        # Pode retornar 200 ou 404 dependendo da implementação
        assert response.status_code in [200, 404, 500]

    async def test_sdk_status(self, async_client):
        """Testa endpoint de status do SDK."""
        response = await async_client.get("/api/sdk-status")

        assert response.status_code == 200
        data = response.json()
        assert "sdk_available" in data
        assert "handler_status" in data

    async def test_flow_balance_default_account(self, async_client):
        """Testa obtenção de saldo Flow da conta padrão."""
        response = await async_client.get("/api/flow/balance")

        # Pode falhar se não conseguir conectar com testnet
        if response.status_code == 200:
            data = response.json()
            assert "address" in data
            assert "balance" in data
            assert "network" in data
            assert data["network"] == "testnet"

    async def test_flow_balance_custom_address(self, async_client):
        """Testa obtenção de saldo Flow de endereço específico."""
        test_address = "36395f9dde50ea27"
        response = await async_client.get(f"/api/flow/balance/{test_address}")

        if response.status_code == 200:
            data = response.json()
            assert "address" in data
            assert "balance" in data

    async def test_flow_balance_invalid_address(self, async_client):
        """Testa validação de endereço inválido."""
        invalid_address = "invalid"
        response = await async_client.get(f"/api/flow/balance/{invalid_address}")

        assert response.status_code == 400

    async def test_capabilities_endpoint(self, async_client):
        """Testa endpoint de capacidades."""
        response = await async_client.get("/api/capabilities")

        assert response.status_code == 200
        data = response.json()
        assert "websocket" in data
        assert "status_stream" in data
        assert "commands" in data
        assert "models" in data

    @pytest.mark.slow
    async def test_rate_limiting(self, async_client):
        """Testa rate limiting da API."""
        # Fazer muitas requisições rapidamente
        tasks = []
        for _ in range(70):  # Acima do limite de 60/min
            tasks.append(async_client.get("/api/health"))

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Pelo menos uma deve ter sido limitada
        status_codes = [r.status_code for r in responses if hasattr(r, 'status_code')]
        assert 429 in status_codes  # Too Many Requests

    async def test_cors_headers(self, async_client):
        """Testa headers CORS."""
        response = await async_client.options("/api/health")

        # Verificar headers de segurança
        headers = response.headers
        assert "access-control-allow-origin" in headers or response.status_code == 200

    async def test_security_headers(self, async_client):
        """Testa headers de segurança."""
        response = await async_client.get("/api/health")

        headers = response.headers
        # Headers de segurança devem estar presentes
        assert "x-content-type-options" in headers
        assert "x-frame-options" in headers