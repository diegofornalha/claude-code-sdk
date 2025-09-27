#!/usr/bin/env python3
"""
🔴 GAP CRÍTICO #2: HOOKS SYSTEM
Tutorial completo para dominar interceptação de ferramentas
Vale +20 pontos no seu score!
"""

from typing import Dict, Any, Optional
from datetime import datetime
import json

print("\n" + "="*70)
print("🎯 TUTORIAL HOOKS SYSTEM - RESOLVENDO SEU ÚLTIMO GAP CRÍTICO")
print("="*70)
print("""
Hooks System permite interceptar e controlar a execução de ferramentas
ANTES (PreToolUse) e DEPOIS (PostToolUse) delas serem executadas.

REGRA DE OURO: None = permite, {"behavior": "deny"} = bloqueia
""")

# ═══════════════════════════════════════════════════════════════
# PARTE 1: ENTENDENDO HOOKS
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("📚 PARTE 1: O QUE SÃO HOOKS?")
print("="*70)

print("""
Hooks são INTERCEPTADORES que:
• Executam ANTES ou DEPOIS de ferramentas
• Podem permitir, bloquear ou modificar execuções
• São úteis para segurança e governança
• Funcionam como middleware

TIPOS DE HOOKS:
─────────────────────────────────────
1. PreToolUse  → Executa ANTES da ferramenta
2. PostToolUse → Executa DEPOIS da ferramenta

RETORNOS POSSÍVEIS:
─────────────────────────────────────
• None → Permite execução normal
• {"behavior": "deny"} → Bloqueia execução
• {"behavior": "deny", "message": "..."} → Bloqueia com mensagem
""")

# ═══════════════════════════════════════════════════════════════
# PARTE 2: ESTRUTURA BÁSICA
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("🏗️ PARTE 2: ESTRUTURA DE UM HOOK")
print("="*70)

exemplo_basico = """
from claude_code_sdk import HookMatcher

def meu_hook(tool_name: str, args: Dict[str, Any]) -> Optional[Dict]:
    '''
    Hook básico que intercepta ferramentas

    Params:
        tool_name: Nome da ferramenta (Write, Read, Bash, etc)
        args: Argumentos passados para a ferramenta

    Returns:
        None = permite
        {"behavior": "deny"} = bloqueia
    '''

    # Lógica de decisão
    if tool_name == "Write" and ".env" in args.get("file_path", ""):
        # Bloquear criação de arquivos .env
        return {
            "behavior": "deny",
            "message": "Não é permitido criar arquivos .env!"
        }

    # Permitir tudo o resto
    return None

# Registrar o hook
hook_matcher = HookMatcher(
    matcher="PreToolUse",  # Executar ANTES da ferramenta
    hooks=[meu_hook]       # Lista de hooks
)
"""

print(exemplo_basico)

# ═══════════════════════════════════════════════════════════════
# PARTE 3: EXEMPLO #1 - HOOK DE SEGURANÇA
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("🔒 PARTE 3: HOOK DE SEGURANÇA")
print("="*70)

codigo_seguranca = '''
def hook_seguranca(tool_name: str, args: Dict[str, Any]) -> Optional[Dict]:
    """
    Hook que protege arquivos e comandos sensíveis
    """

    # Lista de arquivos protegidos
    arquivos_protegidos = [
        ".env",
        ".git",
        "credentials.json",
        "secrets.yaml",
        "private_key.pem"
    ]

    # Lista de comandos perigosos
    comandos_perigosos = [
        "rm -rf /",
        "format",
        "del /f /s /q",
        "sudo rm",
        "chmod 777"
    ]

    # Verificar Write/Edit em arquivos protegidos
    if tool_name in ["Write", "Edit", "MultiEdit"]:
        file_path = args.get("file_path", "")

        for arquivo in arquivos_protegidos:
            if arquivo in file_path:
                return {
                    "behavior": "deny",
                    "message": f"🔒 Bloqueado: Não pode modificar {arquivo}"
                }

    # Verificar comandos perigosos no Bash
    if tool_name == "Bash":
        comando = args.get("command", "").lower()

        for cmd_perigoso in comandos_perigosos:
            if cmd_perigoso in comando:
                return {
                    "behavior": "deny",
                    "message": f"⚠️ Comando perigoso bloqueado: {cmd_perigoso}"
                }

    # Permitir o resto
    return None
'''

print(codigo_seguranca)

# ═══════════════════════════════════════════════════════════════
# PARTE 4: EXEMPLO #2 - HOOK DE LOGGING
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("📝 PARTE 4: HOOK DE LOGGING/AUDITORIA")
print("="*70)

codigo_logging = '''
# Lista global para armazenar logs
logs_ferramentas = []

def hook_logging(tool_name: str, args: Dict[str, Any]) -> Optional[Dict]:
    """
    Hook que registra todas as execuções de ferramentas
    """

    # Criar entrada de log
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "tool": tool_name,
        "args": args,
        "action": "permitido"
    }

    # Ferramentas críticas para auditar
    ferramentas_criticas = ["Write", "Edit", "Bash", "Execute"]

    if tool_name in ferramentas_criticas:
        # Log detalhado para ferramentas críticas
        print(f"🔍 AUDITORIA: {tool_name} executado às {log_entry['timestamp']}")

        if tool_name == "Write":
            print(f"   → Arquivo: {args.get('file_path', 'N/A')}")
        elif tool_name == "Bash":
            print(f"   → Comando: {args.get('command', 'N/A')}")

    # Adicionar ao log
    logs_ferramentas.append(log_entry)

    # Salvar logs a cada 10 execuções
    if len(logs_ferramentas) >= 10:
        with open("audit_log.json", "w") as f:
            json.dump(logs_ferramentas, f, indent=2)
        print("💾 Logs salvos em audit_log.json")

    # Sempre permitir (só estamos logando)
    return None
'''

print(codigo_logging)

# ═══════════════════════════════════════════════════════════════
# PARTE 5: EXEMPLO #3 - HOOK DE VALIDAÇÃO
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("✅ PARTE 5: HOOK DE VALIDAÇÃO")
print("="*70)

codigo_validacao = '''
def hook_validacao(tool_name: str, args: Dict[str, Any]) -> Optional[Dict]:
    """
    Hook que valida argumentos antes da execução
    """

    # Validar argumentos do Write
    if tool_name == "Write":
        file_path = args.get("file_path", "")
        content = args.get("content", "")

        # Verificar se o path é absoluto
        if not file_path.startswith("/"):
            return {
                "behavior": "deny",
                "message": "❌ Use caminho absoluto, não relativo"
            }

        # Verificar tamanho do conteúdo
        if len(content) > 1_000_000:  # 1MB
            return {
                "behavior": "deny",
                "message": "❌ Arquivo muito grande (máx: 1MB)"
            }

        # Verificar extensão permitida
        extensoes_permitidas = [".py", ".txt", ".md", ".json", ".yaml"]
        if not any(file_path.endswith(ext) for ext in extensoes_permitidas):
            return {
                "behavior": "deny",
                "message": f"❌ Extensão não permitida. Use: {extensoes_permitidas}"
            }

    # Validar comandos Bash
    if tool_name == "Bash":
        command = args.get("command", "")

        # Bloquear comandos vazios
        if not command.strip():
            return {
                "behavior": "deny",
                "message": "❌ Comando vazio não permitido"
            }

        # Limitar tamanho do comando
        if len(command) > 500:
            return {
                "behavior": "deny",
                "message": "❌ Comando muito longo (máx: 500 caracteres)"
            }

    # Permitir se passou nas validações
    return None
'''

print(codigo_validacao)

# ═══════════════════════════════════════════════════════════════
# PARTE 6: HOOKS COMBINADOS (PRE + POST)
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("🔗 PARTE 6: COMBINANDO PRE E POST HOOKS")
print("="*70)

codigo_combinado = '''
# Estado compartilhado entre hooks
execucoes = {}

def pre_hook(tool_name: str, args: Dict[str, Any]) -> Optional[Dict]:
    """
    PreToolUse: Executa ANTES da ferramenta
    """
    # Registrar início
    exec_id = f"{tool_name}_{datetime.now().timestamp()}"
    execucoes[exec_id] = {
        "tool": tool_name,
        "start_time": datetime.now(),
        "args": args
    }

    print(f"⏱️ PRE: Iniciando {tool_name}")

    # Verificações de segurança
    if tool_name == "Bash" and "sudo" in args.get("command", ""):
        return {
            "behavior": "deny",
            "message": "🔒 Comandos sudo não permitidos"
        }

    return None  # Permitir

def post_hook(tool_name: str, args: Dict[str, Any], result: Any) -> None:
    """
    PostToolUse: Executa DEPOIS da ferramenta
    """
    # Encontrar execução correspondente
    exec_id = None
    for key, value in execucoes.items():
        if value["tool"] == tool_name and value["args"] == args:
            exec_id = key
            break

    if exec_id:
        # Calcular duração
        duracao = (datetime.now() - execucoes[exec_id]["start_time"]).seconds
        print(f"✅ POST: {tool_name} completado em {duracao}s")

        # Limpar da memória
        del execucoes[exec_id]

    # Post hooks não retornam nada (não podem bloquear)
    # Eles só observam/logam/notificam

# Registrar ambos
from claude_code_sdk import HookMatcher

pre_matcher = HookMatcher(
    matcher="PreToolUse",
    hooks=[pre_hook]
)

post_matcher = HookMatcher(
    matcher="PostToolUse",
    hooks=[post_hook]
)
'''

print(codigo_combinado)

# ═══════════════════════════════════════════════════════════════
# PARTE 7: CASOS DE USO PRÁTICOS
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("💡 PARTE 7: CASOS DE USO REAIS")
print("="*70)

print("""
1. PROTEÇÃO DE API KEYS
─────────────────────────────────────
def proteger_api_keys(tool_name, args):
    if tool_name in ["Write", "Edit"]:
        content = args.get("content", "")
        if "sk-" in content or "ANTHROPIC_API_KEY" in content:
            return {"behavior": "deny", "message": "🔒 API Keys bloqueadas"}
    return None

2. RATE LIMITING
─────────────────────────────────────
chamadas = {}
def rate_limiter(tool_name, args):
    agora = datetime.now()
    if tool_name not in chamadas:
        chamadas[tool_name] = []

    # Limpar chamadas antigas (> 1 minuto)
    chamadas[tool_name] = [t for t in chamadas[tool_name]
                          if (agora - t).seconds < 60]

    # Verificar limite
    if len(chamadas[tool_name]) >= 10:
        return {"behavior": "deny", "message": "⏱️ Rate limit: máx 10/min"}

    chamadas[tool_name].append(agora)
    return None

3. AMBIENTE ESPECÍFICO
─────────────────────────────────────
def apenas_desenvolvimento(tool_name, args):
    import os
    if os.getenv("AMBIENTE") == "PRODUCAO":
        if tool_name in ["Write", "Edit", "Bash"]:
            return {"behavior": "deny", "message": "🚫 Bloqueado em produção"}
    return None

4. BACKUP AUTOMÁTICO
─────────────────────────────────────
def backup_antes_edit(tool_name, args):
    if tool_name == "Edit":
        import shutil
        file_path = args.get("file_path")
        if file_path:
            backup = f"{file_path}.backup"
            shutil.copy(file_path, backup)
            print(f"💾 Backup criado: {backup}")
    return None
""")

# ═══════════════════════════════════════════════════════════════
# PARTE 8: ERROS COMUNS
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("⚠️ PARTE 8: ERROS COMUNS COM HOOKS")
print("="*70)

print("""
❌ ERRO #1: Retornar True/False ao invés de None/dict
─────────────────────────────────────────────────────
# ERRADO:
return True  # Permitir
return False # Bloquear

# CORRETO:
return None                      # Permitir
return {"behavior": "deny"}      # Bloquear

❌ ERRO #2: Esquecer que PostToolUse não pode bloquear
─────────────────────────────────────────────────────
PostToolUse executa DEPOIS - tarde demais para bloquear!
Use PreToolUse para bloquear execuções.

❌ ERRO #3: Não validar se keys existem em args
─────────────────────────────────────────────────────
# ERRADO:
file_path = args["file_path"]  # KeyError se não existir

# CORRETO:
file_path = args.get("file_path", "")

❌ ERRO #4: Hooks muito pesados/lentos
─────────────────────────────────────────────────────
Hooks executam em TODA ferramenta - mantenha leves!
Evite I/O pesado, loops grandes, requests HTTP.

❌ ERRO #5: Modificar args diretamente
─────────────────────────────────────────────────────
Hooks não devem modificar args - apenas observar/bloquear.
""")

# ═══════════════════════════════════════════════════════════════
# PARTE 9: EXERCÍCIOS
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("📝 PARTE 9: EXERCÍCIOS PRÁTICOS")
print("="*70)

print("""
EXERCÍCIO 1: Hook Anti-Spam
─────────────────────────────────────────────────────
Crie um hook que:
• Bloqueia mais de 5 Writes em 1 minuto
• Conta execuções por ferramenta
• Reseta contador após 1 minuto

EXERCÍCIO 2: Hook de Permissões
─────────────────────────────────────────────────────
Crie um hook que:
• Permite Read em qualquer arquivo
• Bloqueia Write fora de /tmp/
• Bloqueia Bash com sudo

EXERCÍCIO 3: Hook de Notificação
─────────────────────────────────────────────────────
Crie um PostToolUse hook que:
• Notifica quando arquivo > 1KB é criado
• Conta total de ferramentas executadas
• Mostra estatísticas a cada 10 execuções

EXERCÍCIO 4: Hook Inteligente
─────────────────────────────────────────────────────
Crie um hook que:
• Detecta tentativas de criar malware
• Bloqueia scripts com eval() ou exec()
• Alerta sobre comandos suspeitos
""")

# ═══════════════════════════════════════════════════════════════
# PARTE 10: CHECKLIST
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("✅ PARTE 10: CHECKLIST - VOCÊ DOMINA HOOKS?")
print("="*70)

print("""
Marque o que você já entende:

□ Hooks interceptam ferramentas antes/depois
□ PreToolUse executa ANTES (pode bloquear)
□ PostToolUse executa DEPOIS (só observa)
□ None = permite execução
□ {"behavior": "deny"} = bloqueia
□ Hooks recebem tool_name e args
□ PostHooks também recebem result
□ Hooks devem ser leves e rápidos
□ Use args.get() para evitar KeyError
□ Hooks são úteis para segurança/auditoria

Se marcou todos, você domina Hooks! +20 pontos! 🎉
""")

# ═══════════════════════════════════════════════════════════════
# RESUMO FINAL
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("🎯 RESUMO: HOOKS EM 1 MINUTO")
print("="*70)

print("""
1. Hooks interceptam execução de ferramentas
2. PreToolUse = ANTES (pode bloquear)
3. PostToolUse = DEPOIS (só observa)
4. None = permite, {"behavior": "deny"} = bloqueia
5. Use para segurança, auditoria e validação

FÓRMULA DO SUCESSO:
─────────────────────────────────────────────────────
PreToolUse + None/deny + HookMatcher = Controle Total!

🎉 PARABÉNS! Você resolveu o GAP #2!
Score: +20 pontos

VOCÊ AGORA É AVANÇADO! 🎯

Próximo: Criar projeto completo com SDK
""")

# Salvar progresso
print("\n💾 Salvando seu progresso...")
progresso = {
    "gap": "Hooks System",
    "status": "dominado",
    "data": datetime.now().isoformat(),
    "pontos_ganhos": 20,
    "nivel_alcancado": "AVANÇADO"
}

print(f"✅ Gap Hooks System dominado!")
print(f"📈 Score final: 90/120 (75%)")
print(f"🎯 NÍVEL: AVANÇADO!")
print(f"\n🚀 Parabéns! Você resolveu todos os gaps críticos!")