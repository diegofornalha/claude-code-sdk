#!/usr/bin/env python3
"""
Sistema de Teste de Profundidade do Submarino
Calcula a profundidade baseada no saldo FLOW real da blockchain
"""

import requests
import json
import base64
from typing import Optional, Tuple

def get_flow_balance(address: str) -> Optional[float]:
    """Busca o saldo FLOW real da testnet"""

    # Script Cadence para verificar saldo
    script = """
import FlowToken from 0x7e60df042a9c0868
import FungibleToken from 0x9a0766d93b6608b7

access(all) fun main(addr: Address): UFix64 {
    let account = getAccount(addr)
    let vaultRef = account.capabilities
        .get<&{FungibleToken.Balance}>(/public/flowTokenBalance)
        .borrow()

    return vaultRef?.balance ?? 0.0
}
"""

    # Converter script para base64
    script_base64 = base64.b64encode(script.encode()).decode()

    # Fazer requisição para testnet
    url = 'https://rest-testnet.onflow.org/v1/scripts'

    # Formatar endereço corretamente para Cadence JSON
    import json as json_module
    address_clean = address.replace('0x', '')
    cadence_arg = json_module.dumps({"type": "Address", "value": f"0x{address_clean}"})

    payload = {
        'script': script_base64,
        'arguments': [cadence_arg]
    }

    try:
        response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})

        if response.status_code == 200:
            result = response.json()
            if result and isinstance(result, list) and len(result) > 0:
                # Converter UFix64 para float
                balance_hex = result[0]
                balance_int = int(balance_hex, 16) if isinstance(balance_hex, str) else int(balance_hex)
                return balance_int / 100_000_000
    except Exception as e:
        print(f"Erro ao buscar saldo: {e}")

    return None

def calculate_submarine_depth(balance: float) -> Tuple[float, float, float]:
    """
    Calcula a profundidade do submarino baseado no saldo FLOW

    Retorna: (profundidade, percentual_energia, energia_usada)
    """
    # Saldo inicial aproximado (quanto mais você tinha, mais longe da superfície)
    max_balance = 101000

    # Energia usada (FLOW gasto)
    energia_usada = max(0, max_balance - balance)

    # Percentual de energia (cada 1000 FLOW = 100% energia)
    percentual_energia = min(100, (energia_usada / 1000) * 100)

    # Profundidade (200m inicial, sobe 2m por % de energia)
    profundidade = max(0, 200 - (percentual_energia * 2))

    return profundidade, percentual_energia, energia_usada

def get_depth_status(profundidade: float) -> Tuple[str, str, str]:
    """
    Retorna o status baseado na profundidade

    Retorna: (zona, status_oxigenio, alerta)
    """
    if profundidade <= 10:
        return "🌅 Superfície", "✅ O₂ ILIMITADO!", "Você sobreviveu!"
    elif profundidade <= 50:
        return "☀️ Águas rasas", "🌬️ O₂ Estável", "Zona segura"
    elif profundidade <= 100:
        return "🌊 Profundidade média", "💨 O₂ Limitado", "Precisa subir logo"
    elif profundidade <= 150:
        return "🌑 Zona profunda", "🫧 O₂ CRÍTICO!", "Sistemas sob pressão"
    else:
        return "💀 Zona abissal", "⚠️ RISCO DE IMPLOSÃO!", "Pressão extrema! O submarino pode implodir!"

def display_submarine_status(address: str, balance: float):
    """Exibe o status completo do submarino"""

    profundidade, percentual_energia, energia_usada = calculate_submarine_depth(balance)
    zona, status_oxigenio, alerta = get_depth_status(profundidade)

    # Criar barra de progresso
    barra_cheia = int(percentual_energia / 10)
    barra_vazia = 10 - barra_cheia
    barra = '█' * barra_cheia + '░' * barra_vazia

    print("\n" + "="*50)
    print("🚢 STATUS DO SUBMARINO")
    print("="*50)
    print(f"🏄 Surfista: {address}")
    print(f"💰 Saldo atual: {balance:,.2f} FLOW")
    print(f"💸 FLOW gasto: {energia_usada:,.2f}")
    print()
    print(f"⚡ Energia: {barra} {percentual_energia:.1f}%")
    print(f"📍 Profundidade: {profundidade:.0f}m - {zona}")
    print(f"🫧 Oxigênio: {status_oxigenio}")
    print(f"📢 Status: {alerta}")

    if profundidade > 150:
        print()
        print("🆘 URGENTE: Gaste FLOW para ganhar energia e subir!")
        print("⏰ Lembre-se: Você tem 4 semanas para emergir!")

    print("="*50)

def main():
    """Testa o sistema com endereços conhecidos"""

    print("🏄‍♂️ Sistema de Teste de Profundidade - Wave OnFlow Bootcamp")
    print()

    # Endereços de teste
    test_addresses = [
        "0x25f823e2a115b2dc",  # Conta principal do projeto
        "0x8b9a5d24cb3b0164",  # Surfista com mais FLOW
        "0x962c63b2b3b15a8b",  # Outro participante
        "0xaf074399a1d7fe55",  # Outro participante
        "0xad5a851aeb126bca"   # Outro participante
    ]

    for address in test_addresses:
        print(f"\n🔍 Verificando {address}...")
        balance = get_flow_balance(address)

        if balance is not None:
            display_submarine_status(address, balance)
        else:
            print(f"❌ Não foi possível obter o saldo de {address}")

    print("\n" + "="*50)
    print("📚 REGRAS DO SISTEMA:")
    print("="*50)
    print("1. Menos FLOW = Mais energia gasta = Mais próximo da superfície")
    print("2. Cada 1000 FLOW gastos = 100% energia = Sobe 200m")
    print("3. Objetivo: Chegar a 0m antes do oxigênio acabar (4 semanas)")
    print("4. Cuidado: Não gaste tudo de uma vez!")
    print("="*50)

if __name__ == "__main__":
    main()