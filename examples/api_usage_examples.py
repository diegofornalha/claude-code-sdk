#!/usr/bin/env python3
"""
Exemplos Práticos de Uso da API Neo4j Agent
============================================
Demonstra como usar os novos endpoints em cenários reais
"""

import requests
import json
from typing import Dict, Any


class Neo4jAgentClient:
    """Cliente Python para API Neo4j Agent."""

    def __init__(self, base_url: str = "http://localhost:8080"):
        """
        Inicializa cliente.

        Args:
            base_url: URL base da API
        """
        self.base_url = base_url
        self.session = requests.Session()

    def get_graph_overview(self) -> Dict[str, Any]:
        """
        Obtém visão geral completa do grafo.

        Returns:
            Estatísticas do grafo
        """
        response = self.session.get(f"{self.base_url}/api/v1/graph/statistics")
        response.raise_for_status()
        return response.json()

    def find_path(
        self,
        start_id: str,
        end_id: str,
        max_depth: int = 10
    ) -> Dict[str, Any]:
        """
        Encontra caminho mais curto entre dois nós.

        Args:
            start_id: ID do nó inicial
            end_id: ID do nó final
            max_depth: Profundidade máxima

        Returns:
            Caminho encontrado ou None
        """
        url = f"{self.base_url}/api/v1/graph/path/{start_id}/{end_id}"
        params = {"max_depth": max_depth}

        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_similar_nodes(
        self,
        node_id: str,
        limit: int = 10,
        threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Encontra nós similares.

        Args:
            node_id: ID do nó de referência
            limit: Máximo de resultados
            threshold: Threshold de similaridade

        Returns:
            Lista de nós similares
        """
        url = f"{self.base_url}/api/v1/graph/node/{node_id}/similar"
        params = {"limit": limit, "threshold": threshold}

        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def analyze_subgraph(
        self,
        node_id: str,
        depth: int = 2
    ) -> Dict[str, Any]:
        """
        Analisa subgrafo centrado em um nó.

        Args:
            node_id: ID do nó central
            depth: Profundidade de análise

        Returns:
            Análise do subgrafo
        """
        url = f"{self.base_url}/api/v1/graph/node/{node_id}/subgraph"
        params = {"depth": depth}

        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_optimization_suggestions(self) -> Dict[str, Any]:
        """
        Obtém sugestões de otimização para o grafo.

        Returns:
            Sugestões de otimização
        """
        response = self.session.get(f"{self.base_url}/api/v1/graph/optimize")
        response.raise_for_status()
        return response.json()

    def export_subgraph(
        self,
        node_ids: list,
        include_relationships: bool = True
    ) -> Dict[str, Any]:
        """
        Exporta subgrafo para JSON.

        Args:
            node_ids: Lista de IDs dos nós
            include_relationships: Se deve incluir relacionamentos

        Returns:
            Grafo exportado em JSON
        """
        url = f"{self.base_url}/api/v1/graph/export"
        data = {
            "node_ids": node_ids,
            "include_relationships": include_relationships
        }

        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def get_metrics_overview(self) -> Dict[str, Any]:
        """
        Obtém visão geral das métricas.

        Returns:
            Métricas globais e por endpoint
        """
        response = self.session.get(f"{self.base_url}/api/v1/metrics/overview")
        response.raise_for_status()
        return response.json()

    def get_slow_queries(self, threshold_ms: float = 1000) -> Dict[str, Any]:
        """
        Obtém lista de queries lentas.

        Args:
            threshold_ms: Threshold em milissegundos

        Returns:
            Lista de queries lentas
        """
        url = f"{self.base_url}/api/v1/analytics/queries/slow"
        params = {"threshold_ms": threshold_ms}

        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_query_recommendations(self) -> Dict[str, Any]:
        """
        Obtém recomendações de otimização de queries.

        Returns:
            Lista de recomendações
        """
        url = f"{self.base_url}/api/v1/analytics/queries/recommendations"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_detailed_health(self) -> Dict[str, Any]:
        """
        Obtém status detalhado de saúde do sistema.

        Returns:
            Status de todos os componentes
        """
        response = self.session.get(f"{self.base_url}/api/v1/health/detailed")
        return response.json()


# ============================================
# EXEMPLOS DE USO
# ============================================

def example_1_graph_overview():
    """Exemplo 1: Obter visão geral do grafo."""
    print("\n" + "="*60)
    print("EXEMPLO 1: Visão Geral do Grafo")
    print("="*60)

    client = Neo4jAgentClient()

    try:
        stats = client.get_graph_overview()

        print(f"\n📊 Estatísticas do Grafo:")
        print(f"  Nós totais: {stats['statistics']['nodes']['total']}")
        print(f"  Relacionamentos totais: {stats['statistics']['relationships']['total']}")
        print(f"  Densidade: {stats['statistics']['metrics']['density']:.4f}")
        print(f"  Grau médio: {stats['statistics']['metrics']['avg_degree']:.2f}")

        print(f"\n📋 Tipos de Nós:")
        for node_type, count in stats['statistics']['nodes']['by_type'].items():
            print(f"  {node_type}: {count}")

    except requests.exceptions.ConnectionError:
        print("❌ Erro: Servidor não está rodando")
    except Exception as e:
        print(f"❌ Erro: {e}")


def example_2_find_connections():
    """Exemplo 2: Encontrar conexões entre nós."""
    print("\n" + "="*60)
    print("EXEMPLO 2: Encontrar Conexões")
    print("="*60)

    client = Neo4jAgentClient()

    # Nota: Substitua com IDs reais do seu grafo
    start_id = "example-start-id"
    end_id = "example-end-id"

    print(f"\n🔍 Buscando caminho de {start_id[:15]}... até {end_id[:15]}...")

    try:
        result = client.find_path(start_id, end_id, max_depth=5)

        if result.get("status") == "success":
            path = result["path"]
            print(f"\n✅ Caminho encontrado!")
            print(f"  Tamanho: {path['length']} relacionamentos")
            print(f"  Nós no caminho: {len(path['nodes'])}")
        else:
            print(f"\n⚠️  {result.get('message', 'Nenhum caminho encontrado')}")

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print("\n⚠️  Nota: Use IDs reais do seu grafo Neo4j")
        else:
            print(f"❌ Erro HTTP: {e}")
    except Exception as e:
        print(f"❌ Erro: {e}")


def example_3_performance_monitoring():
    """Exemplo 3: Monitorar performance da API."""
    print("\n" + "="*60)
    print("EXEMPLO 3: Monitoramento de Performance")
    print("="*60)

    client = Neo4jAgentClient()

    try:
        metrics = client.get_metrics_overview()

        print(f"\n📊 Métricas Globais:")
        global_stats = metrics["global"]
        print(f"  Total de requisições: {global_stats['total_requests']}")
        print(f"  Taxa de erro: {global_stats['error_rate']:.2f}%")
        print(f"  Uptime: {global_stats['uptime_formatted']}")
        print(f"  Req/s: {global_stats['requests_per_second']:.2f}")

        print(f"\n🐌 Endpoints Mais Lentos:")
        for endpoint in metrics["slowest_endpoints"][:3]:
            print(f"  {endpoint['endpoint']}")
            print(f"    Tempo médio: {endpoint['avg_time_ms']:.2f}ms")
            print(f"    Requisições: {endpoint['requests']}")

    except Exception as e:
        print(f"❌ Erro: {e}")


def example_4_query_optimization():
    """Exemplo 4: Otimizar queries lentas."""
    print("\n" + "="*60)
    print("EXEMPLO 4: Otimização de Queries")
    print("="*60)

    client = Neo4jAgentClient()

    try:
        # Obter queries lentas
        slow = client.get_slow_queries(threshold_ms=500)

        print(f"\n🐌 Queries Lentas (>{slow['threshold_ms']}ms):")
        print(f"  Total: {slow['count']}")

        if slow['count'] > 0:
            print(f"\n  Top 3:")
            for query in slow['slow_queries'][:3]:
                print(f"    Tempo médio: {query['avg_time_ms']:.2f}ms")
                print(f"    Execuções: {query['executions']}")
                print(f"    Template: {query['template'][:80]}...")
                print()

        # Obter recomendações
        recommendations = client.get_query_recommendations()

        print(f"\n💡 Recomendações de Otimização:")
        print(f"  Total: {recommendations['count']}")

        if recommendations['count'] > 0:
            for rec in recommendations['recommendations']:
                severity_emoji = {
                    "high": "🔴",
                    "medium": "🟡",
                    "low": "🟢"
                }.get(rec['severity'], "⚪")

                print(f"\n  {severity_emoji} [{rec['severity'].upper()}] {rec['category']}")
                print(f"    {rec['message']}")
                print(f"    💡 {rec['suggestion']}")
                if rec.get('estimated_improvement'):
                    print(f"    📈 Melhoria estimada: {rec['estimated_improvement']}")

    except Exception as e:
        print(f"❌ Erro: {e}")


def example_5_health_monitoring():
    """Exemplo 5: Verificar saúde do sistema."""
    print("\n" + "="*60)
    print("EXEMPLO 5: Verificação de Saúde")
    print("="*60)

    client = Neo4jAgentClient()

    try:
        health = client.get_detailed_health()

        status_emoji = {
            "healthy": "💚",
            "degraded": "🟡",
            "unhealthy": "🔴"
        }.get(health['status'], "⚪")

        print(f"\n{status_emoji} Status Geral: {health['status'].upper()}")

        print(f"\n🔍 Verificações:")
        for check_name, check_data in health['checks'].items():
            check_emoji = "✅" if check_data['healthy'] else "❌"
            print(f"  {check_emoji} {check_name}: {check_data['status']}")

            if 'error' in check_data:
                print(f"    Erro: {check_data['error']}")

        print(f"\n📊 Métricas:")
        metrics = health['metrics']
        print(f"  Requisições totais: {metrics['total_requests']}")
        print(f"  Uptime: {metrics['uptime_formatted']}")
        print(f"  Taxa de erro: {metrics['error_rate']:.2f}%")

    except Exception as e:
        print(f"❌ Erro: {e}")


def main():
    """Executa todos os exemplos."""
    print("\n" + "="*60)
    print("🚀 EXEMPLOS DE USO - API NEO4J AGENT")
    print("="*60)
    print("\nEstes exemplos demonstram como usar os novos endpoints.")
    print("Certifique-se de que o servidor está rodando em localhost:8080")

    # Executa exemplos
    example_1_graph_overview()
    example_2_find_connections()
    example_3_performance_monitoring()
    example_4_query_optimization()
    example_5_health_monitoring()

    print("\n" + "="*60)
    print("✅ Exemplos concluídos!")
    print("="*60)
    print("\nPara mais informações, consulte:")
    print("  - /docs/API_IMPROVEMENTS.md")
    print("  - /docs/QUICK_START.md")
    print("\n")


if __name__ == "__main__":
    main()