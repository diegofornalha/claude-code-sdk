"""
Circuit Breaker Pattern Implementation
======================================
Protege contra falhas em cascata de serviços externos
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Callable
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Estados do circuit breaker."""
    CLOSED = "closed"      # Normal, requisições passam
    OPEN = "open"          # Falhas detectadas, requisições bloqueadas
    HALF_OPEN = "half_open"  # Testando recuperação


class CircuitBreaker:
    """
    Circuit breaker para proteger contra falhas de serviços externos.

    Padrão:
    - CLOSED: Operação normal
    - OPEN: Após N falhas, bloqueia requisições por X segundos
    - HALF_OPEN: Permite 1 requisição teste após timeout
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception,
        success_threshold: int = 2
    ):
        """
        Inicializa o circuit breaker.

        Args:
            name: Nome do serviço protegido
            failure_threshold: Número de falhas para abrir o circuito
            recovery_timeout: Segundos para tentar recuperação
            expected_exception: Tipo de exceção esperada
            success_threshold: Sucessos necessários para fechar circuito
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.success_threshold = success_threshold

        # Estado inicial
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_success_time: Optional[datetime] = None

        # Estatísticas
        self.stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "rejected_calls": 0,
            "state_changes": []
        }

        # Lock para thread-safety
        self.lock = asyncio.Lock()

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Executa função protegida pelo circuit breaker.

        Args:
            func: Função a executar
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados

        Returns:
            Resultado da função

        Raises:
            CircuitOpenError: Se circuito estiver aberto
            Exception: Exceção original da função
        """
        async with self.lock:
            self.stats["total_calls"] += 1

            # Verifica estado atual
            current_state = await self._get_current_state()

            if current_state == CircuitState.OPEN:
                self.stats["rejected_calls"] += 1
                raise CircuitOpenError(
                    f"Circuit breaker '{self.name}' is OPEN. "
                    f"Service unavailable for {self._get_remaining_timeout()}s"
                )

        # Tenta executar a função
        try:
            # Se assíncrona
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                # Se síncrona, executa em thread pool
                result = await asyncio.get_event_loop().run_in_executor(
                    None, func, *args, **kwargs
                )

            # Registra sucesso
            await self._on_success()
            return result

        except self.expected_exception as e:
            # Registra falha
            await self._on_failure()
            raise e

    async def _get_current_state(self) -> CircuitState:
        """Obtém o estado atual considerando timeouts."""
        if self.state == CircuitState.OPEN:
            # Verifica se deve transicionar para HALF_OPEN
            if self.last_failure_time:
                time_since_failure = (datetime.now() - self.last_failure_time).total_seconds()
                if time_since_failure >= self.recovery_timeout:
                    await self._transition_to(CircuitState.HALF_OPEN)

        return self.state

    async def _on_success(self):
        """Processa sucesso de chamada."""
        async with self.lock:
            self.stats["successful_calls"] += 1
            self.last_success_time = datetime.now()

            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                logger.info(
                    f"Circuit breaker '{self.name}' success in HALF_OPEN "
                    f"({self.success_count}/{self.success_threshold})"
                )

                # Fecha circuito após sucessos suficientes
                if self.success_count >= self.success_threshold:
                    await self._transition_to(CircuitState.CLOSED)

            elif self.state == CircuitState.CLOSED:
                # Reset contador de falhas em caso de sucesso
                self.failure_count = 0

    async def _on_failure(self):
        """Processa falha de chamada."""
        async with self.lock:
            self.stats["failed_calls"] += 1
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            logger.warning(
                f"Circuit breaker '{self.name}' failure "
                f"({self.failure_count}/{self.failure_threshold})"
            )

            if self.state == CircuitState.HALF_OPEN:
                # Falha em HALF_OPEN volta para OPEN
                await self._transition_to(CircuitState.OPEN)

            elif self.state == CircuitState.CLOSED:
                # Abre circuito se atingir threshold
                if self.failure_count >= self.failure_threshold:
                    await self._transition_to(CircuitState.OPEN)

    async def _transition_to(self, new_state: CircuitState):
        """Transiciona para novo estado."""
        if self.state != new_state:
            old_state = self.state
            self.state = new_state

            # Reset contadores baseado no novo estado
            if new_state == CircuitState.CLOSED:
                self.failure_count = 0
                self.success_count = 0
            elif new_state == CircuitState.HALF_OPEN:
                self.success_count = 0
                self.failure_count = 0

            # Registra mudança
            self.stats["state_changes"].append({
                "from": old_state.value,
                "to": new_state.value,
                "timestamp": datetime.now().isoformat()
            })

            logger.info(
                f"Circuit breaker '{self.name}' transitioned: "
                f"{old_state.value} -> {new_state.value}"
            )

    def _get_remaining_timeout(self) -> int:
        """Calcula tempo restante de timeout."""
        if self.last_failure_time:
            elapsed = (datetime.now() - self.last_failure_time).total_seconds()
            remaining = max(0, self.recovery_timeout - int(elapsed))
            return remaining
        return 0

    async def reset(self):
        """Reset manual do circuit breaker."""
        async with self.lock:
            await self._transition_to(CircuitState.CLOSED)
            self.failure_count = 0
            self.success_count = 0
            logger.info(f"Circuit breaker '{self.name}' manually reset")

    def get_status(self) -> Dict[str, Any]:
        """Retorna status atual do circuit breaker."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "stats": self.stats,
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "last_success": self.last_success_time.isoformat() if self.last_success_time else None,
            "remaining_timeout": self._get_remaining_timeout() if self.state == CircuitState.OPEN else None
        }


class CircuitOpenError(Exception):
    """Exceção lançada quando circuit breaker está aberto."""
    pass


class CircuitBreakerManager:
    """Gerencia múltiplos circuit breakers."""

    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}

    def get_or_create(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        **kwargs
    ) -> CircuitBreaker:
        """Obtém ou cria um circuit breaker."""
        if name not in self.breakers:
            self.breakers[name] = CircuitBreaker(
                name=name,
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
                **kwargs
            )
        return self.breakers[name]

    def get_all_status(self) -> Dict[str, Any]:
        """Retorna status de todos os breakers."""
        return {
            name: breaker.get_status()
            for name, breaker in self.breakers.items()
        }

    async def reset_all(self):
        """Reset todos os circuit breakers."""
        for breaker in self.breakers.values():
            await breaker.reset()


# Instância global
circuit_manager = CircuitBreakerManager()


# Decorador para facilitar uso
def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    expected_exception: type = Exception
):
    """
    Decorador para proteger funções com circuit breaker.

    Uso:
        @circuit_breaker(name="neo4j", failure_threshold=3)
        async def query_neo4j():
            # código que pode falhar
            pass
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            breaker = circuit_manager.get_or_create(
                name=name,
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
                expected_exception=expected_exception
            )
            return await breaker.call(func, *args, **kwargs)

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper

    return decorator