#!/bin/bash

echo "🚀 Iniciando Neo4j Agent Backend com alta capacidade..."

# Configurações de ambiente para performance
export PYTHONUNBUFFERED=1
export PYTHONASYNCIODEBUG=0
export MALLOC_ARENA_MAX=2

# Limites do sistema
ulimit -n 65536  # Aumenta file descriptors
ulimit -u 32768  # Aumenta processos

# CPU affinity (usar todos os cores)
taskset -c 0-$(nproc --all) \

# Inicia servidor com Gunicorn + Uvicorn workers
gunicorn server:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers $(( $(nproc) * 2 )) \
    --worker-connections 2000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 600 \
    --keep-alive 75 \
    --bind 0.0.0.0:8888 \
    --backlog 2048 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --preload
