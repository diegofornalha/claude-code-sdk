"""
Sistema Avançado de Tratamento de Erros com Telemetria
========================================================
Transforma erros silenciosos em insights acionáveis
"""

import traceback
import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, Callable, List
from enum import Enum
from dataclasses import dataclass, field
import hashlib
import sys
import os
from pathlib import Path

# Adicionar ao Neo4j para aprendizado
try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False


class ErrorSeverity(Enum):
    """Níveis de severidade para classificação automática."""
    CRITICAL = "critical"  # Sistema vai parar
    HIGH = "high"        # Funcionalidade quebrada
    MEDIUM = "medium"    # Degradação de performance
    LOW = "low"          # Avisos e melhorias
    INFO = "info"        # Informacional


class ErrorCategory(Enum):
    """Categorias para agrupamento e análise."""
    NETWORK = "network"
    DATABASE = "database"
    VALIDATION = "validation"
    PERMISSION = "permission"
    RESOURCE = "resource"
    TIMEOUT = "timeout"
    LOGIC = "logic"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Contexto rico para debug completo."""
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    endpoint: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None
    local_vars: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ErrorMetrics:
    """Métricas para análise de padrões."""
    error_hash: str
    count: int = 1
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    affected_sessions: List[str] = field(default_factory=list)


class SmartErrorHandler:
    """
    Handler inteligente que aprende com erros e sugere soluções.
    """

    def __init__(self, app_name: str = "neo4j-agent"):
        self.app_name = app_name
        self.error_patterns: Dict[str, ErrorMetrics] = {}
        self.solutions_cache: Dict[str, str] = {}
        self.error_log_path = Path(f"/tmp/{app_name}_errors.jsonl")
        self.neo4j_driver = None

        # Conectar ao Neo4j se disponível
        if NEO4J_AVAILABLE:
            self._init_neo4j()

        # Carregar soluções conhecidas
        self._load_known_solutions()

    def _init_neo4j(self):
        """Inicializa conexão com Neo4j para salvar aprendizados."""
        try:
            # Usar variáveis de ambiente para credenciais
            neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
            neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
            neo4j_password = os.getenv('NEO4J_PASSWORD')

            if not neo4j_password:
                print("⚠️ NEO4J_PASSWORD não configurada - conexão com Neo4j desabilitada")
                self.neo4j_driver = None
                return

            self.neo4j_driver = GraphDatabase.driver(
                neo4j_uri,
                auth=(neo4j_user, neo4j_password)
            )
        except Exception as e:
            print(f"⚠️ Erro ao conectar ao Neo4j: {e}")
            self.neo4j_driver = None

    def _load_known_solutions(self):
        """Carrega soluções conhecidas para erros comuns."""
        self.solutions_cache = {
            "session_not_found": "Criar nova sessão com create_session()",
            "pool_full": "Aumentar POOL_MAX_SIZE ou limpar conexões antigas",
            "timeout": "Aumentar timeout ou otimizar operação",
            "validation_failed": "Verificar tipos de dados e formato da entrada",
            "permission_denied": "Verificar permissões de arquivo/API",
            "connection_refused": "Verificar se serviço está rodando",
            "memory_error": "Liberar memória ou aumentar limites",
            "import_error": "Instalar dependências com pip/npm",
        }

    def categorize_error(self, error: Exception) -> ErrorCategory:
        """Categoriza automaticamente o erro."""
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()

        # Mapeamento inteligente
        if "timeout" in error_str or "timeout" in error_type:
            return ErrorCategory.TIMEOUT
        elif "connection" in error_str or "network" in error_str:
            return ErrorCategory.NETWORK
        elif "permission" in error_str or "denied" in error_str:
            return ErrorCategory.PERMISSION
        elif "validation" in error_str or "invalid" in error_str:
            return ErrorCategory.VALIDATION
        elif "database" in error_str or "neo4j" in error_str:
            return ErrorCategory.DATABASE
        elif "memory" in error_str or "resource" in error_str:
            return ErrorCategory.RESOURCE
        elif isinstance(error, (KeyError, ValueError, TypeError)):
            return ErrorCategory.LOGIC
        else:
            return ErrorCategory.UNKNOWN

    def assess_severity(self, error: Exception, context: ErrorContext) -> ErrorSeverity:
        """Avalia severidade baseado no impacto."""
        error_type = type(error).__name__

        # Críticos
        if error_type in ["SystemExit", "KeyboardInterrupt", "MemoryError"]:
            return ErrorSeverity.CRITICAL

        # Alto
        if error_type in ["DatabaseError", "ConnectionError", "TimeoutError"]:
            return ErrorSeverity.HIGH

        # Médio
        if error_type in ["ValueError", "KeyError", "AttributeError"]:
            return ErrorSeverity.MEDIUM

        # Baixo
        if error_type in ["Warning", "DeprecationWarning"]:
            return ErrorSeverity.LOW

        # Análise contextual
        if context.endpoint and "/health" in context.endpoint:
            return ErrorSeverity.LOW  # Health checks são menos críticos

        return ErrorSeverity.MEDIUM

    def generate_error_hash(self, error: Exception) -> str:
        """Gera hash único para agrupar erros similares."""
        # Combina tipo e linha principal do erro
        error_sig = f"{type(error).__name__}:{str(error)[:100]}"

        # Adiciona linha do código se disponível
        tb = traceback.extract_tb(error.__traceback__)
        if tb:
            last_frame = tb[-1]
            error_sig += f":{last_frame.filename}:{last_frame.lineno}"

        return hashlib.md5(error_sig.encode()).hexdigest()[:12]

    def suggest_solution(self, error: Exception, category: ErrorCategory) -> Optional[str]:
        """Sugere solução baseada em padrões conhecidos."""
        error_str = str(error).lower()

        # Procura em soluções conhecidas
        for pattern, solution in self.solutions_cache.items():
            if pattern in error_str:
                return solution

        # Sugestões por categoria
        category_solutions = {
            ErrorCategory.NETWORK: "Verificar conectividade e configurações de rede",
            ErrorCategory.DATABASE: "Verificar conexão com Neo4j e credenciais",
            ErrorCategory.VALIDATION: "Revisar formato e tipos dos dados enviados",
            ErrorCategory.PERMISSION: "Verificar permissões de usuário e arquivo",
            ErrorCategory.RESOURCE: "Monitorar uso de CPU/memória e limpar recursos",
            ErrorCategory.TIMEOUT: "Aumentar timeout ou executar em background",
            ErrorCategory.LOGIC: "Revisar lógica e adicionar validações",
        }

        return category_solutions.get(category)

    async def handle_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None,
        reraise: bool = False
    ) -> Dict[str, Any]:
        """
        Processa erro de forma inteligente e retorna análise completa.
        """
        if context is None:
            context = ErrorContext()

        # Captura stack trace completo
        context.stack_trace = traceback.format_exc()

        # Captura variáveis locais do frame onde ocorreu o erro
        tb = error.__traceback__
        if tb:
            frame = tb.tb_frame
            context.local_vars = {
                k: str(v)[:100] for k, v in frame.f_locals.items()
                if not k.startswith("__")
            }

        # Análise automática
        category = self.categorize_error(error)
        severity = self.assess_severity(error, context)
        error_hash = self.generate_error_hash(error)
        solution = self.suggest_solution(error, category)

        # Atualiza métricas
        if error_hash not in self.error_patterns:
            self.error_patterns[error_hash] = ErrorMetrics(error_hash=error_hash)

        metrics = self.error_patterns[error_hash]
        metrics.count += 1
        metrics.last_seen = datetime.now()
        if context.session_id:
            metrics.affected_sessions.append(context.session_id)

        # Monta relatório completo
        error_report = {
            "error_id": error_hash,
            "timestamp": context.timestamp.isoformat(),
            "app": self.app_name,
            "error": {
                "type": type(error).__name__,
                "message": str(error),
                "category": category.value,
                "severity": severity.value,
            },
            "context": {
                "session_id": context.session_id,
                "user_id": context.user_id,
                "request_id": context.request_id,
                "endpoint": context.endpoint,
                "input_data": context.input_data,
            },
            "debug": {
                "stack_trace": context.stack_trace,
                "local_vars": context.local_vars,
            },
            "metrics": {
                "occurrence_count": metrics.count,
                "first_seen": metrics.first_seen.isoformat(),
                "last_seen": metrics.last_seen.isoformat(),
                "affected_sessions": len(set(metrics.affected_sessions)),
            },
            "solution": solution,
            "is_recurring": metrics.count > 1,
        }

        # Salva no arquivo de log
        await self._save_error_log(error_report)

        # Salva no Neo4j se disponível
        if self.neo4j_driver:
            await self._save_to_neo4j(error_report)

        # Notifica se crítico
        if severity == ErrorSeverity.CRITICAL:
            await self._notify_critical_error(error_report)

        # Re-throw se solicitado
        if reraise:
            raise error

        return error_report

    async def _save_error_log(self, error_report: Dict[str, Any]):
        """Salva erro em arquivo JSONL para análise posterior."""
        try:
            with open(self.error_log_path, "a") as f:
                f.write(json.dumps(error_report) + "\n")
        except:
            pass  # Não queremos falhar se não conseguir logar

    async def _save_to_neo4j(self, error_report: Dict[str, Any]):
        """Salva erro no Neo4j para aprendizado."""
        if not self.neo4j_driver:
            return

        try:
            with self.neo4j_driver.session() as session:
                session.run(
                    """
                    CREATE (e:Learning:Error {
                        error_id: $error_id,
                        type: $type,
                        message: $message,
                        category: $category,
                        severity: $severity,
                        solution: $solution,
                        count: $count,
                        timestamp: datetime($timestamp)
                    })
                    """,
                    error_id=error_report["error_id"],
                    type=error_report["error"]["type"],
                    message=error_report["error"]["message"],
                    category=error_report["error"]["category"],
                    severity=error_report["error"]["severity"],
                    solution=error_report.get("solution"),
                    count=error_report["metrics"]["occurrence_count"],
                    timestamp=error_report["timestamp"]
                )
        except:
            pass  # Não falhar se Neo4j não estiver disponível

    async def _notify_critical_error(self, error_report: Dict[str, Any]):
        """Notifica sobre erros críticos (implementar webhook/email)."""
        print(f"\n🚨 ERRO CRÍTICO DETECTADO: {error_report['error_id']}")
        print(f"   Tipo: {error_report['error']['type']}")
        print(f"   Mensagem: {error_report['error']['message']}")
        print(f"   Solução: {error_report.get('solution', 'Investigar manualmente')}")

    def get_error_summary(self) -> Dict[str, Any]:
        """Retorna resumo de todos os erros para dashboard."""
        total_errors = sum(m.count for m in self.error_patterns.values())

        # Agrupa por severidade
        by_severity = {}
        for error_hash, metrics in self.error_patterns.items():
            # Precisaríamos salvar severidade nas métricas para isso
            pass

        return {
            "total_errors": total_errors,
            "unique_errors": len(self.error_patterns),
            "most_common": sorted(
                self.error_patterns.items(),
                key=lambda x: x[1].count,
                reverse=True
            )[:5],
            "recent_errors": sorted(
                self.error_patterns.items(),
                key=lambda x: x[1].last_seen,
                reverse=True
            )[:5],
        }


# Decorator para uso fácil
def smart_error_handler(
    severity: Optional[ErrorSeverity] = None,
    category: Optional[ErrorCategory] = None,
    reraise: bool = False
):
    """
    Decorator para adicionar tratamento inteligente de erros.

    Uso:
        @smart_error_handler(severity=ErrorSeverity.HIGH)
        async def minha_funcao():
            ...
    """
    handler = SmartErrorHandler()

    def decorator(func: Callable):
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                context = ErrorContext(
                    endpoint=func.__name__,
                    input_data={"args": str(args)[:100], "kwargs": str(kwargs)[:100]}
                )

                report = await handler.handle_error(e, context, reraise=reraise)

                # Retorna erro formatado ao invés de quebrar
                return {
                    "error": True,
                    "error_id": report["error_id"],
                    "message": report["error"]["message"],
                    "solution": report.get("solution"),
                }

        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = ErrorContext(
                    endpoint=func.__name__,
                    input_data={"args": str(args)[:100], "kwargs": str(kwargs)[:100]}
                )

                # Versão síncrona
                report = asyncio.run(handler.handle_error(e, context, reraise=reraise))

                return {
                    "error": True,
                    "error_id": report["error_id"],
                    "message": report["error"]["message"],
                    "solution": report.get("solution"),
                }

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


# Instância global para uso direto
error_handler = SmartErrorHandler()