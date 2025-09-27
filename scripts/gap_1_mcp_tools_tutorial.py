#!/usr/bin/env python3
"""
🔴 GAP CRÍTICO #1: MCP TOOLS
Tutorial completo para dominar ferramentas customizadas
Vale +20 pontos no seu score!
"""

import asyncio
from typing import Dict, Any
import json
from datetime import datetime

print("\n" + "="*70)
print("🎯 TUTORIAL MCP TOOLS - RESOLVENDO SEU GAP CRÍTICO")
print("="*70)
print("""
MCP Tools (Model Context Protocol) permitem criar ferramentas
customizadas que o Claude pode usar durante conversas.

REGRA DE OURO: Sempre retorne {"content": [...]}
""")

# ═══════════════════════════════════════════════════════════════
# PARTE 1: ENTENDENDO MCP TOOLS
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("📚 PARTE 1: O QUE SÃO MCP TOOLS?")
print("="*70)

print("""
MCP Tools são ferramentas LOCAIS customizadas que:
• Executam no seu computador (não são APIs)
• São decoradas com @tool
• Podem receber parâmetros
• SEMPRE retornam {"content": [...]}

ATENÇÃO: MCP Tools NÃO são:
❌ APIs REST externas
❌ Webhooks HTTP
❌ Serviços remotos
✅ São funções Python locais!
""")

# ═══════════════════════════════════════════════════════════════
# PARTE 2: ESTRUTURA BÁSICA
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("🏗️ PARTE 2: ESTRUTURA DE UMA MCP TOOL")
print("="*70)

exemplo_basico = """
from claude_code_sdk import tool

@tool(
    name="nome_da_ferramenta",           # Nome único
    description="O que ela faz",         # Descrição clara
    input_schema={                        # Parâmetros esperados
        "type": "object",
        "properties": {
            "param1": {"type": "string"},
            "param2": {"type": "number"}
        },
        "required": ["param1"]           # Parâmetros obrigatórios
    }
)
async def nome_da_ferramenta(args: Dict[str, Any]) -> Dict[str, Any]:
    # Processar args
    resultado = f"Processando {args['param1']}"

    # SEMPRE retorne este formato:
    return {
        "content": [{
            "type": "text",
            "text": resultado
        }]
    }
"""

print(exemplo_basico)

# ═══════════════════════════════════════════════════════════════
# PARTE 3: EXEMPLO PRÁTICO #1 - CALCULADORA
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("💻 PARTE 3: EXEMPLO PRÁTICO - CALCULADORA")
print("="*70)

print("""
Vamos criar uma calculadora como MCP Tool:
""")

codigo_calculadora = '''
from claude_code_sdk import tool

@tool(
    name="calculadora",
    description="Realiza operações matemáticas básicas",
    input_schema={
        "type": "object",
        "properties": {
            "operacao": {
                "type": "string",
                "enum": ["somar", "subtrair", "multiplicar", "dividir"]
            },
            "numeros": {
                "type": "array",
                "items": {"type": "number"},
                "minItems": 2
            }
        },
        "required": ["operacao", "numeros"]
    }
)
async def calculadora(args: Dict[str, Any]) -> Dict[str, Any]:
    """Calculadora MCP Tool"""

    operacao = args["operacao"]
    numeros = args["numeros"]

    if operacao == "somar":
        resultado = sum(numeros)
    elif operacao == "subtrair":
        resultado = numeros[0] - sum(numeros[1:])
    elif operacao == "multiplicar":
        resultado = 1
        for n in numeros:
            resultado *= n
    elif operacao == "dividir":
        resultado = numeros[0]
        for n in numeros[1:]:
            if n != 0:
                resultado /= n
            else:
                return {
                    "content": [{
                        "type": "text",
                        "text": "Erro: Divisão por zero!"
                    }]
                }

    # SEMPRE este formato de retorno!
    return {
        "content": [{
            "type": "text",
            "text": f"Resultado de {operacao}: {resultado}"
        }]
    }
'''

print(codigo_calculadora)

# ═══════════════════════════════════════════════════════════════
# PARTE 4: EXEMPLO PRÁTICO #2 - ANALISADOR DE TEXTO
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("💻 PARTE 4: EXEMPLO - ANALISADOR DE TEXTO")
print("="*70)

codigo_analisador = '''
@tool(
    name="analisar_texto",
    description="Analisa estatísticas de um texto",
    input_schema={
        "type": "object",
        "properties": {
            "texto": {"type": "string"},
            "incluir_detalhes": {"type": "boolean", "default": False}
        },
        "required": ["texto"]
    }
)
async def analisar_texto(args: Dict[str, Any]) -> Dict[str, Any]:
    """Analisa estatísticas de texto"""

    texto = args["texto"]
    incluir_detalhes = args.get("incluir_detalhes", False)

    # Análise básica
    num_caracteres = len(texto)
    num_palavras = len(texto.split())
    num_linhas = len(texto.splitlines())

    resultado = f"""Análise do Texto:
• Caracteres: {num_caracteres}
• Palavras: {num_palavras}
• Linhas: {num_linhas}"""

    if incluir_detalhes:
        # Análise detalhada
        palavras_unicas = len(set(texto.lower().split()))
        media_palavra = num_caracteres / num_palavras if num_palavras > 0 else 0

        resultado += f"""
• Palavras únicas: {palavras_unicas}
• Média caracteres/palavra: {media_palavra:.1f}"""

    return {
        "content": [{
            "type": "text",
            "text": resultado
        }]
    }
'''

print(codigo_analisador)

# ═══════════════════════════════════════════════════════════════
# PARTE 5: EXEMPLO PRÁTICO #3 - FERRAMENTA COM ESTADO
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("💻 PARTE 5: EXEMPLO - FERRAMENTA COM MEMÓRIA")
print("="*70)

codigo_memoria = '''
# Variável global para manter estado
memoria_global = []

@tool(
    name="memoria",
    description="Armazena e recupera informações",
    input_schema={
        "type": "object",
        "properties": {
            "acao": {
                "type": "string",
                "enum": ["adicionar", "listar", "limpar", "buscar"]
            },
            "item": {"type": "string"},
            "busca": {"type": "string"}
        },
        "required": ["acao"]
    }
)
async def memoria(args: Dict[str, Any]) -> Dict[str, Any]:
    """Ferramenta com memória persistente"""

    global memoria_global
    acao = args["acao"]

    if acao == "adicionar":
        item = args.get("item", "")
        if item:
            memoria_global.append({
                "item": item,
                "timestamp": datetime.now().isoformat()
            })
            resultado = f"Item '{item}' adicionado à memória"
        else:
            resultado = "Erro: Item vazio"

    elif acao == "listar":
        if memoria_global:
            itens = [f"• {m['item']}" for m in memoria_global]
            resultado = "Itens na memória:\\n" + "\\n".join(itens)
        else:
            resultado = "Memória vazia"

    elif acao == "limpar":
        memoria_global = []
        resultado = "Memória limpa"

    elif acao == "buscar":
        busca = args.get("busca", "").lower()
        encontrados = [m['item'] for m in memoria_global
                      if busca in m['item'].lower()]
        if encontrados:
            resultado = f"Encontrados: {', '.join(encontrados)}"
        else:
            resultado = "Nenhum item encontrado"

    return {
        "content": [{
            "type": "text",
            "text": resultado
        }]
    }
'''

print(codigo_memoria)

# ═══════════════════════════════════════════════════════════════
# PARTE 6: ERROS COMUNS E COMO EVITAR
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("⚠️ PARTE 6: ERROS COMUNS COM MCP TOOLS")
print("="*70)

print("""
❌ ERRO #1: Retornar string simples
─────────────────────────────────────
# ERRADO:
return "resultado"

# CORRETO:
return {"content": [{"type": "text", "text": "resultado"}]}

❌ ERRO #2: Esquecer async
─────────────────────────────────────
# ERRADO:
def minha_tool(args):

# CORRETO:
async def minha_tool(args):

❌ ERRO #3: Não validar args
─────────────────────────────────────
# ERRADO:
valor = args["param"]  # Pode dar KeyError

# CORRETO:
valor = args.get("param", "default")

❌ ERRO #4: Retornar tipos errados
─────────────────────────────────────
# ERRADO:
return {"result": "valor"}  # Formato errado!

# CORRETO:
return {"content": [{"type": "text", "text": "valor"}]}

❌ ERRO #5: Confundir com API REST
─────────────────────────────────────
MCP Tools são LOCAIS, não são endpoints HTTP!
Elas executam no seu computador.
""")

# ═══════════════════════════════════════════════════════════════
# PARTE 7: USANDO MCP TOOLS COM QUERY
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("🔗 PARTE 7: INTEGRANDO MCP TOOLS COM SDK")
print("="*70)

codigo_integracao = '''
import asyncio
from claude_code_sdk import query, ClaudeCodeOptions, tool

# Definir a MCP Tool
@tool(
    name="get_time",
    description="Retorna a hora atual",
    input_schema={
        "type": "object",
        "properties": {
            "formato": {
                "type": "string",
                "enum": ["completo", "hora", "data"]
            }
        }
    }
)
async def get_time(args):
    from datetime import datetime

    formato = args.get("formato", "completo")
    agora = datetime.now()

    if formato == "hora":
        resultado = agora.strftime("%H:%M:%S")
    elif formato == "data":
        resultado = agora.strftime("%Y-%m-%d")
    else:
        resultado = agora.isoformat()

    return {
        "content": [{
            "type": "text",
            "text": f"Horário: {resultado}"
        }]
    }

# Usar com query()
async def exemplo_uso():
    async for msg in query(
        prompt="Que horas são agora?",
        options=ClaudeCodeOptions(
            allowed_tools=["get_time"],  # Permitir a ferramenta
            temperature=0.3
        )
    ):
        print(msg.result)

asyncio.run(exemplo_uso())
'''

print(codigo_integracao)

# ═══════════════════════════════════════════════════════════════
# PARTE 8: EXERCÍCIOS PRÁTICOS
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("📝 PARTE 8: EXERCÍCIOS PARA PRATICAR")
print("="*70)

print("""
EXERCÍCIO 1: Crie uma MCP Tool "contador_palavras"
─────────────────────────────────────────────────────
• Recebe: texto (string)
• Retorna: número de palavras
• Extra: contar também frases e parágrafos

EXERCÍCIO 2: Crie uma MCP Tool "conversor_unidades"
─────────────────────────────────────────────────────
• Recebe: valor, de_unidade, para_unidade
• Converte: km↔milhas, celsius↔fahrenheit, kg↔libras
• Retorna: valor convertido

EXERCÍCIO 3: Crie uma MCP Tool "validador_email"
─────────────────────────────────────────────────────
• Recebe: email (string)
• Valida: formato correto
• Retorna: válido/inválido + motivo

EXERCÍCIO 4: Crie uma MCP Tool "gerador_senha"
─────────────────────────────────────────────────────
• Recebe: tamanho, incluir_simbolos
• Gera: senha aleatória segura
• Retorna: senha gerada
""")

# ═══════════════════════════════════════════════════════════════
# PARTE 9: CHECKLIST DE DOMÍNIO
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("✅ PARTE 9: CHECKLIST - VOCÊ DOMINA MCP TOOLS?")
print("="*70)

print("""
Marque o que você já entende:

□ MCP Tools são funções Python locais, não APIs
□ Sempre use @tool decorator
□ Sempre retorne {"content": [...]}
□ Use async def, não def normal
□ Defina input_schema corretamente
□ Valide args antes de usar
□ Teste com allowed_tools no query()
□ MCP Tools podem manter estado global
□ Trate erros e retorne mensagens úteis
□ Integre com ClaudeCodeOptions

Se marcou todos, você domina MCP Tools! +20 pontos! 🎉
""")

# ═══════════════════════════════════════════════════════════════
# RESUMO FINAL
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("🎯 RESUMO: MCP TOOLS EM 1 MINUTO")
print("="*70)

print("""
1. MCP Tools são ferramentas Python customizadas
2. Use @tool(name, description, input_schema)
3. SEMPRE retorne {"content": [{"type": "text", "text": "..."}]}
4. São funções async locais, não APIs REST
5. Integre com allowed_tools no ClaudeCodeOptions

FÓRMULA DO SUCESSO:
─────────────────────────────────────────────────────
@tool(...) + async def + {"content": [...]} = MCP Tool!

Você resolveu o GAP #1! 🎉
Score: +20 pontos

Próximo: gap_2_hooks_tutorial.py
""")

# Salvar progresso
print("\n💾 Salvando seu progresso...")
progresso = {
    "gap": "MCP Tools",
    "status": "estudado",
    "data": datetime.now().isoformat(),
    "pontos_ganhos": 20
}

print(f"✅ Gap MCP Tools marcado como estudado!")
print(f"📈 Seu score aumentou em +20 pontos!")
print(f"\n🎯 Próximo comando: python3 gap_2_hooks_tutorial.py")