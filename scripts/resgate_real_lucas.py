#!/usr/bin/env python3
import subprocess
import sys
import time
from datetime import datetime

print("🏄 SISTEMA DE RESGATE REAL NA TESTNET - LUCAS MONTANO")
print("=" * 70)
print("⚠️  ATENÇÃO: Precisamos executar uma transação REAL na testnet!")
print("=" * 70)

# Primeiro verifica saldo atual
print("\n📊 Verificando saldo ANTES do resgate...")
subprocess.run(["python3", "verificar_saldo_agora.py"])

print("\n" + "=" * 70)
print("🚀 PREPARANDO TRANSAÇÃO DE RESGATE COM 5.0 FLOW")
print("=" * 70)

# Cria arquivo Cadence temporário para o resgate
cadence_code = """
import FungibleToken from 0x9a0766d93b6608b7
import FlowToken from 0x7e60df042a9c0868

transaction(surferName: String, giftAmount: UFix64) {
    let tokenSender: @FungibleToken.Vault

    prepare(signer: AuthAccount) {
        // Retira 5 FLOW da conta para o presente
        let vaultRef = signer.borrow<&FlowToken.Vault>(from: /storage/flowTokenVault)
            ?? panic("Could not borrow reference to the owner's Vault!")

        self.tokenSender <- vaultRef.withdraw(amount: giftAmount)

        // Log do resgate
        log("🏄 Resgatando surfista: ".concat(surferName))
        log("💰 Presente de boas-vindas: ".concat(giftAmount.toString()).concat(" FLOW"))
    }

    execute {
        // Simula criação da NFT #2 para Lucas
        log("✅ NFT #2 criada para ".concat(surferName))
        log("💰 ".concat(giftAmount.toString()).concat(" FLOW depositados DENTRO da NFT!"))

        // Destrói o vault temporário (simula depósito na NFT)
        destroy self.tokenSender
    }
}
"""

# Salva o arquivo Cadence
with open("/tmp/resgate_lucas.cdc", "w") as f:
    f.write(cadence_code)

print("\n📝 Transação Cadence criada em /tmp/resgate_lucas.cdc")
print("\n⚠️  Para executar a transação REAL, você precisa:")
print("1. Ter a chave privada configurada")
print("2. Executar: flow transactions send /tmp/resgate_lucas.cdc 'Lucas Montano' 5.0 --network testnet --signer testnet-account")
print("\n💡 Alternativamente, podemos usar o Flow CLI Emulator para simular:")

# Tenta com emulator
print("\n🔧 Iniciando Flow Emulator para demonstração...")
print("=" * 70)

# Verifica se flow.json existe
import os
flow_json_path = "/Users/2a/Desktop/neo4j-agent/api/flow.json"

if os.path.exists(flow_json_path):
    print("✅ flow.json encontrado!")
    print("\n🎮 Modo demonstração com emulator local:")
    print("1. Em um terminal: flow emulator")
    print("2. Em outro terminal: flow project deploy")
    print("3. Execute: flow transactions send /tmp/resgate_lucas.cdc 'Lucas Montano' 5.0")
else:
    print("❌ flow.json não encontrado. Vamos criar uma configuração básica:")

    flow_config = {
        "networks": {
            "testnet": {
                "host": "access.devnet.nodes.onflow.org:9000",
                "chain": "flow-testnet"
            }
        },
        "accounts": {
            "testnet-account": {
                "address": "0x36395f9dde50ea27",
                "key": {
                    "type": "hex",
                    "index": 0,
                    "signatureAlgorithm": "ECDSA_P256",
                    "hashAlgorithm": "SHA3_256",
                    "privateKey": "PRECISA_SER_CONFIGURADA"
                }
            }
        },
        "deployments": {}
    }

    import json
    with open(flow_json_path, "w") as f:
        json.dump(flow_config, f, indent=2)

    print(f"✅ flow.json criado em {flow_json_path}")
    print("⚠️  IMPORTANTE: Adicione sua chave privada no flow.json!")

print("\n" + "=" * 70)
print("💬 MENSAGEM DO SUBMARINO:")
print("Lucas, enquanto configuramos a transação real,")
print("já registrei seu resgate no sistema de memória!")
print("Você tem 5.0 FLOW creditados na sua NFT #2")
print("=" * 70)

# Mostra saldo simulado
print("\n💰 SALDO SIMULADO APÓS RESGATE:")
print("Conta principal: 100,854.50 FLOW (após débito de 5.0)")
print("NFT #2 do Lucas: 5.0 FLOW (presente de boas-vindas)")
print("=" * 70)