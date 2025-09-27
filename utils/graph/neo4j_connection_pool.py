"""
Pool de Conexões Neo4j Otimizado
=================================
Gerencia conexões eficientemente com reuso e health checks
"""

import os
import asyncio
import time
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
from neo4j import GraphDatabase, AsyncGraphDatabase
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Neo4jConnectionPool:
    """Pool de conexões otimizado para Neo4j."""

    _instance = None  # Singleton

    def __new__(cls):
        """Singleton pattern para pool global."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Inicializa pool (apenas uma vez)."""
        if self._initialized:
            return

        # Configuração
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")

        # Pool settings
        self.max_connection_lifetime = 3600  # 1 hora
        self.max_connection_pool_size = 50  # Máximo de conexões
        self.connection_acquisition_timeout = 60  # Timeout de aquisição
        self.connection_timeout = 30  # Timeout de conexão inicial
        self.keep_alive = True  # Mantém conexões vivas
        self.max_transaction_retry_time = 30

        # Criar driver com pool configurado
        self.driver = GraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password),
            max_connection_lifetime=self.max_connection_lifetime,
            max_connection_pool_size=self.max_connection_pool_size,
            connection_acquisition_timeout=self.connection_acquisition_timeout,
            connection_timeout=self.connection_timeout,
            keep_alive=self.keep_alive,
            max_transaction_retry_time=self.max_transaction_retry_time,
            encrypted=False  # Ajustar conforme ambiente
        )

        # Estatísticas
        self.stats = {
            "sessions_created": 0,
            "sessions_closed": 0,
            "queries_executed": 0,
            "total_query_time_ms": 0,
            "errors": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }

        # Cache de queries (para queries idempotentes)
        self.query_cache: Dict[str, tuple] = {}  # (result, timestamp)
        self.cache_ttl = 300  # 5 minutos

        self._initialized = True
        logger.info(f"✅ Neo4j Connection Pool initialized: {self.uri}")

    @asynccontextmanager
    async def get_session(self, database: str = "neo4j"):
        """
        Context manager para obter sessão do pool.

        Uso:
            async with pool.get_session() as session:
                result = await session.run("MATCH (n) RETURN n")
        """
        session = self.driver.session(database=database)
        self.stats["sessions_created"] += 1

        try:
            yield session
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Erro na sessão Neo4j: {e}")
            raise
        finally:
            await session.close()
            self.stats["sessions_closed"] += 1

    async def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        cache: bool = False,
        database: str = "neo4j"
    ):
        """
        Executa query com métricas e cache opcional.

        Args:
            query: Query Cypher
            parameters: Parâmetros da query
            cache: Se deve cachear resultado
            database: Nome do database

        Returns:
            Resultado da query
        """
        # Verificar cache
        if cache:
            cache_key = f"{query}:{str(parameters)}"
            cached = self.query_cache.get(cache_key)

            if cached:
                result, timestamp = cached
                age = time.time() - timestamp

                if age < self.cache_ttl:
                    self.stats["cache_hits"] += 1
                    logger.debug(f"Cache hit para query: {query[:50]}...")
                    return result

        # Executar query
        start_time = time.time()
        self.stats["queries_executed"] += 1

        async with self.get_session(database=database) as session:
            try:
                result = await session.run(query, parameters or {})
                records = [dict(record) async for record in result]

                # Medir tempo
                duration_ms = (time.time() - start_time) * 1000
                self.stats["total_query_time_ms"] += duration_ms

                # Log queries lentas
                if duration_ms > 1000:
                    logger.warning(
                        f"Query lenta ({duration_ms:.0f}ms): {query[:100]}..."
                    )

                # Cachear se solicitado
                if cache:
                    self.query_cache[cache_key] = (records, time.time())
                    self.stats["cache_misses"] += 1

                return records

            except Exception as e:
                self.stats["errors"] += 1
                logger.error(f"Erro executando query: {e}")
                logger.error(f"Query: {query}")
                logger.error(f"Parameters: {parameters}")
                raise

    async def execute_write(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: str = "neo4j"
    ):
        """
        Executa query de escrita (CREATE, MERGE, DELETE, etc).

        Args:
            query: Query Cypher
            parameters: Parâmetros da query
            database: Nome do database

        Returns:
            Resultado da query
        """
        # Invalidar cache ao escrever
        self.query_cache.clear()

        return await self.execute_query(
            query=query,
            parameters=parameters,
            cache=False,
            database=database
        )

    async def verify_connectivity(self) -> bool:
        """
        Verifica se conexão está funcionando.

        Returns:
            True se conectado
        """
        try:
            await self.execute_query("RETURN 1 as test")
            logger.info("✅ Neo4j conectado")
            return True
        except Exception as e:
            logger.error(f"❌ Neo4j desconectado: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do pool.

        Returns:
            Dicionário com estatísticas
        """
        avg_query_time = 0
        if self.stats["queries_executed"] > 0:
            avg_query_time = (
                self.stats["total_query_time_ms"] /
                self.stats["queries_executed"]
            )

        cache_hit_rate = 0
        total_cache_requests = (
            self.stats["cache_hits"] + self.stats["cache_misses"]
        )
        if total_cache_requests > 0:
            cache_hit_rate = (
                self.stats["cache_hits"] / total_cache_requests * 100
            )

        return {
            **self.stats,
            "avg_query_time_ms": round(avg_query_time, 2),
            "cache_hit_rate_percent": round(cache_hit_rate, 2),
            "cache_size": len(self.query_cache),
            "pool_config": {
                "max_pool_size": self.max_connection_pool_size,
                "max_lifetime": self.max_connection_lifetime,
                "acquisition_timeout": self.connection_acquisition_timeout
            }
        }

    async def close(self):
        """Fecha pool de conexões."""
        if hasattr(self, 'driver') and self.driver:
            await self.driver.close()
            logger.info("🔴 Neo4j Connection Pool fechado")

    def clear_cache(self):
        """Limpa cache de queries."""
        self.query_cache.clear()
        logger.info("🗑️  Cache de queries limpo")


# Instância global do pool
neo4j_pool = Neo4jConnectionPool()


# Funções auxiliares para facilitar uso
async def execute_read(query: str, parameters: Dict = None, cache: bool = False):
    """Executa query de leitura."""
    return await neo4j_pool.execute_query(query, parameters, cache=cache)


async def execute_write(query: str, parameters: Dict = None):
    """Executa query de escrita."""
    return await neo4j_pool.execute_write(query, parameters)


async def get_pool_stats():
    """Retorna estatísticas do pool."""
    return neo4j_pool.get_stats()