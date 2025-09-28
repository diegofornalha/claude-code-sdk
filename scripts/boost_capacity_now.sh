#!/bin/bash

echo "🚀 BOOST DE CAPACIDADE DO BACKEND NEO4J AGENT"
echo "============================================="

# 1. MATA SERVIDOR ATUAL
echo "⏹️ Parando servidor atual..."
lsof -ti:8080 | xargs kill -9 2>/dev/null
sleep 2

# 2. CONFIGURAÇÕES DE SISTEMA
echo "⚙️ Aplicando configurações de sistema..."

# Aumenta file descriptors
ulimit -n 65536

# Aumenta processos
ulimit -u 32768

# Configura variáveis de ambiente
export PYTHONUNBUFFERED=1
export PYTHONASYNCIODEBUG=0
export MALLOC_ARENA_MAX=2

# Configurações de alta capacidade
export MAX_WORKERS=16
export CONNECTION_POOL_SIZE=50
export MAX_CONCURRENT_SESSIONS=100
export REQUEST_TIMEOUT=600
export CACHE_SIZE_MB=512

echo "✅ Configurações aplicadas:"
echo "   • Max Workers: $MAX_WORKERS"
echo "   • Pool de Conexões: $CONNECTION_POOL_SIZE"
echo "   • Sessões Simultâneas: $MAX_CONCURRENT_SESSIONS"
echo "   • Timeout: ${REQUEST_TIMEOUT}s"
echo "   • Cache: ${CACHE_SIZE_MB}MB"

# 3. INICIA SERVIDOR OTIMIZADO
echo ""
echo "🚀 Iniciando servidor com alta capacidade..."

cd /Users/2a/Desktop/neo4j-agent/api

# Verifica se tem gunicorn
if command -v gunicorn &> /dev/null; then
    echo "✅ Usando Gunicorn (melhor performance)"

    gunicorn server:app \
        --worker-class uvicorn.workers.UvicornWorker \
        --workers 4 \
        --worker-connections 1000 \
        --timeout 600 \
        --keep-alive 75 \
        --bind 0.0.0.0:8080 \
        --log-level info
else
    echo "⚠️ Gunicorn não encontrado, usando Python direto"
    echo "💡 Instale com: pip3 install gunicorn uvloop"

    # Fallback para Python direto com otimizações
    python3 -O -u server.py
fi