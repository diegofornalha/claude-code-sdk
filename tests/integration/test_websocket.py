"""
Testes de integração para WebSocket.
Testa comunicação bidirecional em tempo real.
"""

import pytest
import asyncio
import json
from fastapi.testclient import TestClient


@pytest.mark.integration
@pytest.mark.websocket
class TestWebSocket:
    """Suite de testes para WebSocket."""

    def test_websocket_connection(self, test_client, valid_session_id):
        """Testa conexão WebSocket básica."""
        with test_client.websocket_connect(f"/ws/advanced/{valid_session_id}") as websocket:
            # Conexão estabelecida com sucesso
            assert websocket is not None

    def test_websocket_send_query(self, test_client, valid_session_id):
        """Testa envio de query via WebSocket."""
        with test_client.websocket_connect(f"/ws/advanced/{valid_session_id}") as websocket:
            # Enviar query
            websocket.send_json({
                "type": "query",
                "message": "Olá via WebSocket"
            })

            # Receber resposta de processamento
            data = websocket.receive_json()
            assert data["type"] in ["processing", "content", "done"]

    def test_websocket_receive_streaming(self, test_client, valid_session_id):
        """Testa recebimento de streaming via WebSocket."""
        with test_client.websocket_connect(f"/ws/advanced/{valid_session_id}") as websocket:
            websocket.send_json({
                "type": "query",
                "message": "Teste streaming"
            })

            # Coletar múltiplas respostas
            responses = []
            for _ in range(5):
                try:
                    data = websocket.receive_json(timeout=2)
                    responses.append(data)
                    if data.get("type") == "done":
                        break
                except:
                    break

            assert len(responses) > 0

    def test_websocket_disconnect(self, test_client, valid_session_id):
        """Testa desconexão WebSocket."""
        with test_client.websocket_connect(f"/ws/advanced/{valid_session_id}") as websocket:
            websocket.send_json({
                "type": "query",
                "message": "Test"
            })
            # WebSocket fecha automaticamente ao sair do context manager

    @pytest.mark.slow
    def test_websocket_concurrent_connections(self, test_client):
        """Testa múltiplas conexões WebSocket simultâneas."""
        session_ids = [
            f"12345678-1234-1234-1234-12345678900{i}"
            for i in range(3)
        ]

        # Abrir múltiplas conexões
        connections = []
        for sid in session_ids:
            ws = test_client.websocket_connect(f"/ws/advanced/{sid}")
            connections.append(ws.__enter__())

        # Todas devem estar conectadas
        assert len(connections) == 3

        # Fechar todas
        for ws in connections:
            ws.__exit__(None, None, None)