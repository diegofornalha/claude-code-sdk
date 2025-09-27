"""
Middleware de Métricas e Monitoramento
======================================
Coleta métricas de performance e uso da API
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Dict, Any, Optional, Callable
import time
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
import json


class MetricsCollector:
    """Coletor centralizado de métricas."""

    def __init__(self, window_size: int = 1000):
        """
        Inicializa coletor de métricas.

        Args:
            window_size: Tamanho da janela de métricas recentes
        """
        self.window_size = window_size

        # Métricas por endpoint
        self.endpoint_metrics: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "count": 0,
                "total_time": 0.0,
                "min_time": float('inf'),
                "max_time": 0.0,
                "errors": 0,
                "status_codes": defaultdict(int)
            }
        )

        # Métricas recentes (janela deslizante)
        self.recent_requests: deque = deque(maxlen=window_size)

        # Métricas globais
        self.global_metrics = {
            "total_requests": 0,
            "total_errors": 0,
            "uptime_start": datetime.utcnow(),
            "active_requests": 0
        }

        # Lock para thread-safety
        self.lock = threading.RLock()

    def record_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        duration: float,
        error: Optional[str] = None
    ):
        """
        Registra métricas de uma requisição.

        Args:
            endpoint: Caminho do endpoint
            method: Método HTTP
            status_code: Código de status da resposta
            duration: Duração em segundos
            error: Mensagem de erro (opcional)
        """
        with self.lock:
            # Chave do endpoint
            key = f"{method}:{endpoint}"

            # Atualiza métricas do endpoint
            metrics = self.endpoint_metrics[key]
            metrics["count"] += 1
            metrics["total_time"] += duration
            metrics["min_time"] = min(metrics["min_time"], duration)
            metrics["max_time"] = max(metrics["max_time"], duration)
            metrics["status_codes"][status_code] += 1

            if status_code >= 400:
                metrics["errors"] += 1

            # Adiciona a janela recente
            self.recent_requests.append({
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "duration": duration,
                "timestamp": datetime.utcnow().isoformat(),
                "error": error
            })

            # Atualiza métricas globais
            self.global_metrics["total_requests"] += 1
            if status_code >= 400:
                self.global_metrics["total_errors"] += 1

    def get_endpoint_stats(self, endpoint: str = None) -> Dict[str, Any]:
        """
        Retorna estatísticas de endpoint(s).

        Args:
            endpoint: Endpoint específico (None para todos)

        Returns:
            Estatísticas formatadas
        """
        with self.lock:
            if endpoint:
                metrics = self.endpoint_metrics.get(endpoint, {})
                if not metrics:
                    return {"error": "Endpoint not found"}

                avg_time = (
                    metrics["total_time"] / metrics["count"]
                    if metrics["count"] > 0 else 0
                )

                return {
                    "endpoint": endpoint,
                    "requests": metrics["count"],
                    "avg_response_time_ms": round(avg_time * 1000, 2),
                    "min_response_time_ms": round(metrics["min_time"] * 1000, 2),
                    "max_response_time_ms": round(metrics["max_time"] * 1000, 2),
                    "errors": metrics["errors"],
                    "error_rate": (
                        metrics["errors"] / metrics["count"] * 100
                        if metrics["count"] > 0 else 0
                    ),
                    "status_codes": dict(metrics["status_codes"])
                }

            # Retorna estatísticas de todos os endpoints
            all_stats = {}
            for key, metrics in self.endpoint_metrics.items():
                avg_time = (
                    metrics["total_time"] / metrics["count"]
                    if metrics["count"] > 0 else 0
                )

                all_stats[key] = {
                    "requests": metrics["count"],
                    "avg_response_time_ms": round(avg_time * 1000, 2),
                    "errors": metrics["errors"],
                    "error_rate": (
                        metrics["errors"] / metrics["count"] * 100
                        if metrics["count"] > 0 else 0
                    )
                }

            return all_stats

    def get_global_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas globais."""
        with self.lock:
            uptime = datetime.utcnow() - self.global_metrics["uptime_start"]

            return {
                "total_requests": self.global_metrics["total_requests"],
                "total_errors": self.global_metrics["total_errors"],
                "error_rate": (
                    self.global_metrics["total_errors"] /
                    self.global_metrics["total_requests"] * 100
                    if self.global_metrics["total_requests"] > 0 else 0
                ),
                "uptime_seconds": uptime.total_seconds(),
                "uptime_formatted": str(uptime).split('.')[0],
                "active_requests": self.global_metrics["active_requests"],
                "requests_per_second": (
                    self.global_metrics["total_requests"] / uptime.total_seconds()
                    if uptime.total_seconds() > 0 else 0
                )
            }

    def get_recent_requests(self, limit: int = 100) -> list:
        """
        Retorna requisições recentes.

        Args:
            limit: Número máximo de requisições a retornar

        Returns:
            Lista de requisições recentes
        """
        with self.lock:
            return list(self.recent_requests)[-limit:]

    def get_slowest_endpoints(self, top_n: int = 5) -> list:
        """
        Retorna endpoints mais lentos.

        Args:
            top_n: Número de endpoints a retornar

        Returns:
            Lista de endpoints mais lentos
        """
        with self.lock:
            endpoint_times = []

            for key, metrics in self.endpoint_metrics.items():
                if metrics["count"] > 0:
                    avg_time = metrics["total_time"] / metrics["count"]
                    endpoint_times.append({
                        "endpoint": key,
                        "avg_time_ms": round(avg_time * 1000, 2),
                        "max_time_ms": round(metrics["max_time"] * 1000, 2),
                        "requests": metrics["count"]
                    })

            # Ordena por tempo médio
            endpoint_times.sort(key=lambda x: x["avg_time_ms"], reverse=True)
            return endpoint_times[:top_n]

    def reset(self):
        """Reseta todas as métricas."""
        with self.lock:
            self.endpoint_metrics.clear()
            self.recent_requests.clear()
            self.global_metrics = {
                "total_requests": 0,
                "total_errors": 0,
                "uptime_start": datetime.utcnow(),
                "active_requests": 0
            }


# Instância global
metrics_collector = MetricsCollector()


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware para coletar métricas de requisições."""

    def __init__(self, app: ASGIApp, collector: MetricsCollector = None):
        """
        Inicializa middleware.

        Args:
            app: Aplicação ASGI
            collector: Coletor de métricas (usa global se None)
        """
        super().__init__(app)
        self.collector = collector or metrics_collector

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Processa requisição e coleta métricas.

        Args:
            request: Request do FastAPI
            call_next: Próximo handler

        Returns:
            Response com headers de métricas
        """
        # Marca início
        start_time = time.time()
        self.collector.global_metrics["active_requests"] += 1

        error_message = None
        status_code = 500

        try:
            # Processa requisição
            response = await call_next(request)
            status_code = response.status_code

            return response

        except Exception as e:
            error_message = str(e)
            status_code = 500
            raise

        finally:
            # Calcula duração
            duration = time.time() - start_time

            # Registra métricas
            self.collector.record_request(
                endpoint=request.url.path,
                method=request.method,
                status_code=status_code,
                duration=duration,
                error=error_message
            )

            # Decrementa contador de requisições ativas
            self.collector.global_metrics["active_requests"] -= 1


class HealthChecker:
    """Verificador de saúde do sistema."""

    def __init__(self, collector: MetricsCollector):
        """
        Inicializa health checker.

        Args:
            collector: Coletor de métricas
        """
        self.collector = collector
        self.checks: Dict[str, Callable] = {}

    def register_check(self, name: str, check_func: Callable):
        """
        Registra uma verificação de saúde.

        Args:
            name: Nome da verificação
            check_func: Função que retorna True se saudável
        """
        self.checks[name] = check_func

    async def check_health(self) -> Dict[str, Any]:
        """
        Executa todas as verificações de saúde.

        Returns:
            Status de saúde do sistema
        """
        results = {}
        all_healthy = True

        for name, check_func in self.checks.items():
            try:
                if asyncio.iscoroutinefunction(check_func):
                    is_healthy = await check_func()
                else:
                    is_healthy = check_func()

                results[name] = {
                    "status": "healthy" if is_healthy else "unhealthy",
                    "healthy": is_healthy
                }

                if not is_healthy:
                    all_healthy = False

            except Exception as e:
                results[name] = {
                    "status": "error",
                    "healthy": False,
                    "error": str(e)
                }
                all_healthy = False

        # Adiciona métricas globais
        global_stats = self.collector.get_global_stats()

        return {
            "status": "healthy" if all_healthy else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": results,
            "metrics": global_stats
        }


# Instância global
health_checker = HealthChecker(metrics_collector)