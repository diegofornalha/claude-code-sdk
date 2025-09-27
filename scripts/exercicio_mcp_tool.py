#!/usr/bin/env python3
"""
💻 EXERCÍCIO PRÁTICO - CRIANDO SUA PRIMEIRA MCP TOOL
Vamos consolidar o que você aprendeu!
"""

import asyncio
from typing import Dict, Any
import random
import string
import re

# Importar o necessário do SDK (simulado para o exercício)
# from claude_code_sdk import tool, query, ClaudeCodeOptions

print("\n" + "="*70)
print("💻 EXERCÍCIO PRÁTICO - MCP TOOLS")
print("="*70)
print("Vamos criar 3 MCP Tools funcionais!\n")

# ═══════════════════════════════════════════════════════════════
# MCP TOOL #1: GERADOR DE SENHAS
# ═══════════════════════════════════════════════════════════════

print("1️⃣ MCP Tool: Gerador de Senhas Seguras")
print("-"*70)

# Simulando @tool decorator
def tool(name, description, input_schema):
    def decorator(func):
        func.tool_name = name
        func.tool_description = description
        func.tool_schema = input_schema
        return func
    return decorator

@tool(
    name="gerar_senha",
    description="Gera senhas seguras com opções customizáveis",
    input_schema={
        "type": "object",
        "properties": {
            "tamanho": {
                "type": "integer",
                "minimum": 8,
                "maximum": 64,
                "default": 16
            },
            "incluir_maiusculas": {
                "type": "boolean",
                "default": True
            },
            "incluir_numeros": {
                "type": "boolean",
                "default": True
            },
            "incluir_simbolos": {
                "type": "boolean",
                "default": True
            }
        }
    }
)
async def gerar_senha(args: Dict[str, Any]) -> Dict[str, Any]:
    """Gera uma senha segura com as opções especificadas"""

    # Pegar parâmetros com valores padrão
    tamanho = args.get("tamanho", 16)
    incluir_maiusculas = args.get("incluir_maiusculas", True)
    incluir_numeros = args.get("incluir_numeros", True)
    incluir_simbolos = args.get("incluir_simbolos", True)

    # Construir conjunto de caracteres
    caracteres = string.ascii_lowercase  # sempre tem minúsculas

    if incluir_maiusculas:
        caracteres += string.ascii_uppercase
    if incluir_numeros:
        caracteres += string.digits
    if incluir_simbolos:
        caracteres += "!@#$%^&*()_+-=[]{}|;:,.<>?"

    # Gerar senha
    senha = ''.join(random.choice(caracteres) for _ in range(tamanho))

    # Calcular força da senha
    forca = "Fraca"
    if tamanho >= 12 and incluir_numeros and incluir_simbolos:
        forca = "Forte"
    elif tamanho >= 10 and (incluir_numeros or incluir_simbolos):
        forca = "Média"

    # SEMPRE retornar neste formato!
    return {
        "content": [{
            "type": "text",
            "text": f"""Senha Gerada:
━━━━━━━━━━━━━━━━━━━━━━━━
{senha}
━━━━━━━━━━━━━━━━━━━━━━━━
Tamanho: {tamanho} caracteres
Força: {forca}
Maiúsculas: {'✅' if incluir_maiusculas else '❌'}
Números: {'✅' if incluir_numeros else '❌'}
Símbolos: {'✅' if incluir_simbolos else '❌'}"""
        }]
    }

# ═══════════════════════════════════════════════════════════════
# MCP TOOL #2: VALIDADOR DE EMAIL
# ═══════════════════════════════════════════════════════════════

print("\n2️⃣ MCP Tool: Validador de Email")
print("-"*70)

@tool(
    name="validar_email",
    description="Valida formato de email e sugere correções",
    input_schema={
        "type": "object",
        "properties": {
            "email": {
                "type": "string"
            },
            "verificar_dominio": {
                "type": "boolean",
                "default": False
            }
        },
        "required": ["email"]
    }
)
async def validar_email(args: Dict[str, Any]) -> Dict[str, Any]:
    """Valida email e fornece feedback detalhado"""

    email = args.get("email", "").strip()
    verificar_dominio = args.get("verificar_dominio", False)

    # Regex para validação básica de email
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    problemas = []
    sugestoes = []

    # Verificações
    if not email:
        problemas.append("Email vazio")
        valido = False
    elif "@" not in email:
        problemas.append("Falta o símbolo @")
        valido = False
    elif email.count("@") > 1:
        problemas.append("Múltiplos símbolos @")
        valido = False
    elif not re.match(padrao, email):
        valido = False
        if email.startswith("@"):
            problemas.append("Email começa com @")
        if email.endswith("@"):
            problemas.append("Email termina com @")
        if ".." in email:
            problemas.append("Pontos duplos consecutivos")
        if not "." in email.split("@")[-1]:
            problemas.append("Domínio sem extensão (.com, .org, etc)")
    else:
        valido = True

    # Verificar domínios comuns
    if verificar_dominio and valido:
        dominios_validos = ["gmail.com", "outlook.com", "yahoo.com", "hotmail.com"]
        dominio = email.split("@")[1]
        if dominio in dominios_validos:
            info_dominio = f"✅ Domínio conhecido: {dominio}"
        else:
            info_dominio = f"⚠️ Domínio não verificado: {dominio}"
    else:
        info_dominio = ""

    # Montar resultado
    if valido:
        resultado = f"""✅ Email Válido!
Email: {email}
Formato: Correto
{info_dominio}"""
    else:
        resultado = f"""❌ Email Inválido!
Email: {email}
Problemas encontrados:
{chr(10).join(f'• {p}' for p in problemas)}

💡 Formato correto: usuario@dominio.com"""

    return {
        "content": [{
            "type": "text",
            "text": resultado
        }]
    }

# ═══════════════════════════════════════════════════════════════
# MCP TOOL #3: ANALISADOR DE TEXTO AVANÇADO
# ═══════════════════════════════════════════════════════════════

print("\n3️⃣ MCP Tool: Analisador de Texto Avançado")
print("-"*70)

@tool(
    name="analisar_texto_completo",
    description="Análise completa de texto com estatísticas detalhadas",
    input_schema={
        "type": "object",
        "properties": {
            "texto": {
                "type": "string"
            },
            "tipo_analise": {
                "type": "string",
                "enum": ["basica", "completa", "sentimento"],
                "default": "basica"
            }
        },
        "required": ["texto"]
    }
)
async def analisar_texto_completo(args: Dict[str, Any]) -> Dict[str, Any]:
    """Analisa texto com múltiplas métricas"""

    texto = args.get("texto", "")
    tipo_analise = args.get("tipo_analise", "basica")

    if not texto:
        return {
            "content": [{
                "type": "text",
                "text": "❌ Erro: Texto vazio fornecido"
            }]
        }

    # Métricas básicas
    caracteres = len(texto)
    palavras = len(texto.split())
    linhas = len(texto.splitlines())
    frases = len(re.split(r'[.!?]+', texto)) - 1

    resultado = f"""📊 ANÁLISE DE TEXTO
{'='*40}
📝 Métricas Básicas:
• Caracteres: {caracteres}
• Palavras: {palavras}
• Linhas: {linhas}
• Frases: {frases}"""

    if tipo_analise in ["completa", "sentimento"]:
        # Análise mais detalhada
        palavras_unicas = len(set(texto.lower().split()))
        media_palavra = caracteres / palavras if palavras > 0 else 0
        palavras_lista = texto.lower().split()

        # Palavras mais comuns (top 3)
        from collections import Counter
        contador = Counter(palavras_lista)
        top_palavras = contador.most_common(3)

        resultado += f"""

📈 Métricas Avançadas:
• Palavras únicas: {palavras_unicas}
• Média caracteres/palavra: {media_palavra:.1f}
• Diversidade vocabular: {(palavras_unicas/palavras*100):.1f}%

🔝 Top 3 Palavras:"""
        for palavra, freq in top_palavras:
            resultado += f"\n   • '{palavra}': {freq}x"

    if tipo_analise == "sentimento":
        # Análise simples de sentimento
        palavras_positivas = ["bom", "ótimo", "excelente", "feliz", "amor", "sucesso"]
        palavras_negativas = ["ruim", "péssimo", "triste", "ódio", "fracasso", "problema"]

        texto_lower = texto.lower()
        pos_count = sum(1 for p in palavras_positivas if p in texto_lower)
        neg_count = sum(1 for p in palavras_negativas if p in texto_lower)

        if pos_count > neg_count:
            sentimento = "😊 Positivo"
        elif neg_count > pos_count:
            sentimento = "😔 Negativo"
        else:
            sentimento = "😐 Neutro"

        resultado += f"""

💭 Análise de Sentimento:
• Palavras positivas: {pos_count}
• Palavras negativas: {neg_count}
• Sentimento geral: {sentimento}"""

    return {
        "content": [{
            "type": "text",
            "text": resultado
        }]
    }

# ═══════════════════════════════════════════════════════════════
# TESTAR AS MCP TOOLS
# ═══════════════════════════════════════════════════════════════

async def testar_tools():
    """Testa as MCP Tools criadas"""

    print("\n" + "="*70)
    print("🧪 TESTANDO AS MCP TOOLS")
    print("="*70)

    # Teste 1: Gerador de Senha
    print("\n📝 Teste 1: Gerando senha forte...")
    resultado = await gerar_senha({
        "tamanho": 20,
        "incluir_maiusculas": True,
        "incluir_numeros": True,
        "incluir_simbolos": True
    })
    print(resultado["content"][0]["text"])

    # Teste 2: Validador de Email
    print("\n📝 Teste 2: Validando emails...")

    emails_teste = [
        "usuario@exemplo.com",
        "invalido@",
        "@exemplo.com",
        "teste@@exemplo.com"
    ]

    for email in emails_teste:
        resultado = await validar_email({"email": email})
        print(f"\nTestando: {email}")
        print(resultado["content"][0]["text"].split('\n')[0])  # Primeira linha

    # Teste 3: Analisador de Texto
    print("\n📝 Teste 3: Analisando texto...")
    texto_exemplo = """MCP Tools são incríveis!
Elas permitem criar ferramentas customizadas.
O Claude Code SDK é muito bom para automação."""

    resultado = await analisar_texto_completo({
        "texto": texto_exemplo,
        "tipo_analise": "completa"
    })
    print(resultado["content"][0]["text"])

# Executar testes
if __name__ == "__main__":
    asyncio.run(testar_tools())

    print("\n" + "="*70)
    print("✅ PARABÉNS! VOCÊ CRIOU 3 MCP TOOLS!")
    print("="*70)
    print("""
Você aprendeu:
1. Como estruturar uma MCP Tool com @tool
2. Como validar e processar args
3. Como SEMPRE retornar {"content": [...]}
4. Como criar ferramentas úteis e reutilizáveis

📈 Score: +20 pontos pelo gap MCP Tools!

🎯 Próximo passo: Resolver o gap de Hooks
Comando: python3 gap_2_hooks_tutorial.py
""")