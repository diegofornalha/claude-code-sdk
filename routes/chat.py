"""
Rotas relacionadas ao chat
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, AsyncGenerator, Dict, Any
import asyncio
import json
import uuid
from datetime import datetime

from core.claude_handler import ClaudeHandler, SessionConfig
from core.input_validator import InputValidator, ValidationError, InputType
from utils.security_utils import sanitize_for_frontend

router = APIRouter(prefix="/api", tags=["chat"])

# Inicializar handlers
claude_handler = ClaudeHandler()
validator = InputValidator()

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    project_id: str = "neo4j-agent"

    def validate_and_sanitize(self):
        """Valida e sanitiza todos os campos"""
        self.message = validator.validate(self.message, InputType.MESSAGE)

        if self.session_id:
            self.session_id = validator.validate(self.session_id, InputType.SESSION_ID)

        self.project_id = validator.validate(self.project_id, InputType.PROJECT_ID)

        return self

@router.post("/chat")
async def chat_stream(chat_message: ChatMessage, request: Request):
    """
    Endpoint principal para chat com Claude via SSE.
    Usa o ClaudeHandler para processar mensagens.
    Inclui validação e sanitização de entrada.
    """

    # Validar e sanitizar entrada
    try:
        chat_message = chat_message.validate_and_sanitize()
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    async def generate_sse() -> AsyncGenerator[str, None]:
        """Gera eventos SSE para streaming."""

        try:
            # Criar ou recuperar sessão
            if not chat_message.session_id:
                session_id = str(uuid.uuid4())
                # Criar nova sessão
                session_config = SessionConfig(
                    project_id=chat_message.project_id,
                    temperature=0.7,
                    model="claude-3-5-sonnet-20241022"
                )
                await claude_handler.create_session(session_id, session_config)

                # Notificar criação de sessão
                yield f"data: {json.dumps({'type': 'session_created', 'session_id': session_id})}\n\n"
            else:
                session_id = chat_message.session_id

            # Processar mensagem com Claude Handler
            async for chunk in claude_handler.send_message(session_id, chat_message.message):
                # Sanitizar conteúdo antes de enviar
                if 'content' in chunk:
                    chunk['content'] = sanitize_for_frontend(chunk['content'])
                if 'text' in chunk:
                    chunk['text'] = sanitize_for_frontend(chunk['text'])

                # Enviar chunk via SSE
                yield f"data: {json.dumps(chunk)}\n\n"

                # Pequena pausa para streaming suave
                await asyncio.sleep(0.01)

            # Evento final
            yield f"data: {json.dumps({'type': 'done', 'session_id': session_id})}\n\n"

        except Exception as e:
            # Enviar erro via SSE
            error_data = {
                "type": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(error_data)}\n\n"

    # Retornar streaming response
    return StreamingResponse(
        generate_sse(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.get("/capabilities")
async def get_capabilities():
    """
    Retorna as capacidades do SDK e do sistema.
    """
    capabilities = {
        "sdk": {
            "name": "Claude Code SDK API",
            "version": "1.1.0",
            "provider": "Anthropic (via SDK)",
            "features": [
                "chat",
                "streaming",
                "memory",
                "sessions",
                "neo4j-integration",
                "metrics",
                "health-checks",
                "query-analysis"
            ]
        },
        "models": [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-5-haiku-20241022"
        ],
        "integrations": {
            "neo4j": {
                "enabled": True,
                "version": "5.x",
                "features": [
                    "graph-statistics",
                    "path-finding",
                    "centrality-analysis",
                    "similarity-search",
                    "subgraph-extraction"
                ]
            },
            "websocket": {
                "enabled": True,
                "features": ["real-time-chat", "session-management"]
            },
            "metrics": {
                "enabled": True,
                "features": ["performance-tracking", "query-analysis", "health-monitoring"]
            }
        },
        "limits": {
            "max_message_length": 50000,
            "max_session_memory": 100,
            "rate_limit": "60 requests/minute",
            "max_file_size": "10MB"
        }
    }
    return capabilities