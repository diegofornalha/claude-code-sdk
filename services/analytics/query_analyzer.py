"""
Analisador de Queries e Performance
====================================
Sistema inteligente para análise e otimização de queries
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import re
import hashlib
import json


@dataclass
class QueryProfile:
    """Perfil de uma query."""
    query_hash: str
    query_template: str
    execution_count: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    avg_time: float = 0.0
    last_execution: Optional[datetime] = None
    errors: int = 0
    slow_executions: int = 0


@dataclass
class QueryRecommendation:
    """Recomendação de otimização."""
    severity: str  # "high", "medium", "low"
    category: str  # "index", "query_structure", "performance"
    message: str
    suggestion: str
    estimated_improvement: Optional[str] = None


class QueryAnalyzer:
    """Analisador inteligente de queries."""

    # Thresholds para análise
    SLOW_QUERY_THRESHOLD_MS = 1000  # 1 segundo
    VERY_SLOW_QUERY_THRESHOLD_MS = 5000  # 5 segundos

    def __init__(self):
        """Inicializa analisador."""
        self.query_profiles: Dict[str, QueryProfile] = {}
        self.query_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000

    def normalize_query(self, query: str) -> str:
        """
        Normaliza query para criar template.

        Args:
            query: Query original

        Returns:
            Query normalizada
        """
        # Remove espaços extras
        normalized = re.sub(r'\s+', ' ', query.strip())

        # Substitui valores literais por placeholders
        normalized = re.sub(r"'[^']*'", "'?'", normalized)  # Strings
        normalized = re.sub(r'\b\d+\b', '?', normalized)  # Números

        return normalized.lower()

    def get_query_hash(self, query: str) -> str:
        """
        Gera hash único para query normalizada.

        Args:
            query: Query a hashear

        Returns:
            Hash MD5 da query
        """
        normalized = self.normalize_query(query)
        return hashlib.md5(normalized.encode()).hexdigest()

    def record_execution(
        self,
        query: str,
        duration_ms: float,
        success: bool = True,
        error: Optional[str] = None
    ):
        """
        Registra execução de uma query.

        Args:
            query: Query executada
            duration_ms: Duração em milissegundos
            success: Se execução foi bem-sucedida
            error: Mensagem de erro (se houver)
        """
        query_hash = self.get_query_hash(query)
        normalized = self.normalize_query(query)

        # Cria ou atualiza perfil
        if query_hash not in self.query_profiles:
            self.query_profiles[query_hash] = QueryProfile(
                query_hash=query_hash,
                query_template=normalized
            )

        profile = self.query_profiles[query_hash]
        profile.execution_count += 1
        profile.total_time += duration_ms
        profile.min_time = min(profile.min_time, duration_ms)
        profile.max_time = max(profile.max_time, duration_ms)
        profile.avg_time = profile.total_time / profile.execution_count
        profile.last_execution = datetime.utcnow()

        if not success:
            profile.errors += 1

        if duration_ms > self.SLOW_QUERY_THRESHOLD_MS:
            profile.slow_executions += 1

        # Adiciona ao histórico
        self.query_history.append({
            "query_hash": query_hash,
            "duration_ms": duration_ms,
            "timestamp": datetime.utcnow().isoformat(),
            "success": success,
            "error": error
        })

        # Limita tamanho do histórico
        if len(self.query_history) > self.max_history_size:
            self.query_history = self.query_history[-self.max_history_size:]

    def get_slow_queries(self, threshold_ms: float = None) -> List[QueryProfile]:
        """
        Retorna queries lentas.

        Args:
            threshold_ms: Threshold personalizado (usa padrão se None)

        Returns:
            Lista de queries lentas ordenadas por tempo médio
        """
        threshold = threshold_ms or self.SLOW_QUERY_THRESHOLD_MS

        slow_queries = [
            profile for profile in self.query_profiles.values()
            if profile.avg_time > threshold
        ]

        # Ordena por tempo médio (descendente)
        slow_queries.sort(key=lambda p: p.avg_time, reverse=True)

        return slow_queries

    def get_most_executed(self, limit: int = 10) -> List[QueryProfile]:
        """
        Retorna queries mais executadas.

        Args:
            limit: Número máximo de queries a retornar

        Returns:
            Lista de queries mais executadas
        """
        profiles = list(self.query_profiles.values())
        profiles.sort(key=lambda p: p.execution_count, reverse=True)
        return profiles[:limit]

    def analyze_query_patterns(self) -> Dict[str, Any]:
        """
        Analisa padrões de uso de queries.

        Returns:
            Análise de padrões
        """
        if not self.query_profiles:
            return {"message": "No query data available"}

        total_queries = sum(p.execution_count for p in self.query_profiles.values())
        total_time = sum(p.total_time for p in self.query_profiles.values())

        slow_queries = self.get_slow_queries()
        very_slow_queries = [
            p for p in self.query_profiles.values()
            if p.avg_time > self.VERY_SLOW_QUERY_THRESHOLD_MS
        ]

        # Análise de distribuição de tempo
        time_buckets = defaultdict(int)
        for profile in self.query_profiles.values():
            if profile.avg_time < 100:
                time_buckets["<100ms"] += profile.execution_count
            elif profile.avg_time < 500:
                time_buckets["100-500ms"] += profile.execution_count
            elif profile.avg_time < 1000:
                time_buckets["500ms-1s"] += profile.execution_count
            elif profile.avg_time < 5000:
                time_buckets["1-5s"] += profile.execution_count
            else:
                time_buckets[">5s"] += profile.execution_count

        return {
            "summary": {
                "total_unique_queries": len(self.query_profiles),
                "total_executions": total_queries,
                "total_time_ms": round(total_time, 2),
                "avg_query_time_ms": round(total_time / total_queries, 2) if total_queries > 0 else 0
            },
            "performance": {
                "slow_queries_count": len(slow_queries),
                "very_slow_queries_count": len(very_slow_queries),
                "slow_query_percentage": (
                    len(slow_queries) / len(self.query_profiles) * 100
                    if self.query_profiles else 0
                )
            },
            "time_distribution": dict(time_buckets),
            "top_slow_queries": [
                {
                    "template": p.query_template[:100],
                    "avg_time_ms": round(p.avg_time, 2),
                    "executions": p.execution_count
                }
                for p in slow_queries[:5]
            ]
        }

    def generate_recommendations(
        self,
        query_hash: Optional[str] = None
    ) -> List[QueryRecommendation]:
        """
        Gera recomendações de otimização.

        Args:
            query_hash: Hash de query específica (None para geral)

        Returns:
            Lista de recomendações
        """
        recommendations = []

        if query_hash:
            # Recomendações para query específica
            profile = self.query_profiles.get(query_hash)
            if not profile:
                return []

            if profile.avg_time > self.VERY_SLOW_QUERY_THRESHOLD_MS:
                recommendations.append(QueryRecommendation(
                    severity="high",
                    category="performance",
                    message=f"Query muito lenta (média: {profile.avg_time:.0f}ms)",
                    suggestion="Revisar estrutura da query e considerar adicionar índices",
                    estimated_improvement="50-80%"
                ))

            if profile.errors > profile.execution_count * 0.1:
                recommendations.append(QueryRecommendation(
                    severity="high",
                    category="reliability",
                    message=f"Alta taxa de erros ({profile.errors}/{profile.execution_count})",
                    suggestion="Verificar validação de dados e tratamento de erros"
                ))

        else:
            # Recomendações gerais
            slow_queries = self.get_slow_queries()

            if len(slow_queries) > len(self.query_profiles) * 0.3:
                recommendations.append(QueryRecommendation(
                    severity="high",
                    category="performance",
                    message=f"{len(slow_queries)} queries lentas detectadas",
                    suggestion="Considerar adicionar índices nas propriedades mais consultadas",
                    estimated_improvement="40-70%"
                ))

            # Verifica queries sem índice (heurística baseada em padrões)
            unindexed_patterns = [
                p for p in self.query_profiles.values()
                if "where" in p.query_template.lower() and
                   "index" not in p.query_template.lower()
            ]

            if unindexed_patterns:
                recommendations.append(QueryRecommendation(
                    severity="medium",
                    category="index",
                    message=f"{len(unindexed_patterns)} queries podem se beneficiar de índices",
                    suggestion="Analisar propriedades usadas em cláusulas WHERE e criar índices apropriados"
                ))

        return recommendations

    def get_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas completas do analisador.

        Returns:
            Estatísticas detalhadas
        """
        patterns = self.analyze_query_patterns()
        recommendations = self.generate_recommendations()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "patterns": patterns,
            "recommendations": [
                {
                    "severity": r.severity,
                    "category": r.category,
                    "message": r.message,
                    "suggestion": r.suggestion,
                    "estimated_improvement": r.estimated_improvement
                }
                for r in recommendations
            ],
            "most_executed": [
                {
                    "template": p.query_template[:100],
                    "executions": p.execution_count,
                    "avg_time_ms": round(p.avg_time, 2)
                }
                for p in self.get_most_executed(5)
            ]
        }


# Instância global
query_analyzer = QueryAnalyzer()