"""
Exemplo de Integração das Rotas de Métricas
===========================================
Demonstra como integrar e usar os novos endpoints de métricas
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# URL base da API
BASE_URL = "http://localhost:8080"


async def fetch_metrics_summary():
    """Busca resumo geral de métricas."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/api/metrics/summary") as response:
            if response.status == 200:
                data = await response.json()
                print("=" * 60)
                print("RESUMO DE MÉTRICAS")
                print("=" * 60)
                print(f"Timestamp: {data['timestamp']}")
                print(f"\nNeo4j - Nós Learning: {data['neo4j']['learning_nodes']['total']}")
                print(f"Neo4j - Relacionamentos: {data['neo4j']['relationships']['total']}")
                print(f"\nAPI - Total de Requisições: {data['api']['total_requests']}")
                print(f"API - Taxa de Erro: {data['api']['error_rate']}%")
                print(f"API - Uptime: {data['api']['uptime']}")
                print("=" * 60)
                return data
            else:
                print(f"Erro: {response.status}")
                return None


async def fetch_graph_statistics():
    """Busca estatísticas detalhadas do grafo."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/api/metrics/graph-stats") as response:
            if response.status == 200:
                data = await response.json()
                print("\n" + "=" * 60)
                print("ESTATÍSTICAS DO GRAFO")
                print("=" * 60)
                stats = data['statistics']
                print(f"Total de Nós: {stats['nodes']['total']}")
                print(f"Total de Relacionamentos: {stats['relationships']['total']}")
                print(f"Densidade do Grafo: {stats['metrics']['density']:.6f}")
                print(f"Grau Médio: {stats['metrics']['avg_degree']:.2f}")
                print(f"Nós Isolados: {stats['nodes']['isolated']}")

                print("\nDistribuição de Nós:")
                for node_type, count in stats['nodes']['by_type'].items():
                    print(f"  - {node_type}: {count}")

                print("=" * 60)
                return data
            else:
                print(f"Erro: {response.status}")
                return None


async def fetch_performance_metrics():
    """Busca métricas de performance."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/api/metrics/performance") as response:
            if response.status == 200:
                data = await response.json()
                print("\n" + "=" * 60)
                print("MÉTRICAS DE PERFORMANCE")
                print("=" * 60)

                api_perf = data['api_performance']['global']
                print(f"Total de Requisições: {api_perf['total_requests']}")
                print(f"Taxa de Erro: {api_perf['error_rate_percent']:.2f}%")
                print(f"Requisições/segundo: {api_perf['requests_per_second']:.2f}")
                print(f"Requisições Ativas: {api_perf['active_requests']}")

                print("\nEndpoints Mais Lentos:")
                for endpoint in data['api_performance']['slowest_endpoints'][:3]:
                    print(f"  - {endpoint['endpoint']}")
                    print(f"    Tempo médio: {endpoint['avg_time_ms']:.2f}ms")
                    print(f"    Tempo máximo: {endpoint['max_time_ms']:.2f}ms")

                print("\nQueries Neo4j:")
                neo4j = data['neo4j_queries']
                print(f"  Total de Queries Únicas: {neo4j['total_unique_queries']}")
                print(f"  Tempo Médio: {neo4j['avg_query_time_ms']:.2f}ms")
                print(f"  Queries Lentas: {neo4j['slow_queries_count']}")

                if data['optimization_recommendations']:
                    print("\nRecomendações de Otimização:")
                    for rec in data['optimization_recommendations'][:3]:
                        print(f"  [{rec['severity'].upper()}] {rec['message']}")
                        print(f"    Sugestão: {rec['suggestion']}")

                print("=" * 60)
                return data
            else:
                print(f"Erro: {response.status}")
                return None


async def fetch_learning_insights():
    """Busca insights de aprendizado."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/api/metrics/learning-insights") as response:
            if response.status == 200:
                data = await response.json()
                print("\n" + "=" * 60)
                print("INSIGHTS DE APRENDIZADO")
                print("=" * 60)

                insights = data['insights']

                print("Nós Mais Conectados:")
                for node in insights['most_connected_nodes'][:5]:
                    print(f"  - {node['name']} ({node['category']})")
                    print(f"    Conexões: {node['connections']}")

                print("\nDistribuição de Conectividade:")
                for level, count in insights['connectivity_distribution'].items():
                    print(f"  - {level}: {count} nós")

                if data['recommendations']:
                    print("\nRecomendações:")
                    for rec in data['recommendations']:
                        print(f"  [{rec['priority'].upper()}] {rec['message']}")
                        print(f"    {rec['suggestion']}")

                print("=" * 60)
                return data
            else:
                print(f"Erro: {response.status}")
                return None


async def monitor_metrics_loop(interval_seconds: int = 60):
    """
    Loop de monitoramento contínuo.

    Args:
        interval_seconds: Intervalo entre verificações
    """
    print(f"Iniciando monitoramento de métricas (intervalo: {interval_seconds}s)")
    print("Pressione Ctrl+C para parar\n")

    try:
        while True:
            print(f"\n[{datetime.now().isoformat()}] Coletando métricas...")

            # Buscar todas as métricas
            await fetch_metrics_summary()
            await asyncio.sleep(2)  # Pausa entre requisições

            await fetch_performance_metrics()
            await asyncio.sleep(2)

            # Aguardar próximo ciclo
            print(f"\nPróxima coleta em {interval_seconds} segundos...")
            await asyncio.sleep(interval_seconds)

    except KeyboardInterrupt:
        print("\n\nMonitoramento interrompido pelo usuário.")


async def comprehensive_report():
    """Gera relatório completo de todas as métricas."""
    print("\n" + "=" * 60)
    print("RELATÓRIO COMPLETO DE MÉTRICAS")
    print(f"Gerado em: {datetime.now().isoformat()}")
    print("=" * 60)

    # Coletar todas as métricas
    summary = await fetch_metrics_summary()
    await asyncio.sleep(1)

    graph_stats = await fetch_graph_statistics()
    await asyncio.sleep(1)

    performance = await fetch_performance_metrics()
    await asyncio.sleep(1)

    learning = await fetch_learning_insights()

    # Salvar em arquivo JSON
    report = {
        "generated_at": datetime.now().isoformat(),
        "summary": summary,
        "graph_statistics": graph_stats,
        "performance": performance,
        "learning_insights": learning
    }

    filename = f"metrics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Relatório salvo em: {filename}")


# Exemplos de uso
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "summary":
            asyncio.run(fetch_metrics_summary())

        elif command == "graph":
            asyncio.run(fetch_graph_statistics())

        elif command == "performance":
            asyncio.run(fetch_performance_metrics())

        elif command == "learning":
            asyncio.run(fetch_learning_insights())

        elif command == "monitor":
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            asyncio.run(monitor_metrics_loop(interval))

        elif command == "report":
            asyncio.run(comprehensive_report())

        else:
            print(f"Comando desconhecido: {command}")
            print("\nUso:")
            print("  python metrics_integration_example.py summary")
            print("  python metrics_integration_example.py graph")
            print("  python metrics_integration_example.py performance")
            print("  python metrics_integration_example.py learning")
            print("  python metrics_integration_example.py monitor [interval]")
            print("  python metrics_integration_example.py report")
    else:
        # Sem argumentos: executar relatório completo
        asyncio.run(comprehensive_report())