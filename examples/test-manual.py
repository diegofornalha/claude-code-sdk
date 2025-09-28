#!/usr/bin/env python3

"""
Teste Manual - Claude Code SDK
Sistema interativo para testar funcionalidades via console
"""

import os
import sys
import json
import subprocess
from datetime import datetime

# Adiciona o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def print_header():
    print("=" * 65)
    print("       TESTE MANUAL - CLAUDE CODE SDK - PYTHON CONSOLE")
    print("=" * 65)
    print()

def test_environment():
    """Testa variáveis de ambiente"""
    print("🔧 TESTE DE AMBIENTE")
    print("-" * 40)

    env_vars = [
        'ANTHROPIC_API_KEY',
        'PORT',
        'CLAUDE_FLOW_API_URL',
        'NEO4J_URI',
        'NEO4J_USER'
    ]

    for var in env_vars:
        value = os.environ.get(var, 'NÃO DEFINIDO')
        if value != 'NÃO DEFINIDO' and len(value) > 20:
            value = value[:20] + '...'
        print(f"  {var}: {value}")

    print()

def test_server_connection():
    """Testa conexão com o servidor"""
    print("🌐 TESTE DE CONEXÃO COM SERVIDOR")
    print("-" * 40)

    try:
        import requests
        port = os.environ.get('PORT', '8080')
        response = requests.get(f"http://localhost:{port}/health")

        if response.status_code == 200:
            print(f"  ✅ Servidor respondendo na porta {port}")
            data = response.json()
            print(f"  Status: {data.get('status', 'OK')}")
        else:
            print(f"  ❌ Servidor retornou código {response.status_code}")
    except Exception as e:
        print(f"  ❌ Erro ao conectar: {str(e)}")

    print()

def test_claude_flow():
    """Testa Claude Flow"""
    print("🌊 TESTE CLAUDE FLOW")
    print("-" * 40)

    try:
        # Verifica versão
        result = subprocess.run(
            ['npx', 'claude-flow', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            print(f"  ✅ Claude Flow instalado")
            print(f"  Versão: {result.stdout.strip()}")
        else:
            print(f"  ❌ Erro ao verificar Claude Flow")

        # Lista modos SPARC
        result = subprocess.run(
            ['npx', 'claude-flow', 'sparc', 'modes'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            print("\n  Modos SPARC disponíveis:")
            lines = result.stdout.strip().split('\n')[:5]
            for line in lines:
                if line.strip():
                    print(f"    • {line.strip()}")

    except subprocess.TimeoutExpired:
        print("  ⏱️ Timeout ao executar comando")
    except Exception as e:
        print(f"  ❌ Erro: {str(e)}")

    print()

def test_memory_neo4j():
    """Testa conexão com Neo4j"""
    print("🧠 TESTE MEMÓRIA NEO4J")
    print("-" * 40)

    try:
        from neo4j import GraphDatabase

        uri = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
        user = os.environ.get('NEO4J_USER', 'neo4j')
        password = os.environ.get('NEO4J_PASSWORD', 'password')

        driver = GraphDatabase.driver(uri, auth=(user, password))

        with driver.session() as session:
            # Teste de conexão
            result = session.run("RETURN 1 AS test")
            if result.single()['test'] == 1:
                print(f"  ✅ Conexão com Neo4j estabelecida")

                # Conta nós Learning
                result = session.run(
                    "MATCH (n:Learning) RETURN count(n) AS count"
                )
                count = result.single()['count']
                print(f"  📊 Total de memórias 'Learning': {count}")

                # Cria uma memória de teste
                timestamp = datetime.now().isoformat()
                result = session.run(
                    """
                    CREATE (n:Learning {
                        name: $name,
                        content: $content,
                        timestamp: $timestamp,
                        type: 'test'
                    })
                    RETURN id(n) AS id
                    """,
                    name=f"Teste Manual {timestamp[:10]}",
                    content="Memória criada via teste manual",
                    timestamp=timestamp
                )

                node_id = result.single()['id']
                print(f"  ✅ Memória de teste criada (ID: {node_id})")

        driver.close()

    except ImportError:
        print("  ⚠️ Biblioteca neo4j não instalada")
        print("  Execute: pip install neo4j")
    except Exception as e:
        print(f"  ❌ Erro ao conectar com Neo4j: {str(e)}")

    print()

def interactive_test():
    """Menu interativo de testes"""
    while True:
        print("\n📋 OPÇÕES DE TESTE:")
        print("  1. Testar ambiente")
        print("  2. Testar servidor")
        print("  3. Testar Claude Flow")
        print("  4. Testar Neo4j")
        print("  5. Executar todos os testes")
        print("  0. Sair")

        choice = input("\nEscolha uma opção: ").strip()

        if choice == '1':
            print()
            test_environment()
        elif choice == '2':
            print()
            test_server_connection()
        elif choice == '3':
            print()
            test_claude_flow()
        elif choice == '4':
            print()
            test_memory_neo4j()
        elif choice == '5':
            print()
            test_environment()
            test_server_connection()
            test_claude_flow()
            test_memory_neo4j()
        elif choice == '0':
            print("\n👋 Encerrando testes. Até logo!\n")
            break
        else:
            print("❌ Opção inválida")

def main():
    print_header()

    # Se passar argumentos, executa teste específico
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()

        if arg in ['env', 'ambiente']:
            test_environment()
        elif arg in ['server', 'servidor']:
            test_server_connection()
        elif arg in ['flow', 'claude-flow']:
            test_claude_flow()
        elif arg in ['neo4j', 'memory', 'memoria']:
            test_memory_neo4j()
        elif arg in ['all', 'todos']:
            test_environment()
            test_server_connection()
            test_claude_flow()
            test_memory_neo4j()
        else:
            print(f"❌ Argumento desconhecido: {arg}")
            print("Use: env, server, flow, neo4j, all")
    else:
        # Modo interativo
        interactive_test()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Interrompido pelo usuário\n")
        sys.exit(0)