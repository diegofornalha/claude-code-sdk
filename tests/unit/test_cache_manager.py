"""
Testes unitários para o Cache Manager.
Testa TTL, eviction policies, e gestão de memória.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from core.cache_manager import CacheManager, CacheStats


class TestCacheManager:
    """Testes para o gerenciador de cache."""

    @pytest.fixture
    def cache_manager(self):
        """Cria instância do cache manager."""
        return CacheManager(max_size=100, default_ttl=60)

    def test_cache_initialization(self, cache_manager):
        """Testa inicialização do cache."""
        assert cache_manager.max_size == 100
        assert cache_manager.default_ttl == 60
        assert cache_manager.size == 0

    async def test_set_and_get(self, cache_manager):
        """Testa operações básicas de set e get."""
        await cache_manager.set("key1", "value1")

        value = await cache_manager.get("key1")
        assert value == "value1"

    async def test_get_nonexistent_key(self, cache_manager):
        """Testa busca de chave inexistente."""
        value = await cache_manager.get("nonexistent")
        assert value is None

    async def test_ttl_expiration(self, cache_manager):
        """Testa expiração por TTL."""
        # Define TTL curto
        await cache_manager.set("key1", "value1", ttl=1)

        # Verifica valor imediatamente
        value = await cache_manager.get("key1")
        assert value == "value1"

        # Espera expiração
        await asyncio.sleep(1.1)

        # Valor deve ter expirado
        value = await cache_manager.get("key1")
        assert value is None

    async def test_update_existing_key(self, cache_manager):
        """Testa atualização de chave existente."""
        await cache_manager.set("key1", "value1")
        await cache_manager.set("key1", "value2")

        value = await cache_manager.get("key1")
        assert value == "value2"

    async def test_delete_key(self, cache_manager):
        """Testa deleção de chave."""
        await cache_manager.set("key1", "value1")

        result = await cache_manager.delete("key1")
        assert result is True

        value = await cache_manager.get("key1")
        assert value is None

    async def test_delete_nonexistent_key(self, cache_manager):
        """Testa deleção de chave inexistente."""
        result = await cache_manager.delete("nonexistent")
        assert result is False

    async def test_clear_all(self, cache_manager):
        """Testa limpeza completa do cache."""
        await cache_manager.set("key1", "value1")
        await cache_manager.set("key2", "value2")
        await cache_manager.set("key3", "value3")

        await cache_manager.clear()

        assert cache_manager.size == 0
        assert await cache_manager.get("key1") is None
        assert await cache_manager.get("key2") is None

    async def test_max_size_enforcement(self):
        """Testa enforcement do tamanho máximo."""
        cache = CacheManager(max_size=3, default_ttl=60)

        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.set("key3", "value3")

        assert cache.size == 3

        # Adicionar 4º item deve remover o mais antigo
        await cache.set("key4", "value4")

        assert cache.size == 3
        assert await cache.get("key1") is None  # Mais antigo removido
        assert await cache.get("key4") == "value4"

    async def test_lru_eviction(self):
        """Testa política de eviction LRU."""
        cache = CacheManager(max_size=3, default_ttl=60)

        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.set("key3", "value3")

        # Acessa key1 para torná-la recente
        await cache.get("key1")

        # Adiciona nova chave, key2 deve ser removida (menos recente)
        await cache.set("key4", "value4")

        assert await cache.get("key1") == "value1"
        assert await cache.get("key2") is None
        assert await cache.get("key4") == "value4"

    async def test_cache_stats(self, cache_manager):
        """Testa coleta de estatísticas."""
        await cache_manager.set("key1", "value1")
        await cache_manager.get("key1")  # hit
        await cache_manager.get("key2")  # miss

        stats = cache_manager.get_stats()

        assert isinstance(stats, CacheStats)
        assert stats.hits > 0
        assert stats.misses > 0
        assert stats.size == 1

    async def test_has_key(self, cache_manager):
        """Testa verificação de existência de chave."""
        await cache_manager.set("key1", "value1")

        assert await cache_manager.has("key1") is True
        assert await cache_manager.has("nonexistent") is False

    async def test_get_many(self, cache_manager):
        """Testa busca múltipla de chaves."""
        await cache_manager.set("key1", "value1")
        await cache_manager.set("key2", "value2")
        await cache_manager.set("key3", "value3")

        values = await cache_manager.get_many(["key1", "key2", "key4"])

        assert values == {
            "key1": "value1",
            "key2": "value2",
            "key4": None
        }

    async def test_set_many(self, cache_manager):
        """Testa inserção múltipla de chaves."""
        items = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        }

        await cache_manager.set_many(items)

        assert await cache_manager.get("key1") == "value1"
        assert await cache_manager.get("key2") == "value2"
        assert await cache_manager.get("key3") == "value3"

    async def test_custom_ttl_per_key(self, cache_manager):
        """Testa TTL customizado por chave."""
        await cache_manager.set("key1", "value1", ttl=1)
        await cache_manager.set("key2", "value2", ttl=10)

        await asyncio.sleep(1.1)

        assert await cache_manager.get("key1") is None
        assert await cache_manager.get("key2") == "value2"

    async def test_namespace_isolation(self, cache_manager):
        """Testa isolamento por namespace."""
        await cache_manager.set("user:1:profile", {"name": "John"})
        await cache_manager.set("user:2:profile", {"name": "Jane"})

        # Busca por namespace
        keys = cache_manager.get_keys_by_namespace("user:1:")

        assert "user:1:profile" in keys
        assert "user:2:profile" not in keys

    async def test_concurrent_access(self, cache_manager):
        """Testa acesso concorrente ao cache."""
        async def set_values(start, end):
            for i in range(start, end):
                await cache_manager.set(f"key{i}", f"value{i}")

        # Executa operações concorrentes
        await asyncio.gather(
            set_values(0, 50),
            set_values(50, 100)
        )

        # Verifica integridade
        for i in range(100):
            value = await cache_manager.get(f"key{i}")
            assert value == f"value{i}" or value is None

    async def test_cache_invalidation_pattern(self, cache_manager):
        """Testa invalidação por padrão."""
        await cache_manager.set("user:1:profile", "data1")
        await cache_manager.set("user:1:settings", "data2")
        await cache_manager.set("user:2:profile", "data3")

        # Invalida todas chaves do user:1
        await cache_manager.invalidate_pattern("user:1:*")

        assert await cache_manager.get("user:1:profile") is None
        assert await cache_manager.get("user:1:settings") is None
        assert await cache_manager.get("user:2:profile") == "data3"

    @pytest.mark.parametrize("value_type,value", [
        ("string", "test"),
        ("int", 123),
        ("float", 123.45),
        ("list", [1, 2, 3]),
        ("dict", {"key": "value"}),
        ("bool", True),
        ("none", None)
    ])
    async def test_different_value_types(self, cache_manager, value_type, value):
        """Testa armazenamento de diferentes tipos de valores."""
        await cache_manager.set(f"key_{value_type}", value)
        result = await cache_manager.get(f"key_{value_type}")
        assert result == value

    async def test_memory_pressure_handling(self):
        """Testa comportamento sob pressão de memória."""
        cache = CacheManager(max_size=10, default_ttl=60)

        # Adiciona muitos itens
        for i in range(20):
            await cache.set(f"key{i}", f"value{i}" * 1000)  # Valores grandes

        # Cache deve manter tamanho máximo
        assert cache.size <= 10

    async def test_get_or_set(self, cache_manager):
        """Testa operação get_or_set."""
        async def compute_value():
            await asyncio.sleep(0.1)
            return "computed_value"

        # Primeira chamada deve computar
        value = await cache_manager.get_or_set("key1", compute_value)
        assert value == "computed_value"

        # Segunda chamada deve usar cache
        start = time.time()
        value = await cache_manager.get_or_set("key1", compute_value)
        elapsed = time.time() - start

        assert value == "computed_value"
        assert elapsed < 0.05  # Deve ser rápido (do cache)