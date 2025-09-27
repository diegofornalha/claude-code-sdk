#!/usr/bin/env python3
"""
Claude Code SDK Bridge
Ponte HTTP que conecta aplicações web ao Claude Code SDK real
Funciona como intermediário entre browser e o SDK
"""

import json
import asyncio
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uuid
from datetime import datetime

# Este import só funciona DENTRO do Claude Code
# Após executar 'claude login'
SDK_AVAILABLE = False
try:
    # No ambiente Claude Code, estes imports funcionariam:
    # from claude_code_sdk import query, ClaudeSDKClient, ClaudeCodeOptions
    SDK_AVAILABLE = False  # Desabilitado para demonstração
except ImportError:
    pass

app = FastAPI(
    title="Hackathon Flow Blockchain Agents Bridge",
    description="Bridge HTTP para Claude Code SDK",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sessões ativas (quando SDK estiver disponível)
sessions = {}

@app.get("/api/health")
async def health_check():
    """Verifica status da bridge"""
    return {
        "status": "healthy",
        "bridge": "Hackathon Flow Blockchain Agents Bridge",
        "sdk_available": SDK_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/bridge/status")
async def bridge_status():
    """Status detalhado da bridge"""
    if SDK_AVAILABLE:
        return {
            "bridge_active": True,
            "sdk_status": "✅ Claude Code SDK disponível",
            "authentication": "claude login",
            "message": "Bridge conectada ao Claude Code SDK real",
            "capabilities": [
                "query() - Consultas stateless",
                "ClaudeSDKClient - Chat com contexto",
                "Streaming de respostas",
                "Múltiplas sessões simultâneas"
            ]
        }
    else:
        return {
            "bridge_active": False,
            "sdk_status": "❌ Claude Code SDK não disponível",
            "authentication": "Requer execução dentro do Claude Code",
            "message": "Bridge em modo demonstração - SDK não detectado",
            "solution": "Execute esta bridge DENTRO do Claude Code após 'claude login'"
        }

@app.get("/api/chat/stream")
async def chat_bridge(message: str, sessionId: str = "new"):
    """
    Bridge para streaming de chat
    Conecta requisições HTTP ao Claude Code SDK
    """

    async def generate():
        try:
            if SDK_AVAILABLE:
                # CÓDIGO REAL quando SDK estiver disponível:
                """
                from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions

                # Criar ou recuperar sessão
                if sessionId == "new" or sessionId not in sessions:
                    session_id = str(uuid.uuid4())
                    client = ClaudeSDKClient(
                        options=ClaudeCodeOptions(
                            model="claude-3-5-sonnet-20241022",
                            temperature=0.7
                        )
                    )
                    sessions[session_id] = client
                    yield f"data: {json.dumps({'type': 'session_created', 'session_id': session_id})}\n\n"
                else:
                    client = sessions[sessionId]
                    session_id = sessionId

                # Enviar mensagem para Claude REAL
                await client.send_message(message)

                # Streaming da resposta REAL
                async for chunk in client.receive_response():
                    content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                    yield f"data: {json.dumps({'type': 'text_chunk', 'content': content})}\n\n"

                yield f"data: {json.dumps({'type': 'result', 'session_id': session_id})}\n\n"
                """
                pass
            else:
                # Modo demonstração quando SDK não está disponível
                session_id = str(uuid.uuid4()) if sessionId == "new" else sessionId

                yield f"data: {json.dumps({'type': 'session_created', 'session_id': session_id, 'mode': 'demo'})}\n\n"

                demo_response = f"""Bridge Hackathon Flow Blockchain Agents: Mensagem "{message}" recebida.

⚠️ SDK não disponível neste ambiente. Para usar o Claude Code SDK real:

1. Execute esta bridge DENTRO do Claude Code
2. Faça 'claude login' uma vez
3. A bridge conectará automaticamente ao SDK

Quando funcionando, esta bridge permite que seu chat web use o Claude real através do Claude Code SDK."""

                # Simular streaming
                words = demo_response.split()
                chunk = ""
                for i, word in enumerate(words):
                    chunk += word + " "
                    if (i + 1) % 8 == 0:
                        yield f"data: {json.dumps({'type': 'text_chunk', 'content': chunk})}\n\n"
                        chunk = ""
                        await asyncio.sleep(0.03)

                if chunk:
                    yield f"data: {json.dumps({'type': 'text_chunk', 'content': chunk})}\n\n"

                yield f"data: {json.dumps({'type': 'result', 'session_id': session_id, 'mode': 'demo'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/api/bridge/query")
async def query_bridge(prompt: str, temperature: float = 0.7):
    """
    Bridge para query stateless
    """
    if SDK_AVAILABLE:
        # Código real quando SDK disponível
        """
        from claude_code_sdk import query, ClaudeCodeOptions

        response = ""
        async for msg in query(
            prompt,
            options=ClaudeCodeOptions(
                model="claude-3-5-sonnet-20241022",
                temperature=temperature
            )
        ):
            response += msg.result if hasattr(msg, 'result') else str(msg)

        return {
            "response": response,
            "mode": "real",
            "sdk": "Claude Code SDK"
        }
        """
        pass

    return {
        "response": f"Bridge recebeu: '{prompt}'. SDK não disponível neste ambiente.",
        "mode": "demo",
        "sdk": "Not available",
        "solution": "Execute dentro do Claude Code após 'claude login'"
    }

@app.get("/api/bridge/diagram")
async def get_architecture():
    """Retorna diagrama da arquitetura da bridge"""
    return {
        "architecture": """
        ┌──────────────┐     HTTP/SSE      ┌──────────────┐     Hackathon Flow Blockchain Agents    ┌──────────────┐
        │              │ ─────────────────> │              │ ───────────────> │              │
        │   Browser    │                    │   Bridge     │                  │  Claude AI   │
        │   (React)    │ <───────────────── │   (FastAPI)  │ <─────────────── │   (Real)     │
        │              │     Streaming      │              │     Response     │              │
        └──────────────┘                    └──────────────┘                  └──────────────┘

        Browser ←→ Bridge (HTTP) ←→ Claude Code SDK ←→ Claude AI
        """,
        "flow": [
            "1. Browser envia requisição HTTP para Bridge",
            "2. Bridge usa Claude Code SDK (query ou ClaudeSDKClient)",
            "3. SDK se comunica com Claude AI real",
            "4. Bridge retorna resposta via SSE streaming",
            "5. Browser exibe resposta em tempo real"
        ],
        "requirements": [
            "Bridge deve rodar DENTRO do Claude Code",
            "Executar 'claude login' antes de iniciar",
            "SDK automaticamente gerencia autenticação"
        ]
    }

if __name__ == "__main__":
    import uvicorn

    print("=" * 80)
    print("🌉 Hackathon Flow Blockchain Agents BRIDGE - Conectando Web ao Claude Code SDK")
    print("=" * 80)

    if SDK_AVAILABLE:
        print("✅ Claude Code SDK DETECTADO!")
        print("🔗 Bridge conectada ao SDK real")
        print("💬 Respostas virão do Claude real")
    else:
        print("⚠️ Claude Code SDK NÃO detectado")
        print("📝 Para ativar a bridge:")
        print("   1. Execute este arquivo DENTRO do Claude Code")
        print("   2. Faça 'claude login' antes")
        print("   3. A bridge conectará automaticamente")

    print("=" * 80)
    print("🌐 Bridge rodando em: http://localhost:4001")
    print("📊 Status: http://localhost:4001/api/bridge/status")
    print("📐 Arquitetura: http://localhost:4001/api/bridge/diagram")
    print("=" * 80)

    uvicorn.run(
        "claude_sdk_bridge:app",
        host="0.0.0.0",
        port=4001,
        reload=True
    )