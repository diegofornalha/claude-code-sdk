#!/usr/bin/env python3
"""
✅ TESTE FINAL COM SEQUENCE NUMBER CORRETO
"""

import subprocess
import json
import os

# Credenciais COMPLETAS confirmadas
ACCOUNT = "0x36395f9dde50ea27"
PRIVATE_KEY = "7c5a857c81fe09a3a21be38e57212a29d1f2a51cae314ae47c5ef62e8afcaec3"
PUBLIC_KEY = "5a4579fec91240793b986203fa25cfbbfd71be1cc54c73ae20e4fdde6f07061a1b2162f7df4acaca118c6b152ca718fc2cbf304ef8625bc6c24143d63c5933d7"
SEQUENCE_NUMBER = 15  # IMPORTANTE!

print("✅ TESTE FINAL COM TODAS AS INFORMAÇÕES")
print("=" * 60)
print(f"💰 Conta: {ACCOUNT}")
print(f"🔑 Chave Privada: {PRIVATE_KEY[:10]}...{PRIVATE_KEY[-6:]}")
print(f"🔓 Chave Pública: {PUBLIC_KEY[:32]}...")
print(f"📊 Algoritmo: ECDSA_secp256k1")
print(f"🔢 Sequence Number: {SEQUENCE_NUMBER}")

# 1. Verificar saldo
print("\n1️⃣ VERIFICANDO CONTA:")
cmd = f"flow accounts get {ACCOUNT} --network testnet -o json 2>/dev/null"
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

if result.returncode == 0:
    data = json.loads(result.stdout)
    balance = data.get('balance', '0')
    print(f"   ✅ Saldo: {balance} FLOW")

    # Pegar o sequence number atual
    keys = data.get('keys', [])
    if keys:
        current_seq = keys[0].get('sequenceNumber', 0)
        print(f"   📝 Sequence Number atual: {current_seq}")

# 2. Criar flow.json com configuração completa
print("\n2️⃣ CONFIGURANDO FLOW.JSON:")

flow_config = {
    "networks": {
        "testnet": "access.devnet.nodes.onflow.org:9000"
    },
    "accounts": {
        "testnet-account": {
            "address": ACCOUNT.replace("0x", ""),
            "key": {
                "type": "hex",
                "index": 0,
                "signatureAlgorithm": "ECDSA_secp256k1",  # Importante!
                "hashAlgorithm": "SHA2_256",
                "privateKey": PRIVATE_KEY
            }
        }
    }
}

config_file = "flow.json"
with open(config_file, "w") as f:
    json.dump(flow_config, f, indent=2)

print(f"   ✅ Configuração criada com ECDSA_secp256k1")

# 3. Testar transação simples
print("\n3️⃣ TESTANDO TRANSAÇÃO:")

test_tx = """
transaction {
    prepare(signer: auth(Storage) &Account) {
        log("✅ FUNCIONOU! Transação assinada com sucesso!")
        log(signer.address.toString())
    }
}
"""

tx_file = "test_transaction.cdc"
with open(tx_file, "w") as f:
    f.write(test_tx)

# Enviar transação
cmd = [
    "flow", "transactions", "send",
    tx_file,
    "--network", "testnet",
    "--signer", "testnet-account",
    "-y"
]

print("   Enviando transação...")
result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

success = False
if "SEALED" in result.stdout:
    if "signature is not valid" not in result.stdout and "Error" not in result.stdout:
        print("   🎉 SUCESSO! TRANSAÇÃO FUNCIONOU!")
        success = True

        # Extrair TX ID
        import re
        tx_match = re.search(r'ID\s+([a-f0-9]{64})', result.stdout)
        if tx_match:
            tx_id = tx_match.group(1)
            print(f"\n   📝 Transaction ID: {tx_id}")
            print(f"   🔗 Ver: https://testnet.flowscan.io/tx/{tx_id}")
    else:
        print("   ❌ Erro de assinatura ainda...")
        print(f"   Output: {result.stdout[:500]}")
else:
    print("   ❌ Transação não foi selada")
    if result.stderr:
        print(f"   Erro: {result.stderr[:500]}")

# 4. Se funcionou, testar registro .find
if success:
    print("\n4️⃣ TESTANDO REGISTRO .FIND:")

    from datetime import datetime
    timestamp = datetime.now().strftime("%H%M%S")
    test_name = f"test{timestamp}"

    find_tx = f"""
    import FIND from 0x35717efbbce11c74
    import FungibleToken from 0x9a0766d93b6608b7
    import FlowToken from 0x7e60df042a9c0868

    transaction(name: String, amount: UFix64) {{
        let vault: @FungibleToken.Vault

        prepare(account: auth(Storage) &Account) {{
            let vaultRef = account.storage.borrow<&FlowToken.Vault>(
                from: /storage/flowTokenVault
            ) ?? panic("Could not borrow Flow token vault")

            self.vault <- vaultRef.withdraw(amount: amount)
        }}

        execute {{
            FIND.bid(name: name, vault: <- self.vault)
            log("Nome registrado: ".concat(name))
        }}
    }}
    """

    find_file = "register_find.cdc"
    with open(find_file, "w") as f:
        f.write(find_tx)

    print(f"   Tentando registrar: {test_name}.find")

    cmd = [
        "flow", "transactions", "send",
        find_file,
        test_name,
        "5.0",
        "--network", "testnet",
        "--signer", "testnet-account",
        "-y"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if "SEALED" in result.stdout and "Error" not in result.stdout:
        print(f"   🎉 NOME .FIND REGISTRADO COM SUCESSO!")
        print(f"   Nome: {test_name}.find")
    else:
        print(f"   ⚠️ Registro .find pode ter falhado")

# Limpar arquivos
for f in [config_file, tx_file, "register_find.cdc"]:
    if os.path.exists(f):
        os.remove(f)

print("\n" + "=" * 60)
if success:
    print("🎊 CONTA 100% FUNCIONAL!")
    print("Com 101,000 FLOW, estamos prontos para tudo!")
else:
    print("⚠️ Ainda há problemas com a assinatura")
    print("Pode ser necessário usar a Flow Wallet para transações")
print("=" * 60)