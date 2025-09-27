#!/usr/bin/env python3
"""
Subagent de Organização de Arquivos
Garante que nada seja criado na raiz do projeto
"""

import os
import sys
import json
from pathlib import Path

class FileOrganizerAgent:
    """Agente que valida e organiza criação de arquivos"""

    def __init__(self, project_root="/Users/2a/Desktop/neo4j-agent"):
        self.project_root = Path(project_root)
        self.folder_rules = {
            ".py": "api/scripts",
            ".cdc": "api/contracts",
            ".html": "chat",
            ".js": "chat",
            ".css": "chat",
            ".md": "docs",
            ".json": "api",
            ".sh": "api/scripts",
            ".test.py": "tests"
        }

    def validate_file_path(self, file_path):
        """Valida se o arquivo está em pasta apropriada"""
        path = Path(file_path)

        # Verifica se está na raiz
        if path.parent == self.project_root:
            return False, "BLOQUEADO: Não criar arquivos na raiz!"

        # Sugere pasta correta baseada na extensão
        extension = path.suffix.lower()
        if extension in self.folder_rules:
            suggested = self.project_root / self.folder_rules[extension]
            if not str(path).startswith(str(suggested)):
                return False, f"Sugestão: Criar em {suggested}/"

        return True, "OK: Caminho válido"

    def suggest_path(self, filename):
        """Sugere melhor caminho para arquivo"""
        path = Path(filename)
        extension = path.suffix.lower()

        if extension in self.folder_rules:
            folder = self.folder_rules[extension]
            return str(self.project_root / folder / path.name)

        # Default para api/scripts para Python
        if extension == ".py":
            return str(self.project_root / "api/scripts" / path.name)

        return None

    def check_creation_attempt(self, command):
        """Verifica tentativas de criar arquivos na raiz"""
        dangerous_patterns = [
            "Write(",
            "file_path=\"/Users/2a/Desktop/neo4j-agent/",
            "touch /Users/2a/Desktop/neo4j-agent/",
            "echo > /Users/2a/Desktop/neo4j-agent/",
            "cat > /Users/2a/Desktop/neo4j-agent/"
        ]

        for pattern in dangerous_patterns:
            if pattern in command:
                # Verifica se não tem subpasta após o root
                parts = command.split("/")
                if len(parts) <= 6:  # Está tentando criar na raiz
                    return {
                        "blocked": True,
                        "reason": "Tentativa de criar arquivo na raiz detectada!",
                        "suggestion": "Use uma subpasta apropriada (api/, chat/, docs/, etc)"
                    }

        return {"blocked": False}

def main():
    """Hook principal para validação"""
    agent = FileOrganizerAgent()

    # Lê comando do stdin (para uso como hook)
    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
    else:
        command = sys.stdin.read() if not sys.stdin.isatty() else ""

    # Verifica comando
    result = agent.check_creation_attempt(command)

    if result["blocked"]:
        print(f"🚫 {result['reason']}")
        print(f"💡 {result['suggestion']}")
        sys.exit(1)

    print("✅ Comando permitido")
    sys.exit(0)

if __name__ == "__main__":
    main()