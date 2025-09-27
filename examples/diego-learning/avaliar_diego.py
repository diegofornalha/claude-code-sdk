#!/usr/bin/env python3
"""
🎯 Avaliação Automática - Diego Fornalha
Baseado no conhecimento atual registrado no Neo4j
"""

from datetime import datetime
import json
from pathlib import Path

def avaliar_conhecimento():
    """Avalia conhecimento baseado em informações conhecidas"""

    print("\n" + "="*60)
    print("📊 AVALIAÇÃO DE CONHECIMENTO - DIEGO FORNALHA")
    print("="*60)

    # Conhecimentos confirmados
    conhece = {
        "conceito_basico": True,  # Já trabalhou com SDK em projetos
        "query_vs_client": False,  # Gap identificado anteriormente
        "autenticacao": True,  # Sabe sobre claude login
        "mcp_tools": False,  # Gap crítico identificado
        "hooks": False,  # Gap crítico identificado
        "allowed_tools": False,  # Precisa aprender
        "async_await": True,  # Desenvolvedor experiente Python
        "streaming": False,  # Ainda não praticou
    }

    # Calcular score detalhado
    score_detalhado = {
        "Fundamentos (20pts)": {
            "query() básico": 10 if conhece["conceito_basico"] else 0,
            "query vs client": 10 if conhece["query_vs_client"] else 0,
        },
        "Autenticação (10pts)": {
            "claude login": 10 if conhece["autenticacao"] else 0,
        },
        "Ferramentas (20pts)": {
            "allowed_tools": 10 if conhece["allowed_tools"] else 0,
            "Tools nativas": 10,  # Conhece File, Search, etc
        },
        "Avançado (30pts)": {
            "MCP Tools": 15 if conhece["mcp_tools"] else 0,
            "Hooks System": 15 if conhece["hooks"] else 0,
        },
        "Async (20pts)": {
            "async/await": 10 if conhece["async_await"] else 0,
            "streaming": 10 if conhece["streaming"] else 0,
        }
    }

    # Calcular totais
    score_total = 0
    max_total = 0

    print("\n📋 ANÁLISE DETALHADA:\n")
    for categoria, items in score_detalhado.items():
        cat_score = sum(items.values())

        print(f"{categoria}")
        for item, pontos in items.items():
            status = "✅" if pontos > 0 else "❌"
            print(f"   {status} {item}: {pontos} pts")

        score_total += cat_score

    max_total = 100  # Total fixo de 100 pontos

    # Score final
    porcentagem = (score_total / max_total) * 100

    print("\n" + "="*60)
    print(f"📊 RESULTADO FINAL")
    print("="*60)
    print(f"\n🎯 Score: {score_total}/100 pontos ({porcentagem:.0f}%)")

    # Determinar nível
    if porcentagem >= 90:
        nivel = "Expert"
    elif porcentagem >= 75:
        nivel = "Avançado"
    elif porcentagem >= 60:
        nivel = "Intermediário"
    elif porcentagem >= 40:
        nivel = "Básico"
    else:
        nivel = "Iniciante"

    print(f"📈 Nível: {nivel}")

    # Gaps identificados
    gaps = []
    if not conhece["mcp_tools"]:
        gaps.append("MCP Tools")
    if not conhece["hooks"]:
        gaps.append("Hooks System")
    if not conhece["query_vs_client"]:
        gaps.append("Query vs Client")
    if not conhece["allowed_tools"]:
        gaps.append("Parâmetro allowed_tools")
    if not conhece["streaming"]:
        gaps.append("Streaming responses")

    print(f"\n🔍 Gaps Identificados ({len(gaps)}):")
    for i, gap in enumerate(gaps, 1):
        print(f"   {i}. {gap}")

    # Plano de ação
    print("\n" + "="*60)
    print("📚 PLANO DE AÇÃO PERSONALIZADO")
    print("="*60)

    print("\n🎯 SEMANA 1 - Fundamentos (Meta: 60/100)")
    print("   Dia 1-2: query() vs ClaudeSDKClient")
    print("   Dia 3-4: Parâmetro allowed_tools")
    print("   Dia 5: Projeto prático - CLI Summarizer")

    print("\n🎯 SEMANA 2-3 - Gaps Críticos (Meta: 75/100)")
    print("   📌 MCP Tools:")
    print("      • Criar ferramenta customizada com @tool")
    print("      • Retornar formato correto: {'content': [...]}")
    print("   📌 Hooks System:")
    print("      • PreToolUse e PostToolUse")
    print("      • Validação e controle de execução")

    print("\n🎯 SEMANA 4 - Avançado (Meta: 85/100)")
    print("   • Streaming com receive_response()")
    print("   • Multi-agent com Task tool")
    print("   • Projeto: Sistema com memória Neo4j")

    print("\n🎯 SEMANA 5-12 - Expert (Meta: 100/100)")
    print("   • Projetos complexos reais")
    print("   • Contribuir para o SDK")
    print("   • Mentorar outros desenvolvedores")

    # Salvar resultado
    resultado = {
        "data": datetime.now().isoformat(),
        "nome": "Diego Fornalha",
        "score_atual": score_total,
        "nivel_atual": nivel,
        "meta_score": 100,
        "gaps": gaps,
        "semana_bootcamp": 1,
        "detalhamento": score_detalhado
    }

    # Criar arquivo de progresso
    progress_file = Path.home() / '.claude' / 'bootcamp' / 'diego_progress.json'
    progress_file.parent.mkdir(parents=True, exist_ok=True)

    with open(progress_file, 'w') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Progresso salvo em: {progress_file}")

    return score_total, nivel, gaps

if __name__ == "__main__":
    score, nivel, gaps = avaliar_conhecimento()

    print("\n" + "="*60)
    print("🚀 PRÓXIMO PASSO IMEDIATO")
    print("="*60)
    print("\n1️⃣ Criar arquivo: 01_hello_claude.py")
    print("2️⃣ Implementar query() básico")
    print("3️⃣ Testar com pergunta simples")
    print("\n💡 Vamos começar agora? Digite: 'vamos criar o hello claude'")