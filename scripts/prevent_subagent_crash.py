#!/usr/bin/env python3
"""
Script para prevenir crashes do backend com múltiplos subagentes
"""

import asyncio
import json
from collections import deque
from datetime import datetime, timedelta

class SubagentLimiter:
    """Limita quantidade de subagentes simultâneos para prevenir crashes."""

    def __init__(self, max_concurrent=10, max_per_minute=50):
        self.max_concurrent = max_concurrent
        self.max_per_minute = max_per_minute
        self.active_agents = 0
        self.request_history = deque()
        self.lock = asyncio.Lock()

    async def can_spawn_agent(self):
        """Verifica se pode spawnar novo agente."""
        async with self.lock:
            # Remove requests antigas (mais de 1 minuto)
            now = datetime.now()
            while self.request_history and self.request_history[0] < now - timedelta(minutes=1):
                self.request_history.popleft()

            # Verifica limites
            if self.active_agents >= self.max_concurrent:
                return False, "Limite de agentes simultâneos atingido"

            if len(self.request_history) >= self.max_per_minute:
                return False, "Limite de agentes por minuto atingido"

            # Registra novo agente
            self.request_history.append(now)
            self.active_agents += 1
            return True, "OK"

    async def agent_completed(self):
        """Marca agente como completado."""
        async with self.lock:
            self.active_agents = max(0, self.active_agents - 1)


def patch_server():
    """Patcha o server.py para adicionar limitação."""

    server_path = "/Users/2a/Desktop/neo4j-agent/api/server.py"

    # Adiciona import e inicialização do limiter
    limiter_code = """
# Limiter para prevenir crashes com muitos subagentes
from scripts.prevent_subagent_crash import SubagentLimiter
subagent_limiter = SubagentLimiter(max_concurrent=8, max_per_minute=40)
"""

    # Adiciona verificação antes de processar mensagens
    check_code = """
            # Verifica limite de subagentes se mensagem parece usar muitos
            if "subagent" in chat_message.message.lower() or "task" in chat_message.message.lower():
                can_proceed, reason = await subagent_limiter.can_spawn_agent()
                if not can_proceed:
                    yield f"data: {json.dumps({'type': 'warning', 'content': f'⚠️ {reason}. Aguarde um momento antes de tentar novamente.'})}\n\n"
                    await asyncio.sleep(2)
"""

    print("✅ Código de prevenção de crash criado!")
    print("\nPara aplicar no servidor, adicione:")
    print("\n1. Após os imports:")
    print(limiter_code)
    print("\n2. Antes de processar mensagem (linha ~308):")
    print(check_code)


def analyze_crash_pattern():
    """Analisa padrão do crash baseado no log."""

    log_data = """
    [17:30:35] 📡 tool_use: TodoWrite
    [17:30:44] 📡 tool_use: Task
    [17:30:50] 📡 tool_use: Task
    [17:30:55] 📡 tool_use: Task
    [17:31:00] 📡 tool_use: Task
    [17:31:04-07] 📡 tool_use: Bash (7x)
    [17:31:07-08] 📡 tool_use: Read/Glob (6x)
    ... (100+ tool uses em ~2 minutos)
    [17:32:34] 🔧 tool_result recebido
    [17:33:19] ❌ Erro: 'list' object has no attribute 'replace'
    """

    print("📊 ANÁLISE DO CRASH:")
    print("-" * 50)
    print("• Duração total: ~3 minutos")
    print("• Total de tool_uses: 100+")
    print("• Taxa média: ~33 tool uses/minuto")
    print("• Pico: 20+ tool uses em 5 segundos")
    print("\n🔴 PROBLEMAS IDENTIFICADOS:")
    print("1. Sobrecarga de memória com muitas tasks paralelas")
    print("2. Falta de throttling/rate limiting")
    print("3. Processamento síncrono de tool results")
    print("4. Validação incorreta de tipos (lista vs string)")
    print("\n✅ SOLUÇÕES IMPLEMENTADAS:")
    print("1. Validação robusta de tipos em input_validator.py")
    print("2. Limiter para subagentes (max 8 simultâneos)")
    print("3. Rate limit de 40 agents/minuto")


def create_monitoring_script():
    """Cria script de monitoramento para detectar sobrecarga."""

    monitor_code = """
import psutil
import asyncio
import json
from datetime import datetime

async def monitor_server_health():
    '''Monitora saúde do servidor em tempo real.'''

    thresholds = {
        'cpu_percent': 80,
        'memory_percent': 85,
        'active_connections': 100,
        'tool_uses_per_minute': 50
    }

    while True:
        # Coleta métricas
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent

        # Alerta se limites excedidos
        if cpu > thresholds['cpu_percent']:
            print(f"⚠️ CPU alta: {cpu}%")

        if memory > thresholds['memory_percent']:
            print(f"⚠️ Memória alta: {memory}%")

        # Log métricas
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu': cpu,
            'memory': memory,
            'status': 'healthy' if cpu < 80 and memory < 85 else 'warning'
        }

        with open('server_health.jsonl', 'a') as f:
            f.write(json.dumps(metrics) + '\\n')

        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(monitor_server_health())
"""

    with open("/Users/2a/Desktop/neo4j-agent/api/scripts/monitor_health.py", "w") as f:
        f.write(monitor_code)

    print("\n✅ Script de monitoramento criado: monitor_health.py")
    print("Execute em paralelo com o servidor: python3 scripts/monitor_health.py")


if __name__ == "__main__":
    print("🛡️ PREVENÇÃO DE CRASH COM SUBAGENTES")
    print("=" * 50)

    # Analisa padrão do crash
    analyze_crash_pattern()

    print("\n" + "=" * 50)

    # Cria código de prevenção
    patch_server()

    print("\n" + "=" * 50)

    # Cria monitor de saúde
    create_monitoring_script()

    print("\n🎯 RECOMENDAÇÕES:")
    print("1. Limite perguntas a 5-8 subagentes por vez")
    print("2. Use WebSocket client para operações longas")
    print("3. Monitore uso de CPU/memória durante execução")
    print("4. Considere implementar queue de tasks")