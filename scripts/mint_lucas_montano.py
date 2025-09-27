#!/usr/bin/env python3
"""
Script para criar a NFT de bag de conhecimento do Lucas Montano
"""

import subprocess
import json
import os
from pathlib import Path

def mint_lucas_montano_nft():
    """Cria a NFT do Lucas Montano com presente inicial de 5 FLOW"""

    print("🌊 INICIANDO RESGATE DO LUCAS MONTANO...")
    print("=" * 60)

    # Configurações
    presente_inicial = "5.0"  # 5 FLOW de presente de boas-vindas

    # Comando Flow para executar a transação
    cmd = [
        "flow", "transactions", "send",
        "./scripts/resgatar_lucas_montano.cdc",
        presente_inicial,  # Presente em FLOW
        "--network", "testnet",
        "--signer", "testnet-account"
    ]

    print(f"🏄‍♂️ Resgatando Lucas Montano...")
    print(f"💰 Presente inicial: {presente_inicial} FLOW")
    print(f"📚 Criando bag de conhecimento...")
    print("")

    try:
        # Executar comando
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd="/Users/2a/Desktop/neo4j-agent/api"
        )

        if result.returncode == 0:
            print("✅ SUCESSO! NFT do Lucas Montano criada!")
            print("")
            print("📊 DETALHES DA NFT:")
            print("=" * 60)
            print("🆔 NFT ID: #0 (primeira NFT da coleção)")
            print("🏄‍♂️ Nome: Lucas Montano")
            print("💰 FLOW no vault: 5.0 FLOW")
            print("📚 Bag de conhecimento: Ativada")
            print("🏆 Pontos iniciais: 150")
            print("📍 Profundidade: 200m (Zona Abissal)")
            print("=" * 60)
            print("")
            print("🎮 LUCAS MONTANO ESTÁ PRONTO PARA JOGAR!")
            print("")

            # Mostrar output da transação
            if result.stdout:
                print("📝 Detalhes da transação:")
                print(result.stdout)

        else:
            print("❌ Erro ao criar NFT!")
            print(f"Erro: {result.stderr}")

            # Se for erro de configuração, dar dicas
            if "account not found" in result.stderr.lower():
                print("\n💡 Dica: Verifique se o flow.json está configurado corretamente")
                print("Execute: flow accounts create para configurar uma conta")

    except FileNotFoundError:
        print("❌ Flow CLI não encontrado!")
        print("💡 Instale com: brew install flow-cli")

    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    # Verificar se estamos no diretório correto
    if not os.path.exists("flow.json"):
        print("⚠️ Arquivo flow.json não encontrado!")
        print("📁 Mudando para o diretório do projeto...")
        os.chdir("/Users/2a/Desktop/neo4j-agent/api")

    mint_lucas_montano_nft()