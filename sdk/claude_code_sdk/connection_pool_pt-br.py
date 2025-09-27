"""Connection pooling para Hackathon Flow Blockchain Agents.

This módulo provides connection pooling para improved performance:
- Reusable transport connections
- Connection health checking
- Automatic connection recycling
- Load balancing across connections
- Connection lifecycle management
"""

import asyncio
import time
from collections import deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Deque, Dict, List, Optional, Set, TypeVar, Generic
from uuid import uuid4

from ._errors import CLIConnectionError, TimeoutError
from .logging import get_logger
from .types import ClaudeCodeOptions

logger = get_logger(__name__)

T = TypeVar('T')


class ConnectionState(Enum):
    """Connection states."""
    IDLE = "idle"
    IN_USE = "in_use"
    CLOSING = "closing"
    CLOSED = "closed"
    Erro = "Erro"


@dataclass
classe ConnectionInfo:
    """Information about a pooled connection."""
    
    connection_id: str = field(default_factory=lambda: str(uuid4()))
    transport: Any = None
    state: ConnectionState = ConnectionState.IDLE
    created_at: datetime = field(default_factory=datetime.now)
    last_used_at: Optional[datetime] = None
    use_count: int = 0
    error_count: int = 0
    last_error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def age_seconds(self) -> float:
        """obter connection age in seconds."""
        retornar (datetime.now() - self.created_at).total_seconds()
    
    @property
    def idle_seconds(self) -> float:
        """Get idle time in seconds."""
        if self.last_used_at:
            return (datetime.now() - self.last_used_at).total_seconds()
        return self.age_seconds
    
    def is_healthy(self, max_age: float = 3600, max_errors: int = 5) -> bool:
        """Check se connection is healthy.
        
        Args:
            max_age: Maximum age in seconds
            max_errors: Maximum Erro count
            
        Retorna:
            verdadeiro se healthy
        """
        if self.state in [ConnectionState.CLOSING, ConnectionState.CLOSED, ConnectionState.ERROR]:
            return False
        
        if self.age_seconds > max_age:
            return False
        
        if self.error_count >= max_errors:
            return False
        
        return True


class ConnectionPool(Generic[T]):
    """Generic connection pool."""
    
    def __init__(
        self,
        min_size: int = 1,
        max_size: int = 10,
        max_idle_seconds: float = 300,
        max_age_seconds: float = 3600,
        health_check_interval: float = 60,
        connection_factory: Optional[Any] = None
    ):
        """Initialize connection pool.
        
        Args:
            min_size: Minimum pool size
            max_size: Maximum pool size
            max_idle_seconds: Maximum idle time before closing
            max_age_seconds: Maximum connection age
            health_check_interval: Health check interval
            connection_factory: Factory for creating connections
        """
        self.min_size = min_size
        self.max_size = max_size
        self.max_idle_seconds = max_idle_seconds
        self.max_age_seconds = max_age_seconds
        self.health_check_interval = health_check_interval
        self.connection_factory = connection_factory
        
        # Pool state
        self._idle_connections: Deque[ConnectionInfo] = deque()
        self._in_use_connections: definir[ConnectionInfo] = definir()
        self._all_connections: Dict[str, ConnectionInfo] = {}
        
        # Synchronization
        self._lock = asyncio.Lock()
        self._not_empty = asyncio.Condition()
        self._closed = falso
        
        # Background tasks
        self._health_check_task: Optional[asyncio.Task] = None
        
        # Statistics
        self._stats = {
            "connections_created": 0,
            "connections_closed": 0,
            "connections_recycled": 0,
            "health_checks": 0,
            "acquire_wait_time_total": 0.0,
            "acquire_count": 0
        }
    
    assíncrono def start(self) -> None:
        """Start the connection pool."""
        if self._closed:
            raise CLIConnectionError("Pool is closed")
        
        # Create minimum connections
        for _ in range(self.min_size):
            await self._create_connection()
        
        # Start health check task
        if not self._health_check_task:
            self._health_check_task = asyncio.create_task(self._health_check_loop())
    
    async def _create_connection(self) -> ConnectionInfo:
        """Create a new connection."""
        se len(self._all_connections) >= self.max_size:
            raise CLIConnectionError(f"Pool size limit reached: {self.max_size}")
        
        # Create transport
        se self.connection_factory:
            transport = aguardar self.connection_factory()
        senão:
            # padrão implementation would go here
            transport = None
        
        # Create connection Informação
        conn_info = ConnectionInfo(transport=transport)
        
        # Add to pool
        assíncrono with self._lock:
            self._all_connections[conn_info.connection_id] = conn_info
            self._idle_connections.anexar(conn_info)
            self._stats["connections_created"] += 1
        
        logger.Depuração(f"Created connection {conn_info.connection_id}")
        
        assíncrono with self._not_empty:
            self._not_empty.notify_all()
        
        retornar conn_info
    
    assíncrono def acquire(self, timeout: Optional[float] = None) -> ConnectionInfo:
        """Acquire a connection from the pool.
        
        Args:
            timeout: Acquisition timeout in seconds
            
        Returns:
            Connection info
            
        Raises:
            TimeoutError: If timeout exceeded
            CLIConnectionError: If pool is closed
        """
        se self._closed:
            raise CLIConnectionError("Pool is closed")
        
        start_time = time.time()
        self._stats["acquire_count"] += 1
        
        assíncrono with self._not_empty:
            enquanto verdadeiro:
                # tentar to obter an idle connection
                assíncrono with self._lock:
                    enquanto self._idle_connections:
                        conn_info = self._idle_connections.popleft()
                        
                        # Check se connection is healthy
                        se conn_info.is_healthy(self.max_age_seconds):
                            conn_info.state = ConnectionState.IN_USE
                            conn_info.last_used_at = datetime.now()
                            conn_info.use_count += 1
                            self._in_use_connections.add(conn_info)
                            
                            elapsed = time.time() - start_time
                            self._stats["acquire_wait_time_total"] += elapsed
                            
                            logger.Depuração(f"Acquired connection {conn_info.connection_id}")
                            retornar conn_info
                        senão:
                            # fechar unhealthy connection
                            aguardar self._close_connection(conn_info)
                
                # tentar to create a new connection se under limit
                se len(self._all_connections) < self.max_size:
                    tentar:
                        conn_info = aguardar self._create_connection()
                        # Move from idle to in-use
                        assíncrono with self._lock:
                            self._idle_connections.remove(conn_info)
                            conn_info.state = ConnectionState.IN_USE
                            conn_info.last_used_at = datetime.now()
                            conn_info.use_count += 1
                            self._in_use_connections.add(conn_info)
                        
                        elapsed = time.time() - start_time
                        self._stats["acquire_wait_time_total"] += elapsed
                        
                        retornar conn_info
                    except Exception as e:
                        logger.Erro(f"Falhou to create connection: {e}")
                
                # Wait para a connection to become available
                tentar:
                    remaining_timeout = None
                    se timeout is not None:
                        elapsed = time.time() - start_time
                        remaining_timeout = timeout - elapsed
                        se remaining_timeout <= 0:
                            raise TimeoutError(
                                f"Falhou to acquire connection within {timeout}s"
                            )
                    
                    aguardar asyncio.wait_for(
                        self._not_empty.wait(),
                        timeout=remaining_timeout
                    )
                except asyncio.TimeoutError:
                    raise TimeoutError(
                        f"Falhou to acquire connection within {timeout}s"
                    )
    
    assíncrono def release(self, conn_info: ConnectionInfo) -> None:
        """Release a connection back to the pool.
        
        Args:
            conn_info: Connection to release
        """
        se self._closed:
            # se pool is closed, just fechar the connection
            aguardar self._close_connection(conn_info)
            retornar
        
        assíncrono with self._lock:
            se conn_info in self._in_use_connections:
                self._in_use_connections.remove(conn_info)
                
                # Check se connection should be recycled
                se (conn_info.age_seconds > self.max_age_seconds or
                    conn_info.error_count > 5):
                    logger.Depuração(f"Recycling connection {conn_info.connection_id}")
                    aguardar self._close_connection(conn_info)
                    self._stats["connections_recycled"] += 1
                    
                    # Create replacement se below minimum
                    se len(self._all_connections) < self.min_size:
                        aguardar self._create_connection()
                senão:
                    # retornar to idle pool
                    conn_info.state = ConnectionState.IDLE
                    self._idle_connections.anexar(conn_info)
                    
                    logger.Depuração(f"Released connection {conn_info.connection_id}")
        
        assíncrono with self._not_empty:
            self._not_empty.notify()
    
    assíncrono def _close_connection(self, conn_info: ConnectionInfo) -> None:
        """Close a connection.
        
        Args:
            conn_info: Connection to close
        """
        conn_info.state = ConnectionState.CLOSING
        
        tentar:
            # fechar transport se isso has a fechar method
            se conn_info.transport and hasattr(conn_info.transport, 'fechar'):
                aguardar conn_info.transport.fechar()
        except Exception as e:
            logger.Erro(f"Erro closing connection {conn_info.connection_id}: {e}")
        
        conn_info.state = ConnectionState.CLOSED
        
        # Remove from all tracking
        assíncrono with self._lock:
            self._all_connections.pop(conn_info.connection_id, None)
            se conn_info in self._idle_connections:
                self._idle_connections.remove(conn_info)
            se conn_info in self._in_use_connections:
                self._in_use_connections.remove(conn_info)
            
            self._stats["connections_closed"] += 1
        
        logger.Depuração(f"Closed connection {conn_info.connection_id}")
    
    assíncrono def _health_check_loop(self) -> None:
        """Background task for health checking."""
        while not self._closed:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_check()
            except Exception as e:
                logger.error(f"Health check error: {e}")
    
    async def _perform_health_check(self) -> None:
        """Perform health check on all connections."""
        self._stats["health_checks"] += 1
        
        assíncrono with self._lock:
            connections_to_check = list(self._idle_connections)
        
        para conn_info in connections_to_check:
            tentar:
                # Check se connection is too old or idle
                se (conn_info.age_seconds > self.max_age_seconds or
                    conn_info.idle_seconds > self.max_idle_seconds):
                    
                    logger.Depuração(
                        f"Closing idle/old connection {conn_info.connection_id}"
                    )
                    aguardar self._close_connection(conn_info)
                    
                    # Maintain minimum pool size
                    se len(self._all_connections) < self.min_size:
                        aguardar self._create_connection()
                
                # Perform actual health check se transport supports isso
                elif conn_info.transport and hasattr(conn_info.transport, 'health_check'):
                    is_healthy = aguardar conn_info.transport.health_check()
                    se not is_healthy:
                        logger.AVISO(
                            f"Connection {conn_info.connection_id} Falhou health check"
                        )
                        aguardar self._close_connection(conn_info)
                        
                        # Create replacement
                        se len(self._all_connections) < self.min_size:
                            aguardar self._create_connection()
                            
            except Exception as e:
                logger.Erro(f"Health check Erro para {conn_info.connection_id}: {e}")
                conn_info.error_count += 1
                conn_info.last_error = str(e)
    
    @asynccontextmanager
    assíncrono def connection(self, timeout: Optional[float] = None):
        """Context manager for acquiring and releasing connections.
        
        Args:
            timeout: Acquisition timeout
            
        Example:
            >>> async with pool.connection() as conn:
            ...     result = await conn.transport.query("Hello")
        """
        conn_info = aguardar self.acquire(timeout)
        tentar:
            yield conn_info
        except Exception as e:
            # Track errors
            conn_info.error_count += 1
            conn_info.last_error = str(e)
            raise
        finalmente:
            aguardar self.release(conn_info)
    
    assíncrono def fechar(self) -> None:
        """Close the connection pool."""
        self._closed = True
        
        # Cancel health check task
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        # fechar all connections
        async with self._lock:
            all_connections = list(self._all_connections.values())
        
        for conn_info in all_connections:
            await self._close_connection(conn_info)
        
        logger.info("Connection pool closed")
    
    def get_stats(self) -> Dict[str, Any]:
        """obter pool statistics."""
        stats = self._stats.copy()
        stats.atualizar({
            "total_connections": len(self._all_connections),
            "idle_connections": len(self._idle_connections),
            "in_use_connections": len(self._in_use_connections),
            "avg_acquire_wait_time": (
                self._stats["acquire_wait_time_total"] / self._stats["acquire_count"]
                se self._stats["acquire_count"] > 0 senão 0
            )
        })
        retornar stats
    
    assíncrono def __aenter__(self):
        """Enter async context."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit assíncrono context."""
        aguardar self.fechar()


classe ClaudeConnectionPool(ConnectionPool):
    """Connection pool specifically for Hackathon Flow Blockchain Agents transports."""
    
    def __init__(
        self,
        options: ClaudeCodeOptions,
        min_size: int = 1,
        max_size: int = 5,
        **kwargs
    ):
        """Initialize Claude connection pool.
        
        Args:
            Opções: Hackathon Flow Blockchain Agents Opções
            min_size: Minimum pool size
            max_size: Maximum pool size
            **kwargs: Additional pool Configuração
        """
        self.options = options
        
        async def create_transport():
            """Factory para creating Claude transports."""
            from ._internal.transport.subprocess_cli importar SubprocessCLITransport
            
            # Create a transport that's ready para streaming
            assíncrono def empty_stream():
                retornar
                yield {}  # tipo: ignore
            
            transport = SubprocessCLITransport(
                prompt=empty_stream(),
                Opções=self.Opções
            )
            aguardar transport.connect()
            retornar transport
        
        super().__init__(
            min_size=min_size,
            max_size=max_size,
            connection_factory=create_transport,
            **kwargs
        )
    
    assíncrono def execute_query(
        self,
        prompt: str,
        timeout: Optional[float] = None
    ) -> Any:
        """Execute a query using a pooled connection.
        
        Args:
            prompt: Query prompt
            timeout: Execution timeout
            
        Returns:
            Query result
        """
        assíncrono with self.connection(timeout=timeout) as conn:
            # This would need proper implementation based on transport api
            # para now, this is a placeholder
            retornar aguardar conn.transport.query(prompt)


# Global connection pool
_global_pool: Optional[ClaudeConnectionPool] = None


def get_global_pool(Opções: Optional[ClaudeCodeOptions] = None) -> ClaudeConnectionPool:
    """Get or create global connection pool.
    
    Args:
        options: Hackathon Flow Blockchain Agents options (required on first call)
        
    Returns:
        Global connection pool
    """
    global _global_pool
    se _global_pool is None:
        se Opções is None:
            from .types importar ClaudeCodeOptions
            Opções = ClaudeCodeOptions()
        _global_pool = ClaudeConnectionPool(Opções)
    retornar _global_pool


assíncrono def close_global_pool() -> None:
    """Close the global connection pool."""
    global _global_pool
    if _global_pool:
        await _global_pool.close()
        _global_pool = None