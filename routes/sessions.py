"""
Rotas relacionadas a sessões
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from core.claude_handler import ClaudeHandler, SessionConfig
from core.session_manager import ClaudeCodeSessionManager
from core.input_validator import InputValidator, ValidationError

router = APIRouter(prefix="/api", tags=["sessions"])

# Inicializar handlers
claude_handler = ClaudeHandler()
session_manager = ClaudeCodeSessionManager()
validator = InputValidator()

class SessionCreate(BaseModel):
    session_id: Optional[str] = None
    project_id: str = "neo4j-agent"
    config: Dict[str, Any] = {}

    def validate_and_sanitize(self):
        """Valida e sanitiza todos os campos"""
        if self.session_id:
            self.session_id = validator.validate_session_id(self.session_id)

        self.project_id = validator.validate_project_id(self.project_id)
        self.config = validator.validate_dict(self.config, "config")

        return self

@router.post("/sessions")
async def create_session(session_create: SessionCreate):
    """Cria uma nova sessão de chat."""

    # Validar e sanitizar entrada
    try:
        session_create = session_create.validate_and_sanitize()
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Usa o session_id fornecido se válido, senão gera novo
    session_id = session_create.session_id if session_create.session_id else str(uuid.uuid4())

    try:
        # Configurar sessão
        session_config = SessionConfig(
            project_id=session_create.project_id,
            **session_create.config
        )

        # Criar sessão no handler
        await claude_handler.create_session(session_id, session_config)

        # Registrar no session manager
        session_manager.create_session(
            session_id=session_id,
            project_id=session_create.project_id
        )

        return {
            "session_id": session_id,
            "project_id": session_create.project_id,
            "status": "created",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
async def list_sessions():
    """Lista todas as sessões ativas."""

    active_sessions = session_manager.get_active_sessions()

    return {
        "sessions": [
            {
                "session_id": session_id,
                "project_id": session.project_id,
                "created_at": session.created_at.isoformat(),
                "messages_count": len(session.messages)
            }
            for session_id, session in active_sessions.items()
        ],
        "total": len(active_sessions)
    }

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Deleta uma sessão específica."""

    # Validar session_id
    try:
        session_id = validator.validate_session_id(session_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        # Remover do handler
        if hasattr(claude_handler, 'close_session'):
            await claude_handler.close_session(session_id)

        # Remover do session manager
        session_manager.close_session(session_id)

        return {
            "session_id": session_id,
            "status": "deleted",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sdk-status")
async def sdk_status():
    """Retorna o status do SDK e da API."""

    status = {
        "api": {
            "status": "online",
            "version": "1.1.0",
            "timestamp": datetime.now().isoformat()
        },
        "sdk": {
            "status": "active",
            "provider": "Claude Code SDK"
        },
        "sessions": {
            "active": len(session_manager.get_active_sessions()),
            "handler_pool": {
                "created": claude_handler.pool_status.get('created', 0),
                "closed": claude_handler.pool_status.get('closed', 0),
                "errors": claude_handler.pool_status.get('errors', 0)
            } if hasattr(claude_handler, 'pool_status') else {}
        }
    }

    return status