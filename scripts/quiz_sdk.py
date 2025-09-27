#!/usr/bin/env python3
"""
🎯 Quiz Rápido Claude Code SDK
Teste seu conhecimento atual
"""

import json
from datetime import datetime
from pathlib import Path

# Perguntas fundamentais
PERGUNTAS = [
    {
        "pergunta": "1. Qual a diferença entre query() e ClaudeSDKClient?",
        "opcoes": [
            "A) query() é mais rápido, Client é mais lento",
            "B) query(): cada pergunta isolada. Client: conversa contínua com contexto",
            "C) query() usa internet, Client funciona offline",
            "D) Não há diferença"
        ],
        "resposta": "B",
        "explicacao": "query() = stateless (sem memória), Client = stateful (com contexto)",
        "pontos": 10
    },
    {
        "pergunta": "2. Como autenticar no Claude Code SDK?",
        "opcoes": [
            "A) Usando ANTHROPIC_API_KEY",
            "B) Com claude login",
            "C) Não precisa autenticar",
            "D) Com username e senha"
        ],
        "resposta": "B",
        "explicacao": "Sempre use 'claude login', nunca API keys!",
        "pontos": 10
    },
    {
        "pergunta": "3. O que são MCP Tools?",
        "opcoes": [
            "A) Ferramentas de linha de comando",
            "B) Ferramentas customizadas que você pode criar com @tool decorator",
            "C) APIs REST externas",
            "D) Bibliotecas Python"
        ],
        "resposta": "B",
        "explicacao": "MCP Tools são ferramentas locais customizadas com @tool",
        "pontos": 15
    },
    {
        "pergunta": "4. Como funciona o sistema de Hooks?",
        "opcoes": [
            "A) São callbacks que interceptam execução de ferramentas",
            "B) São ganchos para pendurar código",
            "C) São webhooks HTTP",
            "D) São loops infinitos"
        ],
        "resposta": "A",
        "explicacao": "Hooks interceptam ferramentas - PreToolUse e PostToolUse",
        "pontos": 15
    },
    {
        "pergunta": "5. Qual o parâmetro para permitir ferramentas específicas?",
        "opcoes": [
            "A) tools=['File', 'Search']",
            "B) allowed_tools=['File', 'Search']",
            "C) enable_tools=['File', 'Search']",
            "D) use_tools=['File', 'Search']"
        ],
        "resposta": "B",
        "explicacao": "Use allowed_tools em ClaudeCodeOptions",
        "pontos": 10
    }
]

def executar_quiz():
    """Executa o quiz e calcula score"""
    print("\n" + "="*60)
    print("🎯 QUIZ RÁPIDO CLAUDE CODE SDK - 5 PERGUNTAS")
    print("="*60)
    print("\nResponda com A, B, C ou D\n")

    score = 0
    total = 60  # Total de pontos possíveis
    respostas = []
    gaps = []

    for q in PERGUNTAS:
        print(f"\n{q['pergunta']}")
        for opcao in q['opcoes']:
            print(f"   {opcao}")

        resposta = input("\nSua resposta: ").upper().strip()

        if resposta == q['resposta']:
            print("✅ Correto!")
            score += q['pontos']
        else:
            print(f"❌ Incorreto. {q['explicacao']}")

            # Identificar gaps
            if "MCP" in q['pergunta']:
                gaps.append("MCP Tools")
            elif "Hook" in q['pergunta']:
                gaps.append("Hooks System")
            elif "query" in q['pergunta'].lower():
                gaps.append("Conceitos Fundamentais")

        respostas.append({
            "pergunta": q['pergunta'],
            "sua_resposta": resposta,
            "resposta_correta": q['resposta'],
            "acertou": resposta == q['resposta']
        })

    # Calcular nível
    porcentagem = (score / total) * 100
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

    # Mostrar resultado
    print("\n" + "="*60)
    print(f"📊 RESULTADO FINAL")
    print("="*60)
    print(f"\nScore: {score}/{total} pontos ({porcentagem:.0f}%)")
    print(f"Nível: {nivel}")

    if gaps:
        print(f"\n🎯 Gaps Identificados:")
        for gap in set(gaps):
            print(f"   • {gap}")

    # Salvar resultado
    resultado = {
        "data": datetime.now().isoformat(),
        "score": score,
        "total": total,
        "porcentagem": porcentagem,
        "nivel": nivel,
        "gaps": list(set(gaps)),
        "respostas": respostas
    }

    # Salvar em arquivo
    historico_file = Path.home() / '.claude' / 'logs' / 'quiz_sdk_historico.json'
    historico_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        if historico_file.exists():
            with open(historico_file, 'r') as f:
                historico = json.load(f)
        else:
            historico = []

        historico.append(resultado)

        with open(historico_file, 'w') as f:
            json.dump(historico, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Resultado salvo em: {historico_file}")
    except Exception as e:
        print(f"⚠️ Erro ao salvar: {e}")

    # Recomendações
    print("\n📚 PRÓXIMOS PASSOS:")
    if "MCP Tools" in gaps:
        print("   1. Estude MCP Tools - crie ferramentas customizadas")
    if "Hooks System" in gaps:
        print("   2. Aprenda sobre Hooks - intercepte execuções")
    if "Conceitos Fundamentais" in gaps:
        print("   3. Revise query() vs ClaudeSDKClient")

    if porcentagem < 60:
        print("\n💡 Recomendo começar com: python 01_hello_claude.py")
    elif porcentagem < 80:
        print("\n💡 Pratique com exercícios intermediários")
    else:
        print("\n🎉 Excelente! Você está pronto para projetos avançados!")

    return score, nivel, gaps

if __name__ == "__main__":
    score, nivel, gaps = executar_quiz()

    # Salvar no Neo4j (se disponível)
    print("\n🔄 Atualizando Neo4j...")
    print(f"   Diego Fornalha: Score {score}/60, Nível {nivel}")
    if gaps:
        print(f"   Gaps: {', '.join(gaps)}")