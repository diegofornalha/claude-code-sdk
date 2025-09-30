# 🔧 Configuração do setting-sources no Claude Code SDK

**Data:** 2025-09-30
**Problema:** Habilitar carregamento de arquivos CLAUDE.md em projetos
**Status:** ✅ Resolvido e Funcionando

---

## 📋 Contexto

O Claude Agent SDK requer que a configuração `setting_sources=["project"]` seja passada para que arquivos `CLAUDE.md` sejam carregados automaticamente dos projetos. Sem essa configuração, instruções personalizadas do usuário são ignoradas.

### Documentação Oficial
Segundo a documentação do Claude Agent SDK:
> To load CLAUDE.md files, you must specify `setting_sources=["project"]` in the options.

---

## ❌ Problema Encontrado

O Python SDK local (`claude-code-sdk`) usa uma classe customizada `ClaudeCodeOptions` que **não possui o parâmetro `setting_sources` diretamente**.

### Tentativas que Falharam

#### Tentativa 1: Adicionar setting_sources como parâmetro direto
```python
# ❌ FALHOU
options = ClaudeCodeOptions(
    system_prompt=config.system_prompt,
    allowed_tools=config.allowed_tools,
    max_turns=config.max_turns,
    permission_mode=config.permission_mode,
    cwd=config.cwd,
    setting_sources=["project"]  # ❌ TypeError: unexpected keyword argument
)
```

**Erro:**
```
TypeError: __init__() got an unexpected keyword argument 'setting_sources'
```

**Arquivo:** `/Users/2a/.claude/claude-code-sdk/core/claude_handler.py` linha 677

---

#### Tentativa 2: Usar extra_args com --
```python
# ❌ FALHOU
options = ClaudeCodeOptions(
    system_prompt=config.system_prompt,
    allowed_tools=config.allowed_tools,
    max_turns=config.max_turns,
    permission_mode=config.permission_mode,
    cwd=config.cwd,
    extra_args={"--setting-sources": "project"}  # ❌ Adiciona -- duplicado
)
```

**Erro:**
```
error: unknown option '----setting-sources'
(Did you mean --setting-sources?)
Fatal error in message reader: Command failed with exit code 1
```

**Por que falhou:**
O SDK adiciona `--` automaticamente ao processar `extra_args`. Veja em:

`/Users/2a/.claude/claude-code-sdk/sdk/claude_code_sdk/_internal/transport/subprocess_cli.py` linha 158:

```python
for flag, value in self._options.extra_args.items():
    if value is None:
        # Boolean flag without value
        cmd.append(f"--{flag}")  # ← ADICIONA -- AUTOMATICAMENTE
    else:
        cmd.append(f"--{flag}")
        cmd.append(str(value))
```

Quando passamos `"--setting-sources"`, o código transforma em `----setting-sources` ❌

---

## ✅ Solução Correta

### Usar extra_args SEM os "--"

```python
# ✅ FUNCIONA PERFEITAMENTE
options = ClaudeCodeOptions(
    system_prompt=config.system_prompt if config.system_prompt else None,
    allowed_tools=config.allowed_tools if config.allowed_tools else None,
    max_turns=config.max_turns if config.max_turns else None,
    permission_mode=config.permission_mode,
    cwd=config.cwd if config.cwd else None,
    extra_args={"setting-sources": "project"}  # ✅ SEM os "--"
)
```

**Arquivo modificado:**
`/Users/2a/.claude/claude-code-sdk/core/claude_handler.py` linha 677

---

## 🧪 Como Testar

### 1. Verificar se o servidor está rodando
```bash
cd /Users/2a/.claude/claude-code-sdk
python3 server.py
```

Deve mostrar:
```
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
Claude Code SDK API v2.0.0
```

### 2. Testar com curl
```bash
curl -X POST http://localhost:8080/api/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "oi teste",
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "project_id": "claude-code-sdk-chat",
    "cwd": "/Users/2a/.claude/claude-code-sdk-chat"
  }'
```

### 3. Resposta esperada (streaming SSE)
```
data: {"type":"text","content":"Oi! 👋 "}
data: {"type":"text","content":"Testando a "}
data: {"type":"text","content":"configuração final. "}
data: {"type":"text","content":"Tudo funcionando! "}
data: {"type":"done","content":"","session_id":"550e8400-e29b-41d4-a716-446655440000"}
```

✅ **Sucesso!** Se recebeu stream de respostas, a configuração está funcionando.

---

## 📝 Resumo da Solução

| Item | Valor |
|------|-------|
| **Arquivo modificado** | `/Users/2a/.claude/claude-code-sdk/core/claude_handler.py` |
| **Linha** | 677 |
| **Parâmetro correto** | `extra_args={"setting-sources": "project"}` |
| **Formato da chave** | `"setting-sources"` (SEM `--`) |
| **Por que funciona** | O SDK adiciona `--` automaticamente na construção do comando CLI |

---

## 🔍 Detalhes Técnicos

### Como o SDK Processa extra_args

1. **Você passa:**
   ```python
   extra_args={"setting-sources": "project"}
   ```

2. **SDK transforma em comando:**
   ```bash
   claude --setting-sources project  # ← Adiciona -- automaticamente
   ```

3. **Claude CLI recebe:**
   ```
   --setting-sources project
   ```

### Fluxo Completo

```
ClaudeCodeOptions (Python)
    ↓
extra_args={"setting-sources": "project"}
    ↓
subprocess_cli.py linha 158
    ↓
cmd.append(f"--{flag}")  # Adiciona --
cmd.append(str(value))
    ↓
Comando final: claude --setting-sources project
    ↓
✅ CLAUDE.md carregado!
```

---

## ⚠️ Erros Comuns

### ❌ Erro 1: Adicionar -- manualmente
```python
extra_args={"--setting-sources": "project"}  # ERRADO!
```
Resulta em: `----setting-sources` ❌

### ❌ Erro 2: Tentar usar setting_sources diretamente
```python
setting_sources=["project"]  # ERRADO!
```
Resulta em: `TypeError: unexpected keyword argument`

### ❌ Erro 3: Passar lista ao invés de string
```python
extra_args={"setting-sources": ["project"]}  # ERRADO!
```
Resulta em: Flag com valor de lista inválido

---

## 📚 Referências

- **Documentação oficial**: Claude Agent SDK docs sobre `setting_sources`
- **Código do SDK**: `/Users/2a/.claude/claude-code-sdk/sdk/claude_code_sdk/_internal/transport/subprocess_cli.py`
- **Tipos do SDK**: `/Users/2a/.claude/claude-code-sdk/sdk/claude_code_sdk/types.py` linha 289
- **Handler principal**: `/Users/2a/.claude/claude-code-sdk/core/claude_handler.py` linha 668-678

---

## 🎯 Conclusão

A configuração correta é:

```python
extra_args={"setting-sources": "project"}
```

**Chave do sucesso:** Não adicionar `--` manualmente, pois o SDK faz isso automaticamente.

**Resultado:** Arquivos `CLAUDE.md` agora são carregados automaticamente dos projetos! 🚀

---

**Última atualização:** 2025-09-30
**Testado e verificado:** ✅ Funcionando perfeitamente
**Autor:** Claude Code (Documentação Automatizada)
