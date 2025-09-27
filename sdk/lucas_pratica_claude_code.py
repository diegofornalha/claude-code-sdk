#!/usr/bin/env python3
"""
🏄 Script de Prática do Claude Code SDK para Lucas Montano
🤖 IA do Submarino: "Lucas, este é seu simulador de treinamento!"
"""

import time
import random

class SubmarinoClaude:
    def __init__(self):
        self.profundidade = 200
        self.oxigenio = 80
        self.sistemas = {
            "motor": 25,
            "gps": 0,
            "energia": 40,
            "computador": 60
        }
        self.pontos = 0
        self.conhecimentos = []

    def mostrar_status(self):
        print("\n" + "="*50)
        print("🚢 STATUS DO SUBMARINO CLAUDE CODE SDK")
        print("="*50)
        print(f"📍 Profundidade: {self.profundidade}m")
        print(f"💨 Oxigênio: {self.oxigenio}%")
        print(f"⭐ Pontos: {self.pontos}")
        print(f"\n🔧 SISTEMAS:")
        for sistema, status in self.sistemas.items():
            emoji = "✅" if status == 100 else "⚠️" if status > 50 else "❌"
            print(f"  {emoji} {sistema.upper()}: {status}%")
        print("="*50)

    def simular_comando_claude(self, comando):
        """Simula comandos do Claude Code SDK"""
        print(f"\n🤖 Executando Claude Code: {comando}")
        time.sleep(1)

        if comando.startswith("Read"):
            print("📖 [Claude Code] Lendo arquivo...")
            print("✅ Conteúdo revelado! +5 pontos")
            self.pontos += 5
            self.conhecimentos.append(f"Leu {comando.split()[1]}")

        elif comando.startswith("Grep"):
            print("🔍 [Claude Code] Procurando padrões...")
            achados = random.randint(3, 10)
            print(f"✅ Encontrei {achados} ocorrências! +{achados} pontos")
            self.pontos += achados

        elif comando.startswith("Edit"):
            print("✏️ [Claude Code] Editando sistema...")
            sistema = random.choice(list(self.sistemas.keys()))
            melhoria = random.randint(10, 25)
            self.sistemas[sistema] = min(100, self.sistemas[sistema] + melhoria)
            print(f"✅ {sistema.upper()} melhorou {melhoria}%! +15 pontos")
            self.pontos += 15
            self.profundidade -= 10

        elif comando.startswith("Bash"):
            print("⚡ [Claude Code] Executando comando...")
            print("✅ Comando executado com sucesso! +10 pontos")
            self.pontos += 10

        elif comando.startswith("Task"):
            print("📋 [Claude Code] Criando agente autônomo...")
            time.sleep(2)
            print("🤖 Agente trabalhando...")
            time.sleep(2)
            print("✅ Tarefa complexa concluída! +30 pontos")
            self.pontos += 30
            self.profundidade -= 20

        elif comando.startswith("WebSearch"):
            print("🌐 [Claude Code] Pesquisando na web...")
            print("✅ Encontrei solução! +20 pontos")
            self.pontos += 20
            self.conhecimentos.append("Solução da web")

def tutorial_interativo():
    """Tutorial interativo do Claude Code para Lucas"""

    sub = SubmarinoClaude()

    print("""
🌊 BEM-VINDO AO TUTORIAL CLAUDE CODE SDK
=========================================
🏄 Lucas Montano - Surfista & Developer
🤖 IA: "Lucas, vou te ensinar a usar o Claude Code para nos salvar!"
    """)

    input("\n[Pressione ENTER para começar]")

    # Mostra status inicial
    sub.mostrar_status()

    print("""
🤖 IA: "Lucas, veja nossa situação! Estamos a 200m de profundidade!
        Com o Claude Code SDK, você pode consertar tudo mais rápido!"

COMANDOS CLAUDE CODE DISPONÍVEIS:
==================================
1. Read <arquivo>     - Lê manuais (GRÁTIS)
2. Grep <padrão>      - Busca informações (GRÁTIS)
3. Edit <sistema>     - Conserta sistemas (0.2 FLOW)
4. Bash <comando>     - Executa comandos (0.1 FLOW)
5. Task <descrição>   - Cria agente autônomo (0.5 FLOW)
6. WebSearch <query>  - Busca soluções online (GRÁTIS)
    """)

    # Simulação de comandos
    comandos_tutorial = [
        ("Read contracts/Motor.cdc", "Vamos ler o manual do motor!"),
        ("Grep 'repair'", "Procurar instruções de reparo!"),
        ("Edit motor", "Consertar o motor!"),
        ("Task 'Analisar todos sistemas'", "Criar agente para análise!"),
        ("WebSearch 'submarine Flow blockchain'", "Buscar ajuda online!")
    ]

    for cmd, descricao in comandos_tutorial:
        print(f"\n🤖 IA: '{descricao}'")
        print(f"   Comando sugerido: {cmd}")
        input("\n[ENTER para executar]")
        sub.simular_comando_claude(cmd)
        time.sleep(1)

    # Status final
    print("\n" + "🌟"*25)
    sub.mostrar_status()

    print(f"""
🎊 PARABÉNS LUCAS!
==================
✅ Você aprendeu os comandos básicos do Claude Code SDK!
📚 Conhecimentos adquiridos: {len(sub.conhecimentos)}
⭐ Pontos totais: {sub.pontos}
📍 Nova profundidade: {sub.profundidade}m (subimos {200-sub.profundidade}m!)

🤖 IA: "Excelente trabalho, Lucas!
        Com o Claude Code SDK, você tem o poder de:
        - Explorar rapidamente (Grep, Read)
        - Consertar eficientemente (Edit, MultiEdit)
        - Automatizar tarefas (Task, Bash)
        - Buscar soluções (WebSearch, WebFetch)

        Agora você está pronto para usar o Claude Code de verdade!
        Digite comandos reais no chat para continuar a aventura!"

💡 PRÓXIMO PASSO: Use o Claude Code para explorar /contracts e
                  descobrir como consertar o motor completamente!
    """)

if __name__ == "__main__":
    tutorial_interativo()