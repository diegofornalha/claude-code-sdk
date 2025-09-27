"""
Sistema de Rate Limiting
========================
Protege API contra abuso e DDoS
"""

import time
from collections import defaultdict, deque, OrderedDict
from typing import Dict, Tuple, Optional
import hashlib
import json


class RateLimiter:
    """Rate limiter com sliding window e burst protection."""

    def __init__(
        self,
        requests_per_minute: int = 60,
        burst_size: int = 10,
        cleanup_interval: int = 300
    ):
        """
        Inicializa o rate limiter.

        Args:
            requests_per_minute: Máximo de requisições por minuto
            burst_size: Tamanho do burst permitido
            cleanup_interval: Intervalo para limpar IPs antigos (segundos)
        """
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.cleanup_interval = cleanup_interval

        # Usa OrderedDict para prevenir memory leak
        # Limita o número máximo de IPs rastreados
        self.MAX_TRACKED_IPS = 10000
        self.requests = OrderedDict()

        # Rastreamento de burst com limite
        self.burst_tracker = OrderedDict()

        # Último cleanup
        self.last_cleanup = time.time()

        # Blacklist temporária com OrderedDict
        self.blacklist = OrderedDict()

        # Estatísticas
        self.stats = {
            "total_requests": 0,
            "blocked_requests": 0,
            "unique_ips": set(),
            "blacklisted_ips": 0
        }

    def is_allowed(self, client_ip: str, endpoint: str = None) -> Tuple[bool, Optional[str]]:
        """
        Verifica se o cliente pode fazer a requisição.

        Args:
            client_ip: IP do cliente
            endpoint: Endpoint específico (opcional)

        Returns:
            (allowed, reason): Tupla com permitido e razão se bloqueado
        """
        current_time = time.time()

        # Cleanup periódico
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_data()

        # Limita número de IPs rastreados para prevenir memory leak
        if len(self.requests) > self.MAX_TRACKED_IPS:
            # Remove os IPs mais antigos (FIFO)
            for _ in range(100):  # Remove 100 IPs mais antigos
                if self.requests:
                    self.requests.popitem(last=False)

        # Verifica blacklist
        if client_ip in self.blacklist:
            if current_time < self.blacklist[client_ip]:
                self.stats["blocked_requests"] += 1
                remaining = int(self.blacklist[client_ip] - current_time)
                return False, f"IP blacklisted for {remaining} seconds"
            else:
                del self.blacklist[client_ip]

        # Obtém ou cria deque para requisições do IP
        if client_ip not in self.requests:
            self.requests[client_ip] = deque(maxlen=self.requests_per_minute)
        ip_requests = self.requests[client_ip]

        # Remove requisições antigas (sliding window)
        cutoff_time = current_time - 60  # 1 minuto
        while ip_requests and ip_requests[0] < cutoff_time:
            ip_requests.popleft()

        # Verifica limite por minuto
        if len(ip_requests) >= self.requests_per_minute:
            self.stats["blocked_requests"] += 1
            self._add_to_blacklist(client_ip, 60)  # Blacklist por 1 minuto
            return False, f"Rate limit exceeded: {self.requests_per_minute}/min"

        # Verifica burst protection
        burst_window = 5  # 5 segundos
        recent_requests = [t for t in ip_requests if t > current_time - burst_window]

        if len(recent_requests) >= self.burst_size:
            self.stats["blocked_requests"] += 1
            self._add_to_blacklist(client_ip, 30)  # Blacklist por 30 segundos
            return False, f"Burst limit exceeded: {self.burst_size} in {burst_window}s"

        # Adiciona nova requisição
        ip_requests.append(current_time)
        self.stats["total_requests"] += 1
        self.stats["unique_ips"].add(client_ip)

        return True, None

    def _add_to_blacklist(self, client_ip: str, duration: int):
        """Adiciona IP à blacklist temporária."""
        self.blacklist[client_ip] = time.time() + duration
        self.stats["blacklisted_ips"] += 1

    def _cleanup_old_data(self):
        """Limpa dados antigos para economizar memória."""
        current_time = time.time()
        cutoff_time = current_time - 3600  # 1 hora

        # Limpa requisições antigas
        for ip in list(self.requests.keys()):
            ip_requests = self.requests[ip]
            if not ip_requests or ip_requests[-1] < cutoff_time:
                del self.requests[ip]

        # Limpa blacklist expirada
        expired_ips = [
            ip for ip, exp_time in self.blacklist.items()
            if exp_time < current_time
        ]
        for ip in expired_ips:
            del self.blacklist[ip]

        self.last_cleanup = current_time

    def get_remaining_quota(self, client_ip: str) -> Dict[str, int]:
        """Retorna quota restante para o IP."""
        current_time = time.time()
        ip_requests = self.requests[client_ip]

        # Remove requisições antigas
        cutoff_time = current_time - 60
        valid_requests = [t for t in ip_requests if t > cutoff_time]

        return {
            "requests_remaining": self.requests_per_minute - len(valid_requests),
            "burst_remaining": self.burst_size - len([
                t for t in valid_requests if t > current_time - 5
            ]),
            "reset_in_seconds": 60
        }

    def reset_client(self, client_ip: str):
        """Reseta o contador de um cliente específico."""
        if client_ip in self.requests:
            del self.requests[client_ip]
        if client_ip in self.blacklist:
            del self.blacklist[client_ip]

    def get_stats(self) -> Dict:
        """Retorna estatísticas do rate limiter."""
        return {
            "total_requests": self.stats["total_requests"],
            "blocked_requests": self.stats["blocked_requests"],
            "unique_clients": len(self.stats["unique_ips"]),
            "currently_blacklisted": len(self.blacklist),
            "active_clients": len(self.requests),
            "block_rate": (
                self.stats["blocked_requests"] / self.stats["total_requests"]
                if self.stats["total_requests"] > 0 else 0
            ) * 100
        }


class AdvancedRateLimiter(RateLimiter):
    """Rate limiter avançado com features adicionais."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Diferentes limites por endpoint
        self.endpoint_limits = {
            "/api/chat": 30,  # Chat mais restritivo
            "/api/health": 120,  # Health check mais permissivo
            "/api/sessions": 60,
            "default": 60
        }

        # Whitelist de IPs
        self.whitelist = set([
            "127.0.0.1",
            "localhost",
            "::1"
        ])

        # Fingerprinting para detectar bots (com OrderedDict)
        self.fingerprints = OrderedDict()

    def is_allowed(self, client_ip: str, endpoint: str = None, headers: dict = None) -> Tuple[bool, Optional[str]]:
        """
        Verificação avançada com fingerprinting.

        Args:
            client_ip: IP do cliente
            endpoint: Endpoint sendo acessado
            headers: Headers da requisição para fingerprinting

        Returns:
            (allowed, reason): Tupla com permitido e razão se bloqueado
        """
        # Whitelist bypass
        if client_ip in self.whitelist:
            return True, None

        # Fingerprinting
        if headers:
            fingerprint = self._generate_fingerprint(headers)
            self.fingerprints[client_ip].add(fingerprint)

            # Detecta comportamento suspeito (muitos fingerprints diferentes)
            if len(self.fingerprints[client_ip]) > 10:
                self._add_to_blacklist(client_ip, 300)  # 5 minutos
                return False, "Suspicious behavior detected"

        # Ajusta limite baseado no endpoint
        if endpoint:
            original_limit = self.requests_per_minute
            self.requests_per_minute = self.endpoint_limits.get(
                endpoint,
                self.endpoint_limits["default"]
            )

        # Checa com rate limiter base
        allowed, reason = super().is_allowed(client_ip, endpoint)

        # Restaura limite original
        if endpoint:
            self.requests_per_minute = original_limit

        return allowed, reason

    def _generate_fingerprint(self, headers: dict) -> str:
        """Gera fingerprint baseado nos headers."""
        fingerprint_data = {
            "user_agent": headers.get("user-agent", ""),
            "accept": headers.get("accept", ""),
            "accept_encoding": headers.get("accept-encoding", ""),
            "accept_language": headers.get("accept-language", "")
        }

        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.md5(fingerprint_str.encode()).hexdigest()

    def add_to_whitelist(self, client_ip: str):
        """Adiciona IP à whitelist."""
        self.whitelist.add(client_ip)

    def remove_from_whitelist(self, client_ip: str):
        """Remove IP da whitelist."""
        self.whitelist.discard(client_ip)


# Instância global
rate_limiter = AdvancedRateLimiter(
    requests_per_minute=60,
    burst_size=10,
    cleanup_interval=300
)