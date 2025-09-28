#!/usr/bin/env python3
"""
Script para iniciar o servidor com alta capacidade
Aplica otimizações sem modificar o código principal
"""

import os
import sys
import asyncio
import multiprocessing

# Configurações de alta performance
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['PYTHONASYNCIODEBUG'] = '0'

# Ajusta limite de file descriptors
import resource
soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
resource.setrlimit(resource.RLIMIT_NOFILE, (min(65536, hard), hard))

print("🚀 Iniciando servidor com configurações de alta capacidade...")
print(f"📊 CPUs disponíveis: {multiprocessing.cpu_count()}")
print(f"📊 Workers recomendados: {multiprocessing.cpu_count() * 2}")

# Importa e modifica configurações antes de importar o servidor
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Patch para aumentar capacidade do connection pool
import sys
sys.modules['HIGH_CAPACITY'] = True

# Configurações customizadas
HIGH_CAPACITY_CONFIG = {
    'connection_pool_size': 50,
    'max_concurrent_sessions': 100,
    'request_timeout': 600,
    'cache_size_mb': 512,
    'max_workers': multiprocessing.cpu_count() * 2
}

# Salva config em variáveis de ambiente
for key, value in HIGH_CAPACITY_CONFIG.items():
    os.environ[f'HC_{key.upper()}'] = str(value)

print("\n📋 Configurações aplicadas:")
for key, value in HIGH_CAPACITY_CONFIG.items():
    print(f"   • {key}: {value}")

print("\n✨ Iniciando servidor otimizado...")

# Importa servidor com configurações aplicadas
import server

# Inicia com uvicorn otimizado
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    print("✅ UVLoop ativado para melhor performance")
except ImportError:
    print("⚠️ UVLoop não instalado, usando asyncio padrão")

import uvicorn

# Configurações do Uvicorn
uvicorn.run(
    server.app,
    host="0.0.0.0",
    port=8080,
    workers=1,  # Use 1 worker por processo Python (inicie múltiplos processos se necessário)
    loop="auto",  # Usa uvloop se disponível
    limit_concurrency=1000,
    limit_max_requests=None,
    timeout_keep_alive=75,
    server_header=False,
    access_log=True,
    log_level="info"
)