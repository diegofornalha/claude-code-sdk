"""
Integração Neo4j Memory para Claude Chat
Persiste contexto e memórias entre sessões
"""

import os
import json
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
import re
from neo4j import AsyncGraphDatabase
from dataclasses import dataclass, asdict

@dataclass
class UserProfile:
    """Perfil do usuário com informações persistentes"""
    name: Optional[str] = None
    username: Optional[str] = None
    preferences: Dict[str, Any] = None
    last_seen: Optional[datetime] = None
    conversation_count: int = 0

class Neo4jMemoryIntegration:
    """Integra o chat com Neo4j para persistir memórias e contexto"""

    def __init__(self):
        # Carrega configurações
        self._load_config()

        # Configurações do Neo4j (mesmas do MCP)
        self.uri = os.getenv("NEO4J_URI", self.config.get("connection", {}).get("uri", "bolt://localhost:7687"))
        self.username = os.getenv("NEO4J_USERNAME", self.config.get("connection", {}).get("username", "neo4j"))
        self.password = os.getenv("NEO4J_PASSWORD", self.config.get("connection", {}).get("password", "12345678"))
        self.database = os.getenv("NEO4J_DATABASE", self.config.get("connection", {}).get("database", "neo4j"))

        self.driver = None
        self.user_profile = UserProfile()
        self.session_context = {}

    def _load_config(self):
        """Carrega configurações do arquivo de configuração"""
        self.config = {}
        try:
            # Tenta carregar configuração do arquivo
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "config", "memory_settings.json"
            )
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    settings = json.load(f)
                    self.config = settings.get("neo4j_memory", {})
                    print(f"✅ Configurações carregadas de {config_path}")
        except Exception as e:
            print(f"⚠️ Usando configurações padrão: {e}")
            self.config = {
                "enabled": True,
                "features": {
                    "context_enrichment": {"enabled": True},
                    "interaction_saving": {"enabled": True},
                    "user_recognition": {"enabled": True}
                }
            }

    async def connect(self):
        """Conecta ao Neo4j"""
        try:
            self.driver = AsyncGraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password),
                max_connection_lifetime=3600
            )
            # Verifica conexão
            async with self.driver.session() as session:
                await session.run("RETURN 1")
            print(f"✅ Conectado ao Neo4j em {self.uri}")
            return True
        except Exception as e:
            print(f"❌ Erro ao conectar ao Neo4j: {e}")
            return False

    async def close(self):
        """Fecha conexão com Neo4j"""
        if self.driver:
            await self.driver.close()

    async def get_user_context(self, query: Optional[str] = None) -> Dict[str, Any]:
        """Busca contexto relevante do usuário no Neo4j"""
        context = {
            "user_profile": None,
            "recent_interactions": [],
            "relevant_memories": [],
            "learned_patterns": []
        }

        if not self.driver:
            return context

        try:
            async with self.driver.session() as session:
                # Busca perfil do usuário (Diego)
                result = await session.run("""
                    MATCH (n:Learning)
                    WHERE n.name CONTAINS 'Diego'
                       OR n.candidato = 'Diego Fornalha'
                       OR n.description CONTAINS 'Diego'
                    RETURN n
                    ORDER BY n.created_at DESC
                    LIMIT 5
                """)

                user_memories = []
                async for record in result:
                    node = record["n"]
                    if "Diego" in str(node.get("name", "")):
                        # Extrai informações do perfil
                        if not self.user_profile.name:
                            self.user_profile.name = "Diego"
                            self.user_profile.username = "2a"
                    user_memories.append(dict(node))

                context["user_profile"] = asdict(self.user_profile)

                # Busca memórias relevantes baseadas na query
                if query:
                    # Extrai palavras-chave
                    keywords = self._extract_keywords(query)

                    # Busca memórias relacionadas
                    cypher_query = """
                        MATCH (n:Learning)
                        WHERE ANY(keyword IN $keywords WHERE
                            toLower(n.name) CONTAINS toLower(keyword) OR
                            toLower(n.description) CONTAINS toLower(keyword) OR
                            toLower(n.task) CONTAINS toLower(keyword) OR
                            toLower(n.result) CONTAINS toLower(keyword)
                        )
                        RETURN n
                        ORDER BY n.created_at DESC
                        LIMIT 10
                    """

                    result = await session.run(cypher_query, keywords=keywords)

                    async for record in result:
                        node = dict(record["n"])
                        # Remove campos desnecessários
                        node.pop("id", None)
                        node.pop("updated_at", None)
                        context["relevant_memories"].append(node)

                # Busca padrões aprendidos
                result = await session.run("""
                    MATCH (n:Learning)
                    WHERE n.type IN ['successful_implementation', 'verified_solution', 'best_practice']
                    RETURN n
                    ORDER BY n.created_at DESC
                    LIMIT 5
                """)

                async for record in result:
                    node = dict(record["n"])
                    context["learned_patterns"].append({
                        "pattern": node.get("name", ""),
                        "description": node.get("description", ""),
                        "category": node.get("category", "")
                    })

        except Exception as e:
            print(f"Erro ao buscar contexto: {e}")

        return context

    async def save_interaction(self, user_message: str, assistant_response: str, session_id: str):
        """Salva interação no Neo4j para aprendizado"""
        if not self.driver:
            return

        try:
            async with self.driver.session() as session:
                # Extrai informações importantes da conversa
                extracted_info = self._extract_important_info(user_message, assistant_response)

                if extracted_info:
                    # Cria nó de memória
                    await session.run("""
                        CREATE (n:Learning {
                            name: $name,
                            type: 'conversation',
                            description: $description,
                            user_message: $user_message,
                            assistant_response: $assistant_response,
                            session_id: $session_id,
                            extracted_entities: $entities,
                            created_at: datetime(),
                            category: 'chat_interaction'
                        })
                    """,
                    name=extracted_info.get("summary", "Chat interaction"),
                    description=extracted_info.get("description", ""),
                    user_message=user_message[:500],  # Limita tamanho
                    assistant_response=assistant_response[:1000],  # Limita tamanho
                    session_id=session_id,
                    entities=json.dumps(extracted_info.get("entities", []))
                    )

                # Atualiza informações do usuário se detectadas
                if "nome" in user_message.lower() or "chamo" in user_message.lower():
                    # Extrai nome mencionado
                    name_match = re.search(r"(?:nome é|chamo|sou o?a?)\s+(\w+)", user_message, re.IGNORECASE)
                    if name_match:
                        detected_name = name_match.group(1)
                        await session.run("""
                            MERGE (u:User {username: '2a'})
                            SET u.name = $name,
                                u.last_interaction = datetime()
                        """, name=detected_name)

                        # Atualiza perfil local
                        self.user_profile.name = detected_name

        except Exception as e:
            print(f"Erro ao salvar interação: {e}")

    def _extract_keywords(self, text: str) -> List[str]:
        """Extrai palavras-chave do texto"""
        # Remove stopwords básicas
        stopwords = {'o', 'a', 'de', 'da', 'do', 'em', 'para', 'com', 'que', 'e', 'é', 'um', 'uma'}

        # Tokeniza e filtra
        words = re.findall(r'\b\w{3,}\b', text.lower())
        keywords = [w for w in words if w not in stopwords]

        # Retorna até 5 palavras-chave mais relevantes
        return list(set(keywords))[:5]

    def _extract_important_info(self, user_message: str, assistant_response: str) -> Optional[Dict]:
        """Extrai informações importantes da conversa"""
        info = {
            "summary": "",
            "description": "",
            "entities": []
        }

        # Detecta menções a nomes próprios
        name_patterns = re.findall(r'\b[A-Z][a-z]+\b', user_message + " " + assistant_response)
        if name_patterns:
            info["entities"].extend(name_patterns)

        # Detecta perguntas importantes
        if "?" in user_message:
            info["summary"] = f"Pergunta: {user_message[:50]}..."
            info["description"] = f"Usuário perguntou: {user_message}"

        # Detecta informações pessoais
        if any(word in user_message.lower() for word in ["nome", "chamo", "sou"]):
            info["summary"] = "Informação pessoal compartilhada"
            info["description"] = user_message
            return info

        # Detecta comandos ou solicitações
        if any(word in user_message.lower() for word in ["crie", "faça", "preciso", "quero"]):
            info["summary"] = "Solicitação de tarefa"
            info["description"] = user_message
            return info

        # Se não há informação relevante, retorna None
        if not info["entities"] and not info["summary"]:
            return None

        return info

    def format_context_for_prompt(self, context: Dict[str, Any]) -> str:
        """Formata o contexto para incluir no prompt do assistente"""
        prompt_parts = []

        # Adiciona perfil do usuário
        if context.get("user_profile") and context["user_profile"].get("name"):
            prompt_parts.append(f"👤 Usuário: {context['user_profile']['name']} (@{context['user_profile'].get('username', '2a')})")

        # Adiciona memórias relevantes
        if context.get("relevant_memories"):
            memories_text = "📚 Contexto relevante:\n"
            for mem in context["relevant_memories"][:3]:  # Limita a 3 memórias
                if mem.get("name"):
                    memories_text += f"- {mem['name']}"
                    if mem.get("description"):
                        memories_text += f": {mem['description'][:100]}..."
                    memories_text += "\n"
            prompt_parts.append(memories_text)

        # Adiciona padrões aprendidos
        if context.get("learned_patterns"):
            patterns_text = "🎯 Padrões conhecidos:\n"
            for pattern in context["learned_patterns"][:2]:  # Limita a 2 padrões
                if pattern.get("pattern"):
                    patterns_text += f"- {pattern['pattern']}\n"
            prompt_parts.append(patterns_text)

        if prompt_parts:
            return "\n".join(prompt_parts) + "\n---\n"
        return ""

# Singleton para uso global
_memory_integration = None

async def get_memory_integration() -> Neo4jMemoryIntegration:
    """Retorna instância singleton da integração de memória"""
    global _memory_integration
    if _memory_integration is None:
        _memory_integration = Neo4jMemoryIntegration()
        await _memory_integration.connect()
    return _memory_integration