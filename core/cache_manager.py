"""
Sistema de Cache Inteligente
============================
Cache com TTL, LRU e invalidação automática
"""

import time
import json
import hashlib
import gzip
import pickle
from typing import Any, Optional, Dict, Callable
from collections import OrderedDict
import threading


class CacheManager:
    """Gerenciador de cache com estratégias avançadas."""

    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: int = 300,
        enable_stats: bool = True,
        compression_threshold: int = 1024  # Compressão para valores > 1KB
    ):
        """
        Inicializa o cache manager.

        Args:
            max_size: Tamanho máximo do cache
            default_ttl: Time-to-live padrão em segundos
            enable_stats: Habilitar estatísticas
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.enable_stats = enable_stats
        self.compression_threshold = compression_threshold

        # Cache LRU implementado com OrderedDict
        self.cache: OrderedDict = OrderedDict()
        self.ttl_data: Dict[str, float] = {}
        self.compressed_keys: set = set()  # Rastreia chaves comprimidas

        # Lock para thread-safety
        self.lock = threading.RLock()

        # Estatísticas
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expirations": 0,
            "total_requests": 0
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém valor do cache.

        Args:
            key: Chave do cache
            default: Valor padrão se não encontrado

        Returns:
            Valor cacheado ou default
        """
        with self.lock:
            self.stats["total_requests"] += 1

            # Verifica se existe
            if key not in self.cache:
                self.stats["misses"] += 1
                return default

            # Verifica TTL
            if self._is_expired(key):
                self._remove(key)
                self.stats["expirations"] += 1
                self.stats["misses"] += 1
                return default

            # Move para o fim (LRU)
            self.cache.move_to_end(key)
            self.stats["hits"] += 1

            # Descomprime se necessário
            value = self.cache[key]
            if key in self.compressed_keys:
                value = self._decompress(value)

            return value

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[list] = None
    ) -> None:
        """
        Define valor no cache.

        Args:
            key: Chave do cache
            value: Valor a cachear
            ttl: Time-to-live específico (opcional)
            tags: Tags para invalidação em grupo
        """
        with self.lock:
            # Remove se já existe para atualizar posição
            if key in self.cache:
                del self.cache[key]
                if key in self.compressed_keys:
                    self.compressed_keys.remove(key)

            # Comprime se necessário
            stored_value = value
            if self._should_compress(value):
                stored_value = self._compress(value)
                self.compressed_keys.add(key)

            # Adiciona no fim
            self.cache[key] = stored_value

            # Define TTL
            ttl = ttl or self.default_ttl
            self.ttl_data[key] = time.time() + ttl

            # Eviction se necessário
            while len(self.cache) > self.max_size:
                self._evict_lru()

    def delete(self, key: str) -> bool:
        """Remove item do cache."""
        with self.lock:
            if key in self.cache:
                self._remove(key)
                return True
            return False

    def clear(self) -> None:
        """Limpa todo o cache."""
        with self.lock:
            self.cache.clear()
            self.ttl_data.clear()
            self.compressed_keys.clear()

    def _is_expired(self, key: str) -> bool:
        """Verifica se item expirou."""
        if key not in self.ttl_data:
            return True
        return time.time() > self.ttl_data[key]

    def _remove(self, key: str) -> None:
        """Remove item internamente."""
        if key in self.cache:
            del self.cache[key]
        if key in self.ttl_data:
            del self.ttl_data[key]
        if key in self.compressed_keys:
            self.compressed_keys.remove(key)

    def _evict_lru(self) -> None:
        """Remove item menos recentemente usado."""
        if self.cache:
            key = next(iter(self.cache))
            self._remove(key)
            self.stats["evictions"] += 1

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache."""
        with self.lock:
            total = self.stats["total_requests"]
            hits = self.stats["hits"]

            return {
                **self.stats,
                "size": len(self.cache),
                "hit_rate": (hits / total * 100) if total > 0 else 0,
                "miss_rate": ((total - hits) / total * 100) if total > 0 else 0
            }

    def _should_compress(self, value: Any) -> bool:
        """Verifica se valor deve ser comprimido."""
        try:
            # Serializa para verificar tamanho
            serialized = pickle.dumps(value)
            return len(serialized) > self.compression_threshold
        except:
            return False

    def _compress(self, value: Any) -> bytes:
        """Comprime valor usando gzip."""
        serialized = pickle.dumps(value)
        return gzip.compress(serialized, compresslevel=1)  # Nível 1 para rapidez

    def _decompress(self, data: bytes) -> Any:
        """Descomprime valor."""
        decompressed = gzip.decompress(data)
        return pickle.loads(decompressed)

    def cleanup_expired(self) -> int:
        """Remove todos os itens expirados."""
        with self.lock:
            expired_keys = [
                key for key in self.cache
                if self._is_expired(key)
            ]

            for key in expired_keys:
                self._remove(key)

            return len(expired_keys)


class ResponseCache(CacheManager):
    """Cache especializado para respostas da API."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.invalidation_rules = {}

    def cache_key_for_request(
        self,
        endpoint: str,
        params: dict = None,
        body: dict = None
    ) -> str:
        """
        Gera chave de cache para requisição.

        Args:
            endpoint: Endpoint da API
            params: Query parameters
            body: Request body

        Returns:
            Chave de cache única
        """
        cache_data = {
            "endpoint": endpoint,
            "params": params or {},
            "body": body or {}
        }

        # Serializa e hash
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_str.encode()).hexdigest()

    def should_cache_response(self, status_code: int, endpoint: str) -> bool:
        """
        Determina se resposta deve ser cacheada.

        Args:
            status_code: Código HTTP da resposta
            endpoint: Endpoint da requisição

        Returns:
            True se deve cachear
        """
        # Não cacheia erros
        if status_code >= 400:
            return False

        # Endpoints que não devem ser cacheados
        no_cache_endpoints = [
            "/api/chat",  # Streaming não deve ser cacheado
            "/api/sessions/create",
            "/api/transaction"
        ]

        for pattern in no_cache_endpoints:
            if pattern in endpoint:
                return False

        return True

    def get_cached_response(
        self,
        endpoint: str,
        params: dict = None,
        body: dict = None
    ) -> Optional[Dict]:
        """
        Obtém resposta cacheada se disponível.

        Args:
            endpoint: Endpoint da API
            params: Query parameters
            body: Request body

        Returns:
            Resposta cacheada ou None
        """
        key = self.cache_key_for_request(endpoint, params, body)
        cached = self.get(key)

        if cached:
            # Adiciona header indicando cache hit
            cached["X-Cache"] = "HIT"
            cached["X-Cache-Key"] = key[:8]  # Primeiros 8 chars da chave

        return cached

    def cache_response(
        self,
        endpoint: str,
        response: dict,
        params: dict = None,
        body: dict = None,
        ttl: Optional[int] = None
    ) -> None:
        """
        Cacheia resposta da API.

        Args:
            endpoint: Endpoint da API
            response: Resposta a cachear
            params: Query parameters
            body: Request body
            ttl: Time-to-live específico
        """
        # Define TTL baseado no endpoint
        if ttl is None:
            endpoint_ttls = {
                "/api/health": 60,  # 1 minuto
                "/api/account": 300,  # 5 minutos
                "/api/stats": 120,  # 2 minutos
            }

            for pattern, endpoint_ttl in endpoint_ttls.items():
                if pattern in endpoint:
                    ttl = endpoint_ttl
                    break

        key = self.cache_key_for_request(endpoint, params, body)
        self.set(key, response, ttl)


class SmartCache(ResponseCache):
    """Cache inteligente com invalidação automática."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dependencies: Dict[str, set] = {}

    def set_with_dependencies(
        self,
        key: str,
        value: Any,
        depends_on: list,
        ttl: Optional[int] = None
    ):
        """
        Define valor com dependências para invalidação.

        Args:
            key: Chave do cache
            value: Valor a cachear
            depends_on: Lista de chaves de dependência
            ttl: Time-to-live
        """
        self.set(key, value, ttl)

        # Registra dependências
        for dep_key in depends_on:
            if dep_key not in self.dependencies:
                self.dependencies[dep_key] = set()
            self.dependencies[dep_key].add(key)

    def invalidate_dependencies(self, key: str):
        """
        Invalida cache de todas as dependências.

        Args:
            key: Chave que foi modificada
        """
        if key in self.dependencies:
            for dep_key in self.dependencies[key]:
                self.delete(dep_key)
            del self.dependencies[key]

    def warm_cache(self, data_loader: Callable, keys: list):
        """
        Pré-aquece o cache com dados.

        Args:
            data_loader: Função para carregar dados
            keys: Lista de chaves para pré-aquecer
        """
        for key in keys:
            if key not in self.cache:
                try:
                    value = data_loader(key)
                    if value is not None:
                        self.set(key, value)
                except Exception as e:
                    print(f"Failed to warm cache for {key}: {e}")


# Instâncias globais
cache_manager = SmartCache(
    max_size=1000,
    default_ttl=300,
    enable_stats=True
)

# Cache específico para respostas de AI
ai_response_cache = ResponseCache(
    max_size=100,
    default_ttl=600,  # 10 minutos para respostas AI
    enable_stats=True
)