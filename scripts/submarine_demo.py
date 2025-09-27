#!/usr/bin/env python3
"""
Demo do Sistema de Profundidade do Submarino
Usando valores conhecidos da testnet para demonstração
"""

def calculate_depth_status(balance):
    """Calcula profundidade e status baseado no saldo FLOW"""

    # Sistema de energia: menos FLOW = mais próximo da superfície
    max_balance = 101000  # Saldo inicial aproximado
    energia_usada = max(0, max_balance - balance)
    percentual_energia = min(100, (energia_usada / 1000) * 100)
    profundidade = max(0, 200 - (percentual_energia * 2))

    return profundidade, percentual_energia, energia_usada

def display_submarine(address, nome, balance):
    """Exibe o status do submarino de forma visual"""

    profundidade, percentual_energia, energia_usada = calculate_depth_status(balance)

    # Barra de progresso
    barra_cheia = int(percentual_energia / 10)
    barra_vazia = 10 - barra_cheia
    barra = '█' * barra_cheia + '░' * barra_vazia

    print(f"\n{'='*60}")
    print(f"🏄 {nome}")
    print(f"📍 Endereço: {address}")
    print(f"💰 Saldo atual: {balance:,.2f} FLOW")
    print(f"💸 FLOW gasto: {energia_usada:,.2f}")
    print()
    print(f"⚡ Energia: {barra} {percentual_energia:.1f}%")
    print(f"📍 Profundidade: {profundidade:.0f}m")

    # Status de oxigênio e risco
    if profundidade <= 10:
        print("🌅 SUPERFÍCIE!")
        print("✅ O₂ ILIMITADO - Você sobreviveu!")
        print("🎊 Parabéns! Missão completa!")
    elif profundidade <= 50:
        print("☀️ Águas rasas")
        print("🌬️ O₂ Estável - Zona segura")
        print("💚 Continue assim!")
    elif profundidade <= 100:
        print("🌊 Profundidade média")
        print("💨 O₂ Limitado - Precisa subir logo")
        print("⚠️ Atenção: Gaste mais FLOW para subir!")
    elif profundidade <= 150:
        print("🌑 Zona profunda")
        print("🫧 O₂ CRÍTICO - Sistemas sob pressão!")
        print("⚠️ PERIGO: Risco de falha nos sistemas!")
    else:
        print("💀 ZONA ABISSAL")
        print("⚠️ RISCO DE IMPLOSÃO - Pressão extrema!")
        print("🆘 URGENTE: Gaste FLOW IMEDIATAMENTE!")
        print("💥 O submarino pode implodir a qualquer momento!")

    print(f"{'='*60}")

def main():
    """Demonstração do sistema com valores conhecidos"""

    print("\n" + "="*60)
    print("🚢 SISTEMA DE PROFUNDIDADE - WAVE ONFLOW BOOTCAMP")
    print("="*60)
    print("\n📚 Como funciona:")
    print("• Menos FLOW = Mais energia gasta = Mais próximo da superfície")
    print("• Cada 1000 FLOW gastos = 100% energia = Sobe 200m")
    print("• Objetivo: Chegar a 0m antes do oxigênio acabar (4 semanas)")
    print("• ⚠️ CUIDADO: Não gaste tudo de uma vez!")

    # Surfistas conhecidos com saldos da testnet
    surfistas = [
        ("0x25f823e2a115b2dc", "Conta Principal do Projeto", 2000.001),
        ("0x8b9a5d24cb3b0164", "Surfista Campeão", 99953.90),
        ("0x962c63b2b3b15a8b", "Surfista Aventureiro", 50000.00),  # Exemplo
        ("0xaf074399a1d7fe55", "Surfista Explorador", 25000.00),   # Exemplo
        ("0xad5a851aeb126bca", "Surfista Corajoso", 1000.00),      # Exemplo
    ]

    print("\n🏄‍♂️ STATUS DOS SURFISTAS:")

    for address, nome, balance in surfistas:
        display_submarine(address, nome, balance)

    # Simulação de progressão
    print("\n" + "="*60)
    print("🎮 SIMULAÇÃO DE PROGRESSÃO")
    print("="*60)

    print("\n📊 Exemplo: Surfista gastando FLOW ao longo do tempo:")

    simulacao_saldos = [
        (100000, "Início da jornada"),
        (95000, "Após 1 semana"),
        (85000, "Após 2 semanas"),
        (60000, "Após 3 semanas"),
        (20000, "Última semana - Quase lá!"),
        (5000, "Últimos dias"),
        (100, "EMERGÊNCIA - Chegou na superfície!")
    ]

    for saldo, descricao in simulacao_saldos:
        profundidade, percentual, gasto = calculate_depth_status(saldo)
        print(f"\n💰 {saldo:,} FLOW - {descricao}")
        print(f"   📍 Profundidade: {profundidade:.0f}m | ⚡ Energia: {percentual:.1f}%")

    print("\n" + "="*60)
    print("🏆 CONQUISTAS POSSÍVEIS:")
    print("="*60)
    print("🏄 Wave Rider - Complete o tutorial")
    print("🤿 Deep Diver - Explore 5 pastas")
    print("🏝️ Island Hopper - Use 10 comandos diferentes")
    print("🌊 Flow Master - Crie seu NFT de Surfista")
    print("🏆 Treasure Hunter - Encontre todos os tesouros")
    print("🚁 Rescue Complete - Chegue à superfície!")

    print("\n" + "="*60)
    print("⏰ LEMBRE-SE: Você tem 4 SEMANAS para emergir!")
    print("💡 Gaste FLOW com sabedoria durante todo o período!")
    print("🎯 Meta: Chegar a 0m de profundidade antes do tempo acabar!")
    print("="*60)

if __name__ == "__main__":
    main()