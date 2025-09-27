#!/usr/bin/env python3
"""
Script para mintar NFT de Surfista com débito real de FLOW
O FLOW será debitado da conta e depositado no vault da NFT
"""

import subprocess
import sys
import json
import datetime

def mint_nft_com_pagamento(nome_surfista: str, valor_flow: float):
    """
    Minta uma NFT debitando FLOW real da conta

    Args:
        nome_surfista: Nome do surfista para a NFT
        valor_flow: Quantidade de FLOW a debitar e depositar na NFT
    """

    print(f"\n🌊 MINT DE NFT COM DÉBITO REAL DE FLOW")
    print(f"{'='*50}")
    print(f"👤 Surfista: {nome_surfista}")
    print(f"💰 Valor a debitar: {valor_flow} FLOW")
    print(f"⚠️  ATENÇÃO: Isso debitará FLOW real da sua conta!")
    print(f"{'='*50}\n")

    # Confirmar com o usuário
    resposta = input("➡️  Deseja continuar? (s/n): ")
    if resposta.lower() != 's':
        print("❌ Operação cancelada!")
        return

    # Comando Flow para executar a transação
    cmd = [
        "flow", "transactions", "send",
        "./scripts/mint_nft_with_payment.cdc",
        nome_surfista,
        str(valor_flow),
        "--network", "testnet",
        "--signer", "testnet-account"
    ]

    print(f"\n🚀 Executando transação na testnet...")
    print(f"📝 Comando: {' '.join(cmd)}\n")

    try:
        # Executar comando
        resultado = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        print("✅ TRANSAÇÃO EXECUTADA COM SUCESSO!")
        print(resultado.stdout)

        # Verificar saldo após a transação
        print("\n📊 Verificando saldo após a transação...")
        check_cmd = ["python3", "scripts/check_flow_balance.py"]
        subprocess.run(check_cmd)

        # Salvar registro da NFT
        nft_data = {
            "surfista": nome_surfista,
            "flow_depositado": valor_flow,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "success",
            "network": "testnet"
        }

        filename = f"nft_{nome_surfista.lower().replace(' ', '_')}.json"
        with open(filename, 'w') as f:
            json.dump(nft_data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Registro salvo em: {filename}")
        print(f"\n🎊 NFT CRIADA COM SUCESSO!")
        print(f"   • Surfista: {nome_surfista}")
        print(f"   • FLOW debitado: {valor_flow}")
        print(f"   • O FLOW está agora DENTRO da NFT!")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ ERRO ao executar transação!")
        print(f"Erro: {e.stderr}")
        print(f"Saída: {e.stdout}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)

def main():
    """Função principal com exemplos"""

    print("\n🏄 MINT DE NFT SURFISTA COM PAGAMENTO REAL")
    print("="*50)
    print("Este script vai:")
    print("1. Debitar FLOW real da sua conta")
    print("2. Criar uma NFT de Surfista")
    print("3. Depositar o FLOW dentro da NFT")
    print("="*50)

    # Pedir informações ao usuário
    print("\n📝 Digite as informações da NFT:")
    nome = input("Nome do Surfista: ").strip()

    if not nome:
        print("❌ Nome não pode ser vazio!")
        sys.exit(1)

    try:
        valor = float(input("Quantidade de FLOW (ex: 5.0): "))
        if valor <= 0:
            print("❌ Valor deve ser maior que zero!")
            sys.exit(1)
        if valor > 100:
            print("⚠️  Valor muito alto! Máximo permitido: 100 FLOW")
            sys.exit(1)
    except ValueError:
        print("❌ Valor inválido!")
        sys.exit(1)

    # Executar mint
    mint_nft_com_pagamento(nome, valor)

if __name__ == "__main__":
    main()