"""
Execução Paralela de Queries Neo4j
===================================
Otimiza performance executando queries simultaneamente
"""

import asyncio
from typing import List, Dict, Any, Callable, Tuple
from utils.graph.neo4j_connection_pool import neo4j_pool
import time
import logging

logger = logging.getLogger(__name__)


class Neo4jParallelExecutor:
    """Executor paralelo de queries Neo4j."""

    @staticmethod
    async def execute_parallel(
        queries: List[Tuple[str, Dict[str, Any]]],
        max_concurrent: int = 10
    ) -> List[Any]:
        """
        Executa múltiplas queries em paralelo.

        Args:
            queries: Lista de tuplas (query, parameters)
            max_concurrent: Máximo de queries concorrentes

        Returns:
            Lista de resultados na mesma ordem

        Example:
            queries = [
                ("MATCH (n:Learning) RETURN count(n)", {}),
                ("MATCH ()-[r]->() RETURN count(r)", {}),
                ("MATCH (n:Learning {type: $type}) RETURN n", {"type": "concept"})
            ]
            results = await Neo4jParallelExecutor.execute_parallel(queries)
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def _execute_single(query: str, params: Dict) -> Any:
            """Executa query única com semáforo."""
            async with semaphore:
                return await neo4j_pool.execute_query(query, params)

        start_time = time.time()

        # Executar todas em paralelo
        tasks = [
            _execute_single(query, params)
            for query, params in queries
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        duration = (time.time() - start_time) * 1000
        logger.info(
            f"✅ Executadas {len(queries)} queries em paralelo em {duration:.0f}ms"
        )

        return results

    @staticmethod
    async def batch_create_nodes(
        nodes_data: List[Dict[str, Any]],
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        Cria múltiplos nós em batches paralelos.

        Args:
            nodes_data: Lista de propriedades dos nós
            batch_size: Tamanho de cada batch

        Returns:
            Estatísticas da criação
        """
        start_time = time.time()
        total_created = 0

        # Dividir em batches
        batches = [
            nodes_data[i:i + batch_size]
            for i in range(0, len(nodes_data), batch_size)
        ]

        async def _create_batch(batch: List[Dict]) -> int:
            """Cria um batch de nós."""
            query = """
                UNWIND $nodes as node_data
                CREATE (n:Learning)
                SET n = node_data
                RETURN count(n) as created
            """

            result = await neo4j_pool.execute_write(
                query,
                {"nodes": batch}
            )

            return result[0]["created"] if result else 0

        # Executar batches em paralelo
        results = await asyncio.gather(*[
            _create_batch(batch) for batch in batches
        ])

        total_created = sum(results)
        duration = (time.time() - start_time) * 1000

        return {
            "total_nodes_created": total_created,
            "batches": len(batches),
            "batch_size": batch_size,
            "duration_ms": duration,
            "nodes_per_second": int(total_created / (duration / 1000))
        }

    @staticmethod
    async def batch_create_relationships(
        relationships: List[Tuple[str, str, str, Dict]],
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        Cria múltiplos relacionamentos em batches.

        Args:
            relationships: Lista de (from_id, to_id, type, properties)
            batch_size: Tamanho de cada batch

        Returns:
            Estatísticas da criação
        """
        start_time = time.time()

        # Dividir em batches
        batches = [
            relationships[i:i + batch_size]
            for i in range(0, len(relationships), batch_size)
        ]

        async def _create_batch(batch: List[Tuple]) -> int:
            """Cria um batch de relacionamentos."""
            # Converter para formato adequado
            rel_data = [
                {
                    "from_id": from_id,
                    "to_id": to_id,
                    "type": rel_type,
                    "props": props
                }
                for from_id, to_id, rel_type, props in batch
            ]

            query = """
                UNWIND $rels as rel_data
                MATCH (from), (to)
                WHERE elementId(from) = rel_data.from_id
                  AND elementId(to) = rel_data.to_id
                CALL apoc.create.relationship(
                    from,
                    rel_data.type,
                    rel_data.props,
                    to
                ) YIELD rel
                RETURN count(rel) as created
            """

            result = await neo4j_pool.execute_write(
                query,
                {"rels": rel_data}
            )

            return result[0]["created"] if result else 0

        # Executar batches em paralelo
        results = await asyncio.gather(*[
            _create_batch(batch) for batch in batches
        ])

        total_created = sum(results)
        duration = (time.time() - start_time) * 1000

        return {
            "total_relationships_created": total_created,
            "batches": len(batches),
            "batch_size": batch_size,
            "duration_ms": duration,
            "rels_per_second": int(total_created / (duration / 1000))
        }

    @staticmethod
    async def parallel_aggregations(
        node_label: str = "Learning"
    ) -> Dict[str, Any]:
        """
        Executa múltiplas agregações em paralelo.

        Args:
            node_label: Label dos nós para agregar

        Returns:
            Dicionário com todas as agregações
        """
        queries = [
            # Total de nós
            (
                f"MATCH (n:{node_label}) RETURN count(n) as total",
                {}
            ),
            # Por tipo
            (
                f"""
                MATCH (n:{node_label})
                RETURN n.type as type, count(*) as count
                ORDER BY count DESC
                """,
                {}
            ),
            # Por usuário
            (
                f"""
                MATCH (n:{node_label})
                WHERE n.user IS NOT NULL
                RETURN n.user as user, count(*) as count
                ORDER BY count DESC
                LIMIT 10
                """,
                {}
            ),
            # Nós criados por mês
            (
                f"""
                MATCH (n:{node_label})
                WHERE n.created_at IS NOT NULL
                WITH date(n.created_at).year + '-' + date(n.created_at).month as month
                RETURN month, count(*) as count
                ORDER BY month DESC
                LIMIT 12
                """,
                {}
            ),
            # Relacionamentos totais
            (
                f"MATCH (:{node_label})-[r]->() RETURN count(r) as total_rels",
                {}
            )
        ]

        results = await Neo4jParallelExecutor.execute_parallel(queries)

        return {
            "total_nodes": results[0][0]["total"] if results[0] else 0,
            "by_type": results[1] if results[1] else [],
            "by_user": results[2] if results[2] else [],
            "by_month": results[3] if results[3] else [],
            "total_relationships": results[4][0]["total_rels"] if results[4] else 0
        }


# Exemplos de uso
async def example_parallel_queries():
    """Exemplo de uso de queries paralelas."""
    executor = Neo4jParallelExecutor()

    # Executar múltiplas queries simultaneamente
    queries = [
        ("MATCH (n:Learning) RETURN count(n) as total", {}),
        ("MATCH ()-[r:RELATES_TO]->() RETURN count(r) as rels", {}),
        ("MATCH (n:Learning {type: 'concept'}) RETURN n LIMIT 10", {})
    ]

    results = await executor.execute_parallel(queries)
    print(f"Resultados: {results}")


async def example_batch_insert():
    """Exemplo de inserção em batch."""
    executor = Neo4jParallelExecutor()

    # Criar 1000 nós em batches de 100
    nodes = [
        {
            "name": f"Node {i}",
            "type": "test",
            "value": i
        }
        for i in range(1000)
    ]

    stats = await executor.batch_create_nodes(nodes, batch_size=100)
    print(f"Criados: {stats}")