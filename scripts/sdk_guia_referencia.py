#!/usr/bin/env python3
"""
📚 GUIA DE REFERÊNCIA RÁPIDA - CLAUDE CODE SDK
Todos os conceitos essenciais em um só lugar
"""

def mostrar_guia():
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                    CLAUDE CODE SDK - GUIA RÁPIDO                      ║
╚══════════════════════════════════════════════════════════════════════╝

🎯 CONCEITOS FUNDAMENTAIS
═══════════════════════════════════════════════════════════════════════

1️⃣ QUERY vs CLIENT
─────────────────────────────────────────────────────────────────────
query()                          │ ClaudeSDKClient
─────────────────────────────────────────────────────────────────────
• Pergunta única                │ • Conversa contínua
• Sem memória (stateless)       │ • Com contexto (stateful)
• Mais simples                   │ • Mais complexo
• Para tarefas isoladas         │ • Para diálogos

📝 Exemplo query():
```python
async for msg in query("O que é Python?"):
    print(msg.result)
```

📝 Exemplo Client:
```python
client = ClaudeSDKClient()
await client.send_message("Olá!")
async for msg in client.receive_response():
    print(msg.result)
```

2️⃣ AUTENTICAÇÃO
─────────────────────────────────────────────────────────────────────
✅ SEMPRE USE:     claude login
❌ NUNCA USE:      ANTHROPIC_API_KEY

3️⃣ CLAUDECODEOPTIONS - PARÂMETROS PRINCIPAIS
─────────────────────────────────────────────────────────────────────
options = ClaudeCodeOptions(
    model="claude-3-5-sonnet-20241022",     # Modelo
    temperature=0.7,                         # Criatividade (0.0-1.0)
    allowed_tools=["File", "Search"],       # Ferramentas permitidas
    system_prompt="Você é um assistente",   # Prompt do sistema
    max_tokens=4096                         # Tokens máximos
)

🔧 FERRAMENTAS DISPONÍVEIS
═══════════════════════════════════════════════════════════════════════

📁 FILE TOOLS
─────────────────────────────────────────────────────────────────────
• Read       - Ler arquivos
• Write      - Criar/sobrescrever arquivos
• Edit       - Editar trechos específicos
• MultiEdit  - Múltiplas edições em um arquivo

🔍 SEARCH TOOLS
─────────────────────────────────────────────────────────────────────
• Grep       - Buscar padrões em arquivos
• Glob       - Buscar arquivos por nome
• WebSearch  - Buscar na web
• WebFetch   - Buscar conteúdo de URL

⚙️ SYSTEM TOOLS
─────────────────────────────────────────────────────────────────────
• Bash       - Executar comandos shell
• Execute    - Executar código Python
• TodoWrite  - Gerenciar lista de tarefas
• Task       - Delegar para sub-agentes

🔴 GAPS CRÍTICOS - VOCÊ PRECISA DOMINAR
═══════════════════════════════════════════════════════════════════════

1. MCP TOOLS (Model Context Protocol)
─────────────────────────────────────────────────────────────────────
Criar ferramentas customizadas:

```python
from claude_code_sdk import tool

@tool(
    name="calculadora",
    description="Faz cálculos matemáticos",
    input_schema={
        "type": "object",
        "properties": {
            "operacao": {"type": "string"},
            "numeros": {"type": "array", "items": {"type": "number"}}
        }
    }
)
async def calculadora(args):
    # IMPORTANTE: Sempre retorne {"content": [...]}
    return {
        "content": [{
            "type": "text",
            "text": f"Resultado: {sum(args['numeros'])}"
        }]
    }
```

2. HOOKS SYSTEM
─────────────────────────────────────────────────────────────────────
Interceptar execução de ferramentas:

```python
from claude_code_sdk import HookMatcher

def validar_ferramenta(tool_name, args):
    if tool_name == "Write" and ".env" in args.get("file_path", ""):
        return {"behavior": "deny", "message": "Não pode criar .env!"}
    return None  # None = permitir

hook = HookMatcher(
    matcher="PreToolUse",
    hooks=[validar_ferramenta]
)
```

📈 NÍVEIS DE PROFICIÊNCIA
═══════════════════════════════════════════════════════════════════════

Score  │ Nível         │ Conhecimentos
───────┼───────────────┼─────────────────────────────────────────
0-39   │ 🌱 Iniciante  │ Não conhece SDK
40-59  │ 🌿 Básico     │ query() básico, autenticação
60-74  │ 🌳 Intermed.  │ Ferramentas, async/await
75-89  │ 🎯 Avançado   │ MCP Tools, Hooks parcial
90-100 │ 🏆 Expert     │ Domina tudo + multi-agent

⚡ DICAS DE OURO
═══════════════════════════════════════════════════════════════════════

1. Sempre use async/await - o SDK é 100% assíncrono
2. query() para simples, Client para complexo
3. MCP Tools SEMPRE retornam {"content": [...]}
4. Hooks: None = permite, {"behavior": "deny"} = bloqueia
5. temperature: 0.1 = consistente, 0.9 = criativo
6. allowed_tools limita quais ferramentas Claude pode usar
7. NUNCA hardcode API keys - sempre claude login

🚀 COMANDOS ÚTEIS
═══════════════════════════════════════════════════════════════════════

claude login                     # Autenticar
python3 01_hello_claude.py       # Primeiro exercício
python3 quiz_sdk.py              # Testar conhecimento

📚 ESTRUTURA DE APRENDIZADO
═══════════════════════════════════════════════════════════════════════

Semanas 1-3:  Fundamentos (query, options, auth)
Semanas 4-6:  Ferramentas (File, Search, System)
Semanas 7-10: Gaps Críticos (MCP, Hooks)
Semanas 11-12: Expert (Client, streaming, multi-agent)

💡 EXEMPLO COMPLETO
═══════════════════════════════════════════════════════════════════════

```python
import asyncio
from claude_code_sdk import query, ClaudeCodeOptions

async def main():
    # Configurar opções
    options = ClaudeCodeOptions(
        model="claude-3-5-sonnet-20241022",
        temperature=0.7,
        allowed_tools=["File", "Search"],
        system_prompt="Você é um assistente útil"
    )

    # Fazer pergunta
    async for msg in query("Crie um hello.py", options=options):
        print(msg.result)

if __name__ == "__main__":
    asyncio.run(main())
```

╔══════════════════════════════════════════════════════════════════════╗
║         Dúvidas? Execute: python3 quiz_sdk.py --completo            ║
╚══════════════════════════════════════════════════════════════════════╝
""")

if __name__ == "__main__":
    mostrar_guia()

    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Execute: python3 01_hello_claude.py")
    print("2. Teste seu conhecimento: python3 quiz_sdk.py")
    print("3. Pratique com exercícios: python3 exercicios_praticos_pt_br.py 1")