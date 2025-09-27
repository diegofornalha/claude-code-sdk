#!/bin/bash

# Script para executar testes do Neo4j Agent API
# Uso: ./scripts/run_tests.sh [tipo] [opções]

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Sem cor

echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${BLUE}    Neo4j Agent API - Test Runner${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"

# Função de ajuda
show_help() {
    echo ""
    echo "Uso: ./scripts/run_tests.sh [TIPO] [OPÇÕES]"
    echo ""
    echo "TIPOS:"
    echo "  all          - Executa todos os testes (padrão)"
    echo "  unit         - Apenas testes unitários"
    echo "  integration  - Apenas testes de integração"
    echo "  performance  - Apenas testes de performance"
    echo "  security     - Apenas testes de segurança"
    echo "  quick        - Testes rápidos (sem slow e performance)"
    echo ""
    echo "OPÇÕES:"
    echo "  -c, --coverage   - Gera relatório de cobertura"
    echo "  -v, --verbose    - Output verboso"
    echo "  -h, --help       - Mostra esta ajuda"
    echo "  -p, --parallel   - Executa testes em paralelo"
    echo "  --html          - Gera relatório HTML"
    echo ""
    echo "Exemplos:"
    echo "  ./scripts/run_tests.sh                    # Todos os testes"
    echo "  ./scripts/run_tests.sh unit -c            # Unit tests com cobertura"
    echo "  ./scripts/run_tests.sh integration -v     # Integration com verbose"
    echo "  ./scripts/run_tests.sh quick -p           # Testes rápidos em paralelo"
    echo ""
}

# Parse argumentos
TEST_TYPE="all"
COVERAGE=""
VERBOSE=""
PARALLEL=""
HTML_REPORT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        all|unit|integration|performance|security|quick)
            TEST_TYPE="$1"
            shift
            ;;
        -c|--coverage)
            COVERAGE="--cov=core --cov=server --cov-report=term-missing --cov-report=html"
            shift
            ;;
        -v|--verbose)
            VERBOSE="-vv"
            shift
            ;;
        -p|--parallel)
            PARALLEL="-n auto"
            shift
            ;;
        --html)
            HTML_REPORT="--html=test-report.html --self-contained-html"
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Opção desconhecida: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Verificar se pytest está instalado
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}✗ pytest não encontrado${NC}"
    echo -e "${YELLOW}Instale as dependências: pip install -r tests/requirements-test.txt${NC}"
    exit 1
fi

# Configurar pytest command base
PYTEST_CMD="pytest"

# Adicionar opções
if [ -n "$VERBOSE" ]; then
    PYTEST_CMD="$PYTEST_CMD $VERBOSE"
else
    PYTEST_CMD="$PYTEST_CMD -v"
fi

if [ -n "$PARALLEL" ]; then
    PYTEST_CMD="$PYTEST_CMD $PARALLEL"
fi

if [ -n "$COVERAGE" ]; then
    PYTEST_CMD="$PYTEST_CMD $COVERAGE"
fi

if [ -n "$HTML_REPORT" ]; then
    PYTEST_CMD="$PYTEST_CMD $HTML_REPORT"
fi

# Executar testes baseado no tipo
echo ""
case $TEST_TYPE in
    all)
        echo -e "${GREEN}▶ Executando TODOS os testes...${NC}"
        $PYTEST_CMD tests/
        ;;
    unit)
        echo -e "${GREEN}▶ Executando testes UNITÁRIOS...${NC}"
        $PYTEST_CMD tests/unit/ -m unit
        ;;
    integration)
        echo -e "${GREEN}▶ Executando testes de INTEGRAÇÃO...${NC}"
        $PYTEST_CMD tests/integration/ -m integration
        ;;
    performance)
        echo -e "${YELLOW}▶ Executando testes de PERFORMANCE (pode demorar)...${NC}"
        $PYTEST_CMD tests/performance/ -m performance
        ;;
    security)
        echo -e "${GREEN}▶ Executando testes de SEGURANÇA...${NC}"
        $PYTEST_CMD tests/ -m security
        ;;
    quick)
        echo -e "${GREEN}▶ Executando testes RÁPIDOS...${NC}"
        $PYTEST_CMD tests/ -m "not slow and not performance"
        ;;
esac

# Verificar resultado
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}    ✓ Todos os testes passaram!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"

    if [ -n "$COVERAGE" ]; then
        echo ""
        echo -e "${BLUE}📊 Relatório de cobertura gerado em: htmlcov/index.html${NC}"
    fi

    if [ -n "$HTML_REPORT" ]; then
        echo -e "${BLUE}📊 Relatório HTML gerado em: test-report.html${NC}"
    fi
else
    echo ""
    echo -e "${RED}═══════════════════════════════════════════════════${NC}"
    echo -e "${RED}    ✗ Alguns testes falharam${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════${NC}"
    exit 1
fi