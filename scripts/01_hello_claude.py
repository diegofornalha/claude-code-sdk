#!/usr/bin/env python3
"""
🎯 Exercício 1: Hello Claude com SDK
Aprenda o básico do Claude Code SDK
"""

import asyncio
from claude_code_sdk import query, ClaudeCodeOptions

async def exemplo_basico():
    """Exemplo mais simples possível com query()"""

    print("\n" + "="*60)
    print("🎯 EXERCÍCIO 1: HELLO CLAUDE")
    print("="*60)

    # query() é para perguntas simples sem contexto
    print("\n📝 Fazendo uma pergunta simples ao Claude...")

    resposta = ""
    async for msg in query(
        prompt="Olá Claude! Responda em português: Qual a capital do Brasil?",
        options=ClaudeCodeOptions(
            model="claude-3-5-sonnet-20241022",
            temperature=0.7
        )
    ):
        resposta = msg.result

    print(f"\n🤖 Claude respondeu: {resposta}")

    print("\n" + "-"*60)
    print("📚 CONCEITO APRENDIDO:")
    print("-"*60)
    print("""
✅ query() é para perguntas ÚNICAS
✅ Cada pergunta é independente (sem memória)
✅ Use async/await sempre
✅ ClaudeCodeOptions controla o comportamento

Quando usar query():
• Perguntas simples e diretas
• Não precisa de contexto anterior
• Tarefas isoladas

Quando NÃO usar query():
• Conversas com múltiplas mensagens
• Precisa lembrar do contexto
• Diálogos interativos
    """)

async def exemplo_com_ferramentas():
    """Exemplo usando ferramentas permitidas"""

    print("\n" + "="*60)
    print("🔧 EXERCÍCIO 2: USANDO FERRAMENTAS")
    print("="*60)

    print("\n📝 Pedindo ao Claude para listar arquivos...")

    resposta = ""
    async for msg in query(
        prompt="Liste os arquivos Python (.py) no diretório atual",
        options=ClaudeCodeOptions(
            model="claude-3-5-sonnet-20241022",
            allowed_tools=["Bash", "Glob"],  # Permitir ferramentas específicas
            temperature=0.7
        )
    ):
        resposta = msg.result

    print(f"\n🤖 Resultado: {resposta}")

    print("\n" + "-"*60)
    print("📚 CONCEITO APRENDIDO:")
    print("-"*60)
    print("""
✅ allowed_tools permite ferramentas específicas
✅ Claude pode executar comandos com Bash
✅ Claude pode buscar arquivos com Glob

Ferramentas disponíveis:
• File: Read, Write, Edit, MultiEdit
• Search: Grep, Glob, WebSearch
• System: Bash, Execute, TodoWrite
    """)

async def exemplo_temperatura():
    """Exemplo mostrando o efeito da temperatura"""

    print("\n" + "="*60)
    print("🌡️ EXERCÍCIO 3: TEMPERATURA (CRIATIVIDADE)")
    print("="*60)

    # Temperatura baixa = mais consistente
    print("\n📝 Testando com temperatura 0.1 (conservador)...")

    resposta_baixa = ""
    async for msg in query(
        prompt="Complete: O céu é...",
        options=ClaudeCodeOptions(
            model="claude-3-5-sonnet-20241022",
            temperature=0.1  # Muito conservador
        )
    ):
        resposta_baixa = msg.result

    print(f"Temperatura 0.1: {resposta_baixa}")

    # Temperatura alta = mais criativo
    print("\n📝 Testando com temperatura 0.9 (criativo)...")

    resposta_alta = ""
    async for msg in query(
        prompt="Complete: O céu é...",
        options=ClaudeCodeOptions(
            model="claude-3-5-sonnet-20241022",
            temperature=0.9  # Muito criativo
        )
    ):
        resposta_alta = msg.result

    print(f"Temperatura 0.9: {resposta_alta}")

    print("\n" + "-"*60)
    print("📚 CONCEITO APRENDIDO:")
    print("-"*60)
    print("""
✅ temperature controla criatividade (0.0 a 1.0)
✅ 0.0-0.3 = Tarefas técnicas, código
✅ 0.7-0.9 = Tarefas criativas, brainstorm

Use temperatura baixa para:
• Código e comandos
• Respostas factuais
• Análise de dados

Use temperatura alta para:
• Escrita criativa
• Brainstorming
• Ideias novas
    """)

async def main():
    """Executa todos os exercícios"""

    print("\n" + "="*70)
    print("🚀 BEM-VINDO AO BOOTCAMP CLAUDE CODE SDK!")
    print("="*70)
    print("""
Este é seu primeiro exercício prático.
Vamos aprender os conceitos fundamentais do SDK.

Requisito: Você precisa ter feito 'claude login' antes!
    """)

    # Exercício 1: Básico
    await exemplo_basico()

    # Perguntar se quer continuar
    input("\n⏸️ Pressione ENTER para continuar...")

    # Exercício 2: Ferramentas
    await exemplo_com_ferramentas()

    input("\n⏸️ Pressione ENTER para continuar...")

    # Exercício 3: Temperatura
    await exemplo_temperatura()

    # Resumo final
    print("\n" + "="*70)
    print("🎉 PARABÉNS! VOCÊ COMPLETOU O EXERCÍCIO 1")
    print("="*70)
    print("""
✅ Você aprendeu:
   1. Como usar query() para perguntas simples
   2. Como permitir ferramentas com allowed_tools
   3. Como controlar criatividade com temperature

📈 Progresso: Score 11 → 20 (Iniciante)

🎯 Próximo exercício:
   python3 exercicios_praticos_pt_br.py 1

💡 Lembre-se:
   • query() = sem memória (stateless)
   • ClaudeSDKClient = com memória (stateful)
   • Sempre use async/await
   • NUNCA use API keys!
    """)

if __name__ == "__main__":
    # Verificar se tem autenticação
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        print("\n💡 Dica: Você fez 'claude login' antes de executar?")
        print("   Execute: claude login")