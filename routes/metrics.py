"""
Rotas de métricas e monitoramento
"""
from fastapi import APIRouter

from middleware.monitoring.metrics_middleware import metrics_collector

router = APIRouter(prefix="/api/v1", tags=["metrics"])

@router.get("/metrics/overview")
async def metrics_overview():
    """Visão geral das métricas."""
    return metrics_collector.get_overview()

@router.get("/metrics/endpoint/{endpoint:path}")
async def endpoint_metrics(endpoint: str):
    """Métricas detalhadas de um endpoint específico."""
    stats = metrics_collector.get_endpoint_stats(f"/{endpoint}")
    if not stats:
        return {"error": "Endpoint não encontrado"}
    return stats

@router.get("/metrics/recent-requests")
async def recent_requests():
    """Requisições recentes."""
    return {
        "requests": metrics_collector.get_recent_requests(limit=100)
    }