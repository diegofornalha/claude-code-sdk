#!/usr/bin/env python3
"""
🔄 REVISÃO INTERATIVA - CLAUDE CODE SDK
Vamos consolidar o que você aprendeu!
"""

import asyncio
from datetime import datetime
from pathlib import Path
import json

class RevisaoSDK:
    def __init__(self):
        self.conceitos_revisados = []
        self.score_atual = 11  # Score inicial
        self.conceitos_dominados = []
        self.conceitos_pendentes = []

    def revisar_conceitos_fundamentais(self):
        """Revisa os conceitos básicos aprendidos"""

        print("\n" + "="*70)
        print("📚 REVISÃO: CONCEITOS FUNDAMENTAIS")
        print("="*70)

        conceitos = {
            "query_vs_client": {
                "titulo": "query() vs ClaudeSDKClient",
                "aprendido": """
✅ query()
   • Pergunta única, sem memória
   • Stateless (cada pergunta é isolada)
   • Mais simples de usar
   • Ideal para: tarefas pontuais

✅ ClaudeSDKClient
   • Conversa contínua com contexto
   • Stateful (mantém histórico)
   • Mais complexo
   • Ideal para: diálogos interativos
                """,
                "exemplo": """
# query() - Simples
async for msg in query("O que é Python?"):
    print(msg.result)

# Client - Com contexto
client = ClaudeSDKClient()
await client.send_message("Olá")
async for msg in client.receive_response():
    print(msg.result)
                """,
                "quiz": {
                    "pergunta": "Quando usar query() ao invés de Client?",
                    "resposta": "Para perguntas únicas sem necessidade de contexto"
                }
            },
            "autenticacao": {
                "titulo": "Autenticação Correta",
                "aprendido": """
✅ SEMPRE USE: claude login
❌ NUNCA USE: ANTHROPIC_API_KEY

Por quê?
• claude login = autenticação segura oficial
• API keys = método antigo, não recomendado
• Hooks bloqueiam uso de API keys automaticamente
                """,
                "exemplo": """
# Terminal
$ claude login

# No código - NUNCA faça isso:
# client = Anthropic(api_key="sk-...")  ❌

# Sempre faça isso:
from claude_code_sdk import query  ✅
                """,
                "quiz": {
                    "pergunta": "Como autenticar no Claude Code SDK?",
                    "resposta": "Usando 'claude login' no terminal"
                }
            },
            "claudecodeoptions": {
                "titulo": "ClaudeCodeOptions",
                "aprendido": """
Parâmetros principais:
• model: Modelo do Claude
• temperature: Criatividade (0.0-1.0)
• allowed_tools: Ferramentas permitidas
• system_prompt: Contexto do sistema
• max_tokens: Limite de tokens
                """,
                "exemplo": """
options = ClaudeCodeOptions(
    model="claude-3-5-sonnet-20241022",
    temperature=0.7,  # 0.1=consistente, 0.9=criativo
    allowed_tools=["File", "Search", "Bash"],
    system_prompt="Você é um expert em Python"
)
                """,
                "quiz": {
                    "pergunta": "O que controla a criatividade das respostas?",
                    "resposta": "O parâmetro temperature (0.0 a 1.0)"
                }
            }
        }

        for key, conceito in conceitos.items():
            print(f"\n{'─'*70}")
            print(f"📖 {conceito['titulo']}")
            print(conceito['aprendido'])

            if 'exemplo' in conceito:
                print("\n💡 Exemplo:")
                print(conceito['exemplo'])

            self.conceitos_revisados.append(key)

        return conceitos

    def revisar_ferramentas(self):
        """Revisa as ferramentas do SDK"""

        print("\n" + "="*70)
        print("🔧 REVISÃO: FERRAMENTAS DO SDK")
        print("="*70)

        ferramentas = {
            "file_tools": {
                "categoria": "📁 File Tools",
                "tools": [
                    ("Read", "Ler arquivos"),
                    ("Write", "Criar/sobrescrever arquivos"),
                    ("Edit", "Editar trechos específicos"),
                    ("MultiEdit", "Múltiplas edições")
                ]
            },
            "search_tools": {
                "categoria": "🔍 Search Tools",
                "tools": [
                    ("Grep", "Buscar padrões em arquivos"),
                    ("Glob", "Buscar arquivos por nome"),
                    ("WebSearch", "Buscar na web"),
                    ("WebFetch", "Buscar conteúdo de URL")
                ]
            },
            "system_tools": {
                "categoria": "⚙️ System Tools",
                "tools": [
                    ("Bash", "Executar comandos shell"),
                    ("Execute", "Executar código Python"),
                    ("TodoWrite", "Gerenciar tarefas"),
                    ("Task", "Delegar para sub-agentes")
                ]
            }
        }

        print("\nFerramentas disponíveis com allowed_tools:\n")

        for categoria, dados in ferramentas.items():
            print(f"\n{dados['categoria']}")
            for tool, desc in dados['tools']:
                print(f"  • {tool}: {desc}")

        print("\n💡 Como usar:")
        print("""
options = ClaudeCodeOptions(
    allowed_tools=["File", "Search", "Bash"]  # Permite estas ferramentas
)
        """)

        return ferramentas

    def identificar_gaps_criticos(self):
        """Identifica e explica os gaps críticos"""

        print("\n" + "="*70)
        print("🔴 GAPS CRÍTICOS - FOCO NECESSÁRIO")
        print("="*70)

        gaps = {
            "mcp_tools": {
                "titulo": "MCP Tools (Model Context Protocol)",
                "importancia": "CRÍTICO - Score +20 pontos",
                "explicacao": """
MCP Tools permitem criar ferramentas customizadas:

```python
from claude_code_sdk import tool

@tool(
    name="minha_ferramenta",
    description="Descrição da ferramenta",
    input_schema={...}
)
async def minha_ferramenta(args):
    # SEMPRE retorne {"content": [...]}
    return {
        "content": [{
            "type": "text",
            "text": "resultado"
        }]
    }
```

⚠️ REGRA DE OURO: Sempre retorne {"content": [...]}
                """,
                "exercicio": "gap_1_mcp_tools_tutorial.py"
            },
            "hooks_system": {
                "titulo": "Hooks System",
                "importancia": "CRÍTICO - Score +20 pontos",
                "explicacao": """
Hooks interceptam execução de ferramentas:

```python
from claude_code_sdk import HookMatcher

def validar(tool_name, args):
    if tool_name == "Write":
        # Bloquear
        return {"behavior": "deny"}
    # Permitir
    return None

hook = HookMatcher(
    matcher="PreToolUse",
    hooks=[validar]
)
```

⚠️ REGRA: None = permite, {"behavior": "deny"} = bloqueia
                """,
                "exercicio": "gap_2_hooks_tutorial.py"
            }
        }

        for gap_id, gap in gaps.items():
            print(f"\n{'─'*70}")
            print(f"🎯 {gap['titulo']}")
            print(f"   Importância: {gap['importancia']}")
            print(gap['explicacao'])
            print(f"\n   📝 Exercício: {gap['exercicio']}")

        return gaps

    def calcular_evolucao(self):
        """Calcula a evolução do aprendizado"""

        print("\n" + "="*70)
        print("📈 SUA EVOLUÇÃO")
        print("="*70)

        # Simular evolução baseada no que foi revisado
        pontos_ganhos = 0

        # Conceitos básicos revisados
        if "query_vs_client" in self.conceitos_revisados:
            pontos_ganhos += 5
            self.conceitos_dominados.append("Diferença query vs Client")

        if "autenticacao" in self.conceitos_revisados:
            pontos_ganhos += 5
            self.conceitos_dominados.append("Autenticação com claude login")

        if "claudecodeoptions" in self.conceitos_revisados:
            pontos_ganhos += 5
            self.conceitos_dominados.append("ClaudeCodeOptions")

        # Atualizar score
        novo_score = self.score_atual + pontos_ganhos

        print(f"""
Score Inicial: {self.score_atual}/100
Pontos Ganhos: +{pontos_ganhos}
Score Atual: {novo_score}/100

✅ Conceitos Dominados:""")
        for conceito in self.conceitos_dominados:
            print(f"   • {conceito}")

        print(f"""
🎯 Conceitos Pendentes (Gaps):
   • MCP Tools (CRÍTICO)
   • Hooks System (CRÍTICO)
   • ClaudeSDKClient avançado
   • Streaming responses

📊 Progresso no Bootcamp:
   Fase 1 (Fundamentos): 40% concluído
   Fase 2 (Ferramentas): 0% concluído
   Fase 3 (Gaps Críticos): 0% concluído
   Fase 4 (Expert): 0% concluído
        """)

        return novo_score

    def gerar_plano_proximos_passos(self, score):
        """Gera plano para próximos passos"""

        print("\n" + "="*70)
        print("🚀 PRÓXIMOS PASSOS")
        print("="*70)

        if score < 30:
            print("""
📌 FASE 1 - FUNDAMENTOS (Você está aqui!)
─────────────────────────────────────
1. Completar exercícios básicos:
   python3 exercicios_praticos_pt_br.py 1
   python3 exercicios_praticos_pt_br.py 2

2. Praticar query() com diferentes opções:
   • Variar temperature
   • Testar diferentes allowed_tools

3. Entender async/await profundamente
   • Todo código SDK é assíncrono!
            """)
        elif score < 60:
            print("""
📌 FASE 2 - FERRAMENTAS
─────────────────────────────────
1. Dominar File Tools:
   • Read, Write, Edit, MultiEdit

2. Dominar Search Tools:
   • Grep para buscar padrões
   • Glob para buscar arquivos

3. System Tools:
   • Bash para comandos
   • TodoWrite para organização
            """)
        else:
            print("""
📌 FASE 3 - GAPS CRÍTICOS
─────────────────────────────────
1. MCP Tools (URGENTE):
   python3 gap_1_mcp_tools_tutorial.py

2. Hooks System (URGENTE):
   python3 gap_2_hooks_tutorial.py

3. Multi-agent com Task
            """)

        print("""
💡 DICA DO DIA:
─────────────────────────────────
"O segredo para dominar o SDK é prática constante.
 Faça um exercício por dia, mesmo que pequeno!"

🎯 Meta da Semana:
   • Aumentar score em +15 pontos
   • Dominar pelo menos 1 gap crítico
   • Criar 1 projeto próprio com SDK
        """)

    def salvar_progresso(self, score):
        """Salva o progresso da revisão"""

        progresso = {
            "data_revisao": datetime.now().isoformat(),
            "score_inicial": self.score_atual,
            "score_final": score,
            "conceitos_dominados": self.conceitos_dominados,
            "conceitos_revisados": self.conceitos_revisados
        }

        # Salvar em arquivo
        log_dir = Path.home() / '.claude' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)

        arquivo = log_dir / 'revisao_sdk_progresso.json'

        # Carregar histórico existente
        if arquivo.exists():
            with open(arquivo, 'r') as f:
                historico = json.load(f)
        else:
            historico = []

        historico.append(progresso)

        with open(arquivo, 'w') as f:
            json.dump(historico, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Progresso salvo em: {arquivo}")

def main():
    """Executa a revisão interativa"""

    print("\n" + "="*70)
    print("🔄 REVISÃO INTERATIVA - CLAUDE CODE SDK")
    print("="*70)
    print("""
Vamos revisar tudo que você aprendeu até agora!
Esta revisão vai consolidar seu conhecimento.
    """)

    revisao = RevisaoSDK()

    # 1. Revisar conceitos fundamentais
    input("\n⏸️ Pressione ENTER para revisar CONCEITOS FUNDAMENTAIS...")
    revisao.revisar_conceitos_fundamentais()

    # 2. Revisar ferramentas
    input("\n⏸️ Pressione ENTER para revisar FERRAMENTAS...")
    revisao.revisar_ferramentas()

    # 3. Identificar gaps
    input("\n⏸️ Pressione ENTER para ver seus GAPS CRÍTICOS...")
    revisao.identificar_gaps_criticos()

    # 4. Calcular evolução
    input("\n⏸️ Pressione ENTER para ver sua EVOLUÇÃO...")
    novo_score = revisao.calcular_evolucao()

    # 5. Próximos passos
    input("\n⏸️ Pressione ENTER para ver PRÓXIMOS PASSOS...")
    revisao.gerar_plano_proximos_passos(novo_score)

    # 6. Salvar progresso
    revisao.salvar_progresso(novo_score)

    # Mensagem final
    print("\n" + "="*70)
    print("🎉 REVISÃO COMPLETA!")
    print("="*70)
    print(f"""
Parabéns por revisar seu conhecimento!

📊 Resumo:
   • Score evoluiu: {revisao.score_atual} → {novo_score}
   • Conceitos dominados: {len(revisao.conceitos_dominados)}
   • Gaps identificados: 2 críticos

🎯 Ação Imediata:
   1. Execute: python3 exercicios_praticos_pt_br.py 1
   2. Depois: python3 gap_1_mcp_tools_tutorial.py

Continue assim e você será EXPERT em 12 semanas! 🚀
    """)

if __name__ == "__main__":
    main()