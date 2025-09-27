"""
Testes unitários para o sistema de Rate Limiting.
Testa janela deslizante, limites por IP e recuperação de rate limit.
"""

import pytest
import time
from unittest.mock import Mock, patch
from core.rate_limiter import EnhancedRateLimiter


class TestEnhancedRateLimiter:
    """Testes para o rate limiter melhorado."""

    def test_rate_limiter_initialization(self):
        """Testa inicialização do rate limiter."""
        limiter = EnhancedRateLimiter(max_requests=60, window_seconds=60)

        assert limiter.max_requests == 60
        assert limiter.window_seconds == 60
        assert len(limiter.requests) == 0

    def test_first_request_allowed(self):
        """Testa que primeira requisição é sempre permitida."""
        limiter = EnhancedRateLimiter(max_requests=5, window_seconds=60)

        result = limiter.check_rate_limit("192.168.1.1")
        assert result is True
        assert len(limiter.requests["192.168.1.1"]) == 1

    def test_rate_limit_enforcement(self):
        """Testa que limite de requisições é respeitado."""
        limiter = EnhancedRateLimiter(max_requests=3, window_seconds=60)
        client_ip = "192.168.1.1"

        # Primeiras 3 requisições devem passar
        for i in range(3):
            assert limiter.check_rate_limit(client_ip) is True

        # 4ª requisição deve ser bloqueada
        assert limiter.check_rate_limit(client_ip) is False

    def test_sliding_window_cleanup(self):
        """Testa limpeza de requisições antigas na janela deslizante."""
        limiter = EnhancedRateLimiter(max_requests=3, window_seconds=1)
        client_ip = "192.168.1.1"

        # Faz 3 requisições
        for i in range(3):
            limiter.check_rate_limit(client_ip)

        # Espera janela expirar
        time.sleep(1.1)

        # Nova requisição deve ser permitida após expiração
        assert limiter.check_rate_limit(client_ip) is True

    def test_multiple_clients_independent(self):
        """Testa que clientes diferentes têm limites independentes."""
        limiter = EnhancedRateLimiter(max_requests=2, window_seconds=60)

        client1 = "192.168.1.1"
        client2 = "192.168.1.2"

        # Client 1 atinge limite
        assert limiter.check_rate_limit(client1) is True
        assert limiter.check_rate_limit(client1) is True
        assert limiter.check_rate_limit(client1) is False

        # Client 2 deve ter limite próprio
        assert limiter.check_rate_limit(client2) is True
        assert limiter.check_rate_limit(client2) is True

    def test_get_retry_after(self):
        """Testa cálculo de tempo até próxima tentativa."""
        limiter = EnhancedRateLimiter(max_requests=2, window_seconds=60)
        client_ip = "192.168.1.1"

        # Faz requisições até limite
        limiter.check_rate_limit(client_ip)
        limiter.check_rate_limit(client_ip)

        # Verifica tempo de retry
        retry_after = limiter.get_retry_after(client_ip)
        assert 0 < retry_after <= 60

    def test_retry_after_empty_client(self):
        """Testa retry_after para cliente sem requisições."""
        limiter = EnhancedRateLimiter(max_requests=5, window_seconds=60)

        retry_after = limiter.get_retry_after("new-client")
        assert retry_after == 0

    def test_high_volume_requests(self):
        """Testa comportamento com alto volume de requisições."""
        limiter = EnhancedRateLimiter(max_requests=100, window_seconds=60)
        client_ip = "192.168.1.1"

        # Faz 100 requisições válidas
        for i in range(100):
            assert limiter.check_rate_limit(client_ip) is True

        # 101ª deve ser bloqueada
        assert limiter.check_rate_limit(client_ip) is False

    def test_concurrent_clients(self):
        """Testa múltiplos clientes simultâneos."""
        limiter = EnhancedRateLimiter(max_requests=5, window_seconds=60)

        clients = [f"192.168.1.{i}" for i in range(10)]

        for client in clients:
            for _ in range(5):
                assert limiter.check_rate_limit(client) is True
            # 6ª requisição bloqueada
            assert limiter.check_rate_limit(client) is False

    @pytest.mark.parametrize("max_requests,window_seconds", [
        (10, 30),
        (50, 60),
        (100, 120),
        (5, 10)
    ])
    def test_different_configurations(self, max_requests, window_seconds):
        """Testa diferentes configurações de rate limiting."""
        limiter = EnhancedRateLimiter(
            max_requests=max_requests,
            window_seconds=window_seconds
        )

        assert limiter.max_requests == max_requests
        assert limiter.window_seconds == window_seconds

    def test_edge_case_zero_window(self):
        """Testa caso extremo com janela zero."""
        limiter = EnhancedRateLimiter(max_requests=5, window_seconds=0)
        client_ip = "192.168.1.1"

        # Todas requisições devem ser limpas imediatamente
        for _ in range(10):
            result = limiter.check_rate_limit(client_ip)
            # Comportamento pode variar, mas não deve crashar
            assert isinstance(result, bool)

    def test_cleanup_old_requests_performance(self):
        """Testa performance da limpeza de requisições antigas."""
        limiter = EnhancedRateLimiter(max_requests=1000, window_seconds=1)
        client_ip = "192.168.1.1"

        # Adiciona muitas requisições
        for _ in range(500):
            limiter.check_rate_limit(client_ip)

        # Espera expiração
        time.sleep(1.1)

        # Verifica limpeza
        start = time.time()
        limiter.check_rate_limit(client_ip)
        elapsed = time.time() - start

        # Limpeza deve ser rápida (< 100ms)
        assert elapsed < 0.1

    def test_ipv6_addresses(self):
        """Testa suporte a endereços IPv6."""
        limiter = EnhancedRateLimiter(max_requests=3, window_seconds=60)
        ipv6 = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"

        for _ in range(3):
            assert limiter.check_rate_limit(ipv6) is True

        assert limiter.check_rate_limit(ipv6) is False

    def test_special_characters_in_ip(self):
        """Testa IPs com caracteres especiais (ex: proxies)."""
        limiter = EnhancedRateLimiter(max_requests=2, window_seconds=60)

        special_ips = [
            "192.168.1.1, 10.0.0.1",  # X-Forwarded-For
            "unknown",
            "::1",  # IPv6 localhost
        ]

        for ip in special_ips:
            assert limiter.check_rate_limit(ip) is True
            assert limiter.check_rate_limit(ip) is True
            assert limiter.check_rate_limit(ip) is False