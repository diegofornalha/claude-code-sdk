#!/usr/bin/env python3
"""
Teste de conexão com Neo4j
"""

import os
import sys
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Adiciona o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_neo4j_connection():
    """Testa a conexão com Neo4j."""

    print("🔍 TESTE DE CONEXÃO COM NEO4J")
    print("=" * 60)

    # Verifica variáveis de ambiente
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_user = os.getenv("NEO4J_USER")
    neo4j_password = os.getenv("NEO4J_PASSWORD")

    print(f"📋 Configuração:")
    print(f"  URI: {neo4j_uri}")
    print(f"  User: {neo4j_user}")
    print(f"  Password: {'*' * len(neo4j_password) if neo4j_password else 'NOT SET'}")
    print()

    if not all([neo4j_uri, neo4j_user, neo4j_password]):
        print("❌ Variáveis de ambiente não configuradas!")
        print("   Configure NEO4J_URI, NEO4J_USER e NEO4J_PASSWORD")
        return False

    try:
        from neo4j import GraphDatabase

        print("📡 Conectando ao Neo4j...")

        # Tenta conectar
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

        # Testa a conexão
        with driver.session() as session:
            result = session.run("RETURN 1 AS test")
            record = result.single()

            if record and record["test"] == 1:
                print("✅ Conexão bem-sucedida!")

                # Conta nós Learning
                result = session.run("""
                    MATCH (n:Learning)
                    RETURN count(n) as total
                """)
                count_record = result.single()
                count = count_record["total"] if count_record else 0
                print(f"\n📊 Estatísticas:")
                print(f"  Total de nós Learning: {count}")

                # Lista alguns nós recentes
                result = session.run("""
                    MATCH (n:Learning)
                    RETURN n.title AS title, n.content AS content, n.timestamp AS timestamp
                    ORDER BY n.timestamp DESC
                    LIMIT 3
                """)

                print(f"\n📝 Últimas memórias:")
                records = list(result)
                if records:
                    for i, record in enumerate(records, 1):
                        title = record.get("title", "Sem título")
                        content = record.get("content", "")
                        if content and len(content) > 50:
                            content = content[:50] + "..."
                        print(f"  {i}. {title}")
                        if content:
                            print(f"     {content}")
                else:
                    print("  Nenhuma memória encontrada ainda.")

                driver.close()
                return True

    except ImportError:
        print("❌ Biblioteca neo4j não instalada!")
        print("   Execute: pip3 install neo4j")
        return False

    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        print("\n💡 Verifique se:")
        print("  1. O Neo4j está rodando em localhost:7687")
        print("  2. As credenciais estão corretas")
        print("  3. O banco de dados está acessível")
        return False

if __name__ == "__main__":
    success = test_neo4j_connection()

    if success:
        print("\n✅ NEO4J ESTÁ CONFIGURADO E FUNCIONANDO!")
        print("   A integração com o chat está habilitada.")
    else:
        print("\n⚠️ NEO4J NÃO ESTÁ ACESSÍVEL")
        print("   O chat funcionará mas sem persistência de memórias.")