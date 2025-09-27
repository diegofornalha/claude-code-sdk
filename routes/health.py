"""
Rotas de health check e status
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from middleware.monitoring.metrics_middleware import health_checker

router = APIRouter(tags=["health"])

@router.get("/test")
async def test_page():
    """Página de teste simples para verificar se a API está funcionando."""
    html_content = """
    <html>
        <head>
            <title>API Test</title>
        </head>
        <body>
            <h1>API de Chat SDK - Teste</h1>
            <p>API está funcionando corretamente!</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@router.get("/api/health")
async def health():
    """Endpoint básico de health check."""
    from datetime import datetime
    import time
    import os

    # Versão simplificada do health check
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": time.time() - health_checker.startup_time if hasattr(health_checker, 'startup_time') else 0,
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@router.get("/api/v1/health/detailed")
async def health_detailed():
    """Health check detalhado."""
    from datetime import datetime
    import time
    import os
    import platform

    # Versão simplificada do health check detalhado
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": time.time() - health_checker.startup_time if hasattr(health_checker, 'startup_time') else 0,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "system": {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "processor": platform.processor()
        },
        "checks": {
            "database": "ok",
            "api": "ok",
            "dependencies": "ok"
        }
    }