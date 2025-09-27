#!/usr/bin/env python3
"""
🎯 Avaliação Automática de Conhecimento Claude Code SDK
Sistema para verificar nível atual e criar plano personalizado
"""

import json
from datetime import datetime
from pathlib import Path

def avaliar_conhecimento_base():
    """Avalia conhecimento básico do SDK"""

    print("\n" + "="*70)
    print("🎯 AVALIAÇÃO INICIAL - CLAUDE CODE SDK BOOTCAMP")
    print("="*70)

    # Simulando respostas típicas de um iniciante
    conhecimento_atual = {
        "conceitos_basicos": {
            "query_vs_client": False,  # Não sabe a diferença
            "autenticacao": False,     # Não conhece claude login
            "async_await": True,        # Conhece Python async
        },
        "ferramentas": {
            "file_tools": False,        # Não usou File, Edit, etc
            "search_tools": False,      # Não usou Grep, Glob
            "system_tools": False,      # Não usou Bash, Execute
        },
        "avancado": {
            "mcp_tools": False,         # GAP CRÍTICO #1
            "hooks_system": False,      # GAP CRÍTICO #2
            "multi_agent": False,       # Não conhece Task tool
        }
    }

    # Calcular score
    total_items = 9
    conhecidos = sum([
        conhecimento_atual["conceitos_basicos"]["query_vs_client"],
        conhecimento_atual["conceitos_basicos"]["autenticacao"],
        conhecimento_atual["conceitos_basicos"]["async_await"],
        conhecimento_atual["ferramentas"]["file_tools"],
        conhecimento_atual["ferramentas"]["search_tools"],
        conhecimento_atual["ferramentas"]["system_tools"],
        conhecimento_atual["avancado"]["mcp_tools"],
        conhecimento_atual["avancado"]["hooks_system"],
        conhecimento_atual["avancado"]["multi_agent"]
    ])

    score_inicial = int((conhecidos / total_items) * 100)

    # Identificar gaps
    gaps = []
    if not conhecimento_atual["conceitos_basicos"]["query_vs_client"]:
        gaps.append("query() vs ClaudeSDKClient")
    if not conhecimento_atual["conceitos_basicos"]["autenticacao"]:
        gaps.append("Autenticação (claude login)")
    if not conhecimento_atual["avancado"]["mcp_tools"]:
        gaps.append("MCP Tools (GAP CRÍTICO)")
    if not conhecimento_atual["avancado"]["hooks_system"]:
        gaps.append("Hooks System (GAP CRÍTICO)")

    return score_inicial, gaps, conhecimento_atual

def criar_plano_personalizado(score, gaps):
    """Cria plano de estudos baseado no score e gaps"""

    plano = {
        "fase_1_fundamentos": {
            "semanas": "1-3",
            "objetivo": "Score 45→60",
            "topicos": [
                "✅ query() para consultas simples",
                "✅ ClaudeCodeOptions básico",
                "✅ Autenticação com claude login",
                "✅ Async/await patterns"
            ],
            "exercicios": [
                "01_hello_claude.py",
                "exercicios_praticos_pt_br.py (1-3)"
            ]
        },
        "fase_2_ferramentas": {
            "semanas": "4-6",
            "objetivo": "Score 60→70",
            "topicos": [
                "📁 File Tools (Read, Write, Edit)",
                "🔍 Search Tools (Grep, Glob)",
                "⚙️ System Tools (Bash, Execute)",
                "📝 TodoWrite para organização"
            ],
            "exercicios": [
                "exercicios_praticos_pt_br.py (4-5)"
            ]
        },
        "fase_3_gaps_criticos": {
            "semanas": "7-10",
            "objetivo": "Score 70→85",
            "topicos": [
                "🔴 MCP Tools - Criar ferramentas customizadas",
                "🔴 Hooks System - Interceptar execuções",
                "🤖 Multi-agent com Task tool"
            ],
            "exercicios": [
                "gap_1_mcp_tools_tutorial.py",
                "gap_2_hooks_tutorial.py",
                "exercicios_praticos_pt_br.py (6-7)"
            ]
        },
        "fase_4_expert": {
            "semanas": "11-12",
            "objetivo": "Score 85→100",
            "topicos": [
                "🚀 ClaudeSDKClient avançado",
                "🔄 Streaming com receive_response()",
                "🎯 Orquestração multi-agente",
                "💾 Integração Neo4j Memory"
            ],
            "projetos": [
                "Projeto final: Sistema completo com SDK"
            ]
        }
    }

    return plano

def gerar_relatorio():
    """Gera relatório completo de avaliação"""

    print("\n🔍 Analisando seu conhecimento atual...")
    score, gaps, conhecimento = avaliar_conhecimento_base()

    # Determinar nível
    if score < 40:
        nivel = "Iniciante"
        emoji = "🌱"
    elif score < 60:
        nivel = "Básico"
        emoji = "🌿"
    elif score < 75:
        nivel = "Intermediário"
        emoji = "🌳"
    elif score < 90:
        nivel = "Avançado"
        emoji = "🎯"
    else:
        nivel = "Expert"
        emoji = "🏆"

    print("\n" + "="*70)
    print(f"📊 RESULTADO DA AVALIAÇÃO")
    print("="*70)
    print(f"\n{emoji} Nível Atual: {nivel}")
    print(f"📈 Score: {score}/100")
    print(f"⏱️ Tempo estimado até Expert: {12 if score < 40 else 8} semanas")

    if gaps:
        print(f"\n🎯 GAPS IDENTIFICADOS:")
        for gap in gaps:
            if "CRÍTICO" in gap:
                print(f"   🔴 {gap}")
            else:
                print(f"   ⚠️ {gap}")

    # Criar plano
    plano = criar_plano_personalizado(score, gaps)

    print("\n" + "="*70)
    print("📚 SEU PLANO PERSONALIZADO DE ESTUDOS")
    print("="*70)

    for fase_nome, fase_dados in plano.items():
        print(f"\n📌 {fase_nome.upper().replace('_', ' ')}")
        print(f"   Semanas: {fase_dados.get('semanas', 'N/A')}")
        print(f"   Meta: {fase_dados.get('objetivo', 'N/A')}")

        if 'topicos' in fase_dados:
            print("\n   Tópicos:")
            for topico in fase_dados['topicos']:
                print(f"      {topico}")

        if 'exercicios' in fase_dados:
            print("\n   Exercícios:")
            for exercicio in fase_dados['exercicios']:
                print(f"      → {exercicio}")

        if 'projetos' in fase_dados:
            print("\n   Projetos:")
            for projeto in fase_dados['projetos']:
                print(f"      → {projeto}")

    # Salvar resultado
    resultado = {
        "data": datetime.now().isoformat(),
        "score_inicial": score,
        "nivel": nivel,
        "gaps": gaps,
        "plano": plano
    }

    # Criar diretório se não existir
    log_dir = Path.home() / '.claude' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)

    # Salvar avaliação
    arquivo = log_dir / 'bootcamp_avaliacao.json'
    with open(arquivo, 'w') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Avaliação salva em: {arquivo}")

    # Próximos passos imediatos
    print("\n" + "="*70)
    print("🚀 COMEÇAR AGORA")
    print("="*70)

    if score < 40:
        print("""
1️⃣ Primeiro exercício (5 minutos):
   python3 01_hello_claude.py

2️⃣ Entender conceitos básicos:
   - query() = pergunta única sem contexto
   - Client = conversa com memória

3️⃣ Configurar autenticação:
   claude login

💡 Dica: Comece simples! Um hello world funcional vale mais que teoria complexa.
""")
    elif score < 60:
        print("""
1️⃣ Praticar ferramentas básicas:
   python3 exercicios_praticos_pt_br.py 1

2️⃣ Focar nos gaps críticos:
   - MCP Tools: criar ferramentas customizadas
   - Hooks: interceptar execuções

💡 Dica: Os gaps críticos são eliminatórios em projetos reais!
""")
    else:
        print("""
1️⃣ Projetos avançados:
   - Implementar sistema com MCP Tools
   - Criar hooks para governança

2️⃣ Integração Neo4j:
   - Persistir conhecimento
   - Criar sistema de memória

💡 Dica: Foque em projetos práticos para consolidar conhecimento!
""")

    return resultado

if __name__ == "__main__":
    resultado = gerar_relatorio()

    print("\n" + "="*70)
    print("💬 MENSAGEM DO MENTOR")
    print("="*70)
    print("""
Olá! Sou seu mentor no Bootcamp Claude Code SDK.

Minha missão é transformar você em um EXPERT do SDK em 12 semanas.

Lembre-se:
• Use query() para perguntas simples
• Use Client para conversas com contexto
• SEMPRE autentique com 'claude login'
• MCP Tools e Hooks são CRÍTICOS - não pule!
• Async/await sempre que possível

Vamos começar! 🚀

Digite: python3 01_hello_claude.py
""")