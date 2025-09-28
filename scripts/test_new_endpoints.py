#!/usr/bin/env python3
"""
Script de Teste para Novos Endpoints da API
============================================
Testa funcionalidades de análise de grafos, métricas e analytics
"""

import requests
import json
import time
from typing import Dict, Any
from datetime import datetime


class APITester:
    """Classe para testar endpoints da API."""

    def __init__(self, base_url: str = "http://localhost:8080"):
        """
        Inicializa tester.

        Args:
            base_url: URL base da API
        """
        self.base_url = base_url
        self.results = []

    def test_endpoint(
        self,
        method: str,
        endpoint: str,
        expected_status: int = 200,
        data: Dict[str, Any] = None,
        params: Dict[str, Any] = None
    ) -> bool:
        """
        Testa um endpoint.

        Args:
            method: Método HTTP (GET, POST, etc)
            endpoint: Caminho do endpoint
            expected_status: Status code esperado
            data: Dados do body (para POST)
            params: Query parameters

        Returns:
            True se teste passou
        """
        url = f"{self.base_url}{endpoint}"

        print(f"\n{'='*60}")
        print(f"🧪 Testando: {method} {endpoint}")
        print(f"{'='*60}")

        try:
            start = time.time()

            if method == "GET":
                response = requests.get(url, params=params, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)
            else:
                print(f"❌ Método não suportado: {method}")
                return False

            duration = (time.time() - start) * 1000

            # Verifica status code
            status_ok = response.status_code == expected_status

            if status_ok:
                print(f"✅ Status: {response.status_code} (esperado: {expected_status})")
            else:
                print(f"❌ Status: {response.status_code} (esperado: {expected_status})")

            # Tenta parsear JSON
            try:
                json_data = response.json()
                print(f"📊 Resposta JSON válida")

                # Mostra primeiras linhas
                pretty_json = json.dumps(json_data, indent=2, ensure_ascii=False)
                lines = pretty_json.split('\n')[:15]
                print('\n'.join(lines))
                if len(pretty_json.split('\n')) > 15:
                    print("... (truncado)")

            except Exception as e:
                print(f"⚠️  Resposta não é JSON: {e}")
                print(f"Body: {response.text[:200]}")

            print(f"⏱️  Tempo de resposta: {duration:.2f}ms")

            # Registra resultado
            self.results.append({
                "endpoint": endpoint,
                "method": method,
                "status": response.status_code,
                "expected_status": expected_status,
                "passed": status_ok,
                "duration_ms": duration,
                "timestamp": datetime.now().isoformat()
            })

            return status_ok

        except requests.exceptions.Timeout:
            print(f"❌ Timeout ao conectar com {url}")
            return False
        except requests.exceptions.ConnectionError:
            print(f"❌ Erro de conexão com {url}")
            print("⚠️  Certifique-se de que o servidor está rodando!")
            return False
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            return False

    def run_all_tests(self):
        """Executa todos os testes."""
        print("\n" + "="*60)
        print("🚀 INICIANDO TESTES DA API NEO4J AGENT")
        print("="*60)

        # 1. Health check básico
        print("\n\n📋 CATEGORIA: HEALTH CHECKS")
        self.test_endpoint("GET", "/api/health")
        self.test_endpoint("GET", "/api/v1/health/detailed")

        # 2. Testes de análise de grafos
        print("\n\n📊 CATEGORIA: ANÁLISE DE GRAFOS")
        self.test_endpoint("GET", "/api/v1/graph/statistics")
        self.test_endpoint("GET", "/api/v1/graph/optimize")

        # 3. Testes de métricas
        print("\n\n📈 CATEGORIA: MÉTRICAS E MONITORAMENTO")
        self.test_endpoint("GET", "/api/v1/metrics/overview")
        self.test_endpoint("GET", "/api/v1/metrics/recent-requests", params={"limit": 10})

        # 4. Testes de analytics
        print("\n\n🔍 CATEGORIA: ANALYTICS DE QUERIES")
        self.test_endpoint("GET", "/api/v1/analytics/queries/statistics")
        self.test_endpoint("GET", "/api/v1/analytics/queries/slow")
        self.test_endpoint("GET", "/api/v1/analytics/queries/recommendations")

        # 5. Teste de endpoint que não existe (deve retornar 404)
        print("\n\n🚫 CATEGORIA: TESTES NEGATIVOS")
        self.test_endpoint("GET", "/api/v1/nonexistent", expected_status=404)

        # Resumo dos resultados
        self.print_summary()

    def print_summary(self):
        """Imprime resumo dos testes."""
        print("\n\n" + "="*60)
        print("📊 RESUMO DOS TESTES")
        print("="*60)

        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = total - passed

        print(f"\nTotal de testes: {total}")
        print(f"✅ Passaram: {passed}")
        print(f"❌ Falharam: {failed}")

        if failed > 0:
            print("\n❌ Testes que falharam:")
            for result in self.results:
                if not result["passed"]:
                    print(f"  - {result['method']} {result['endpoint']}")
                    print(f"    Status: {result['status']} (esperado: {result['expected_status']})")

        # Estatísticas de performance
        durations = [r["duration_ms"] for r in self.results if r.get("duration_ms")]
        if durations:
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            min_duration = min(durations)

            print(f"\n⏱️  Estatísticas de Performance:")
            print(f"  - Tempo médio: {avg_duration:.2f}ms")
            print(f"  - Mais rápido: {min_duration:.2f}ms")
            print(f"  - Mais lento: {max_duration:.2f}ms")

        # Taxa de sucesso
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"\n📊 Taxa de sucesso: {success_rate:.1f}%")

        if success_rate == 100:
            print("\n🎉 Todos os testes passaram com sucesso!")
        elif success_rate >= 80:
            print("\n✅ Maioria dos testes passou")
        else:
            print("\n⚠️  Muitos testes falharam - revisar implementação")

        print("\n" + "="*60)


def main():
    """Função principal."""
    # Permite especificar URL base via argumento
    import sys

    base_url = "http://localhost:8080"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    print(f"🌐 Testando API em: {base_url}")

    tester = APITester(base_url)
    tester.run_all_tests()


if __name__ == "__main__":
    main()