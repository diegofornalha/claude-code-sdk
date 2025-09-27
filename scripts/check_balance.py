#!/usr/bin/env python3
"""
Script para verificar saldo de conta Flow
"""
import requests
import json

def check_flow_balance(address):
    """Verifica o saldo de uma conta Flow"""

    # Flow Testnet Access Node
    testnet_url = "https://rest-testnet.onflow.org"

    # Endpoint para obter informações da conta
    endpoint = f"{testnet_url}/v1/accounts/{address}"

    try:
        response = requests.get(endpoint)

        if response.status_code == 200:
            data = response.json()

            # Extrair saldo
            balance = data.get('balance', '0')

            # Converter de microFLOW para FLOW (dividir por 10^8)
            balance_flow = int(balance) / 100_000_000

            print(f"\n💰 Informações da Conta Flow")
            print(f"{'='*50}")
            print(f"📍 Endereço: {address}")
            print(f"💎 Saldo: {balance_flow:.8f} FLOW")
            print(f"🔢 Saldo (microFLOW): {balance}")

            # Mostrar contratos deployados se houver
            contracts = data.get('contracts', {})
            if contracts:
                print(f"\n📜 Contratos Deployados:")
                for name in contracts.keys():
                    print(f"   • {name}")

            # Mostrar chaves da conta
            keys = data.get('keys', [])
            if keys:
                print(f"\n🔑 Chaves da Conta: {len(keys)} chave(s)")

            return balance_flow

        else:
            print(f"❌ Erro ao consultar conta: Status {response.status_code}")
            print(f"Resposta: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Erro na requisição: {str(e)}")
        return None

if __name__ == "__main__":
    # Endereço fornecido
    address = "0x25f823e2a115b2dc"

    print(f"🔍 Consultando saldo da conta Flow: {address}")
    balance = check_flow_balance(address)

    if balance is not None:
        print(f"\n✅ Consulta realizada com sucesso!")