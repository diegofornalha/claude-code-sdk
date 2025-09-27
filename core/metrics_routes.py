"""
Rotas de Métricas para Neo4j Agent API
=======================================
Endpoints para monitoramento e estatísticas do sistema
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Dict, Any, Optional
import os

# Importar utilitários Neo4j
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.graph.neo4j_advanced import get_neo4j_utils
from middleware.monitoring.metrics_middleware import metrics_collector
from services.analytics.query_analyzer import query_analyzer


# Router para métricas
router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/summary")
async def get_metrics_summary():
    """
    Retorna resumo geral de métricas do sistema.

    Inclui:
    - Total de memórias (nós com label "Learning")
    - Estatísticas de relacionamentos
    - Performance da API
    - Saúde do sistema
    """
    try:
        neo4j_utils = get_neo4j_utils()

        # Buscar total de memórias (Learning)
        with neo4j_utils.driver.session() as session:
            # Total de nós Learning
            result = session.run("""
                MATCH (n:Learning)
                RETURN count(n) as total_learning
            """)
            total_learning = result.single()["total_learning"]

            # Breakdown por tipo de propriedade
            result = session.run("""
                MATCH (n:Learning)
                WITH n,
                     CASE
                         WHEN n.category IS NOT NULL THEN n.category
                         ELSE 'uncategorized'
                     END as category
                RETURN category, count(*) as count
                ORDER BY count DESC
            """)
            learning_by_category = {
                record["category"]: record["count"]
                for record in result
            }

            # Total de relacionamentos
            result = session.run("""
                MATCH (n:Learning)-[r]-()
                RETURN count(DISTINCT r) as total_relationships
            """)
            total_relationships = result.single()["total_relationships"]

            # Relacionamentos mais comuns
            result = session.run("""
                MATCH (n:Learning)-[r]-()
                RETURN type(r) as relationship_type, count(*) as count
                ORDER BY count DESC
                LIMIT 5
            """)
            top_relationships = [
                {"type": record["relationship_type"], "count": record["count"]}
                for record in result
            ]

        # Métricas da API
        global_stats = metrics_collector.get_global_stats()

        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "neo4j": {
                "learning_nodes": {
                    "total": total_learning,
                    "by_category": learning_by_category
                },
                "relationships": {
                    "total": total_relationships,
                    "top_types": top_relationships
                }
            },
            "api": {
                "total_requests": global_stats["total_requests"],
                "error_rate": round(global_stats["error_rate"], 2),
                "uptime": global_stats["uptime_formatted"],
                "requests_per_second": round(global_stats["requests_per_second"], 2)
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar métricas: {str(e)}"
        )


@router.get("/graph-stats")
async def get_graph_statistics():
    """
    Retorna estatísticas detalhadas do grafo Neo4j.

    Inclui:
    - Contagem de nós por tipo
    - Contagem de relacionamentos por tipo
    - Densidade do grafo
    - Grau médio dos nós
    - Nós isolados
    """
    try:
        neo4j_utils = get_neo4j_utils()
        stats = neo4j_utils.get_graph_statistics()

        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "statistics": {
                "nodes": {
                    "total": stats.total_nodes,
                    "by_type": stats.node_types,
                    "isolated": stats.isolated_nodes
                },
                "relationships": {
                    "total": stats.total_relationships,
                    "by_type": stats.relationship_types
                },
                "metrics": {
                    "density": round(stats.density, 6),
                    "avg_degree": round(stats.avg_degree, 2)
                }
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar estatísticas do grafo: {str(e)}"
        )


@router.get("/performance")
async def get_performance_metrics():
    """
    Retorna métricas de performance do sistema.

    Inclui:
    - Tempo médio de resposta por endpoint
    - Endpoints mais lentos
    - Taxa de erro
    - Estatísticas de queries Neo4j
    - Recomendações de otimização
    """
    try:
        # Métricas da API
        global_stats = metrics_collector.get_global_stats()
        endpoint_stats = metrics_collector.get_endpoint_stats()
        slowest_endpoints = metrics_collector.get_slowest_endpoints(top_n=5)

        # Análise de queries
        query_stats = query_analyzer.get_statistics()
        slow_queries = query_analyzer.get_slow_queries()

        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "api_performance": {
                "global": {
                    "total_requests": global_stats["total_requests"],
                    "total_errors": global_stats["total_errors"],
                    "error_rate_percent": round(global_stats["error_rate"], 2),
                    "uptime_seconds": global_stats["uptime_seconds"],
                    "requests_per_second": round(global_stats["requests_per_second"], 2),
                    "active_requests": global_stats["active_requests"]
                },
                "slowest_endpoints": slowest_endpoints
            },
            "neo4j_queries": {
                "total_unique_queries": query_stats["patterns"]["summary"]["total_unique_queries"],
                "total_executions": query_stats["patterns"]["summary"]["total_executions"],
                "avg_query_time_ms": query_stats["patterns"]["summary"]["avg_query_time_ms"],
                "slow_queries_count": query_stats["patterns"]["performance"]["slow_queries_count"],
                "slow_query_percentage": round(
                    query_stats["patterns"]["performance"]["slow_query_percentage"], 2
                )
            },
            "optimization_recommendations": query_stats.get("recommendations", [])
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar métricas de performance: {str(e)}"
        )


@router.get("/learning-insights")
async def get_learning_insights():
    """
    Retorna insights sobre as memórias de aprendizado (Learning).

    Inclui:
    - Crescimento temporal de memórias
    - Categorias mais populares
    - Memórias mais conectadas
    - Sugestões de organização
    """
    try:
        neo4j_utils = get_neo4j_utils()

        with neo4j_utils.driver.session() as session:
            # Memórias mais conectadas
            result = session.run("""
                MATCH (n:Learning)
                OPTIONAL MATCH (n)-[r]-()
                WITH n, count(r) as connections
                ORDER BY connections DESC
                LIMIT 10
                RETURN elementId(n) as id,
                       n.name as name,
                       n.category as category,
                       connections
            """)
            most_connected = [
                {
                    "id": record["id"],
                    "name": record["name"],
                    "category": record["category"],
                    "connections": record["connections"]
                }
                for record in result
            ]

            # Distribuição de conexões
            result = session.run("""
                MATCH (n:Learning)
                OPTIONAL MATCH (n)-[r]-()
                WITH n, count(r) as connections
                WITH CASE
                    WHEN connections = 0 THEN 'isolated'
                    WHEN connections <= 2 THEN 'low_connectivity'
                    WHEN connections <= 5 THEN 'medium_connectivity'
                    ELSE 'high_connectivity'
                END as connectivity_level, count(*) as count
                RETURN connectivity_level, count
            """)
            connectivity_distribution = {
                record["connectivity_level"]: record["count"]
                for record in result
            }

            # Memórias criadas recentemente (se tiver timestamp)
            result = session.run("""
                MATCH (n:Learning)
                WHERE n.created_at IS NOT NULL
                WITH n
                ORDER BY n.created_at DESC
                LIMIT 5
                RETURN elementId(n) as id,
                       n.name as name,
                       n.created_at as created_at
            """)
            recent_learning = [
                {
                    "id": record["id"],
                    "name": record["name"],
                    "created_at": record["created_at"]
                }
                for record in result
            ]

        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "insights": {
                "most_connected_nodes": most_connected,
                "connectivity_distribution": connectivity_distribution,
                "recent_learning": recent_learning if recent_learning else "No timestamp data available"
            },
            "recommendations": _generate_learning_recommendations(
                connectivity_distribution,
                len(most_connected)
            )
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar insights de aprendizado: {str(e)}"
        )


def _generate_learning_recommendations(
    connectivity: Dict[str, int],
    connected_count: int
) -> list:
    """
    Gera recomendações baseadas nos dados de conectividade.

    Args:
        connectivity: Distribuição de conectividade
        connected_count: Número de nós conectados

    Returns:
        Lista de recomendações
    """
    recommendations = []

    isolated = connectivity.get("isolated", 0)
    if isolated > 0:
        recommendations.append({
            "priority": "high",
            "category": "connectivity",
            "message": f"{isolated} memórias isoladas detectadas",
            "suggestion": "Considere conectar memórias relacionadas para melhorar a navegabilidade"
        })

    low_connectivity = connectivity.get("low_connectivity", 0)
    if low_connectivity > connected_count * 0.5:
        recommendations.append({
            "priority": "medium",
            "category": "connectivity",
            "message": f"{low_connectivity} memórias com baixa conectividade",
            "suggestion": "Adicionar mais relacionamentos entre conceitos relacionados"
        })

    if not recommendations:
        recommendations.append({
            "priority": "low",
            "category": "health",
            "message": "Grafo de conhecimento está bem estruturado",
            "suggestion": "Continue mantendo boas práticas de organização"
        })

    return recommendations