"""
Rotas de WebSocket
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
import json
import asyncio

from core.websocket_handler import ws_manager
from core.command_stream import command_stream
from core.claude_handler import ClaudeHandler
from core.session_manager import ClaudeCodeSessionManager

router = APIRouter(tags=["websocket"])

# Inicializar handlers
claude_handler = ClaudeHandler()
session_manager = ClaudeCodeSessionManager()

@router.websocket("/ws/advanced/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint avançado para comunicação em tempo real.
    """
    await ws_manager.connect(websocket, session_id)

    try:
        while True:
            # Receber mensagem do cliente
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Processar diferentes tipos de mensagem
            message_type = message_data.get("type", "chat")

            if message_type == "chat":
                # Processar mensagem de chat
                message = message_data.get("message", "")

                async for chunk in claude_handler.send_message(session_id, message):
                    await ws_manager.send_personal_message(
                        json.dumps(chunk),
                        session_id
                    )

            elif message_type == "command":
                # Processar comando
                command = message_data.get("command", "")
                result = await command_stream.process_command(session_id, command)
                await ws_manager.send_personal_message(
                    json.dumps({"type": "command_result", "result": result}),
                    session_id
                )

            elif message_type == "ping":
                # Responder ao ping
                await ws_manager.send_personal_message(
                    json.dumps({"type": "pong"}),
                    session_id
                )

    except WebSocketDisconnect:
        ws_manager.disconnect(session_id)
        await ws_manager.broadcast(
            json.dumps({
                "type": "user_disconnected",
                "session_id": session_id
            })
        )

    except Exception as e:
        await ws_manager.send_personal_message(
            json.dumps({
                "type": "error",
                "error": str(e)
            }),
            session_id
        )
        ws_manager.disconnect(session_id)

@router.get("/api/stream/status/{session_id}")
async def stream_status(session_id: str):
    """Status do stream de comandos para uma sessão."""
    status = command_stream.get_session_status(session_id)
    if not status:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    return status

@router.post("/api/command/{session_id}")
async def execute_command(session_id: str, command: dict):
    """Executa comando via API REST."""
    try:
        command_type = command.get("type", "")
        command_data = command.get("data", {})

        result = await command_stream.process_command(
            session_id,
            command_type,
            **command_data
        )

        return {
            "session_id": session_id,
            "command": command_type,
            "result": result,
            "status": "success"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))