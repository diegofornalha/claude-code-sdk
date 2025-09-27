#!/bin/bash
# Configuração do Hook de Organização de Arquivos

echo "🔧 Configurando Hook de Organização de Arquivos..."

# Cria arquivo de configuração do hook
cat > ~/.claude/hooks/file-organizer.json << 'EOF'
{
  "name": "file-organizer",
  "description": "Previne criação de arquivos na raiz do projeto",
  "triggers": ["Write", "MultiEdit", "bash"],
  "script": "python3 /Users/2a/Desktop/neo4j-agent/api/scripts/file_organizer_agent.py",
  "enabled": true
}
EOF

echo "✅ Hook configurado!"
echo ""
echo "📋 Regras implementadas:"
echo "  ❌ Bloqueia criação na raiz do projeto"
echo "  ✅ Força uso de pastas apropriadas:"
echo "     - api/ → Scripts Python e configurações"
echo "     - api/scripts/ → Scripts auxiliares"
echo "     - api/contracts/ → Contratos Cadence"
echo "     - chat/ → Interface HTML/JS/CSS"
echo "     - docs/ → Documentação"
echo "     - tests/ → Testes"
echo ""
echo "🎯 Hook ativo para todos os comandos do Claude!"