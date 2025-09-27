#!/usr/bin/env python3
"""
💻 EXERCÍCIO PRÁTICO - SISTEMA COMPLETO DE HOOKS
Implementando um sistema de segurança com Hooks
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json
import os

print("\n" + "="*70)
print("🔒 SISTEMA DE SEGURANÇA COM HOOKS")
print("="*70)
print("Vamos criar um sistema completo de hooks para proteção!\n")

# ═══════════════════════════════════════════════════════════════
# HOOK #1: PROTEÇÃO DE ARQUIVOS SENSÍVEIS
# ═══════════════════════════════════════════════════════════════

class SecurityHooks:
    """Sistema completo de hooks de segurança"""

    def __init__(self):
        # Contadores para rate limiting
        self.tool_calls = {}
        # Logs de auditoria
        self.audit_log = []
        # Arquivos/pastas protegidos
        self.protected_paths = [
            ".env", ".git", "node_modules",
            "credentials", "secrets", "private",
            ".ssh", ".aws", ".config"
        ]
        # Comandos bloqueados
        self.blocked_commands = [
            "rm -rf", "sudo", "chmod 777",
            "format", "> /dev/null"
        ]

    def hook_protecao_arquivos(self, tool_name: str, args: Dict[str, Any]) -> Optional[Dict]:
        """
        Hook que protege arquivos e diretórios sensíveis
        """
        print(f"🔍 Verificando: {tool_name}")

        # Verificar ferramentas de escrita/edição
        if tool_name in ["Write", "Edit", "MultiEdit"]:
            file_path = args.get("file_path", "").lower()

            # Verificar cada path protegido
            for protected in self.protected_paths:
                if protected in file_path:
                    mensagem = f"""
🔒 ACESSO NEGADO
─────────────────────────────────
Arquivo: {file_path}
Motivo: Path protegido ({protected})
Ação: Bloqueado por segurança
─────────────────────────────────
"""
                    print(mensagem)
                    return {
                        "behavior": "deny",
                        "message": f"Arquivo protegido: {protected}"
                    }

            # Verificar conteúdo sensível
            if tool_name == "Write":
                content = args.get("content", "")
                if self._contem_segredos(content):
                    print("🔑 Possível API key ou senha detectada!")
                    return {
                        "behavior": "deny",
                        "message": "Conteúdo sensível detectado (API keys/senhas)"
                    }

        print(f"✅ {tool_name} permitido")
        return None  # Permitir

    def _contem_segredos(self, content: str) -> bool:
        """Detecta possíveis segredos no conteúdo"""
        patterns = [
            "sk-",  # OpenAI/Anthropic keys
            "ANTHROPIC_API_KEY",
            "API_KEY",
            "SECRET_KEY",
            "password=",
            "passwd=",
            "token="
        ]
        content_lower = content.lower()
        return any(pattern.lower() in content_lower for pattern in patterns)

# ═══════════════════════════════════════════════════════════════
# HOOK #2: RATE LIMITING
# ═══════════════════════════════════════════════════════════════

    def hook_rate_limit(self, tool_name: str, args: Dict[str, Any]) -> Optional[Dict]:
        """
        Hook que limita número de execuções por minuto
        """
        agora = datetime.now()

        # Inicializar contador se não existe
        if tool_name not in self.tool_calls:
            self.tool_calls[tool_name] = []

        # Limpar chamadas antigas (> 1 minuto)
        self.tool_calls[tool_name] = [
            timestamp for timestamp in self.tool_calls[tool_name]
            if (agora - timestamp).seconds < 60
        ]

        # Definir limites por ferramenta
        limites = {
            "Write": 5,
            "Bash": 10,
            "Edit": 7,
            "WebFetch": 3,
            "Execute": 5
        }

        limite = limites.get(tool_name, 15)  # Limite padrão: 15

        # Verificar se excedeu limite
        if len(self.tool_calls[tool_name]) >= limite:
            tempo_espera = 60 - (agora - self.tool_calls[tool_name][0]).seconds
            print(f"""
⏱️ RATE LIMIT ATINGIDO
─────────────────────────────────
Ferramenta: {tool_name}
Limite: {limite} chamadas/minuto
Chamadas: {len(self.tool_calls[tool_name])}
Espere: {tempo_espera} segundos
─────────────────────────────────
""")
            return {
                "behavior": "deny",
                "message": f"Rate limit: máx {limite}/min. Espere {tempo_espera}s"
            }

        # Adicionar chamada atual
        self.tool_calls[tool_name].append(agora)
        print(f"📊 {tool_name}: {len(self.tool_calls[tool_name])}/{limite} chamadas")
        return None

# ═══════════════════════════════════════════════════════════════
# HOOK #3: VALIDAÇÃO DE COMANDOS
# ═══════════════════════════════════════════════════════════════

    def hook_validacao_comandos(self, tool_name: str, args: Dict[str, Any]) -> Optional[Dict]:
        """
        Hook que valida e bloqueia comandos perigosos
        """
        if tool_name == "Bash":
            comando = args.get("command", "").lower()

            # Verificar comandos bloqueados
            for blocked in self.blocked_commands:
                if blocked in comando:
                    print(f"""
⚠️ COMANDO BLOQUEADO
─────────────────────────────────
Comando: {args.get('command')}
Padrão perigoso: {blocked}
Ação: Bloqueado por segurança
─────────────────────────────────
""")
                    return {
                        "behavior": "deny",
                        "message": f"Comando perigoso: {blocked}"
                    }

            # Verificar comandos suspeitos
            suspeitos = ["curl", "wget", "nc", "telnet"]
            for suspeito in suspeitos:
                if suspeito in comando:
                    print(f"⚠️ Comando suspeito detectado: {suspeito}")
                    # Permitir mas com aviso (não bloqueia)

        return None

# ═══════════════════════════════════════════════════════════════
# HOOK #4: AUDITORIA E LOGGING
# ═══════════════════════════════════════════════════════════════

    def hook_auditoria(self, tool_name: str, args: Dict[str, Any]) -> Optional[Dict]:
        """
        Hook que registra todas as operações para auditoria
        """
        # Criar entrada de log
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "args_summary": self._resumir_args(args),
            "user": os.getenv("USER", "unknown"),
            "pid": os.getpid()
        }

        # Adicionar ao log
        self.audit_log.append(log_entry)

        # Ferramentas críticas para log detalhado
        criticas = ["Write", "Edit", "Bash", "Execute"]
        if tool_name in criticas:
            print(f"📝 AUDIT LOG: {tool_name} às {log_entry['timestamp'][:19]}")

        # Salvar logs periodicamente
        if len(self.audit_log) >= 10:
            self._salvar_logs()

        return None  # Sempre permitir (só loga)

    def _resumir_args(self, args: Dict) -> Dict:
        """Resume argumentos para o log"""
        resumo = {}
        for key, value in args.items():
            if isinstance(value, str) and len(value) > 100:
                resumo[key] = value[:100] + "..."
            else:
                resumo[key] = value
        return resumo

    def _salvar_logs(self):
        """Salva logs em arquivo"""
        try:
            with open("security_audit.json", "a") as f:
                for entry in self.audit_log:
                    json.dump(entry, f)
                    f.write("\n")
            print(f"💾 {len(self.audit_log)} logs salvos em security_audit.json")
            self.audit_log = []  # Limpar buffer
        except Exception as e:
            print(f"❌ Erro salvando logs: {e}")

# ═══════════════════════════════════════════════════════════════
# HOOK COMBINADO - SISTEMA COMPLETO
# ═══════════════════════════════════════════════════════════════

    def hook_sistema_completo(self, tool_name: str, args: Dict[str, Any]) -> Optional[Dict]:
        """
        Hook master que combina todas as verificações
        """
        print("\n" + "-"*50)
        print(f"🛡️ SISTEMA DE SEGURANÇA - {tool_name}")
        print("-"*50)

        # 1. Verificar rate limit
        resultado = self.hook_rate_limit(tool_name, args)
        if resultado:
            return resultado

        # 2. Verificar proteção de arquivos
        resultado = self.hook_protecao_arquivos(tool_name, args)
        if resultado:
            return resultado

        # 3. Validar comandos
        resultado = self.hook_validacao_comandos(tool_name, args)
        if resultado:
            return resultado

        # 4. Registrar auditoria (sempre executa)
        self.hook_auditoria(tool_name, args)

        print(f"✅ {tool_name} aprovado por todas verificações")
        return None  # Tudo OK

# ═══════════════════════════════════════════════════════════════
# DEMONSTRAÇÃO DO SISTEMA
# ═══════════════════════════════════════════════════════════════

def demonstrar_sistema():
    """Demonstra o sistema de hooks em ação"""

    print("\n" + "="*70)
    print("🧪 TESTANDO SISTEMA DE HOOKS")
    print("="*70)

    # Criar instância do sistema
    security = SecurityHooks()

    # Casos de teste
    casos_teste = [
        # Caso 1: Tentar escrever .env (DEVE BLOQUEAR)
        {
            "tool": "Write",
            "args": {"file_path": "/app/.env", "content": "SECRET=123"},
            "esperado": "BLOQUEAR"
        },
        # Caso 2: Escrever arquivo normal (DEVE PERMITIR)
        {
            "tool": "Write",
            "args": {"file_path": "/tmp/test.txt", "content": "Hello"},
            "esperado": "PERMITIR"
        },
        # Caso 3: Comando perigoso (DEVE BLOQUEAR)
        {
            "tool": "Bash",
            "args": {"command": "sudo rm -rf /"},
            "esperado": "BLOQUEAR"
        },
        # Caso 4: Comando normal (DEVE PERMITIR)
        {
            "tool": "Bash",
            "args": {"command": "ls -la"},
            "esperado": "PERMITIR"
        },
        # Caso 5: Conteúdo com API key (DEVE BLOQUEAR)
        {
            "tool": "Write",
            "args": {"file_path": "/tmp/config.txt", "content": "API_KEY=sk-1234567890"},
            "esperado": "BLOQUEAR"
        }
    ]

    # Executar testes
    for i, caso in enumerate(casos_teste, 1):
        print(f"\n{'='*50}")
        print(f"TESTE #{i}: {caso['esperado']}")
        print('='*50)

        resultado = security.hook_sistema_completo(
            caso["tool"],
            caso["args"]
        )

        if resultado and caso["esperado"] == "BLOQUEAR":
            print(f"✅ CORRETO: Bloqueado como esperado")
        elif not resultado and caso["esperado"] == "PERMITIR":
            print(f"✅ CORRETO: Permitido como esperado")
        else:
            print(f"❌ ERRO: Resultado inesperado!")

    # Mostrar estatísticas
    print("\n" + "="*70)
    print("📊 ESTATÍSTICAS DO SISTEMA")
    print("="*70)

    print(f"""
Chamadas por ferramenta:
""")
    for tool, calls in security.tool_calls.items():
        print(f"  • {tool}: {len(calls)} chamadas")

    print(f"""
Logs de auditoria: {len(security.audit_log)} entradas
Rate limits aplicados: SIM
Proteção de arquivos: ATIVA
Validação de comandos: ATIVA
""")

# ═══════════════════════════════════════════════════════════════
# EXECUTAR DEMONSTRAÇÃO
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    demonstrar_sistema()

    print("\n" + "="*70)
    print("🎉 PARABÉNS! VOCÊ DOMINA HOOKS!")
    print("="*70)
    print("""
Você implementou:
✅ Hook de proteção de arquivos
✅ Hook de rate limiting
✅ Hook de validação de comandos
✅ Hook de auditoria/logging
✅ Sistema combinado completo

CONCEITOS DOMINADOS:
• PreToolUse para bloquear execuções
• None = permite, dict = bloqueia
• Validação com args.get()
• Sistema de segurança completo

📈 Score: +20 pontos pelo gap Hooks!
📊 Score Total: 90/120 (75%)
🎯 NÍVEL: AVANÇADO!

Próximo passo: Criar um projeto completo!
""")