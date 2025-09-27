# Suite de Testes - Neo4j Agent API

Suite completa de testes para o projeto Neo4j Agent API com cobertura mínima de 80%.

## 📁 Estrutura

```
tests/
├── conftest.py              # Configuração global e fixtures
├── pytest.ini               # Configuração do pytest
├── requirements-test.txt    # Dependências de teste
├── unit/                    # Testes unitários
│   ├── test_input_validator.py
│   ├── test_claude_handler.py
│   └── test_session_manager.py
├── integration/             # Testes de integração
│   ├── test_api_endpoints.py
│   ├── test_chat_flow.py
│   └── test_websocket.py
├── e2e/                     # Testes end-to-end
├── performance/             # Testes de carga
│   └── test_load.py
├── mocks/                   # Mocks reutilizáveis
│   ├── mock_claude_sdk.py
│   └── mock_neo4j.py
└── fixtures/                # Dados de teste
    └── sample_data.py
```

## 🚀 Executando Testes

### Instalar dependências
```bash
pip install -r requirements.txt
pip install -r tests/requirements-test.txt
```

### Executar todos os testes
```bash
pytest
```

### Executar por tipo
```bash
# Testes unitários apenas
pytest tests/unit/ -m unit

# Testes de integração
pytest tests/integration/ -m integration

# Testes de performance
pytest tests/performance/ -m performance -m slow
```

### Executar com cobertura
```bash
pytest --cov=core --cov=server --cov-report=html --cov-report=term
```

### Executar testes específicos
```bash
# Por arquivo
pytest tests/unit/test_input_validator.py

# Por classe
pytest tests/unit/test_input_validator.py::TestInputValidator

# Por método
pytest tests/unit/test_input_validator.py::TestInputValidator::test_xss_protection
```

### Executar em paralelo
```bash
pytest -n auto  # Usa todos os CPUs disponíveis
pytest -n 4     # Usa 4 workers
```

## 🏷️ Marcadores (Markers)

Os testes são organizados por marcadores:

- `@pytest.mark.unit` - Testes unitários (funções isoladas)
- `@pytest.mark.integration` - Testes de integração
- `@pytest.mark.e2e` - Testes end-to-end
- `@pytest.mark.api` - Testes de endpoints API
- `@pytest.mark.websocket` - Testes de WebSocket
- `@pytest.mark.security` - Testes de segurança
- `@pytest.mark.performance` - Testes de performance
- `@pytest.mark.slow` - Testes lentos (>5s)
- `@pytest.mark.neo4j` - Requer Neo4j rodando

### Executar por marcador
```bash
pytest -m unit
pytest -m "integration and not slow"
pytest -m "security"
```

## 📊 Cobertura de Código

Meta: **Mínimo 80% de cobertura**

### Visualizar cobertura
```bash
# Gerar relatório
pytest --cov=core --cov=server --cov-report=html

# Abrir no navegador
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Cobertura atual
```bash
pytest --cov=core --cov=server --cov-report=term-missing
```

## 🔧 Configuração

### pytest.ini
Configuração principal do pytest com marcadores e opções.

### conftest.py
Fixtures globais compartilhadas:
- `test_client` - Cliente FastAPI de teste
- `async_client` - Cliente async para testes de integração
- `mock_claude_client` - Mock do Claude SDK
- `mock_neo4j_driver` - Mock do Neo4j
- `input_validator` - Instância do validador
- `claude_handler` - Handler do Claude
- `session_manager` - Gerenciador de sessões

## 🧪 Tipos de Testes

### Unit Tests
Testam componentes isolados com mocks:
- `InputValidator` - Validação e sanitização
- `ClaudeHandler` - Gerenciamento de sessões
- `SessionManager` - Rastreamento de sessões

### Integration Tests
Testam fluxos completos da API:
- Endpoints REST
- Streaming SSE
- WebSocket bidirecional
- Rate limiting
- Security headers

### Performance Tests
Medem desempenho e carga:
- Requisições concorrentes
- Tempo de resposta
- Uso de memória
- Rate limiter

## 🛡️ Testes de Segurança

Protegem contra:
- XSS (Cross-Site Scripting)
- SQL Injection
- Path Traversal
- Command Injection
- Template Injection

## 🐳 Neo4j para Testes

### Docker
```bash
docker run -d \
  --name neo4j-test \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/testpassword \
  neo4j:5.15
```

### Configurar variáveis
```bash
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=testpassword
```

## 📈 CI/CD

GitHub Actions configurado em `.github/workflows/tests.yml`:

- ✅ Executa em Python 3.10, 3.11, 3.12
- ✅ Neo4j rodando como serviço
- ✅ Testes unitários + integração
- ✅ Cobertura de código
- ✅ Lint (flake8)
- ✅ Type checking (mypy)
- ✅ Security scan (bandit)
- ✅ Dependency check (safety)
- ✅ Upload de relatórios

## 📝 Escrevendo Novos Testes

### Template de teste unitário
```python
import pytest
from core.my_module import MyClass

@pytest.mark.unit
class TestMyClass:
    def test_my_function(self):
        # Arrange
        obj = MyClass()

        # Act
        result = obj.my_function()

        # Assert
        assert result == expected_value
```

### Template de teste async
```python
import pytest

@pytest.mark.asyncio
async def test_async_function(async_client):
    response = await async_client.get("/api/endpoint")
    assert response.status_code == 200
```

### Usando mocks
```python
from unittest.mock import Mock, patch

def test_with_mock(mock_claude_client):
    mock_claude_client.query.return_value = "mocked response"

    with patch('core.module.ClaudeClient', return_value=mock_claude_client):
        # Test code
        pass
```

## 🔍 Debugging Testes

### Executar com output detalhado
```bash
pytest -vv -s
```

### Parar no primeiro erro
```bash
pytest -x
```

### Executar último teste que falhou
```bash
pytest --lf
```

### Debugar com pdb
```bash
pytest --pdb
```

## 📚 Recursos

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)

## 🤝 Contribuindo

1. Sempre adicione testes para novo código
2. Mantenha cobertura acima de 80%
3. Use marcadores apropriados
4. Documente testes complexos
5. Execute testes localmente antes de commit

---

**Meta de Cobertura**: 80% mínimo
**Tempo Máximo por Teste**: 30s (exceto testes marcados como `slow`)