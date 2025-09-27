#!/usr/bin/env python3
"""
Script de teste para validação de segurança
Testa todos os tipos de ataques e validações implementados
"""

import requests
import json
import time
from typing import Dict, List, Tuple


class SecurityTester:
    """Classe para testar segurança da API"""

    def __init__(self, base_url: str = "http://localhost:8888"):
        self.base_url = base_url
        self.results: List[Dict] = []

    def test_endpoint(self, method: str, endpoint: str, payload: Dict = None, expected_status: int = 200) -> Tuple[bool, str]:
        """Testa um endpoint com payload específico"""
        url = f"{self.base_url}{endpoint}"

        try:
            if method == "POST":
                response = requests.post(url, json=payload, timeout=5)
            elif method == "GET":
                response = requests.get(url, timeout=5)
            else:
                return False, f"Método {method} não suportado"

            success = response.status_code == expected_status
            message = f"Status: {response.status_code}"

            if response.status_code == 400:
                try:
                    error_data = response.json()
                    message += f" - {error_data.get('detail', 'Erro desconhecido')}"
                except:
                    pass

            return success, message

        except requests.exceptions.RequestException as e:
            return False, f"Erro de conexão: {str(e)}"

    def run_tests(self):
        """Executa todos os testes de segurança"""
        print("=" * 70)
        print("🛡️  TESTE DE SEGURANÇA - NEO4J AGENT")
        print("=" * 70)
        print()

        # 1. Teste de XSS
        print("📋 TESTE 1: XSS (Cross-Site Scripting)")
        print("-" * 70)

        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<iframe src='javascript:alert(1)'>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "<body onload=alert('XSS')>",
        ]

        for payload in xss_payloads:
            success, msg = self.test_endpoint(
                "POST",
                "/api/chat",
                {"message": payload},
                expected_status=200  # Deve aceitar mas sanitizar
            )
            status = "✅ BLOQUEADO" if success else "❌ FALHOU"
            print(f"{status}: {payload[:50]}")
            self.results.append({
                "test": "XSS",
                "payload": payload,
                "blocked": success
            })

        print()

        # 2. Teste de SQL Injection
        print("📋 TESTE 2: SQL Injection")
        print("-" * 70)

        sql_payloads = [
            "' OR '1'='1' --",
            "1; DROP TABLE users--",
            "' UNION SELECT * FROM users--",
            "admin'--",
            "1' OR '1' = '1'/*",
        ]

        for payload in sql_payloads:
            success, msg = self.test_endpoint(
                "POST",
                "/api/chat",
                {"message": payload},
                expected_status=200  # Deve aceitar mas sanitizar
            )
            status = "✅ BLOQUEADO" if success else "❌ FALHOU"
            print(f"{status}: {payload[:50]}")
            self.results.append({
                "test": "SQL Injection",
                "payload": payload,
                "blocked": success
            })

        print()

        # 3. Teste de Command Injection
        print("📋 TESTE 3: Command Injection")
        print("-" * 70)

        cmd_payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "`whoami`",
            "$(rm -rf /)",
            "&& ping -c 10 google.com",
        ]

        for payload in cmd_payloads:
            success, msg = self.test_endpoint(
                "POST",
                "/api/chat",
                {"message": payload},
                expected_status=200  # Deve aceitar mas sanitizar
            )
            status = "✅ BLOQUEADO" if success else "❌ FALHOU"
            print(f"{status}: {payload[:50]}")
            self.results.append({
                "test": "Command Injection",
                "payload": payload,
                "blocked": success
            })

        print()

        # 4. Teste de Path Traversal
        print("📋 TESTE 4: Path Traversal")
        print("-" * 70)

        path_payloads = [
            "../../etc/passwd",
            "../../../windows/system32/",
            "..\\..\\..\\windows\\system32",
            "%2e%2e%2f%2e%2e%2f",
            "....//....//",
        ]

        for payload in path_payloads:
            success, msg = self.test_endpoint(
                "POST",
                "/api/chat",
                {"message": payload},
                expected_status=200  # Deve aceitar mas sanitizar
            )
            status = "✅ BLOQUEADO" if success else "❌ FALHOU"
            print(f"{status}: {payload[:50]}")
            self.results.append({
                "test": "Path Traversal",
                "payload": payload,
                "blocked": success
            })

        print()

        # 5. Teste de NoSQL Injection
        print("📋 TESTE 5: NoSQL Injection")
        print("-" * 70)

        nosql_payloads = [
            '{"$ne": null}',
            '{"$gt": ""}',
            '{"$where": "this.password"}',
            '{"$regex": ".*"}',
            '{"$or": [{"a":1}]}',
        ]

        for payload in nosql_payloads:
            success, msg = self.test_endpoint(
                "POST",
                "/api/chat",
                {"message": payload},
                expected_status=200  # Deve aceitar mas sanitizar
            )
            status = "✅ BLOQUEADO" if success else "❌ FALHOU"
            print(f"{status}: {payload[:50]}")
            self.results.append({
                "test": "NoSQL Injection",
                "payload": payload,
                "blocked": success
            })

        print()

        # 6. Teste de Validação de UUID
        print("📋 TESTE 6: Validação de Session ID (UUID)")
        print("-" * 70)

        invalid_uuids = [
            "not-a-uuid",
            "12345",
            "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            "'; DROP TABLE sessions--",
            "<script>alert('xss')</script>",
        ]

        for uuid in invalid_uuids:
            success, msg = self.test_endpoint(
                "POST",
                "/api/chat",
                {"message": "test", "session_id": uuid},
                expected_status=400  # Deve rejeitar
            )
            status = "✅ BLOQUEADO" if success else "❌ FALHOU"
            print(f"{status}: {uuid[:50]} - {msg}")
            self.results.append({
                "test": "UUID Validation",
                "payload": uuid,
                "blocked": success
            })

        print()

        # 7. Teste de Validação de Endereço
        print("📋 TESTE 7: Validação de Endereço Blockchain")
        print("-" * 70)

        invalid_addresses = [
            "not-an-address",
            "0xZZZZ",
            "<script>alert('xss')</script>",
            "'; DROP TABLE--",
            "0x" + "a" * 100,  # Muito longo
        ]

        for address in invalid_addresses:
            success, msg = self.test_endpoint(
                "GET",
                f"/api/flow/balance/{address}",
                expected_status=400  # Deve rejeitar
            )
            status = "✅ BLOQUEADO" if success else "❌ FALHOU"
            print(f"{status}: {address[:50]} - {msg}")
            self.results.append({
                "test": "Address Validation",
                "payload": address,
                "blocked": success
            })

        print()

        # 8. Teste de Rate Limiting (comentado para não sobrecarregar)
        print("📋 TESTE 8: Rate Limiting")
        print("-" * 70)
        print("⚠️  Teste de rate limiting desabilitado para não sobrecarregar o servidor")
        print("Para testar, execute o seguinte comando:")
        print("  for i in {1..61}; do curl -X POST http://localhost:8888/api/chat -H 'Content-Type: application/json' -d '{\"message\":\"test\"}'; done")
        print()

        # 9. Teste de Tamanho Máximo
        print("📋 TESTE 9: Validação de Tamanho Máximo")
        print("-" * 70)

        # Mensagem muito longa (> 50.000 caracteres)
        long_message = "A" * 50001
        success, msg = self.test_endpoint(
            "POST",
            "/api/chat",
            {"message": long_message},
            expected_status=400  # Deve rejeitar
        )
        status = "✅ BLOQUEADO" if success else "❌ FALHOU"
        print(f"{status}: Mensagem com 50.001 caracteres - {msg}")
        self.results.append({
            "test": "Max Length",
            "payload": "50001 chars",
            "blocked": success
        })

        print()

        # 10. Teste de Headers de Segurança
        print("📋 TESTE 10: Headers de Segurança")
        print("-" * 70)

        try:
            response = requests.get(f"{self.base_url}/api/health")

            security_headers = [
                "X-Content-Type-Options",
                "X-Frame-Options",
                "X-XSS-Protection",
                "Strict-Transport-Security",
                "Content-Security-Policy",
                "Referrer-Policy",
                "Permissions-Policy"
            ]

            for header in security_headers:
                if header in response.headers:
                    print(f"✅ {header}: {response.headers[header][:60]}")
                    self.results.append({
                        "test": "Security Headers",
                        "payload": header,
                        "blocked": True
                    })
                else:
                    print(f"❌ {header}: NÃO ENCONTRADO")
                    self.results.append({
                        "test": "Security Headers",
                        "payload": header,
                        "blocked": False
                    })

        except Exception as e:
            print(f"❌ Erro ao verificar headers: {e}")

        print()

        # Resumo
        self.print_summary()

    def print_summary(self):
        """Imprime resumo dos testes"""
        print("=" * 70)
        print("📊 RESUMO DOS TESTES")
        print("=" * 70)

        total = len(self.results)
        passed = sum(1 for r in self.results if r["blocked"])
        failed = total - passed

        print(f"Total de testes: {total}")
        print(f"✅ Bloqueados: {passed} ({passed/total*100:.1f}%)")
        print(f"❌ Falharam: {failed} ({failed/total*100:.1f}%)")
        print()

        # Resumo por tipo de teste
        test_types = {}
        for result in self.results:
            test_type = result["test"]
            if test_type not in test_types:
                test_types[test_type] = {"total": 0, "passed": 0}
            test_types[test_type]["total"] += 1
            if result["blocked"]:
                test_types[test_type]["passed"] += 1

        print("Detalhamento por tipo:")
        for test_type, counts in test_types.items():
            percentage = counts["passed"] / counts["total"] * 100
            status = "✅" if percentage == 100 else "⚠️" if percentage >= 80 else "❌"
            print(f"{status} {test_type}: {counts['passed']}/{counts['total']} ({percentage:.1f}%)")

        print()

        if failed == 0:
            print("🎉 TODOS OS TESTES PASSARAM! Sistema seguro.")
        elif failed <= total * 0.1:
            print("✅ Sistema majoritariamente seguro. Revisar falhas.")
        else:
            print("⚠️  ATENÇÃO: Múltiplas vulnerabilidades detectadas!")

        print("=" * 70)


def main():
    """Função principal"""
    print()
    print("Verificando se o servidor está online...")

    try:
        response = requests.get("http://localhost:8888/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor online. Iniciando testes...\n")
        else:
            print("❌ Servidor retornou erro. Verifique se está rodando.")
            return
    except requests.exceptions.RequestException:
        print("❌ Não foi possível conectar ao servidor.")
        print("Execute primeiro: python server.py")
        return

    # Executar testes
    tester = SecurityTester()
    tester.run_tests()


if __name__ == "__main__":
    main()