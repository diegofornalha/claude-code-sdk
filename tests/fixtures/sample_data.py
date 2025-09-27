"""
Fixtures de dados de teste.
Dados de exemplo para uso em testes.
"""

# ============================================
# SESSÕES DE EXEMPLO
# ============================================

SAMPLE_SESSIONS = [
    {
        "session_id": "12345678-1234-1234-1234-123456789001",
        "project_id": "test-project-1",
        "created_at": "2025-09-27T10:00:00Z"
    },
    {
        "session_id": "12345678-1234-1234-1234-123456789002",
        "project_id": "test-project-2",
        "created_at": "2025-09-27T11:00:00Z"
    },
    {
        "session_id": "12345678-1234-1234-1234-123456789003",
        "project_id": "test-project-3",
        "created_at": "2025-09-27T12:00:00Z"
    }
]


# ============================================
# MENSAGENS DE CHAT DE EXEMPLO
# ============================================

SAMPLE_MESSAGES = [
    {
        "message": "Olá, Claude! Como você está?",
        "session_id": "12345678-1234-1234-1234-123456789001",
        "project_id": "test-project"
    },
    {
        "message": "Pode me ajudar com Python?",
        "session_id": "12345678-1234-1234-1234-123456789002",
        "project_id": "test-project"
    },
    {
        "message": "Explique async/await em JavaScript",
        "project_id": "test-project"  # Sem session_id
    }
]


# ============================================
# MEMÓRIAS NEO4J DE EXEMPLO
# ============================================

SAMPLE_MEMORIES = [
    {
        "label": "Learning",
        "properties": {
            "name": "Python Basics",
            "description": "Fundamentos de Python",
            "category": "programming",
            "created_at": "2025-09-27T10:00:00Z"
        }
    },
    {
        "label": "Learning",
        "properties": {
            "name": "FastAPI Tutorial",
            "description": "Como criar APIs com FastAPI",
            "category": "web",
            "created_at": "2025-09-27T11:00:00Z"
        }
    },
    {
        "label": "Learning",
        "properties": {
            "name": "Neo4j Graph Database",
            "description": "Bancos de dados de grafo",
            "category": "database",
            "created_at": "2025-09-27T12:00:00Z"
        }
    }
]


# ============================================
# ENTRADAS MALICIOSAS PARA TESTES DE SEGURANÇA
# ============================================

MALICIOUS_INPUTS = [
    # XSS Attacks
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert('XSS')>",
    "javascript:alert(1)",
    "<iframe src='evil.com'></iframe>",
    "<svg/onload=alert('XSS')>",

    # SQL Injection
    "'; DROP TABLE users; --",
    "' OR '1'='1",
    "admin'--",
    "1' UNION SELECT * FROM users--",

    # Path Traversal
    "../../../etc/passwd",
    "..\\..\\..\\windows\\system32",
    "../../sensitive.env",

    # Template Injection
    "{{7*7}}",
    "${7*7}",
    "<%=7*7%>",

    # Command Injection
    "; ls -la",
    "| cat /etc/passwd",
    "& whoami",

    # Null bytes
    "%00null",
    "\x00admin"
]


# ============================================
# RESPOSTAS CLAUDE DE EXEMPLO
# ============================================

SAMPLE_CLAUDE_RESPONSES = [
    {
        "type": "content",
        "content": "Olá! Estou funcionando perfeitamente.",
        "session_id": "12345678-1234-1234-1234-123456789001"
    },
    {
        "type": "tool_use",
        "name": "bash",
        "id": "tool_123",
        "session_id": "12345678-1234-1234-1234-123456789001"
    },
    {
        "type": "result",
        "input_tokens": 100,
        "output_tokens": 200,
        "cost_usd": 0.005,
        "session_id": "12345678-1234-1234-1234-123456789001"
    }
]


# ============================================
# DADOS DE FLOW BLOCKCHAIN
# ============================================

SAMPLE_FLOW_ACCOUNTS = [
    {
        "address": "0x36395f9dde50ea27",
        "balance": 101000,  # Flow balance em unidades
        "network": "testnet"
    },
    {
        "address": "0x1234567890abcdef",
        "balance": 50000,
        "network": "testnet"
    }
]


# ============================================
# CONFIGURAÇÕES DE SESSÃO DE EXEMPLO
# ============================================

SAMPLE_SESSION_CONFIGS = [
    {
        "project_id": "neo4j-agent",
        "temperature": 0.7,
        "model": "claude-3-5-sonnet-20241022",
        "permission_mode": "bypassPermissions"
    },
    {
        "project_id": "test-project",
        "temperature": 0.9,
        "model": "claude-3-5-sonnet-20241022",
        "system_prompt": "You are a helpful assistant",
        "permission_mode": "bypassPermissions"
    }
]