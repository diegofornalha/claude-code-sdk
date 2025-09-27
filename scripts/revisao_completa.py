#!/usr/bin/env python3
"""
📚 REVISÃO COMPLETA - CLAUDE CODE SDK
Tudo que você aprendeu até agora!
"""

from datetime import datetime
from pathlib import Path
import json

def executar_revisao():
    print("\n" + "="*70)
    print("🔄 REVISÃO COMPLETA - CLAUDE CODE SDK BOOTCAMP")
    print("="*70)

    # ═══════════════════════════════════════════════════════════════
    # PARTE 1: CONCEITOS QUE VOCÊ JÁ APRENDEU
    # ═══════════════════════════════════════════════════════════════

    print("\n" + "="*70)
    print("✅ CONCEITOS QUE VOCÊ JÁ APRENDEU")
    print("="*70)

    print("""
1️⃣ QUERY vs CLIENT
─────────────────────────────────────────────────────────
query()                     │ ClaudeSDKClient
─────────────────────────────────────────────────────────
• Stateless (sem memória)   │ • Stateful (com contexto)
• Pergunta única            │ • Conversa contínua
• Mais simples              │ • Mais complexo
• asyncio obrigatório       │ • asyncio obrigatório

📝 Você aprendeu: Use query() para tarefas simples e isoladas

2️⃣ AUTENTICAÇÃO
─────────────────────────────────────────────────────────
✅ CORRETO: claude login
❌ ERRADO: ANTHROPIC_API_KEY

📝 Você aprendeu: SEMPRE use 'claude login', hooks bloqueiam API keys

3️⃣ CLAUDECODEOPTIONS
─────────────────────────────────────────────────────────
options = ClaudeCodeOptions(
    model="claude-3-5-sonnet-20241022",
    temperature=0.7,        # 0.1=consistente, 0.9=criativo
    allowed_tools=["File"], # Ferramentas permitidas
    system_prompt="..."     # Contexto
)

📝 Você aprendeu: temperature controla criatividade
""")

    # ═══════════════════════════════════════════════════════════════
    # PARTE 2: FERRAMENTAS DISPONÍVEIS
    # ═══════════════════════════════════════════════════════════════

    print("\n" + "="*70)
    print("🔧 FERRAMENTAS QUE VOCÊ PODE USAR")
    print("="*70)

    print("""
📁 FILE TOOLS
─────────────────────────────────────────────────────────
• Read       → Ler arquivos
• Write      → Criar/sobrescrever
• Edit       → Editar trechos
• MultiEdit  → Múltiplas edições

🔍 SEARCH TOOLS
─────────────────────────────────────────────────────────
• Grep       → Buscar padrões
• Glob       → Buscar arquivos
• WebSearch  → Buscar na web
• WebFetch   → Conteúdo de URLs

⚙️ SYSTEM TOOLS
─────────────────────────────────────────────────────────
• Bash       → Comandos shell
• Execute    → Código Python
• TodoWrite  → Gerenciar tarefas
• Task       → Sub-agentes
""")

    # ═══════════════════════════════════════════════════════════════
    # PARTE 3: SEUS GAPS CRÍTICOS
    # ═══════════════════════════════════════════════════════════════

    print("\n" + "="*70)
    print("🔴 GAPS CRÍTICOS QUE VOCÊ PRECISA RESOLVER")
    print("="*70)

    print("""
GAP #1: MCP TOOLS (Vale +20 pontos!)
─────────────────────────────────────────────────────────
❌ Você ainda não sabe criar ferramentas customizadas

Como resolver:
```python
@tool(name="calc", description="...", input_schema={...})
async def calc(args):
    return {"content": [{"type": "text", "text": "resultado"}]}
```

⚠️ SEMPRE retorne {"content": [...]}

GAP #2: HOOKS SYSTEM (Vale +20 pontos!)
─────────────────────────────────────────────────────────
❌ Você ainda não sabe interceptar ferramentas

Como resolver:
```python
def hook(tool_name, args):
    if tool_name == "Write":
        return {"behavior": "deny"}  # Bloqueia
    return None  # Permite
```

⚠️ None = permite, dict = bloqueia
""")

    # ═══════════════════════════════════════════════════════════════
    # PARTE 4: SUA EVOLUÇÃO
    # ═══════════════════════════════════════════════════════════════

    print("\n" + "="*70)
    print("📈 SUA EVOLUÇÃO ATÉ AGORA")
    print("="*70)

    score_inicial = 11
    conceitos_aprendidos = 3  # query, auth, options
    pontos_ganhos = conceitos_aprendidos * 5
    score_atual = score_inicial + pontos_ganhos

    print(f"""
INÍCIO DO BOOTCAMP
──────────────────────────────────────────────────────────
Score Inicial: {score_inicial}/100 (Iniciante)
Gaps: 4 (2 críticos)

APÓS REVISÃO
──────────────────────────────────────────────────────────
✅ Conceitos Dominados: {conceitos_aprendidos}
   • Diferença query() vs Client
   • Autenticação correta
   • ClaudeCodeOptions básico

📈 Score Atual: {score_atual}/100 (Básico)
🎯 Gaps Restantes: 2 CRÍTICOS (MCP + Hooks)

PROGRESSO NO BOOTCAMP
──────────────────────────────────────────────────────────
Fase 1 (Fundamentos):   ████░░░░░░ 40%
Fase 2 (Ferramentas):   ░░░░░░░░░░ 0%
Fase 3 (Gaps Críticos): ░░░░░░░░░░ 0%
Fase 4 (Expert):        ░░░░░░░░░░ 0%

Semana: 1/12
Nível: Básico → Próximo: Intermediário (60 pontos)
""")

    # ═══════════════════════════════════════════════════════════════
    # PARTE 5: EXERCÍCIOS PRÁTICOS
    # ═══════════════════════════════════════════════════════════════

    print("\n" + "="*70)
    print("💻 VAMOS PRATICAR!")
    print("="*70)

    print("""
EXERCÍCIO RÁPIDO #1 - query() básico
─────────────────────────────────────────────────────────
```python
import asyncio
from claude_code_sdk import query, ClaudeCodeOptions

async def exercicio1():
    # Tarefa: Pergunte a capital da França
    async for msg in query(
        prompt="Qual a capital da França?",
        options=ClaudeCodeOptions(temperature=0.3)
    ):
        print(f"Resposta: {msg.result}")

asyncio.run(exercicio1())
```

EXERCÍCIO RÁPIDO #2 - Usando ferramentas
─────────────────────────────────────────────────────────
```python
async def exercicio2():
    # Tarefa: Liste arquivos .py no diretório
    async for msg in query(
        prompt="Liste todos arquivos .py aqui",
        options=ClaudeCodeOptions(
            allowed_tools=["Glob", "Bash"]
        )
    ):
        print(msg.result)

asyncio.run(exercicio2())
```

EXERCÍCIO RÁPIDO #3 - Temperature
─────────────────────────────────────────────────────────
```python
async def exercicio3():
    # Compare respostas com diferentes temperatures

    # Conservador (0.1)
    async for msg in query(
        prompt="Escreva um haiku sobre programação",
        options=ClaudeCodeOptions(temperature=0.1)
    ):
        print(f"Conservador: {msg.result}")

    # Criativo (0.9)
    async for msg in query(
        prompt="Escreva um haiku sobre programação",
        options=ClaudeCodeOptions(temperature=0.9)
    ):
        print(f"Criativo: {msg.result}")

asyncio.run(exercicio3())
```
""")

    # ═══════════════════════════════════════════════════════════════
    # PARTE 6: PLANO DE AÇÃO
    # ═══════════════════════════════════════════════════════════════

    print("\n" + "="*70)
    print("🎯 SEU PLANO DE AÇÃO IMEDIATO")
    print("="*70)

    print(f"""
HOJE (15 minutos)
─────────────────────────────────────────────────────────
□ Execute: python3 01_hello_claude.py
□ Teste os 3 exercícios acima
□ Anote suas dúvidas

AMANHÃ (30 minutos)
─────────────────────────────────────────────────────────
□ Estude MCP Tools (GAP CRÍTICO #1)
□ Execute: python3 gap_1_mcp_tools_tutorial.py
□ Crie uma ferramenta customizada simples

ESTA SEMANA
─────────────────────────────────────────────────────────
□ Complete Fase 1 (Fundamentos)
□ Aumente score para 45+ pontos
□ Resolva pelo menos 1 gap crítico

META DO MÊS
─────────────────────────────────────────────────────────
□ Score 60+ (Intermediário)
□ Dominar MCP Tools e Hooks
□ Criar projeto próprio com SDK
""")

    # ═══════════════════════════════════════════════════════════════
    # PARTE 7: DICAS FINAIS
    # ═══════════════════════════════════════════════════════════════

    print("\n" + "="*70)
    print("💡 DICAS DO MENTOR")
    print("="*70)

    print("""
1. PRÁTICA > TEORIA
   "Código que funciona vale mais que teoria perfeita"

2. FOQUE NOS GAPS CRÍTICOS
   MCP Tools e Hooks valem 40 pontos juntos!

3. USE ASYNC SEMPRE
   Todo SDK é assíncrono - acostume-se!

4. ERRO É APRENDIZADO
   Cada erro ensina algo novo

5. 15 MINUTOS POR DIA
   Consistência vence intensidade
""")

    # Salvar progresso
    progresso = {
        "data_revisao": datetime.now().isoformat(),
        "score_inicial": score_inicial,
        "score_atual": score_atual,
        "conceitos_dominados": [
            "query vs Client",
            "Autenticação",
            "ClaudeCodeOptions"
        ],
        "gaps_restantes": [
            "MCP Tools",
            "Hooks System"
        ],
        "fase_atual": 1,
        "semana": 1
    }

    # Salvar em arquivo
    log_dir = Path.home() / '.claude' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)

    arquivo = log_dir / 'bootcamp_revisao.json'

    historico = []
    if arquivo.exists():
        with open(arquivo, 'r') as f:
            historico = json.load(f)

    historico.append(progresso)

    with open(arquivo, 'w') as f:
        json.dump(historico, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Revisão salva em: {arquivo}")

    # ═══════════════════════════════════════════════════════════════
    # MENSAGEM FINAL
    # ═══════════════════════════════════════════════════════════════

    print("\n" + "="*70)
    print("🚀 VOCÊ ESTÁ NO CAMINHO CERTO!")
    print("="*70)

    print(f"""
Score evoluiu: 11 → {score_atual} (+{pontos_ganhos} pontos)
Nível: Iniciante → Básico

Continue praticando diariamente e você será EXPERT!

Próximo comando:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
python3 01_hello_claude.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Boa sorte! 🎯
""")

if __name__ == "__main__":
    executar_revisao()