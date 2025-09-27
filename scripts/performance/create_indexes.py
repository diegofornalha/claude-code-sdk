"""
Script para criar índices e constraints no Neo4j
================================================
Executa otimizações de performance no banco de dados
"""

import os
import sys
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()


class Neo4jIndexManager:
    """Gerenciador de índices e constraints do Neo4j."""

    def __init__(self):
        """Inicializa conexão com Neo4j."""
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        """Fecha conexão."""
        if self.driver:
            self.driver.close()

    def create_all_indexes(self):
        """Cria todos os índices recomendados."""
        print("🔍 Criando índices no Neo4j...")

        with self.driver.session() as session:
            # 1. Índice no label Learning + propriedade name (BUSCA MAIS COMUM)
            try:
                session.run("""
                    CREATE INDEX learning_name_idx IF NOT EXISTS
                    FOR (n:Learning) ON (n.name)
                """)
                print("✅ Índice: Learning.name")
            except Exception as e:
                print(f"⚠️  Learning.name já existe ou erro: {e}")

            # 2. Índice no label Learning + propriedade type
            try:
                session.run("""
                    CREATE INDEX learning_type_idx IF NOT EXISTS
                    FOR (n:Learning) ON (n.type)
                """)
                print("✅ Índice: Learning.type")
            except Exception as e:
                print(f"⚠️  Learning.type já existe ou erro: {e}")

            # 3. Índice composto para buscas por usuário e timestamp
            try:
                session.run("""
                    CREATE INDEX learning_user_timestamp_idx IF NOT EXISTS
                    FOR (n:Learning) ON (n.user, n.created_at)
                """)
                print("✅ Índice composto: Learning.user + Learning.created_at")
            except Exception as e:
                print(f"⚠️  Índice composto já existe ou erro: {e}")

            # 4. Índice full-text para busca de conteúdo
            try:
                session.run("""
                    CREATE FULLTEXT INDEX learning_content_fulltext IF NOT EXISTS
                    FOR (n:Learning) ON EACH [n.name, n.description, n.content]
                """)
                print("✅ Índice full-text: Learning (name, description, content)")
            except Exception as e:
                print(f"⚠️  Índice full-text já existe ou erro: {e}")

            # 5. Índice em elementId para lookups diretos
            try:
                session.run("""
                    CREATE INDEX learning_element_id_idx IF NOT EXISTS
                    FOR (n:Learning) ON (elementId(n))
                """)
                print("✅ Índice: elementId(Learning)")
            except Exception as e:
                print(f"⚠️  elementId já existe ou erro: {e}")

            # 6. Constraint de unicidade (opcional mas recomendado)
            try:
                session.run("""
                    CREATE CONSTRAINT learning_unique_name IF NOT EXISTS
                    FOR (n:Learning) REQUIRE n.name IS UNIQUE
                """)
                print("✅ Constraint: Learning.name UNIQUE")
            except Exception as e:
                print(f"⚠️  Constraint já existe ou erro: {e}")

    def analyze_indexes(self):
        """Analisa índices existentes."""
        print("\n📊 Analisando índices existentes...")

        with self.driver.session() as session:
            result = session.run("SHOW INDEXES")
            indexes = [dict(record) for record in result]

            if not indexes:
                print("❌ Nenhum índice encontrado!")
                return

            print(f"✅ {len(indexes)} índices encontrados:")
            for idx in indexes:
                print(f"   - {idx.get('name', 'unnamed')}: {idx.get('labelsOrTypes', [])} ON {idx.get('properties', [])}")

    def analyze_query_performance(self):
        """Analisa performance de queries comuns."""
        print("\n⚡ Testando performance de queries...")

        with self.driver.session() as session:
            import time

            # Query 1: Busca por name SEM índice
            start = time.time()
            session.run("MATCH (n:Learning {name: 'Claude Code SDK'}) RETURN n LIMIT 1")
            duration1 = (time.time() - start) * 1000
            print(f"   Query 1 (busca por name): {duration1:.2f}ms")

            # Query 2: Busca por type
            start = time.time()
            session.run("MATCH (n:Learning) WHERE n.type = 'concept' RETURN n LIMIT 10")
            duration2 = (time.time() - start) * 1000
            print(f"   Query 2 (busca por type): {duration2:.2f}ms")

            # Query 3: Full scan
            start = time.time()
            session.run("MATCH (n:Learning) RETURN count(n)")
            duration3 = (time.time() - start) * 1000
            print(f"   Query 3 (count total): {duration3:.2f}ms")

            # Query 4: Com relacionamentos
            start = time.time()
            session.run("""
                MATCH (n:Learning)-[r]-(m)
                RETURN count(r) LIMIT 100
            """)
            duration4 = (time.time() - start) * 1000
            print(f"   Query 4 (com relacionamentos): {duration4:.2f}ms")

    def get_recommendations(self):
        """Gera recomendações de otimização."""
        print("\n💡 Recomendações de Otimização:")

        with self.driver.session() as session:
            # Verifica tamanho do grafo
            result = session.run("MATCH (n) RETURN count(n) as total")
            total_nodes = result.single()["total"]

            if total_nodes > 10000:
                print(f"   ⚠️  Grafo grande ({total_nodes} nós) - índices são CRÍTICOS")
            else:
                print(f"   ℹ️  Grafo pequeno ({total_nodes} nós) - índices melhoram mas não críticos")

            # Verifica nós isolados
            result = session.run("MATCH (n) WHERE NOT (n)-[]-() RETURN count(n) as isolated")
            isolated = result.single()["isolated"]

            if isolated > 100:
                print(f"   ⚠️  {isolated} nós isolados - considerar limpeza")

            # Verifica densidade
            result = session.run("""
                MATCH (n)
                WITH count(n) as nodes
                MATCH ()-[r]->()
                RETURN nodes, count(r) as rels
            """)
            record = result.single()
            nodes = record["nodes"]
            rels = record["rels"]

            if nodes > 0:
                density = (2 * rels) / (nodes * (nodes - 1)) if nodes > 1 else 0
                print(f"   📊 Densidade do grafo: {density:.6f}")

                if density < 0.01:
                    print("   ℹ️  Grafo esparso - considerar usar índices de range")


def main():
    """Função principal."""
    manager = Neo4jIndexManager()

    try:
        print("=" * 60)
        print("🚀 Otimização de Performance - Neo4j Agent API")
        print("=" * 60)

        # Análise inicial
        manager.analyze_indexes()
        manager.get_recommendations()

        # Cria índices
        print("\n" + "=" * 60)
        manager.create_all_indexes()

        # Análise pós-criação
        manager.analyze_indexes()

        # Testa performance
        manager.analyze_query_performance()

        print("\n" + "=" * 60)
        print("✅ Otimização concluída com sucesso!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Erro durante otimização: {e}")
        sys.exit(1)
    finally:
        manager.close()


if __name__ == "__main__":
    main()