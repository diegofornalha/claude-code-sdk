#!/usr/bin/env python3
"""
MCP Proxy para Claude Code SDK
Este servidor MCP expõe o Claude Code SDK real via ferramentas MCP
Permite que aplicações web usem o SDK indiretamente
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

# MCP Server framework
from mcp import Server, Tool
from mcp.types import TextContent, ToolResult

# Claude Code SDK (disponível dentro do Claude Code)
try:
    from claude_code_sdk import query, ClaudeSDKClient, ClaudeCodeOptions
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    print("⚠️ Claude Code SDK não disponível - modo simulado")

# Criar servidor MCP
server = Server("claude-proxy-mcp")

# Armazenar sessões de chat
chat_sessions: Dict[str, Any] = {}

@server.tool(
    name="claude_query",
    description="Envia uma query simples para Claude Code SDK (stateless)",
    input_schema={
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Pergunta ou comando para o Claude"
            },
            "temperature": {
                "type": "number",
                "description": "Temperatura (0.0 a 1.0)",
                "default": 0.7
            },
            "model": {
                "type": "string",
                "description": "Modelo do Claude",
                "default": "claude-3-5-sonnet-20241022"
            }
        },
        "required": ["prompt"]
    }
)
async def claude_query_tool(args: Dict[str, Any]) -> ToolResult:
    """
    Ferramenta MCP para query stateless usando Claude Code SDK
    """
    prompt = args.get("prompt", "")
    temperature = args.get("temperature", 0.7)
    model = args.get("model", "claude-3-5-sonnet-20241022")

    if not SDK_AVAILABLE:
        return ToolResult(
            content=[TextContent(
                type="text",
                text="Claude Code SDK não disponível neste ambiente. Execute dentro do Claude Code."
            )]
        )

    try:
        # Usar Claude Code SDK REAL
        response_text = ""
        async for msg in query(
            prompt,
            options=ClaudeCodeOptions(
                model=model,
                temperature=temperature
            )
        ):
            if hasattr(msg, 'result'):
                response_text += msg.result
            elif hasattr(msg, 'content'):
                response_text += msg.content
            else:
                response_text += str(msg)

        return ToolResult(
            content=[TextContent(
                type="text",
                text=response_text
            )]
        )

    except Exception as e:
        return ToolResult(
            content=[TextContent(
                type="text",
                text=f"Erro ao usar Claude Code SDK: {str(e)}"
            )]
        )

@server.tool(
    name="claude_chat_create",
    description="Cria uma sessão de chat com Claude Code SDK (stateful)",
    input_schema={
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "description": "ID da sessão (opcional)"
            },
            "system_prompt": {
                "type": "string",
                "description": "System prompt para o chat",
                "default": "Você é um assistente útil especializado em Claude Code SDK."
            },
            "model": {
                "type": "string",
                "description": "Modelo do Claude",
                "default": "claude-3-5-sonnet-20241022"
            }
        }
    }
)
async def claude_chat_create_tool(args: Dict[str, Any]) -> ToolResult:
    """
    Cria uma nova sessão de chat usando ClaudeSDKClient
    """
    session_id = args.get("session_id", str(uuid.uuid4()))
    system_prompt = args.get("system_prompt", "Você é um assistente útil.")
    model = args.get("model", "claude-3-5-sonnet-20241022")

    if not SDK_AVAILABLE:
        return ToolResult(
            content=[TextContent(
                type="text",
                text="Claude Code SDK não disponível. Execute dentro do Claude Code."
            )]
        )

    try:
        # Criar cliente REAL do Claude Code SDK
        client = ClaudeSDKClient(
            options=ClaudeCodeOptions(
                model=model,
                system_prompt=system_prompt,
                temperature=0.7
            )
        )

        # Armazenar sessão
        chat_sessions[session_id] = {
            "client": client,
            "created_at": datetime.now().isoformat(),
            "messages": []
        }

        return ToolResult(
            content=[TextContent(
                type="text",
                text=json.dumps({
                    "session_id": session_id,
                    "status": "created",
                    "sdk_available": True
                })
            )]
        )

    except Exception as e:
        return ToolResult(
            content=[TextContent(
                type="text",
                text=f"Erro ao criar sessão: {str(e)}"
            )]
        )

@server.tool(
    name="claude_chat_send",
    description="Envia mensagem para sessão de chat existente",
    input_schema={
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "description": "ID da sessão de chat"
            },
            "message": {
                "type": "string",
                "description": "Mensagem para enviar"
            }
        },
        "required": ["session_id", "message"]
    }
)
async def claude_chat_send_tool(args: Dict[str, Any]) -> ToolResult:
    """
    Envia mensagem para sessão de chat e retorna resposta
    """
    session_id = args.get("session_id")
    message = args.get("message")

    if not SDK_AVAILABLE:
        return ToolResult(
            content=[TextContent(
                type="text",
                text="Claude Code SDK não disponível."
            )]
        )

    if session_id not in chat_sessions:
        return ToolResult(
            content=[TextContent(
                type="text",
                text=f"Sessão {session_id} não encontrada. Crie uma nova sessão primeiro."
            )]
        )

    try:
        session = chat_sessions[session_id]
        client = session["client"]

        # Enviar mensagem usando Claude Code SDK REAL
        await client.send_message(message)

        # Receber resposta
        response_text = ""
        async for chunk in client.receive_response():
            if hasattr(chunk, 'content'):
                response_text += chunk.content
            else:
                response_text += str(chunk)

        # Armazenar no histórico
        session["messages"].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        session["messages"].append({
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.now().isoformat()
        })

        return ToolResult(
            content=[TextContent(
                type="text",
                text=response_text
            )]
        )

    except Exception as e:
        return ToolResult(
            content=[TextContent(
                type="text",
                text=f"Erro ao enviar mensagem: {str(e)}"
            )]
        )

@server.tool(
    name="claude_chat_history",
    description="Obtém histórico de uma sessão de chat",
    input_schema={
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "description": "ID da sessão"
            }
        },
        "required": ["session_id"]
    }
)
async def claude_chat_history_tool(args: Dict[str, Any]) -> ToolResult:
    """
    Retorna histórico de mensagens de uma sessão
    """
    session_id = args.get("session_id")

    if session_id not in chat_sessions:
        return ToolResult(
            content=[TextContent(
                type="text",
                text="Sessão não encontrada"
            )]
        )

    session = chat_sessions[session_id]
    return ToolResult(
        content=[TextContent(
            type="text",
            text=json.dumps({
                "session_id": session_id,
                "created_at": session["created_at"],
                "messages": session["messages"],
                "total_messages": len(session["messages"])
            }, indent=2)
        )]
    )

@server.tool(
    name="claude_sessions_list",
    description="Lista todas as sessões de chat ativas",
    input_schema={
        "type": "object",
        "properties": {}
    }
)
async def claude_sessions_list_tool(args: Dict[str, Any]) -> ToolResult:
    """
    Lista todas as sessões ativas
    """
    sessions_info = []
    for sid, session in chat_sessions.items():
        sessions_info.append({
            "session_id": sid,
            "created_at": session["created_at"],
            "messages_count": len(session["messages"])
        })

    return ToolResult(
        content=[TextContent(
            type="text",
            text=json.dumps({
                "total_sessions": len(sessions_info),
                "sdk_available": SDK_AVAILABLE,
                "sessions": sessions_info
            }, indent=2)
        )]
    )

@server.tool(
    name="claude_check_sdk",
    description="Verifica se Claude Code SDK está disponível",
    input_schema={
        "type": "object",
        "properties": {}
    }
)
async def claude_check_sdk_tool(args: Dict[str, Any]) -> ToolResult:
    """
    Verifica disponibilidade do Claude Code SDK
    """
    if SDK_AVAILABLE:
        status = "✅ Claude Code SDK está disponível e funcionando!"
        info = "Use as ferramentas MCP para acessar o SDK"
    else:
        status = "❌ Claude Code SDK não está disponível"
        info = "Execute este servidor dentro do Claude Code após 'claude login'"

    return ToolResult(
        content=[TextContent(
            type="text",
            text=json.dumps({
                "available": SDK_AVAILABLE,
                "status": status,
                "info": info,
                "tools": [
                    "claude_query - Query stateless",
                    "claude_chat_create - Criar sessão de chat",
                    "claude_chat_send - Enviar mensagem",
                    "claude_chat_history - Ver histórico",
                    "claude_sessions_list - Listar sessões"
                ]
            }, indent=2)
        )]
    )

async def main():
    """
    Inicia o servidor MCP
    """
    print("=" * 80)
    print("🚀 MCP PROXY - Claude Code SDK")
    print("=" * 80)

    if SDK_AVAILABLE:
        print("✅ Claude Code SDK DETECTADO!")
        print("🔧 Ferramentas MCP disponíveis para proxy")
    else:
        print("⚠️ Claude Code SDK NÃO detectado")
        print("💡 Execute dentro do Claude Code")

    print("=" * 80)
    print("📡 Servidor MCP iniciado")
    print("🔌 Use estas ferramentas via MCP client")
    print("=" * 80)

    # Rodar servidor MCP
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())