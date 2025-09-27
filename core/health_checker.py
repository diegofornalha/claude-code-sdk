"""
Health Checker System
=====================
Monitora saúde de dependências e serviços
"""

import asyncio
import aiohttp
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging
from neo4j import AsyncGraphDatabase
from neo4j.exceptions import Neo4jError

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Status de saúde do serviço."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ServiceHealth:
    """Informações de saúde de um serviço."""

    def __init__(self, name: str):
        self.name = name
        self.status = HealthStatus.UNKNOWN
        self.last_check = None
        self.response_time = None
        self.error_message = None
        self.consecutive_failures = 0
        self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "name": self.name,
            "status": self.status.value,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "response_time_ms": self.response_time,
            "error": self.error_message,
            "consecutive_failures": self.consecutive_failures,
            "metadata": self.metadata
        }


class HealthChecker:
    """Sistema de health check para dependências."""

    def __init__(self, check_interval: int = 30):
        """
        Inicializa o health checker.

        Args:
            check_interval: Intervalo entre checks em segundos
        """
        self.check_interval = check_interval
        self.services: Dict[str, ServiceHealth] = {}
        self.check_task = None
        self.running = False

        # Thresholds
        self.RESPONSE_TIME_THRESHOLD_MS = 1000
        self.MAX_CONSECUTIVE_FAILURES = 3

    async def start(self):
        """Inicia o monitoramento de saúde."""
        if not self.running:
            self.running = True
            self.check_task = asyncio.create_task(self._check_loop())
            logger.info("Health checker iniciado")

    async def stop(self):
        """Para o monitoramento de saúde."""
        self.running = False
        if self.check_task:
            self.check_task.cancel()
            try:
                await self.check_task
            except asyncio.CancelledError:
                pass
        logger.info("Health checker parado")

    async def _check_loop(self):
        """Loop principal de verificação de saúde."""
        while self.running:
            try:
                await self.check_all_services()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Erro no health check loop: {e}")
                await asyncio.sleep(self.check_interval)

    async def check_all_services(self):
        """Verifica saúde de todos os serviços."""
        tasks = []

        # Neo4j
        tasks.append(self.check_neo4j())

        # Claude API (simulado)
        tasks.append(self.check_claude_api())

        # Sistema local
        tasks.append(self.check_system())

        # Executa todos os checks em paralelo
        await asyncio.gather(*tasks, return_exceptions=True)

    async def check_neo4j(self) -> ServiceHealth:
        """Verifica saúde do Neo4j."""
        service_name = "neo4j"

        if service_name not in self.services:
            self.services[service_name] = ServiceHealth(service_name)

        health = self.services[service_name]
        start_time = time.time()

        try:
            # Importa configurações
            import os
            from dotenv import load_dotenv
            load_dotenv()

            uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            username = os.getenv("NEO4J_USERNAME", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "password")

            # Testa conexão com Neo4j
            driver = AsyncGraphDatabase.driver(uri, auth=(username, password))

            async with driver.session() as session:
                result = await session.run("RETURN 1 as health")
                record = await result.single()

                if record and record["health"] == 1:
                    response_time = (time.time() - start_time) * 1000
                    health.response_time = response_time
                    health.last_check = datetime.now()
                    health.error_message = None
                    health.consecutive_failures = 0

                    # Determina status baseado no tempo de resposta
                    if response_time < self.RESPONSE_TIME_THRESHOLD_MS:
                        health.status = HealthStatus.HEALTHY
                    else:
                        health.status = HealthStatus.DEGRADED
                        health.metadata["warning"] = "High response time"
                else:
                    raise Exception("Unexpected response from Neo4j")

            await driver.close()

        except Exception as e:
            health.status = HealthStatus.UNHEALTHY
            health.last_check = datetime.now()
            health.error_message = str(e)
            health.consecutive_failures += 1
            health.response_time = None

            logger.error(f"Neo4j health check failed: {e}")

        return health

    async def check_claude_api(self) -> ServiceHealth:
        """Verifica saúde da API do Claude (simulado)."""
        service_name = "claude_api"

        if service_name not in self.services:
            self.services[service_name] = ServiceHealth(service_name)

        health = self.services[service_name]
        start_time = time.time()

        try:
            # Simula check da API
            # Em produção, faria uma chamada real para API de health
            await asyncio.sleep(0.01)  # Simula latência

            response_time = (time.time() - start_time) * 1000
            health.response_time = response_time
            health.last_check = datetime.now()
            health.status = HealthStatus.HEALTHY
            health.error_message = None
            health.consecutive_failures = 0

        except Exception as e:
            health.status = HealthStatus.UNHEALTHY
            health.last_check = datetime.now()
            health.error_message = str(e)
            health.consecutive_failures += 1

        return health

    async def check_system(self) -> ServiceHealth:
        """Verifica saúde do sistema local."""
        service_name = "system"

        if service_name not in self.services:
            self.services[service_name] = ServiceHealth(service_name)

        health = self.services[service_name]

        try:
            import psutil

            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)

            # Memória
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Disco
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent

            health.metadata = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent
            }

            health.last_check = datetime.now()
            health.error_message = None
            health.consecutive_failures = 0

            # Determina status baseado em recursos
            if cpu_percent > 90 or memory_percent > 90 or disk_percent > 90:
                health.status = HealthStatus.DEGRADED
                health.metadata["warning"] = "High resource usage"
            else:
                health.status = HealthStatus.HEALTHY

        except Exception as e:
            health.status = HealthStatus.UNKNOWN
            health.error_message = str(e)
            health.consecutive_failures += 1
            logger.warning(f"System health check failed: {e}")

        return health

    async def get_health_status(self) -> Dict[str, Any]:
        """Retorna status de saúde consolidado."""
        # Executa check se necessário
        if not self.services:
            await self.check_all_services()

        # Determina status geral
        all_statuses = [s.status for s in self.services.values()]

        if all(s == HealthStatus.HEALTHY for s in all_statuses):
            overall_status = HealthStatus.HEALTHY
        elif any(s == HealthStatus.UNHEALTHY for s in all_statuses):
            overall_status = HealthStatus.UNHEALTHY
        elif any(s == HealthStatus.DEGRADED for s in all_statuses):
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.UNKNOWN

        return {
            "status": overall_status.value,
            "timestamp": datetime.now().isoformat(),
            "services": {
                name: service.to_dict()
                for name, service in self.services.items()
            }
        }

    async def is_service_healthy(self, service_name: str) -> bool:
        """Verifica se um serviço específico está saudável."""
        if service_name not in self.services:
            return False

        service = self.services[service_name]

        # Considera saudável se não há muitas falhas consecutivas
        if service.consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES:
            return False

        return service.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]


# Instância global
health_checker = HealthChecker()


# Decorator para health check
def require_healthy_service(service_name: str):
    """
    Decorator que verifica se serviço está saudável antes de executar.

    Uso:
        @require_healthy_service("neo4j")
        async def query_database():
            pass
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if not await health_checker.is_service_healthy(service_name):
                raise Exception(f"Service {service_name} is not healthy")
            return await func(*args, **kwargs)

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper

    return decorator