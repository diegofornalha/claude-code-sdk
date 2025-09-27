"""
Testes de carga e performance.
Mede desempenho sob alta carga.
"""

import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from httpx import AsyncClient


@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.asyncio
class TestPerformance:
    """Suite de testes de performance e carga."""

    async def test_concurrent_health_checks(self, async_client):
        """Testa múltiplas requisições health check simultâneas."""
        num_requests = 100
        start_time = time.time()

        tasks = [async_client.get("/api/health") for _ in range(num_requests)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        elapsed_time = time.time() - start_time

        # Contar sucessos
        successful = sum(1 for r in responses if hasattr(r, 'status_code') and r.status_code == 200)

        # Métricas
        print(f"\n📊 Performance Metrics:")
        print(f"   Total requests: {num_requests}")
        print(f"   Successful: {successful}")
        print(f"   Failed: {num_requests - successful}")
        print(f"   Total time: {elapsed_time:.2f}s")
        print(f"   Requests/sec: {num_requests / elapsed_time:.2f}")
        print(f"   Avg time per request: {(elapsed_time / num_requests) * 1000:.2f}ms")

        # Assertions
        assert successful >= num_requests * 0.95  # 95% de sucesso mínimo
        assert elapsed_time < 10.0  # Menos de 10 segundos

    async def test_session_creation_performance(self, async_client):
        """Testa performance de criação de sessões."""
        num_sessions = 50
        start_time = time.time()

        tasks = [
            async_client.post("/api/sessions", json={"project_id": f"perf-test-{i}"})
            for i in range(num_sessions)
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        elapsed_time = time.time() - start_time

        # Contar sucessos
        successful = sum(1 for r in responses if hasattr(r, 'status_code') and r.status_code == 200)

        print(f"\n📊 Session Creation Performance:")
        print(f"   Sessions created: {successful}/{num_sessions}")
        print(f"   Total time: {elapsed_time:.2f}s")
        print(f"   Avg time per session: {(elapsed_time / num_sessions) * 1000:.2f}ms")

        assert successful >= num_sessions * 0.9  # 90% de sucesso

    async def test_endpoint_response_time(self, async_client):
        """Testa tempo de resposta de endpoints críticos."""
        endpoints = [
            "/api/health",
            "/api/sdk-status",
            "/api/sessions",
            "/api/capabilities"
        ]

        response_times = {}

        for endpoint in endpoints:
            times = []
            for _ in range(10):
                start = time.time()
                response = await async_client.get(endpoint)
                elapsed = (time.time() - start) * 1000  # ms

                if response.status_code == 200:
                    times.append(elapsed)

            if times:
                avg_time = sum(times) / len(times)
                max_time = max(times)
                min_time = min(times)

                response_times[endpoint] = {
                    "avg": avg_time,
                    "max": max_time,
                    "min": min_time
                }

        print(f"\n📊 Endpoint Response Times:")
        for endpoint, times in response_times.items():
            print(f"   {endpoint}:")
            print(f"      Avg: {times['avg']:.2f}ms")
            print(f"      Min: {times['min']:.2f}ms")
            print(f"      Max: {times['max']:.2f}ms")

        # Todos os endpoints devem responder em menos de 1 segundo em média
        for times in response_times.values():
            assert times['avg'] < 1000.0

    async def test_memory_usage_under_load(self, async_client):
        """Testa uso de memória sob carga."""
        import psutil
        import os

        process = psutil.Process(os.getpid())

        # Memória inicial
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Criar muitas sessões
        num_sessions = 100
        tasks = [
            async_client.post("/api/sessions", json={"project_id": f"mem-test-{i}"})
            for i in range(num_sessions)
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

        # Memória após carga
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        print(f"\n📊 Memory Usage:")
        print(f"   Initial: {initial_memory:.2f}MB")
        print(f"   Final: {final_memory:.2f}MB")
        print(f"   Increase: {memory_increase:.2f}MB")
        print(f"   Per session: {memory_increase / num_sessions:.2f}MB")

        # Não deve consumir mais de 500MB de memória adicional
        assert memory_increase < 500.0

    async def test_rate_limiter_performance(self, async_client):
        """Testa performance do rate limiter."""
        num_requests = 100
        start_time = time.time()

        tasks = [async_client.get("/api/health") for _ in range(num_requests)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        elapsed_time = time.time() - start_time

        # Contar rate limits
        rate_limited = sum(
            1 for r in responses
            if hasattr(r, 'status_code') and r.status_code == 429
        )

        print(f"\n📊 Rate Limiter Performance:")
        print(f"   Total requests: {num_requests}")
        print(f"   Rate limited: {rate_limited}")
        print(f"   Allowed: {num_requests - rate_limited}")

        # Rate limiter deve estar funcionando
        assert rate_limited > 0  # Deve ter limitado alguma requisição

    @pytest.mark.skip(reason="Teste muito pesado, executar manualmente")
    async def test_stress_test(self, async_client):
        """Teste de stress extremo - executar manualmente."""
        num_concurrent = 500
        num_rounds = 10

        total_success = 0
        total_failed = 0

        print(f"\n🔥 Stress Test - {num_concurrent * num_rounds} requests")

        for round_num in range(num_rounds):
            tasks = [async_client.get("/api/health") for _ in range(num_concurrent)]
            responses = await asyncio.gather(*tasks, return_exceptions=True)

            success = sum(1 for r in responses if hasattr(r, 'status_code') and r.status_code == 200)
            failed = num_concurrent - success

            total_success += success
            total_failed += failed

            print(f"   Round {round_num + 1}: {success}/{num_concurrent} successful")

        print(f"\n📊 Total Results:")
        print(f"   Total successful: {total_success}")
        print(f"   Total failed: {total_failed}")
        print(f"   Success rate: {(total_success / (total_success + total_failed)) * 100:.2f}%")

        # Pelo menos 80% de sucesso em condições extremas
        assert total_success >= (total_success + total_failed) * 0.8