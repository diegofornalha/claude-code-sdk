#!/usr/bin/env python3
"""
🔴 MCP TOOLS - RESUMO ESSENCIAL PARA DIEGO
"""

print("="*70)
print("🎯 MCP TOOLS - TUDO QUE VOCÊ PRECISA SABER")
print("="*70)

# ============================================================================
# O ESSENCIAL
# ============================================================================
print("""
📚 MCP TOOLS - CONCEITO FUNDAMENTAL

MCP Tools são ferramentas customizadas que você cria para o Claude usar.
É como criar superpoderes específicos que o Claude não tinha antes!

✅ SEMPRE LEMBRE:
1. Use decorator @tool
2. Função SEMPRE async
3. Retorno SEMPRE no formato específico
4. Permitir em allowed_tools
""")

print("\n" + "="*70)
print("🔧 ESTRUTURA COMPLETA DE UMA MCP TOOL")
print("="*70)

print("""
from claude_code_sdk import tool
from typing import Dict, Any

@tool(
    name="calculadora",                  # Nome único
    description="Calcula expressões",    # Descrição clara
    input_schema={                       # Schema dos parâmetros
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Expressão matemática"
            }
        },
        "required": ["expression"]       # Parâmetros obrigatórios
    }
)
async def calculadora_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    # 🔴 SEMPRE async def, NUNCA só def!

    # Pegar parâmetros do dicionário args
    expr = args.get("expression", "0")

    # Processar
    resultado = eval(expr)

    # 🔴 ESTRUTURA DE RETORNO OBRIGATÓRIA - MEMORIZE!
    return {
        "content": [
            {
                "type": "text",
                "text": f"Resultado: {resultado}"
            }
        ]
    }
""")

print("\n" + "="*70)
print("🎮 COMO USAR NO CLAUDE")
print("="*70)

print("""
from claude_code_sdk import query, ClaudeCodeOptions

# PASSO 1: Configurar opções permitindo a ferramenta
options = ClaudeCodeOptions(
    allowed_tools=["calculadora"],    # 🔴 CRÍTICO: Permitir sua tool!
    temperature=0.2
)

# PASSO 2: Usar com query()
async def main():
    prompt = "Use a calculadora para somar 42 + 17"

    async for msg in query(prompt, options=options):
        print(msg)

# PASSO 3: Executar
import asyncio
asyncio.run(main())
""")

print("\n" + "="*70)
print("❌ ERROS COMUNS (VOCÊ FEZ ESTES!)")
print("="*70)

print("""
❌ ERRO 1: Não usar async
   ERRADO:  def minha_tool(args):
   CERTO:   async def minha_tool(args):

❌ ERRO 2: Retorno errado
   ERRADO:  return resultado
   ERRADO:  return {"result": resultado}
   CERTO:   return {"content": [{"type": "text", "text": str(resultado)}]}

❌ ERRO 3: Esquecer allowed_tools
   ERRADO:  options = ClaudeCodeOptions()
   CERTO:   options = ClaudeCodeOptions(allowed_tools=["minha_tool"])

❌ ERRO 4: Args não é dicionário
   ERRADO:  async def tool(expression: str)
   CERTO:   async def tool(args: Dict[str, Any])
""")

print("\n" + "="*70)
print("📝 EXEMPLO COMPLETO - FERRAMENTA DE ANÁLISE")
print("="*70)

print("""
@tool(
    name="analisador_codigo",
    description="Analisa métricas de código Python",
    input_schema={
        "type": "object",
        "properties": {
            "codigo": {"type": "string"},
            "metrica": {
                "type": "string",
                "enum": ["linhas", "funcoes", "complexidade"]
            }
        },
        "required": ["codigo", "metrica"]
    }
)
async def analisador_codigo(args: Dict[str, Any]) -> Dict[str, Any]:
    codigo = args.get("codigo", "")
    metrica = args.get("metrica", "linhas")

    if metrica == "linhas":
        resultado = f"Código tem {codigo.count('\\n')+1} linhas"
    elif metrica == "funcoes":
        resultado = f"Encontrei {codigo.count('def ')} funções"
    else:
        resultado = "Métrica não implementada"

    return {
        "content": [{"type": "text", "text": resultado}]
    }
""")

print("\n" + "="*70)
print("🏆 CHECKLIST PARA SCORE 100")
print("="*70)

print("""
□ Sei usar @tool decorator
□ Sempre uso async def
□ Retorno {"content": [{"type": "text", "text": "..."}]}
□ Uso Dict[str, Any] para args
□ Adiciono em allowed_tools
□ Sei criar input_schema
□ Entendo properties e required
□ Posso criar tools com estado
□ Sei registrar múltiplas tools
□ Consigo debugar erros de MCP
""")

print("\n" + "="*70)
print("🚀 PRÓXIMOS PASSOS")
print("="*70)

print("""
1. PRATIQUE: Crie 3 MCP tools diferentes
   - Uma para manipular strings
   - Uma para fazer cálculos
   - Uma com estado persistente

2. TESTE: Use suas tools com Claude

3. AVANCE: Aprenda sobre Hooks (Gap #2)

Diego, você está a 20 pontos de resolver este gap!
Dedique 30 minutos hoje para praticar MCP Tools.

Score atual: 46/100
Score após dominar MCP: 66/100 (+20 pontos!)
""")

print("\n" + "="*70)
print("💾 Salvando resumo...")

# Salvar progresso
import json
from datetime import datetime

progresso = {
    "aluno": "Diego Fornalha",
    "data": datetime.now().isoformat(),
    "gap": "MCP Tools",
    "status": "estudando",
    "score_antes": 46,
    "score_potencial": 66,
    "conceitos_aprendidos": [
        "@tool decorator",
        "async functions",
        "return format",
        "allowed_tools",
        "input_schema"
    ]
}

with open("mcp_progresso_diego.json", "w") as f:
    json.dump(progresso, f, indent=2)

print("✅ Progresso salvo em mcp_progresso_diego.json")
print("\n🎯 Execute novamente quando quiser revisar!")
print("="*70)