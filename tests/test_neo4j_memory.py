#!/usr/bin/env python3
"""
Teste da integração Neo4j Memory com o chat
"""

import asyncio
import json
from core.neo4j_memory_integration import get_memory_integration

async def test_memory():
    """Testa a integração de memória Neo4j"""

    print("🧪 Testando integração de memória Neo4j...")

    # Obter instância da integração
    memory = await get_memory_integration()

    # Teste 1: Buscar contexto do usuário
    print("\n📖 Teste 1: Buscando contexto do usuário...")
    context = await memory.get_user_context(query="meu nome")

    if context.get("user_profile"):
        print(f"✅ Perfil encontrado: {context['user_profile']}")
    else:
        print("⚠️ Perfil não encontrado")

    if context.get("relevant_memories"):
        print(f"✅ Memórias encontradas: {len(context['relevant_memories'])} memórias")
        for mem in context['relevant_memories'][:2]:
            print(f"  - {mem.get('name', 'Sem nome')}")
    else:
        print("⚠️ Nenhuma memória relevante encontrada")

    # Teste 2: Salvar interação
    print("\n💾 Teste 2: Salvando nova interação...")
    await memory.save_interaction(
        user_message="Meu nome é Diego, sou desenvolvedor",
        assistant_response="Olá Diego! Prazer em conhecê-lo. Como posso ajudar você com seu projeto de desenvolvimento?",
        session_id="test-session-001"
    )
    print("✅ Interação salva com sucesso")

    # Teste 3: Verificar se a memória foi persistida
    print("\n🔍 Teste 3: Verificando persistência...")
    await asyncio.sleep(1)  # Aguarda um pouco para garantir que foi salvo

    new_context = await memory.get_user_context(query="Diego desenvolvedor")
    if new_context.get("relevant_memories"):
        found = False
        for mem in new_context['relevant_memories']:
            if "Diego" in str(mem.get("user_message", "")) or "Diego" in str(mem.get("description", "")):
                found = True
                print(f"✅ Memória encontrada: {mem.get('name', 'Conversa')}")
                break

        if not found:
            print("⚠️ Memória não encontrada após salvamento")

    # Teste 4: Formatação de contexto
    print("\n📝 Teste 4: Formatando contexto para prompt...")
    formatted = memory.format_context_for_prompt(context)
    if formatted:
        print("✅ Contexto formatado:")
        print(formatted[:200] + "..." if len(formatted) > 200 else formatted)
    else:
        print("⚠️ Contexto vazio")

    # Fechar conexão
    await memory.close()
    print("\n✅ Testes concluídos!")

if __name__ == "__main__":
    asyncio.run(test_memory())