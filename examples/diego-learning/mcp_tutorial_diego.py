#!/usr/bin/env python3
"""
🔴 GAP CRÍTICO 1: MCP TOOLS - TUTORIAL INTERATIVO
Tutorial criado especificamente para Diego Fornalha
"""

import json
from typing import Dict, Any

print("="*70)
print("🎯 DOMINANDO MCP TOOLS - RESOLVENDO SEU GAP #1")
print("="*70)

# ============================================================================
# CONCEITO FUNDAMENTAL
# ============================================================================
print("""
📚 O QUE SÃO MCP TOOLS?

MCP (Model Context Protocol) Tools são ferramentas CUSTOMIZADAS que você
cria para o Claude usar. É como dar superpoderes específicos ao Claude!

COMPONENTES ESSENCIAIS:
1. @tool decorator - marca a função como ferramenta
2. async function - SEMPRE assíncrona
3. Retorno específico - estrutura padronizada
""")

input("\n➡️  Pressione ENTER para ver a estrutura...")

# ============================================================================
# ESTRUTURA CORRETA
# ============================================================================
print("\n" + "="*70)
print("🔧 ESTRUTURA DE UMA MCP TOOL")
print("="*70)

exemplo_codigo = '''
@tool(
    name="calculadora",              # Nome único da ferramenta
    description="Faz cálculos",      # O que ela faz
    input_schema={                   # Parâmetros esperados
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Expressão matemática"
            }
        },
        "required": ["expression"]
    }
)
async def calculadora_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    # SEMPRE async!
    expr = args.get("expression", "0")
    resultado = eval(expr)  # Calcular

    # 🔴 ESTRUTURA DE RETORNO OBRIGATÓRIA!
    return {
        "content": [
            {
                "type": "text",
                "text": f"Resultado: {resultado}"
            }
        ]
    }
'''

print(exemplo_codigo)

input("\n➡️  Pressione ENTER para o quiz...")

# ============================================================================
# QUIZ INTERATIVO
# ============================================================================
print("\n" + "="*70)
print("📝 QUIZ MCP TOOLS - TESTE SEU CONHECIMENTO")
print("="*70)

score = 0
total = 5

# Pergunta 1
print("\n❓ PERGUNTA 1: Qual decorator usamos para criar uma MCP tool?")
print("   A) @mcp_tool")
print("   B) @tool")
print("   C) @custom_tool")
print("   D) @claude_tool")
resposta = input("\nSua resposta (A/B/C/D): ").upper()
if resposta == "B":
    print("✅ Correto! Usamos @tool")
    score += 20
else:
    print("❌ Incorreto. A resposta é B) @tool")

# Pergunta 2
print("\n❓ PERGUNTA 2: As funções MCP tool devem ser:")
print("   A) síncronas (def)")
print("   B) assíncronas (async def)")
print("   C) generators")
print("   D) classes")
resposta = input("\nSua resposta (A/B/C/D): ").upper()
if resposta == "B":
    print("✅ Correto! Sempre async def")
    score += 20
else:
    print("❌ Incorreto. A resposta é B) assíncronas (async def)")

# Pergunta 3
print("\n❓ PERGUNTA 3: Qual a estrutura de retorno CORRETA?")
print("   A) return resultado")
print("   B) return {'result': valor}")
print("   C) return {'content': [{'type': 'text', 'text': 'resultado'}]}")
print("   D) return None")
resposta = input("\nSua resposta (A/B/C/D): ").upper()
if resposta == "C":
    print("✅ Correto! Essa é a estrutura obrigatória!")
    score += 20
else:
    print("❌ Incorreto. A resposta é C - memorize essa estrutura!")

# Pergunta 4
print("\n❓ PERGUNTA 4: Como permitimos MCP tools no Claude?")
print("   A) api_key=TOOL_KEY")
print("   B) ClaudeCodeOptions(allowed_tools=['minha_tool'])")
print("   C) enable_tools=True")
print("   D) tools.activate()")
resposta = input("\nSua resposta (A/B/C/D): ").upper()
if resposta == "B":
    print("✅ Correto! Usamos allowed_tools em ClaudeCodeOptions")
    score += 20
else:
    print("❌ Incorreto. Use B) ClaudeCodeOptions(allowed_tools=['minha_tool'])")

# Pergunta 5
print("\n❓ PERGUNTA 5: O parâmetro 'args' em uma MCP tool é:")
print("   A) Uma string")
print("   B) Um número")
print("   C) Um dicionário (Dict)")
print("   D) Uma lista")
resposta = input("\nSua resposta (A/B/C/D): ").upper()
if resposta == "C":
    print("✅ Correto! args é sempre Dict[str, Any]")
    score += 20
else:
    print("❌ Incorreto. args é sempre C) Um dicionário")

# ============================================================================
# RESULTADO
# ============================================================================
print("\n" + "="*70)
print(f"🏆 SEU SCORE: {score}/100")
print("="*70)

if score == 100:
    print("""
    🎉 PARABÉNS DIEGO! VOCÊ DOMINOU MCP TOOLS!

    ✅ Gap #1 RESOLVIDO
    ✅ Score +20 pontos no bootcamp

    Próximo: Gap #2 - Hooks System
    """)
elif score >= 60:
    print("""
    📈 BOM PROGRESSO!

    Você entendeu os conceitos básicos.
    Revise as questões erradas e refaça o quiz.
    """)
else:
    print("""
    📚 PRECISA REVISAR!

    MCP Tools é crítico para seu progresso.
    Releia o tutorial e tente novamente.
    """)

# ============================================================================
# EXEMPLO PRÁTICO
# ============================================================================
if score < 100:
    print("\n" + "="*70)
    print("📌 EXEMPLO PRÁTICO PARA MEMORIZAR")
    print("="*70)
    print("""
    # PASSO 1: Criar a ferramenta
    @tool(name="minha_tool", description="Faz algo útil", input_schema={...})
    async def minha_tool(args: Dict) -> Dict:
        resultado = processar(args)
        return {"content": [{"type": "text", "text": resultado}]}

    # PASSO 2: Permitir no Claude
    options = ClaudeCodeOptions(allowed_tools=["minha_tool"])

    # PASSO 3: Usar
    async for msg in query("Use minha_tool para...", options=options):
        print(msg)
    """)

# ============================================================================
# SALVAR PROGRESSO
# ============================================================================
print("\n" + "="*70)
print("💾 SALVANDO SEU PROGRESSO")
print("="*70)

progresso = {
    "aluno": "Diego Fornalha",
    "tutorial": "MCP Tools",
    "score_quiz": score,
    "gap_resolvido": score == 100,
    "data": "2025-01-24"
}

with open("progresso_mcp_tools.json", "w") as f:
    json.dump(progresso, f, indent=2)

print(f"✅ Progresso salvo em progresso_mcp_tools.json")
print(f"   Score no quiz: {score}/100")

if score == 100:
    print("\n🚀 PRÓXIMO PASSO: python mcp_exercicio_pratico.py")
else:
    print("\n🔄 REFAÇA: python mcp_tutorial_diego.py")

print("\n" + "="*70)