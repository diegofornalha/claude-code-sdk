"""
Rotas de analytics e análise de queries
"""
from fastapi import APIRouter

from services.analytics.query_analyzer import query_analyzer

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

@router.get("/queries/statistics")
async def query_statistics():
    """Estatísticas de queries processadas."""
    return query_analyzer.get_statistics()

@router.get("/queries/slow")
async def slow_queries(threshold_ms: float = 1000, limit: int = 20):
    """Queries lentas acima do threshold."""
    slow = query_analyzer.get_slow_queries(threshold_ms, limit)
    return {
        "threshold_ms": threshold_ms,
        "queries": slow,
        "count": len(slow)
    }

@router.get("/queries/recommendations")
async def query_recommendations():
    """Recomendações de otimização baseadas em análise."""
    recommendations = query_analyzer.get_optimization_recommendations()

    return {
        "recommendations": recommendations,
        "statistics": query_analyzer.get_statistics(),
        "patterns": query_analyzer.analyze_patterns()
    }