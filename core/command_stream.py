"""
Stream de comandos e status via SSE
Permite que clientes recebam atualizações de status em tempo real
"""

import asyncio
import json
from typing import AsyncGenerator, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class CommandStreamManager:
    """Gerenciador de streams de comandos e status."""

    def __init__(self):
        self.status_queues: Dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    async def create_status_stream(self, session_id: str) -> AsyncGenerator[str, None]:
        """Cria um stream SSE para status e comandos."""
        queue = self.status_queues[session_id]
        self.active_sessions[session_id] = {
            "connected": True,
            "started_at": datetime.utcnow().isoformat()
        }

        try:
            # Envia status inicial
            yield self._format_sse({
                "type": "connected",
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            })

            # Loop principal do stream
            while self.active_sessions.get(session_id, {}).get("connected"):
                try:
                    # Aguarda por novos status/comandos
                    status = await asyncio.wait_for(queue.get(), timeout=30.0)

                    if status is None:  # Sinal para fechar
                        break

                    yield self._format_sse(status)

                except asyncio.TimeoutError:
                    # Envia heartbeat para manter conexão viva
                    yield self._format_sse({
                        "type": "heartbeat",
                        "timestamp": datetime.utcnow().isoformat()
                    })

        except asyncio.CancelledError:
            logger.info(f"Stream de status cancelado: {session_id}")
        finally:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            if session_id in self.status_queues:
                del self.status_queues[session_id]

    def _format_sse(self, data: Dict[str, Any]) -> str:
        """Formata dados para SSE."""
        return f"data: {json.dumps(data)}\n\n"

    async def send_status(self, session_id: str, status_type: str, data: Optional[Dict] = None):
        """Envia status para o stream de uma sessão."""
        if session_id not in self.status_queues:
            return

        status_message = {
            "type": status_type,
            "timestamp": datetime.utcnow().isoformat()
        }

        if data:
            status_message.update(data)

        await self.status_queues[session_id].put(status_message)

    async def send_thinking_status(self, session_id: str):
        """Indica que o Claude está pensando."""
        await self.send_status(session_id, "thinking", {
            "message": "Claude está processando sua mensagem..."
        })

    async def send_neo4j_status(self, session_id: str, operation: str):
        """Indica operação no Neo4j."""
        await self.send_status(session_id, "neo4j_operation", {
            "operation": operation,
            "message": f"Executando {operation} no Neo4j..."
        })

    async def send_processing_status(self, session_id: str, step: str, progress: Optional[float] = None):
        """Indica progresso de processamento."""
        status_data = {
            "step": step,
            "message": f"Processando: {step}"
        }

        if progress is not None:
            status_data["progress"] = progress

        await self.send_status(session_id, "processing", status_data)

    async def send_error_status(self, session_id: str, error: str):
        """Envia status de erro."""
        await self.send_status(session_id, "error", {
            "error": error,
            "recoverable": True
        })

    async def send_completion_status(self, session_id: str, stats: Optional[Dict] = None):
        """Indica conclusão do processamento."""
        status_data = {
            "message": "Processamento concluído"
        }

        if stats:
            status_data["stats"] = stats

        await self.send_status(session_id, "completed", status_data)

    async def close_stream(self, session_id: str):
        """Fecha o stream de uma sessão."""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["connected"] = False

        if session_id in self.status_queues:
            await self.status_queues[session_id].put(None)


# Singleton para gerenciar todos os streams
command_stream = CommandStreamManager()