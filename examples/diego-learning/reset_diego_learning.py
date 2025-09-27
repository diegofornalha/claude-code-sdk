#!/usr/bin/env python3
"""
🔄 RESET DO APRENDIZADO DO DIEGO
Script para zerar o progresso e começar do zero
"""

import json
import os
from datetime import datetime

def reset_diego_progress():
    """
    Reseta todo o progresso do Diego para começar do zero
    """

    # Estado inicial do Diego
    initial_state = {
        "user": "diego-fornalha",
        "start_date": datetime.now().isoformat(),
        "current_week": 0,
        "total_weeks": 12,
        "score": {
            "current": 0,
            "target": 100,
            "history": []
        },
        "completed_modules": [],
        "skills": {
            "flow_basics": False,
            "eliza_framework": False,
            "agentkit": False,
            "mcp_tools": False,
            "defi_tools": False,
            "plugin_development": False,
            "ai_integration": False
        },
        "achievements": [],
        "notes": "Starting fresh - Hackathon Flow Blockchain 2024"
    }

    # Salvar estado inicial
    with open("diego_progress.json", "w") as f:
        json.dump(initial_state, f, indent=2)

    print("✅ Progresso do Diego resetado com sucesso!")
    print(f"📊 Score: {initial_state['score']['current']}/{initial_state['score']['target']}")
    print(f"📅 Semana: {initial_state['current_week']}/{initial_state['total_weeks']}")
    print("🎯 Pronto para começar do zero!")

    return initial_state

def create_learning_checkpoints():
    """
    Cria checkpoints de aprendizado para acompanhar progresso
    """

    checkpoints = {
        "week_1": {
            "title": "Fundamentos do Flow MCP",
            "topics": [
                "Instalar e configurar Flow MCP no Cursor",
                "Executar primeira consulta de saldo",
                "Buscar informação de conta",
                "Recuperar código de contrato",
                "Entender estrutura de contas Flow"
            ],
            "points": 10,
            "status": "pending"
        },
        "week_2": {
            "title": "Flow DeFi MCP Tools",
            "topics": [
                "Consultar preços de tokens",
                "Analisar pools de liquidez",
                "Executar swap simulado",
                "Monitorar histórico de preços",
                "Gerenciar tokens ERC20"
            ],
            "points": 15,
            "status": "pending"
        },
        "week_3": {
            "title": "Eliza Framework",
            "topics": [
                "Configurar ambiente Eliza",
                "Criar primeiro agente",
                "Personalizar character",
                "Integrar com Claude/GPT",
                "Deploy de agente básico"
            ],
            "points": 20,
            "status": "pending"
        },
        "week_4": {
            "title": "Plugin Development",
            "topics": [
                "Estrutura de plugin",
                "Criar ações customizadas",
                "Implementar serviços",
                "Testar plugin localmente",
                "Publicar no registry"
            ],
            "points": 15,
            "status": "pending"
        },
        "week_5": {
            "title": "AgentKit Integration",
            "topics": [
                "Setup AgentKit com Flow",
                "Configurar LLM (Claude/GPT)",
                "Implementar wallet Viem",
                "Criar agente autônomo",
                "Executar transações"
            ],
            "points": 20,
            "status": "pending"
        },
        "week_6": {
            "title": "Projeto Final",
            "topics": [
                "Combinar todas as ferramentas",
                "Criar DeFi Dashboard",
                "Implementar chat interface",
                "Adicionar automação",
                "Deploy em produção"
            ],
            "points": 20,
            "status": "pending"
        }
    }

    # Salvar checkpoints
    with open("diego_checkpoints.json", "w") as f:
        json.dump(checkpoints, f, indent=2)

    print("\n📋 Checkpoints de aprendizado criados:")
    for week, data in checkpoints.items():
        print(f"  {week}: {data['title']} (+{data['points']} pontos)")

    return checkpoints

def create_daily_tracker():
    """
    Cria um tracker diário para acompanhar atividades
    """

    daily_log = {
        "format": "Use este formato para cada dia de estudo",
        "template": {
            "date": "YYYY-MM-DD",
            "hours_studied": 0,
            "topics_covered": [],
            "code_written": {
                "files_created": 0,
                "lines_written": 0
            },
            "challenges_faced": [],
            "solutions_found": [],
            "tomorrow_goals": [],
            "confidence_level": "1-10",
            "notes": ""
        },
        "logs": []
    }

    # Salvar template de log diário
    with open("diego_daily_log.json", "w") as f:
        json.dump(daily_log, f, indent=2)

    print("\n📝 Tracker diário criado!")
    print("   Use diego_daily_log.json para registrar progresso diário")

    return daily_log

if __name__ == "__main__":
    print("=" * 60)
    print("🔄 RESETANDO APRENDIZADO DO DIEGO")
    print("=" * 60)

    # 1. Reset do progresso
    state = reset_diego_progress()

    # 2. Criar checkpoints
    checkpoints = create_learning_checkpoints()

    # 3. Criar tracker diário
    daily = create_daily_tracker()

    print("\n" + "=" * 60)
    print("🚀 SISTEMA RESETADO - PRONTO PARA COMEÇAR!")
    print("=" * 60)
    print("\n📚 Próximos passos:")
    print("1. Abra diego_progress.json para ver seu estado atual")
    print("2. Consulte diego_checkpoints.json para ver o plano de estudo")
    print("3. Use diego_daily_log.json para registrar progresso diário")
    print("4. Execute test_step_by_step.py para começar os testes")
    print("\n💡 Dica: Comece pela Semana 1 - Fundamentos do Flow MCP")