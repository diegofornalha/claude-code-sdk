"""
Sistema Avançado de Manipulação de Grafos Neo4j
==================================================
Utilitários para análise, otimização e visualização de grafos
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import os
from neo4j import GraphDatabase


@dataclass
class GraphStats:
    """Estatísticas de grafo."""
    total_nodes: int
    total_relationships: int
    node_types: Dict[str, int]
    relationship_types: Dict[str, int]
    density: float
    avg_degree: float
    isolated_nodes: int


@dataclass
class PathResult:
    """Resultado de busca de caminho."""
    nodes: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    length: int
    total_weight: float


class Neo4jAdvancedUtils:
    """Utilitários avançados para Neo4j."""

    def __init__(self, uri: str = None, user: str = None, password: str = None):
        """
        Inicializa conexão com Neo4j.

        Args:
            uri: URI do Neo4j (usa NEO4J_URI do .env se None)
            user: Usuário (usa NEO4J_USER do .env se None)
            password: Senha (usa NEO4J_PASSWORD do .env se None)
        """
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password")

        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        """Fecha conexão com Neo4j."""
        if self.driver:
            self.driver.close()

    def get_graph_statistics(self) -> GraphStats:
        """
        Retorna estatísticas completas do grafo.

        Returns:
            Estatísticas detalhadas
        """
        with self.driver.session() as session:
            # Total de nós e relacionamentos
            result = session.run("""
                MATCH (n)
                OPTIONAL MATCH (n)-[r]->()
                RETURN count(DISTINCT n) as nodes, count(DISTINCT r) as rels
            """)
            record = result.single()
            total_nodes = record["nodes"]
            total_relationships = record["rels"]

            # Tipos de nós
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as label, count(*) as count
                ORDER BY count DESC
            """)
            node_types = {record["label"]: record["count"] for record in result}

            # Tipos de relacionamentos
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, count(*) as count
                ORDER BY count DESC
            """)
            relationship_types = {record["type"]: record["count"] for record in result}

            # Densidade do grafo
            # Densidade = 2 * E / (N * (N - 1)) para grafo direcionado
            density = 0.0
            if total_nodes > 1:
                max_edges = total_nodes * (total_nodes - 1)
                density = (2 * total_relationships) / max_edges if max_edges > 0 else 0.0

            # Grau médio
            avg_degree = (2 * total_relationships / total_nodes) if total_nodes > 0 else 0.0

            # Nós isolados
            result = session.run("""
                MATCH (n)
                WHERE NOT (n)-[]-()
                RETURN count(n) as isolated
            """)
            isolated_nodes = result.single()["isolated"]

            return GraphStats(
                total_nodes=total_nodes,
                total_relationships=total_relationships,
                node_types=node_types,
                relationship_types=relationship_types,
                density=density,
                avg_degree=avg_degree,
                isolated_nodes=isolated_nodes
            )

    def find_shortest_path(
        self,
        start_id: str,
        end_id: str,
        max_depth: int = 10,
        relationship_types: Optional[List[str]] = None
    ) -> Optional[PathResult]:
        """
        Encontra o caminho mais curto entre dois nós.

        Args:
            start_id: ID do nó inicial
            end_id: ID do nó final
            max_depth: Profundidade máxima de busca
            relationship_types: Tipos de relacionamentos permitidos

        Returns:
            PathResult com o caminho encontrado ou None
        """
        with self.driver.session() as session:
            rel_filter = ""
            if relationship_types:
                rel_types_str = "|".join(f":{t}" for t in relationship_types)
                rel_filter = f"[{rel_types_str}*1..{max_depth}]"
            else:
                rel_filter = f"[*1..{max_depth}]"

            query = f"""
                MATCH (start), (end)
                WHERE elementId(start) = $start_id AND elementId(end) = $end_id
                MATCH path = shortestPath((start)-{rel_filter}-(end))
                RETURN path
            """

            result = session.run(query, start_id=start_id, end_id=end_id)
            record = result.single()

            if not record:
                return None

            path = record["path"]
            nodes = [dict(node) for node in path.nodes]
            relationships = [dict(rel) for rel in path.relationships]

            return PathResult(
                nodes=nodes,
                relationships=relationships,
                length=len(relationships),
                total_weight=len(relationships)  # Pode ser expandido com pesos reais
            )

    def find_communities(self, min_size: int = 3) -> List[Set[str]]:
        """
        Detecta comunidades no grafo usando algoritmo de Louvain.

        Args:
            min_size: Tamanho mínimo da comunidade

        Returns:
            Lista de conjuntos de IDs de nós em cada comunidade
        """
        with self.driver.session() as session:
            # Implementação simplificada: agrupa por tipo de nó e relacionamentos fortes
            query = """
                MATCH (n)
                WITH labels(n)[0] as label, collect(elementId(n)) as nodes
                WHERE size(nodes) >= $min_size
                RETURN label, nodes
            """

            result = session.run(query, min_size=min_size)
            communities = [set(record["nodes"]) for record in result]

            return communities

    def get_node_centrality(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Calcula centralidade de nós (degree centrality).

        Args:
            top_n: Número de nós mais centrais a retornar

        Returns:
            Lista de nós com suas centralidades
        """
        with self.driver.session() as session:
            query = """
                MATCH (n)
                OPTIONAL MATCH (n)-[r]-()
                WITH n, count(r) as degree
                RETURN elementId(n) as id,
                       labels(n) as labels,
                       properties(n) as props,
                       degree
                ORDER BY degree DESC
                LIMIT $top_n
            """

            result = session.run(query, top_n=top_n)

            centrality_scores = []
            for record in result:
                centrality_scores.append({
                    "id": record["id"],
                    "labels": record["labels"],
                    "properties": record["props"],
                    "degree": record["degree"],
                    "centrality_score": record["degree"]  # Simplificado
                })

            return centrality_scores

    def find_similar_nodes(
        self,
        node_id: str,
        limit: int = 10,
        similarity_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Encontra nós similares baseado em propriedades e relacionamentos.

        Args:
            node_id: ID do nó de referência
            limit: Número máximo de resultados
            similarity_threshold: Threshold de similaridade (0-1)

        Returns:
            Lista de nós similares com score de similaridade
        """
        with self.driver.session() as session:
            query = """
                MATCH (target)
                WHERE elementId(target) = $node_id

                // Encontra nós com mesmos labels
                MATCH (similar)
                WHERE labels(similar) = labels(target)
                  AND elementId(similar) <> $node_id

                // Calcula similaridade baseada em relacionamentos comuns
                OPTIONAL MATCH (target)-[r1]->(common)<-[r2]-(similar)
                WITH similar, count(DISTINCT common) as shared_connections,
                     labels(similar) as labels,
                     properties(similar) as props

                // Score baseado em conexões compartilhadas
                WITH similar, labels, props, shared_connections,
                     CASE WHEN shared_connections > 0
                          THEN shared_connections * 0.1
                          ELSE 0.1
                     END as similarity_score

                WHERE similarity_score >= $threshold

                RETURN elementId(similar) as id,
                       labels, props,
                       similarity_score,
                       shared_connections
                ORDER BY similarity_score DESC
                LIMIT $limit
            """

            result = session.run(
                query,
                node_id=node_id,
                threshold=similarity_threshold,
                limit=limit
            )

            similar_nodes = []
            for record in result:
                similar_nodes.append({
                    "id": record["id"],
                    "labels": record["labels"],
                    "properties": record["props"],
                    "similarity_score": record["similarity_score"],
                    "shared_connections": record["shared_connections"]
                })

            return similar_nodes

    def analyze_subgraph(
        self,
        center_node_id: str,
        depth: int = 2,
        relationship_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analisa subgrafo centrado em um nó.

        Args:
            center_node_id: ID do nó central
            depth: Profundidade de análise
            relationship_types: Tipos de relacionamentos a considerar

        Returns:
            Análise detalhada do subgrafo
        """
        with self.driver.session() as session:
            rel_filter = ""
            if relationship_types:
                rel_types_str = "|".join(f":{t}" for t in relationship_types)
                rel_filter = f"[{rel_types_str}*0..{depth}]"
            else:
                rel_filter = f"[*0..{depth}]"

            query = f"""
                MATCH (center)
                WHERE elementId(center) = $center_id

                CALL {{
                    WITH center
                    MATCH path = (center)-{rel_filter}-(connected)
                    RETURN connected, relationships(path) as rels
                }}

                WITH center, collect(DISTINCT connected) as nodes,
                     reduce(r = [], rel in collect(rels) | r + rel) as all_rels

                UNWIND all_rels as rel
                WITH center, nodes, collect(DISTINCT rel) as relationships

                RETURN elementId(center) as center_id,
                       properties(center) as center_props,
                       size(nodes) as node_count,
                       size(relationships) as relationship_count,
                       nodes, relationships
            """

            result = session.run(query, center_id=center_node_id)
            record = result.single()

            if not record:
                return {
                    "center_id": center_node_id,
                    "error": "Node not found"
                }

            # Análise de tipos
            nodes_by_type = {}
            for node in record["nodes"]:
                node_labels = list(node.labels)
                label = node_labels[0] if node_labels else "Unknown"
                nodes_by_type[label] = nodes_by_type.get(label, 0) + 1

            rels_by_type = {}
            for rel in record["relationships"]:
                rel_type = rel.type
                rels_by_type[rel_type] = rels_by_type.get(rel_type, 0) + 1

            return {
                "center_id": record["center_id"],
                "center_properties": record["center_props"],
                "subgraph_size": {
                    "nodes": record["node_count"],
                    "relationships": record["relationship_count"]
                },
                "composition": {
                    "nodes_by_type": nodes_by_type,
                    "relationships_by_type": rels_by_type
                },
                "depth": depth
            }

    def optimize_queries(self) -> Dict[str, Any]:
        """
        Analisa e sugere otimizações para o banco.

        Returns:
            Sugestões de otimização
        """
        with self.driver.session() as session:
            suggestions = []

            # Verifica índices
            result = session.run("SHOW INDEXES")
            indexes = [dict(record) for record in result]

            if not indexes:
                suggestions.append({
                    "type": "index",
                    "severity": "high",
                    "message": "Nenhum índice encontrado. Considere criar índices para propriedades frequentemente consultadas."
                })

            # Verifica constraints
            result = session.run("SHOW CONSTRAINTS")
            constraints = [dict(record) for record in result]

            if not constraints:
                suggestions.append({
                    "type": "constraint",
                    "severity": "medium",
                    "message": "Nenhuma constraint encontrada. Considere adicionar constraints de unicidade."
                })

            # Verifica nós sem relacionamentos
            result = session.run("""
                MATCH (n)
                WHERE NOT (n)-[]-()
                RETURN count(n) as isolated_count
            """)
            isolated_count = result.single()["isolated_count"]

            if isolated_count > 100:
                suggestions.append({
                    "type": "data_quality",
                    "severity": "low",
                    "message": f"{isolated_count} nós isolados encontrados. Considere remover ou conectar."
                })

            return {
                "timestamp": datetime.utcnow().isoformat(),
                "indexes": len(indexes),
                "constraints": len(constraints),
                "suggestions": suggestions,
                "optimization_needed": len(suggestions) > 0
            }

    def export_subgraph_json(
        self,
        node_ids: List[str],
        include_relationships: bool = True
    ) -> Dict[str, Any]:
        """
        Exporta subgrafo para formato JSON.

        Args:
            node_ids: Lista de IDs de nós para exportar
            include_relationships: Se deve incluir relacionamentos

        Returns:
            Grafo em formato JSON
        """
        with self.driver.session() as session:
            # Busca nós
            query_nodes = """
                MATCH (n)
                WHERE elementId(n) IN $node_ids
                RETURN elementId(n) as id, labels(n) as labels, properties(n) as properties
            """

            result = session.run(query_nodes, node_ids=node_ids)
            nodes = [
                {
                    "id": record["id"],
                    "labels": record["labels"],
                    "properties": dict(record["properties"])
                }
                for record in result
            ]

            relationships = []
            if include_relationships:
                query_rels = """
                    MATCH (source)-[r]->(target)
                    WHERE elementId(source) IN $node_ids AND elementId(target) IN $node_ids
                    RETURN elementId(r) as id,
                           elementId(source) as source,
                           elementId(target) as target,
                           type(r) as type,
                           properties(r) as properties
                """

                result = session.run(query_rels, node_ids=node_ids)
                relationships = [
                    {
                        "id": record["id"],
                        "source": record["source"],
                        "target": record["target"],
                        "type": record["type"],
                        "properties": dict(record["properties"])
                    }
                    for record in result
                ]

            return {
                "graph": {
                    "nodes": nodes,
                    "relationships": relationships
                },
                "metadata": {
                    "exported_at": datetime.utcnow().isoformat(),
                    "node_count": len(nodes),
                    "relationship_count": len(relationships)
                }
            }


# Instância global reutilizável
_neo4j_utils_instance = None


def get_neo4j_utils() -> Neo4jAdvancedUtils:
    """Obtém instância singleton dos utilitários Neo4j."""
    global _neo4j_utils_instance
    if _neo4j_utils_instance is None:
        _neo4j_utils_instance = Neo4jAdvancedUtils()
    return _neo4j_utils_instance