"""
Pacote de testes para Neo4j Agent API.

Organização:
- unit/: Testes unitários para componentes isolados
- integration/: Testes de integração de fluxos completos
- e2e/: Testes end-to-end
- performance/: Testes de carga e performance
- mocks/: Mocks reutilizáveis
- fixtures/: Dados de teste

Executar:
    pytest                    # Todos os testes
    pytest -m unit           # Apenas unitários
    pytest -m integration    # Apenas integração
    pytest --cov             # Com cobertura
"""

__version__ = "1.0.0"