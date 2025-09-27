"""
Sistema de Cache Inteligente para Queries Neo4j
================================================
Integra cache manager com queries do grafo
"""

import hashlib
import json
from typing import Dict, Any, Optional, List
from core.cache_manager import SmartCache
from utils.graph.neo4j_connection_pool import neo4j_pool


class Neo4jCachedQueries:
    """Queries Neo4j com cache inteligente."""

    def __init__(self):
        """Inicializa sistema de cache."""
        # Cache específico para Neo4j (maior TTL para dados estáveis)
        self.cache = SmartCache(
            max_size=500,  # 500 queries cacheadas
            default_ttl=600,  # 10 minutos padrão
            enable_stats=True
        )

    def _generate_cache_key(
        self,
        query: str,
        parameters: Optional[Dict] = None
    ) -> str:
        """
        Gera chave única para query + parâmetros.

        Args:
            query: Query Cypher
            parameters: Parâmetros da query

        Returns:
            Hash MD5 da combinação
        """
        cache_data = {
            "query": query.strip(),
            "params": parameters or {}
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()

    async def get_graph_statistics(
        self,
        ttl: int = 300  # 5 minutos
    ) -> Dict[str, Any]:
        """
        Obtém estatísticas do grafo COM CACHE.

        Args:
            ttl: Tempo de cache em segundos

        Returns:
            Estatísticas do grafo
        """
        cache_key = "graph_statistics"
        cached = self.cache.get(cache_key)

        if cached:
            return cached

        # Executar query otimizada (UMA SÓ QUERY ao invés de 3)
        query = """
            MATCH (n)
            WITH n
            OPTIONAL MATCH (n)-[r]->()
            WITH count(DISTINCT n) as total_nodes,
                 count(DISTINCT r) as total_rels,
                 collect(DISTINCT labels(n)[0]) as node_labels,
                 collect(DISTINCT type(r)) as rel_types

            // Conta nós por label
            UNWIND node_labels as label
            WITH total_nodes, total_rels, label, rel_types
            MATCH (n)
            WHERE labels(n)[0] = label
            WITH total_nodes, total_rels, label, count(n) as label_count, rel_types

            // Conta relacionamentos por tipo
            UNWIND rel_types as rel_type
            WITH total_nodes, total_rels, label, label_count, rel_type
            MATCH ()-[r]->()
            WHERE type(r) = rel_type
            WITH total_nodes, total_rels,
                 collect({label: label, count: label_count}) as node_types,
                 rel_type, count(r) as rel_count

            RETURN total_nodes,
                   total_rels,
                   node_types,
                   collect({type: rel_type, count: rel_count}) as rel_types
        """

        result = await neo4j_pool.execute_query(query, cache=False)

        if not result:
            return {"error": "No data"}

        record = result[0]

        # Formatar resultado
        stats = {
            "total_nodes": record["total_nodes"],
            "total_relationships": record["total_rels"],
            "node_types": {
                item["label"]: item["count"]
                for item in record["node_types"]
            },
            "relationship_types": {
                item["type"]: item["count"]
                for item in record["rel_types"]
            }
        }

        # Cachear resultado
        self.cache.set(cache_key, stats, ttl=ttl)

        return stats

    async def search_learning_nodes(
        self,
        search_term: str,
        limit: int = 20,
        ttl: int = 300
    ) -> List[Dict[str, Any]]:
        """
        Busca nós Learning por termo COM CACHE.

        Args:
            search_term: Termo de busca
            limit: Limite de resultados
            ttl: TTL do cache

        Returns:
            Lista de nós encontrados
        """
        # Gerar chave de cache
        cache_key = self._generate_cache_key(
            "search_learning",
            {"term": search_term, "limit": limit}
        )

        cached = self.cache.get(cache_key)
        if cached:
            return cached

        # Query otimizada com ÍNDICE
        query = """
            MATCH (n:Learning)
            WHERE n.name CONTAINS $term
               OR n.description CONTAINS $term
               OR n.type CONTAINS $term
            RETURN elementId(n) as id,
                   n.name as name,
                   n.type as type,
                   n.description as description,
                   n.created_at as created_at
            ORDER BY n.created_at DESC
            LIMIT $limit
        """

        parameters = {"term": search_term, "limit": limit}
        result = await neo4j_pool.execute_query(query, parameters)

        # Cachear resultado
        self.cache.set(cache_key, result, ttl=ttl)

        return result

    async def get_node_with_relationships(
        self,
        node_id: str,
        depth: int = 1,
        ttl: int = 600  # 10 minutos - dados menos voláteis
    ) -> Dict[str, Any]:
        """
        Obtém nó e relacionamentos COM CACHE.

        Args:
            node_id: ID do nó
            depth: Profundidade de busca
            ttl: TTL do cache

        Returns:
            Nó com relacionamentos
        """
        cache_key = self._generate_cache_key(
            "node_relationships",
            {"id": node_id, "depth": depth}
        )

        cached = self.cache.get(cache_key)
        if cached:
            return cached

        # Query otimizada
        query = f"""
            MATCH (center)
            WHERE elementId(center) = $node_id

            // Busca relacionamentos até profundidade N
            CALL {{
                WITH center
                MATCH path = (center)-[*0..{depth}]-(connected)
                RETURN collect(DISTINCT connected) as nodes,
                       collect(DISTINCT relationships(path)) as rels
            }}

            WITH center, nodes, rels
            UNWIND rels as rel_list
            WITH center, nodes, reduce(acc = [], r IN rel_list | acc + r) as all_rels

            RETURN elementId(center) as center_id,
                   properties(center) as center_props,
                   [n IN nodes | {{
                       id: elementId(n),
                       labels: labels(n),
                       props: properties(n)
                   }}] as connected_nodes,
                   [r IN all_rels | {{
                       type: type(r),
                       props: properties(r)
                   }}] as relationships
        """

        result = await neo4j_pool.execute_query(
            query,
            {"node_id": node_id}
        )

        if not result:
            return {"error": "Node not found"}

        # Cachear resultado
        self.cache.set(cache_key, result[0], ttl=ttl)

        return result[0]

    async def get_most_connected_nodes(
        self,
        limit: int = 10,
        ttl: int = 300
    ) -> List[Dict[str, Any]]:
        """
        Obtém nós mais conectados COM CACHE.

        Args:
            limit: Número de nós
            ttl: TTL do cache

        Returns:
            Lista de nós ordenados por conexões
        """
        cache_key = f"most_connected_{limit}"
        cached = self.cache.get(cache_key)

        if cached:
            return cached

        # Query otimizada
        query = """
            MATCH (n:Learning)
            OPTIONAL MATCH (n)-[r]-()
            WITH n, count(r) as degree
            WHERE degree > 0
            RETURN elementId(n) as id,
                   n.name as name,
                   n.type as type,
                   degree
            ORDER BY degree DESC
            LIMIT $limit
        """

        result = await neo4j_pool.execute_query(
            query,
            {"limit": limit}
        )

        # Cachear resultado
        self.cache.set(cache_key, result, ttl=ttl)

        return result

    def invalidate_cache(self, pattern: Optional[str] = None):
        """
        Invalida cache (chamar após writes).

        Args:
            pattern: Padrão de chave para invalidar (None = tudo)
        """
        if pattern:
            # TODO: Implementar invalidação seletiva
            pass
        else:
            self.cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache."""
        return self.cache.get_stats()


# Instância global
neo4j_cached = Neo4jCachedQueries()