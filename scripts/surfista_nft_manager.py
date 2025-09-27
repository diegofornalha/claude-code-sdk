#!/usr/bin/env python3
"""
Sistema de Gerenciamento de NFT do Surfista
Permite criar NFTs e adicionar conhecimento à bag
"""

import json
import time
from typing import Dict, Any, Optional

class SurfistaNFTManager:
    def __init__(self):
        self.contract_address = "0x25f823e2a115b2dc"
        self.surfistas_registrados = {}  # Cache local dos surfistas
        self.nome_registry = {}  # Registro de nomes para evitar duplicatas

    def resgatar_surfista(self, nome: str, wallet_address: str) -> Dict[str, Any]:
        """
        Resgata um surfista criando sua NFT única
        Se o nome já existir, adiciona #2, #3, etc.

        Args:
            nome: Nome do surfista (ex: "Diego")
            wallet_address: Endereço da carteira do surfista

        Returns:
            Informações da transação e ID da NFT
        """

        # Verificar se o nome já existe e criar nome único
        nome_base = nome
        nome_final = nome

        if nome_base in self.nome_registry:
            # Nome já existe, adicionar número
            self.nome_registry[nome_base] += 1
            nome_final = f"{nome_base}#{self.nome_registry[nome_base]}"
        else:
            # Primeiro surfista com esse nome
            self.nome_registry[nome_base] = 1

        # Simular criação da NFT (em produção seria uma transação real)
        nft_id = len(self.surfistas_registrados)
        timestamp = time.time()

        surfista_data = {
            "id": nft_id,
            "nome": nome_final,
            "nome_base": nome_base,
            "wallet": wallet_address,
            "data_resgate": timestamp,
            "profundidade_atual": 200,  # Começa no fundo
            "energia_gasta": 0.0,
            "pontos_total": 100,  # Bonus inicial por ser resgatado
            "bag_de_conhecimento": [
                {
                    "tipo": "conquista",
                    "descricao": "🏄 Resgatado pelo submarino!",
                    "pontos": 100,
                    "timestamp": timestamp
                }
            ],
            "conquistas": {
                "Flow Master": True  # NFT criada
            }
        }

        self.surfistas_registrados[wallet_address] = surfista_data

        # Retornar resposta formatada
        return {
            "sucesso": True,
            "transacao": f"0x{''.join(['a1b2c3d4'] * 8)}",  # Hash simulado
            "nft_id": nft_id,
            "mensagem": f"""
🎊 SURFISTA RESGATADO COM SUCESSO!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏄 Nome: {nome_final}
🆔 NFT ID: #{nft_id}
📍 Carteira: {wallet_address}

🎁 BÔNUS DE RESGATE:
• 100 pontos iniciais
• Badge: 🏄 Flow Master
• NFT única registrada na blockchain

📊 STATUS INICIAL:
• Profundidade: 200m (Zona Abissal)
• Energia: 0%
• Objetivo: Gastar FLOW para subir!

💡 DICA: Cada comando e exploração adiciona conhecimento à sua bag!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """
        }

    def adicionar_conhecimento(
        self,
        wallet_address: str,
        tipo: str,
        descricao: str,
        pontos: int
    ) -> bool:
        """
        Adiciona conhecimento à bag do surfista

        Args:
            wallet_address: Endereço da carteira
            tipo: Tipo do conhecimento (comando, arquivo, funcionalidade, tesouro)
            descricao: Descrição do conhecimento adquirido
            pontos: Pontos ganhos
        """

        if wallet_address not in self.surfistas_registrados:
            return False

        surfista = self.surfistas_registrados[wallet_address]

        conhecimento = {
            "tipo": tipo,
            "descricao": descricao,
            "pontos": pontos,
            "timestamp": time.time()
        }

        surfista["bag_de_conhecimento"].append(conhecimento)
        surfista["pontos_total"] += pontos

        # Verificar conquistas
        self._verificar_conquistas(surfista)

        return True

    def atualizar_profundidade(self, wallet_address: str, flow_balance: float) -> Dict[str, Any]:
        """
        Atualiza a profundidade do submarino baseado no saldo FLOW
        LÓGICA: Menos FLOW = Mais energia gasta = Mais próximo da superfície
        """

        if wallet_address not in self.surfistas_registrados:
            return {"erro": "Surfista não registrado"}

        surfista = self.surfistas_registrados[wallet_address]

        # Calcular energia e profundidade - SISTEMA CORRETO
        max_balance = 101000  # Saldo inicial aproximado
        energia_gasta = max(0, max_balance - flow_balance)  # FLOW gasto desde o início
        percentual_energia_gasta = min(100, (energia_gasta / 1000) * 100)  # % de energia GASTA
        profundidade = max(0, 200 - (percentual_energia_gasta * 2))  # Sobe 2m por % de energia gasta

        surfista["energia_gasta"] = energia_gasta
        surfista["profundidade_atual"] = int(profundidade)

        # Verificar conquista de superfície
        if profundidade <= 10:
            surfista["conquistas"]["Rescue Complete"] = True

        return {
            "profundidade": int(profundidade),
            "energia_gasta": energia_gasta,
            "percentual_energia_gasta": percentual_energia_gasta  # Retorna % de energia GASTA
        }

    def ver_status(self, wallet_address: str) -> Optional[Dict[str, Any]]:
        """
        Retorna o status completo do surfista
        """

        if wallet_address not in self.surfistas_registrados:
            return None

        surfista = self.surfistas_registrados[wallet_address]
        profundidade = surfista["profundidade_atual"]

        # Determinar zona e status
        if profundidade <= 10:
            zona = "🌅 Superfície"
            oxigenio = "✅ O₂ ILIMITADO"
        elif profundidade <= 50:
            zona = "☀️ Águas rasas"
            oxigenio = "🌬️ O₂ Estável"
        elif profundidade <= 100:
            zona = "🌊 Profundidade média"
            oxigenio = "💨 O₂ Limitado"
        elif profundidade <= 150:
            zona = "🌑 Zona profunda"
            oxigenio = "🫧 O₂ CRÍTICO"
        else:
            zona = "💀 Zona abissal"
            oxigenio = "⚠️ RISCO DE IMPLOSÃO"

        return {
            "id": surfista["id"],
            "nome": surfista["nome"],
            "profundidade": profundidade,
            "zona": zona,
            "oxigenio": oxigenio,
            "energia_gasta": surfista["energia_gasta"],
            "pontos": surfista["pontos_total"],
            "conquistas": surfista["conquistas"],
            "bag_conhecimento": surfista["bag_de_conhecimento"],
            "total_conhecimentos": len(surfista["bag_de_conhecimento"])
        }

    def _verificar_conquistas(self, surfista: Dict[str, Any]):
        """
        Verifica e atualiza conquistas do surfista
        """

        bag = surfista["bag_de_conhecimento"]

        # Wave Rider - Completou o tutorial
        if len(bag) >= 5:
            surfista["conquistas"]["Wave Rider"] = True

        # Deep Diver - Explorou 5 pastas
        arquivos = [c for c in bag if c["tipo"] == "arquivo"]
        if len(arquivos) >= 5:
            surfista["conquistas"]["Deep Diver"] = True

        # Island Hopper - 10 comandos diferentes
        comandos = [c for c in bag if c["tipo"] == "comando"]
        if len(comandos) >= 10:
            surfista["conquistas"]["Island Hopper"] = True

        # Treasure Hunter - 100 pontos
        if surfista["pontos_total"] >= 100:
            surfista["conquistas"]["Treasure Hunter"] = True


def demonstrar_sistema():
    """
    Demonstração do sistema de NFT do Surfista
    """

    print("\n" + "="*60)
    print("🏄 SISTEMA DE NFT DO SURFISTA - DEMONSTRAÇÃO")
    print("="*60)

    # Criar manager
    manager = SurfistaNFTManager()

    # Demonstrar sistema de numeração de nomes
    print("\n1️⃣ DEMONSTRANDO SISTEMA DE NUMERAÇÃO...")
    print("-" * 40)
    print("Vários surfistas com o mesmo nome base:")

    # Resgatar múltiplos surfistas com mesmo nome
    nomes_teste = [
        ("Diego", "0x25f823e2a115b2dc"),
        ("Diego", "0x8b9a5d24cb3b0164"),
        ("Diego", "0x962c63b2b3b15a8b"),
        ("Maria", "0xaf074399a1d7fe55"),
        ("Diego", "0xad5a851aeb126bca"),
        ("Maria", "0xe712bbfbeeef1cfa"),
    ]

    for nome, wallet in nomes_teste:
        resultado = manager.resgatar_surfista(nome, wallet)
        nome_final = manager.surfistas_registrados[wallet]["nome"]
        print(f"✅ {nome} → {nome_final} (NFT #{manager.surfistas_registrados[wallet]['id']})")

    # Usar o primeiro Diego para o resto da demonstração
    print("\n2️⃣ DETALHES DO PRIMEIRO DIEGO...")
    print("-" * 40)

    resultado = manager.resgatar_surfista(
        nome="João",
        wallet_address="0x123456789"
    )

    print(resultado["mensagem"])

    # Adicionar conhecimentos à bag do primeiro Diego
    print("\n3️⃣ ADICIONANDO CONHECIMENTOS À BAG...")
    print("-" * 40)

    conhecimentos = [
        ("comando", "Executou 'ls' para explorar", 5),
        ("arquivo", "Explorou /api/contracts", 10),
        ("funcionalidade", "Descobriu sistema de NFTs", 15),
        ("tesouro", "Encontrou tesouro escondido", 25),
        ("comando", "Executou 'flow scripts'", 5),
    ]

    for tipo, desc, pontos in conhecimentos:
        manager.adicionar_conhecimento(
            wallet_address="0x25f823e2a115b2dc",  # Primeiro Diego
            tipo=tipo,
            descricao=desc,
            pontos=pontos
        )
        print(f"✅ {desc} (+{pontos} pontos)")

    # Simular gasto de FLOW e atualização de profundidade
    print("\n4️⃣ SIMULANDO GASTO DE FLOW...")
    print("-" * 40)

    saldos_simulados = [100000, 95000, 85000, 50000, 10000]

    for saldo in saldos_simulados:
        status = manager.atualizar_profundidade("0x25f823e2a115b2dc", saldo)
        print(f"💰 Saldo: {saldo:,} FLOW → 📍 Profundidade: {status['profundidade']}m")

    # Ver status final do primeiro Diego
    print("\n5️⃣ STATUS FINAL DOS SURFISTAS...")
    print("-" * 40)

    status_final = manager.ver_status("0x25f823e2a115b2dc")

    if status_final:
        print(f"""
🏄 {status_final['nome']} (NFT #{status_final['id']})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 STATUS:
• Profundidade: {status_final['profundidade']}m
• Zona: {status_final['zona']}
• Oxigênio: {status_final['oxigenio']}
• Pontos: {status_final['pontos']}
• Conhecimentos: {status_final['total_conhecimentos']}

🏆 CONQUISTAS:
""")
        for conquista, desbloqueada in status_final['conquistas'].items():
            if desbloqueada:
                print(f"  ✅ {conquista}")

        print("\n📚 BAG DE CONHECIMENTO:")
        for i, conhecimento in enumerate(status_final['bag_conhecimento'][-5:], 1):
            print(f"  {i}. [{conhecimento['tipo']}] {conhecimento['descricao']} (+{conhecimento['pontos']})")

    print("\n" + "="*60)
    print("🎯 NFT do Surfista salva todo o progresso na blockchain!")
    print("💡 Continue explorando para adicionar mais conhecimento!")
    print("="*60)


if __name__ == "__main__":
    demonstrar_sistema()