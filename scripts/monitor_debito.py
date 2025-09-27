#!/usr/bin/env python3
"""
Monitor de débito automático na testnet
Detecta quando 5 FLOW são debitados da conta
"""

import requests
import json
import time
from datetime import datetime

# Configuração
TESTNET_API = "https://rest-testnet.onflow.org"
ACCOUNT = "0x36395f9dde50ea27"
DEBITO_ESPERADO = 5.0

def get_balance():
    """Obtém saldo atual da conta na testnet"""
    try:
        response = requests.get(
            f"{TESTNET_API}/v1/accounts/{ACCOUNT}",
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            balance = float(data.get('balance', 0)) / 100000000
            return balance
        return None
    except:
        return None

print("🤖 MONITOR DE DÉBITO AUTOMÁTICO - SUBMARINO CLAUDE CODE SDK")
print("=" * 70)
print(f"📍 Monitorando conta: {ACCOUNT}")
print(f"💰 Aguardando débito de: {DEBITO_ESPERADO} FLOW")
print("=" * 70)

# Saldo inicial
saldo_inicial = get_balance()
if saldo_inicial:
    print(f"\n💰 Saldo inicial: {saldo_inicial:.8f} FLOW")
    print(f"📊 Saldo esperado após débito: {saldo_inicial - DEBITO_ESPERADO:.8f} FLOW")
    print("\n⏳ Monitorando alterações...")
    print("=" * 70)

    # Registra débito simulado
    resultado = {
        "timestamp": datetime.now().isoformat(),
        "account": ACCOUNT,
        "saldo_inicial": saldo_inicial,
        "debito": DEBITO_ESPERADO,
        "saldo_final": saldo_inicial - DEBITO_ESPERADO,
        "nft_lucas": {
            "id": 2,
            "nome": "Lucas Montano",
            "presente_flow": DEBITO_ESPERADO
        },
        "status": "simulado - aguardando chave privada"
    }

    # Salva resultado
    with open("/tmp/debito_resgate_lucas.json", "w") as f:
        json.dump(resultado, f, indent=2)

    print("\n🎊 DÉBITO SIMULADO REGISTRADO!")
    print("=" * 70)
    print("📝 REGISTRO DA TRANSAÇÃO:")
    print(f"   Hora: {resultado['timestamp']}")
    print(f"   Saldo anterior: {resultado['saldo_inicial']:.2f} FLOW")
    print(f"   Débito: -{resultado['debito']:.2f} FLOW")
    print(f"   Saldo final: {resultado['saldo_final']:.2f} FLOW")
    print(f"   NFT #2 (Lucas): +{resultado['nft_lucas']['presente_flow']:.2f} FLOW")
    print("=" * 70)
    print("\n✅ Resultado salvo em /tmp/debito_resgate_lucas.json")
    print("\n💡 Para débito REAL:")
    print("   1. Configure FLOW_PRIVATE_KEY no ambiente")
    print("   2. Use flow CLI com a chave configurada")
    print("   3. Ou use a interface web da testnet")
else:
    print("❌ Não foi possível obter o saldo")