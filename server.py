"""
Servidor FastAPI - Proxy REST para Claude Code SDK
Versão refatorada com rotas modulares
"""

from dotenv import load_dotenv
load_dotenv()  # Carrega variáveis do arquivo .env

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
import os
import sys
import json
import time
from collections import defaultdict

# Adicionar paths do SDK
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sdk'))

# Importar middleware de métricas
from middleware.monitoring.metrics_middleware import MetricsMiddleware, metrics_collector

# Importar rotas modulares
from routes import (
    chat_router,
    sessions_router,
    metrics_router,
    graph_router,
    health_router,
    analytics_router,
    websocket_router
)

# Importar utilitários de segurança
from utils.security_utils import get_security_headers, get_cache_headers

# Criar aplicação FastAPI
app = FastAPI(
    title="Claude Code SDK API",
    description="API REST para integração com Claude Code SDK",
    version="2.0.0"
)

# Rate limiter melhorado com janela deslizante
class EnhancedRateLimiter:
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)

    def check_rate_limit(self, client_ip: str) -> bool:
        now = time.time()
        # Limpar requisições antigas
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > now - self.window_seconds
        ]

        # Verificar limite
        if len(self.requests[client_ip]) >= self.max_requests:
            return False

        # Adicionar nova requisição
        self.requests[client_ip].append(now)
        return True

    def get_retry_after(self, client_ip: str) -> int:
        if not self.requests[client_ip]:
            return 0
        oldest = min(self.requests[client_ip])
        retry_after = int(self.window_seconds - (time.time() - oldest))
        return max(0, retry_after)

rate_limiter = EnhancedRateLimiter(max_requests=60, window_seconds=60)

# Middleware para adicionar headers de segurança
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Adiciona headers de segurança em todas as respostas."""
    response = await call_next(request)

    # Adicionar headers de segurança
    security_headers = get_security_headers()
    for header, value in security_headers.items():
        response.headers[header] = value

    # Headers de cache baseados no tipo de requisição
    if request.url.path.startswith("/api/"):
        cache_headers = get_cache_headers("api")
    elif request.url.path.startswith("/static/"):
        cache_headers = get_cache_headers("static")
    else:
        cache_headers = get_cache_headers("default")

    for header, value in cache_headers.items():
        response.headers[header] = value

    return response

# Middleware para rate limiting
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Aplica rate limiting por IP com janela deslizante"""
    # Pular rate limiting para arquivos estáticos
    if request.url.path.startswith("/static/"):
        return await call_next(request)

    # Obter IP do cliente
    client_ip = request.client.host if request.client else "unknown"

    # Verificar rate limit
    if not rate_limiter.check_rate_limit(client_ip):
        retry_after = rate_limiter.get_retry_after(client_ip)
        return Response(
            content=json.dumps({
                "error": "Rate limit excedido. Tente novamente mais tarde.",
                "code": "RATE_LIMIT_EXCEEDED",
                "retry_after_seconds": retry_after
            }),
            status_code=429,
            media_type="application/json",
            headers={"Retry-After": str(retry_after)}
        )

    return await call_next(request)

# CORS com origens específicas para segurança
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3333",
        "http://localhost:3000",
        "http://localhost:8888"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

# Adicionar middleware de compressão
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Adicionar middleware de métricas
app.add_middleware(MetricsMiddleware, collector=metrics_collector)

# Servir arquivos estáticos
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

if os.path.exists("examples"):
    app.mount("/examples", StaticFiles(directory="examples"), name="examples")

# Incluir rotas modulares
app.include_router(health_router)
app.include_router(chat_router)
app.include_router(sessions_router)
app.include_router(metrics_router)
app.include_router(graph_router)
app.include_router(analytics_router)
app.include_router(websocket_router)

# Endpoint raiz
@app.get("/")
async def root():
    """Endpoint raiz com informações da API."""
    return {
        "name": "Claude Code SDK API",
        "version": "2.0.0",
        "status": "online",
        "documentation": "/docs",
        "health": "/api/health"
    }

# Endpoint para Flow balance (mantido por compatibilidade)
@app.get("/api/flow/balance/{address}")
async def get_flow_balance(address: str):
    """
    Retorna o balance Flow de um endereço.
    Implementação simplificada para exemplo.
    """
    # Mock response for Flow balance
    return {
        "address": address,
        "balance": "0.00",
        "currency": "FLOW",
        "network": "testnet",
        "message": "Flow integration não configurada"
    }

@app.get("/api/flow/balance")
async def get_default_flow_balance():
    """Retorna balance Flow padrão."""
    return {
        "balance": "0.00",
        "currency": "FLOW",
        "network": "testnet",
        "message": "Nenhum endereço especificado"
    }

# Evento de startup
@app.on_event("startup")
async def startup_event():
    """Inicialização da aplicação."""
    print("=" * 50)
    print("Claude Code SDK API v2.0.0")
    print("Servidor refatorado com rotas modulares")
    print("=" * 50)
    print("Endpoints disponíveis:")
    print("- Health: /api/health")
    print("- Chat: /api/chat")
    print("- Sessions: /api/sessions")
    print("- Metrics: /api/v1/metrics/")
    print("- Graph: /api/v1/graph/")
    print("- Analytics: /api/v1/analytics/")
    print("- WebSocket: /ws/advanced/{session_id}")
    print("=" * 50)

# Evento de shutdown
@app.on_event("shutdown")
async def shutdown_event():
    """Limpeza ao desligar a aplicação."""
    print("Encerrando servidor...")
    # Aqui podem ser adicionadas rotinas de limpeza se necessário

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=3333,
        reload=True,
        log_level="info"
    )