#!/usr/bin/env python3
"""
Script demonstrativo para criar a NFT de bag de conhecimento do Lucas Montano
Simula a criação da NFT e mostra todas as funcionalidades
"""

import json
import datetime
import random

class LucasMontanoNFT:
    def __init__(self):
        self.id = 0  # Primeira NFT da coleção
        self.nome = "Lucas Montano"
        self.data_resgate = datetime.datetime.now().isoformat()
        self.profundidade_atual = 200
        self.energia_gasta = 0.0
        self.pontos_total = 150  # 100 pelo resgate + 50 pelo presente
        self.flow_no_vault = 5.0
        self.bag_de_conhecimento = []
        self.conquistas = {}
        self.mensagens = []

        # Adicionar conhecimento inicial
        self._adicionar_conhecimento_inicial()

    def _adicionar_conhecimento_inicial(self):
        """Adiciona conhecimentos iniciais do resgate"""
        self.bag_de_conhecimento = [
            {
                "tipo": "conquista",
                "descricao": "Resgatado pelo submarino XR-7000!",
                "pontos": 100,
                "timestamp": self.data_resgate
            },
            {
                "tipo": "tesouro",
                "descricao": "Presente de boas-vindas: 5.0 FLOW",
                "pontos": 50,
                "timestamp": self.data_resgate
            }
        ]

        # Conquista inicial
        self.conquistas["Flow Master"] = True

    def adicionar_conhecimento(self, tipo, descricao, pontos):
        """Adiciona novo conhecimento à bag"""
        conhecimento = {
            "tipo": tipo,
            "descricao": descricao,
            "pontos": pontos,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.bag_de_conhecimento.append(conhecimento)
        self.pontos_total += pontos

        # Verificar novas conquistas
        self._verificar_conquistas()

        return conhecimento

    def _verificar_conquistas(self):
        """Verifica e atualiza conquistas"""
        if self.pontos_total >= 100:
            self.conquistas["Treasure Hunter"] = True

        if len(self.bag_de_conhecimento) >= 5:
            self.conquistas["Deep Diver"] = True

        if self.profundidade_atual <= 10:
            self.conquistas["Rescue Complete"] = True

    def atualizar_profundidade(self, energia_adicional):
        """Atualiza profundidade baseada na energia gasta"""
        self.energia_gasta += energia_adicional
        # Cada 1000 FLOW = sobe 200m
        percentual = (self.energia_gasta / 1000.0) * 100.0
        profundidade = 200.0 - (percentual * 2.0)
        self.profundidade_atual = max(0, int(profundidade))
        return self.profundidade_atual

    def status(self):
        """Mostra status completo da NFT"""
        return {
            "id": self.id,
            "nome": self.nome,
            "profundidade": f"{self.profundidade_atual}m",
            "energia_gasta": f"{self.energia_gasta:.2f} FLOW",
            "pontos": self.pontos_total,
            "flow_no_vault": f"{self.flow_no_vault} FLOW",
            "conhecimentos": len(self.bag_de_conhecimento),
            "conquistas": list(self.conquistas.keys())
        }

def criar_nft_lucas():
    """Cria e demonstra a NFT do Lucas Montano"""

    print("🌊" * 30)
    print("🏄‍♂️ CRIANDO NFT DE BAG DE CONHECIMENTO PARA LUCAS MONTANO!")
    print("🌊" * 30)
    print()

    # Criar NFT
    nft = LucasMontanoNFT()

    print("✨ NFT CRIADA COM SUCESSO!")
    print("=" * 60)
    print()

    # Mostrar detalhes
    print("📊 DETALHES DA SUA NFT:")
    print("-" * 60)
    print(f"🆔 NFT ID: #{nft.id}")
    print(f"🏄‍♂️ Nome: {nft.nome}")
    print(f"📅 Data do resgate: {nft.data_resgate}")
    print(f"📍 Profundidade atual: {nft.profundidade_atual}m (Zona Abissal)")
    print(f"⚡ Energia gasta: {nft.energia_gasta} FLOW")
    print(f"💰 FLOW no vault da NFT: {nft.flow_no_vault} FLOW")
    print(f"🏆 Pontos totais: {nft.pontos_total}")
    print()

    print("📚 BAG DE CONHECIMENTO:")
    print("-" * 60)
    for i, conhecimento in enumerate(nft.bag_de_conhecimento, 1):
        print(f"{i}. [{conhecimento['tipo']}] {conhecimento['descricao']} (+{conhecimento['pontos']} pontos)")
    print()

    print("🏆 CONQUISTAS DESBLOQUEADAS:")
    print("-" * 60)
    for conquista in nft.conquistas.keys():
        print(f"✅ {conquista}")
    print()

    print("🎮 SISTEMA DE JOGO:")
    print("-" * 60)
    print("Cada ação adiciona conhecimento à sua bag:")
    print("• Comandos executados: +5 pontos")
    print("• Arquivos explorados: +10 pontos")
    print("• Funcionalidades descobertas: +15 pontos")
    print("• Tesouros encontrados: +25 pontos")
    print("• Desafios completados: +50 pontos")
    print()

    print("⚡ SISTEMA DE ENERGIA:")
    print("-" * 60)
    print("• Gastar FLOW = Ganhar energia = Subir")
    print("• Cada 1000 FLOW gastos = Sobe 200m")
    print("• Objetivo: Chegar na superfície (0m)")
    print()

    print("🎯 PRÓXIMOS PASSOS:")
    print("-" * 60)
    print("1. Explorar os compartimentos do submarino (digite 'ls')")
    print("2. Ler arquivos para ganhar conhecimento")
    print("3. Consertar sistemas danificados")
    print("4. Cooperar com Diego Fornalha")
    print("5. Usar FLOW para subir à superfície")
    print()

    print("🌊" * 30)
    print("🎊 LUCAS, SUA NFT ESTÁ PRONTA!")
    print("🎮 BOA SORTE NA AVENTURA SUBMARINA!")
    print("🌊" * 30)

    # Salvar NFT em JSON
    nft_data = {
        "nft": nft.status(),
        "bag_completa": nft.bag_de_conhecimento,
        "metadata": {
            "criado_em": nft.data_resgate,
            "blockchain": "Flow Testnet",
            "contrato": "SurfistaNFT",
            "address": "0x25f823e2a115b2dc"
        }
    }

    with open("lucas_montano_nft.json", "w") as f:
        json.dump(nft_data, f, indent=2)

    print("\n💾 NFT salva em: lucas_montano_nft.json")

    return nft

if __name__ == "__main__":
    criar_nft_lucas()