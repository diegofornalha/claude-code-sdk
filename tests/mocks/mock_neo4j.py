"""
Mocks para Neo4j.
Simula driver e sessões Neo4j para testes.
"""

from typing import List, Dict, Any, Optional
from unittest.mock import MagicMock


class MockNeo4jRecord:
    """Mock de Record do Neo4j."""

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    def __getitem__(self, key):
        return self._data.get(key)

    def data(self):
        return self._data

    def values(self):
        return list(self._data.values())

    def keys(self):
        return list(self._data.keys())


class MockNeo4jResult:
    """Mock de Result do Neo4j."""

    def __init__(self, records: List[Dict[str, Any]]):
        self._records = [MockNeo4jRecord(r) for r in records]
        self._index = 0

    def __iter__(self):
        return iter(self._records)

    def __next__(self):
        if self._index >= len(self._records):
            raise StopIteration
        record = self._records[self._index]
        self._index += 1
        return record

    def single(self):
        """Retorna único registro."""
        if len(self._records) == 0:
            return None
        return self._records[0]

    def data(self):
        """Retorna todos os dados."""
        return [r.data() for r in self._records]


class MockNeo4jSession:
    """Mock de Session do Neo4j."""

    def __init__(self, data: Optional[List[Dict]] = None):
        self._data = data or []
        self._closed = False

    def run(self, query: str, parameters: Optional[Dict] = None):
        """Simula execução de query."""
        # Retorna dados mockados baseado na query
        if "MATCH" in query or "CREATE" in query:
            return MockNeo4jResult(self._data)
        return MockNeo4jResult([])

    def close(self):
        """Fecha sessão."""
        self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class MockNeo4jDriver:
    """Mock de Driver do Neo4j."""

    def __init__(self, data: Optional[List[Dict]] = None):
        self._data = data or []
        self._closed = False

    def session(self, **kwargs):
        """Cria nova sessão."""
        return MockNeo4jSession(self._data)

    def close(self):
        """Fecha driver."""
        self._closed = True

    def verify_connectivity(self):
        """Verifica conectividade."""
        return True


class MockNeo4jMemoryStore:
    """Mock de store de memórias no Neo4j."""

    def __init__(self):
        self.memories: Dict[str, Dict] = {}
        self.connections: List[Dict] = []

    def create_memory(self, label: str, properties: Dict):
        """Cria memória."""
        memory_id = f"mem_{len(self.memories)}"
        self.memories[memory_id] = {
            "id": memory_id,
            "label": label,
            **properties
        }
        return memory_id

    def get_memory(self, memory_id: str):
        """Obtém memória."""
        return self.memories.get(memory_id)

    def search_memories(self, query: str, label: Optional[str] = None):
        """Busca memórias."""
        results = []
        for mem in self.memories.values():
            if label and mem.get("label") != label:
                continue
            # Busca simples por query no nome
            if query.lower() in mem.get("name", "").lower():
                results.append(mem)
        return results

    def create_connection(self, from_id: str, to_id: str, connection_type: str):
        """Cria conexão entre memórias."""
        connection = {
            "from": from_id,
            "to": to_id,
            "type": connection_type
        }
        self.connections.append(connection)
        return connection

    def get_connections(self, memory_id: str):
        """Obtém conexões de uma memória."""
        return [
            c for c in self.connections
            if c["from"] == memory_id or c["to"] == memory_id
        ]


def create_mock_driver(sample_data: Optional[List[Dict]] = None):
    """Factory para criar mock driver com dados de teste."""
    return MockNeo4jDriver(sample_data)


def create_mock_memory_store():
    """Factory para criar mock memory store."""
    return MockNeo4jMemoryStore()