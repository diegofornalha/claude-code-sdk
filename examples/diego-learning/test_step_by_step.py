#!/usr/bin/env python3
"""
🧪 TESTE PASSO-A-PASSO DO SISTEMA
Valida cada componente do projeto de forma incremental
"""

import json
import time
import asyncio
import requests
from datetime import datetime
from typing import Dict, Any, List

class StepByStepTester:
    """
    Testador incremental do sistema
    """

    def __init__(self):
        self.api_url = "http://localhost:8888"
        self.results = []
        self.score = 0
        self.max_score = 100

    def log_result(self, test_name: str, success: bool, details: str = ""):
        """
        Registra resultado de teste
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "test": test_name,
            "success": success,
            "details": details
        }
        self.results.append(result)

        # Emoji baseado no resultado
        emoji = "✅" if success else "❌"
        print(f"{emoji} {test_name}: {details}")

        # Adicionar pontos se passou
        if success:
            self.score += 5

    def test_1_server_health(self):
        """
        Teste 1: Verificar se o servidor está rodando
        """
        print("\n📍 TESTE 1: Health Check do Servidor")
        print("-" * 40)

        try:
            response = requests.get(f"{self.api_url}/api/health")
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Server Health Check",
                    True,
                    f"Servidor rodando: {data['service']}"
                )
                return True
            else:
                self.log_result(
                    "Server Health Check",
                    False,
                    f"Status code: {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_result(
                "Server Health Check",
                False,
                f"Erro de conexão: {str(e)}"
            )
            return False

    def test_2_sdk_status(self):
        """
        Teste 2: Verificar status do SDK
        """
        print("\n📍 TESTE 2: Status do Claude SDK")
        print("-" * 40)

        try:
            response = requests.get(f"{self.api_url}/api/sdk-status")
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "SDK Status Check",
                    data.get("sdk_available", False),
                    data.get("info", "SDK status retrieved")
                )
                return data.get("sdk_available", False)
            else:
                self.log_result(
                    "SDK Status Check",
                    False,
                    f"Status code: {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_result(
                "SDK Status Check",
                False,
                f"Erro: {str(e)}"
            )
            return False

    def test_3_create_session(self):
        """
        Teste 3: Criar uma sessão de chat
        """
        print("\n📍 TESTE 3: Criar Sessão")
        print("-" * 40)

        try:
            payload = {
                "project_id": "test-diego",
                "config": {
                    "temperature": 0.7,
                    "model": "claude-3-5-sonnet-20241022"
                }
            }

            response = requests.post(
                f"{self.api_url}/api/sessions",
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Create Session",
                    True,
                    f"Session ID: {data.get('session_id', 'N/A')[:8]}..."
                )
                return data.get("session_id")
            else:
                self.log_result(
                    "Create Session",
                    False,
                    f"Status: {response.status_code}"
                )
                return None
        except Exception as e:
            self.log_result(
                "Create Session",
                False,
                f"Erro: {str(e)}"
            )
            return None

    def test_4_send_message(self):
        """
        Teste 4: Enviar mensagem de teste
        """
        print("\n📍 TESTE 4: Enviar Mensagem")
        print("-" * 40)

        try:
            payload = {
                "message": "Olá! Este é um teste do Diego. Responda com OK se recebeu.",
                "project_id": "test-diego"
            }

            response = requests.post(
                f"{self.api_url}/api/chat",
                json=payload,
                stream=True,
                timeout=10
            )

            if response.status_code == 200:
                # Ler algumas linhas da resposta
                lines_read = 0
                for line in response.iter_lines():
                    if lines_read < 5 and line:
                        lines_read += 1

                self.log_result(
                    "Send Message",
                    True,
                    f"Mensagem enviada e resposta recebida"
                )
                return True
            else:
                self.log_result(
                    "Send Message",
                    False,
                    f"Status: {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_result(
                "Send Message",
                False,
                f"Erro: {str(e)}"
            )
            return False

    def test_5_list_sessions(self):
        """
        Teste 5: Listar sessões ativas
        """
        print("\n📍 TESTE 5: Listar Sessões")
        print("-" * 40)

        try:
            response = requests.get(f"{self.api_url}/api/sessions")

            if response.status_code == 200:
                data = response.json()
                total = data.get("total", 0)
                self.log_result(
                    "List Sessions",
                    True,
                    f"Total de sessões ativas: {total}"
                )
                return True
            else:
                self.log_result(
                    "List Sessions",
                    False,
                    f"Status: {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_result(
                "List Sessions",
                False,
                f"Erro: {str(e)}"
            )
            return False

    def test_6_flow_mcp_tools(self):
        """
        Teste 6: Verificar Flow MCP Tools
        """
        print("\n📍 TESTE 6: Flow MCP Tools")
        print("-" * 40)

        # Verificar se os diretórios existem
        import os

        flow_mcp_exists = os.path.exists("/Users/2a/Desktop/neo4j-agent/api/flow-mcp")
        flow_defi_exists = os.path.exists("/Users/2a/Desktop/neo4j-agent/api/flow-defi-mcp")

        self.log_result(
            "Flow MCP Core Tools",
            flow_mcp_exists,
            "Diretório flow-mcp encontrado" if flow_mcp_exists else "Não encontrado"
        )

        self.log_result(
            "Flow DeFi MCP Tools",
            flow_defi_exists,
            "Diretório flow-defi-mcp encontrado" if flow_defi_exists else "Não encontrado"
        )

        return flow_mcp_exists and flow_defi_exists

    def test_7_documentation(self):
        """
        Teste 7: Verificar documentação
        """
        print("\n📍 TESTE 7: Documentação")
        print("-" * 40)

        import os

        docs_to_check = [
            "bootcamp-ai-agents-flow.md",
            "guia-agentkit-flow.md",
            "flow-mcp-protocol.md",
            "usar-flow-mcp-cursor.md",
            "timeline-aprendizado-flow-mcp.md"
        ]

        docs_found = 0
        for doc in docs_to_check:
            path = f"/Users/2a/Desktop/neo4j-agent/docs/{doc}"
            if os.path.exists(path):
                docs_found += 1

        self.log_result(
            "Documentation Check",
            docs_found == len(docs_to_check),
            f"Documentos encontrados: {docs_found}/{len(docs_to_check)}"
        )

        return docs_found == len(docs_to_check)

    def test_8_interface(self):
        """
        Teste 8: Verificar interface HTML
        """
        print("\n📍 TESTE 8: Interface de Chat")
        print("-" * 40)

        import os

        html_exists = os.path.exists("/Users/2a/Desktop/neo4j-agent/chat_debug.html")

        if html_exists:
            # Verificar se tem o título correto
            with open("/Users/2a/Desktop/neo4j-agent/chat_debug.html", "r") as f:
                content = f.read()
                has_correct_title = "Hackathon Flow Blockchain Agents" in content

            self.log_result(
                "Interface HTML",
                html_exists and has_correct_title,
                "Interface encontrada e configurada" if has_correct_title else "Interface desatualizada"
            )
            return has_correct_title
        else:
            self.log_result(
                "Interface HTML",
                False,
                "Arquivo não encontrado"
            )
            return False

    def run_all_tests(self):
        """
        Executa todos os testes em sequência
        """
        print("=" * 60)
        print("🧪 TESTE COMPLETO DO SISTEMA - DIEGO LEARNING")
        print("=" * 60)
        print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Objetivo: Validar todos os componentes")
        print("=" * 60)

        # Executar testes
        tests = [
            self.test_1_server_health,
            self.test_2_sdk_status,
            self.test_3_create_session,
            self.test_4_send_message,
            self.test_5_list_sessions,
            self.test_6_flow_mcp_tools,
            self.test_7_documentation,
            self.test_8_interface
        ]

        for test in tests:
            test()
            time.sleep(1)  # Pausa entre testes

        # Relatório final
        self.print_report()

    def print_report(self):
        """
        Imprime relatório final
        """
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO FINAL")
        print("=" * 60)

        # Contar sucessos e falhas
        successes = sum(1 for r in self.results if r["success"])
        failures = len(self.results) - successes

        print(f"✅ Testes aprovados: {successes}")
        print(f"❌ Testes falhados: {failures}")
        print(f"📈 Taxa de sucesso: {(successes/len(self.results)*100):.1f}%")
        print(f"🎯 Score: {self.score}/{self.max_score}")

        # Salvar relatório
        report = {
            "date": datetime.now().isoformat(),
            "total_tests": len(self.results),
            "passed": successes,
            "failed": failures,
            "score": self.score,
            "max_score": self.max_score,
            "results": self.results
        }

        with open("diego_test_report.json", "w") as f:
            json.dump(report, f, indent=2)

        print("\n💾 Relatório salvo em: diego_test_report.json")

        # Recomendações baseadas no score
        print("\n" + "=" * 60)
        print("💡 RECOMENDAÇÕES")
        print("=" * 60)

        if self.score >= 80:
            print("🏆 Excelente! Sistema funcionando perfeitamente!")
            print("   Você está pronto para começar o bootcamp!")
        elif self.score >= 60:
            print("👍 Bom! Sistema funcionando com pequenos problemas.")
            print("   Verifique os testes que falharam antes de continuar.")
        elif self.score >= 40:
            print("⚠️ Atenção! Alguns componentes críticos não estão funcionando.")
            print("   Corrija os problemas antes de prosseguir.")
        else:
            print("🔴 Crítico! Muitos componentes falharam.")
            print("   Revise a instalação e configuração do sistema.")

        print("\n📚 Próximo passo: Execute reset_diego_learning.py para começar do zero!")

if __name__ == "__main__":
    tester = StepByStepTester()
    tester.run_all_tests()