
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
            f.write(json.dumps(metrics) + '\n')

        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(monitor_server_health())
