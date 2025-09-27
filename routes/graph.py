"""
Rotas relacionadas ao grafo Neo4j
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from utils.graph.neo4j_advanced import get_neo4j_utils

router = APIRouter(prefix="/api/v1/graph", tags=["graph"])

class ExportRequest(BaseModel):
    format: str = "graphml"
    include_properties: bool = True
    max_nodes: Optional[int] = 1000

@router.get("/statistics")
async def graph_statistics():
    """Estatísticas gerais do grafo."""
    try:
        neo4j_utils = get_neo4j_utils()
        if not neo4j_utils:
            raise HTTPException(status_code=503, detail="Neo4j não disponível")

        stats = neo4j_utils.get_graph_statistics()
        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/path/{start_id}/{end_id}")
async def find_path(start_id: str, end_id: str, max_depth: int = 5):
    """Encontra caminho entre dois nós."""
    try:
        neo4j_utils = get_neo4j_utils()
        if not neo4j_utils:
            raise HTTPException(status_code=503, detail="Neo4j não disponível")

        path = neo4j_utils.find_shortest_path(start_id, end_id, max_depth)
        if not path:
            return {"message": "Nenhum caminho encontrado", "path": []}

        return {
            "path": path,
            "length": len(path) - 1
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/node/{node_id}/centrality")
async def node_centrality(node_id: str):
    """Calcula métricas de centralidade para um nó."""
    try:
        neo4j_utils = get_neo4j_utils()
        if not neo4j_utils:
            raise HTTPException(status_code=503, detail="Neo4j não disponível")

        centrality = neo4j_utils.calculate_centrality(node_id)
        return centrality

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/node/{node_id}/similar")
async def find_similar_nodes(node_id: str, limit: int = 10):
    """Encontra nós similares baseado em propriedades e conexões."""
    try:
        neo4j_utils = get_neo4j_utils()
        if not neo4j_utils:
            raise HTTPException(status_code=503, detail="Neo4j não disponível")

        similar = neo4j_utils.find_similar_nodes(node_id, limit)
        return {
            "node_id": node_id,
            "similar_nodes": similar,
            "count": len(similar)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/node/{node_id}/subgraph")
async def get_subgraph(node_id: str, depth: int = 2, limit: int = 100):
    """Extrai subgrafo ao redor de um nó."""
    try:
        neo4j_utils = get_neo4j_utils()
        if not neo4j_utils:
            raise HTTPException(status_code=503, detail="Neo4j não disponível")

        subgraph = neo4j_utils.get_subgraph(node_id, depth, limit)
        return subgraph

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/optimize")
async def optimize_graph():
    """Sugestões de otimização para o grafo."""
    try:
        neo4j_utils = get_neo4j_utils()
        if not neo4j_utils:
            raise HTTPException(status_code=503, detail="Neo4j não disponível")

        suggestions = neo4j_utils.get_optimization_suggestions()
        return suggestions

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export")
async def export_graph(request: ExportRequest):
    """Exporta o grafo em diferentes formatos."""
    try:
        neo4j_utils = get_neo4j_utils()
        if not neo4j_utils:
            raise HTTPException(status_code=503, detail="Neo4j não disponível")

        export_data = neo4j_utils.export_graph(
            format=request.format,
            include_properties=request.include_properties,
            max_nodes=request.max_nodes
        )
        return export_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))