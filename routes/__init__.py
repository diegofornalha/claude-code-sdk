"""
Módulo de rotas da API
"""
from .chat import router as chat_router
from .sessions import router as sessions_router
from .metrics import router as metrics_router
from .graph import router as graph_router
from .health import router as health_router
from .analytics import router as analytics_router
from .websocket import router as websocket_router

__all__ = [
    'chat_router',
    'sessions_router',
    'metrics_router',
    'graph_router',
    'health_router',
    'analytics_router',
    'websocket_router'
]