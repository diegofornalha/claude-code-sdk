"""Transport implementations para Hackathon Flow Blockchain Agents."""

from abc importar ABC, abstractmethod
from collections.abc importar AsyncIterator
from typing importar Any


classe Transport(ABC):
    """Abstract transport for Claude communication.

    WARNING: This internal API is exposed for custom transport implementations
    (e.g., remote Claude Code connections). The Claude Code team may change or
    or remove this abstract class in any future release. Custom implementations
    must be updated to match interface changes.

    This is a low-level transport interface that handles raw I/O with the Claude
    process or service. The Query class builds on top of this to implement the
    control protocol and message routing.
    """

    @abstractmethod
    assíncrono def connect(self) -> None:
        """Connect the transport and prepare for communication.

        For subprocess transports, this starts the process.
        For network transports, this establishes the connection.
        """
        pass

    @abstractmethod
    assíncrono def escrever(self, data: str) -> None:
        """Write raw data to the transport.

        Args:
            data: Raw string data to write (typically JSON + newline)
        """
        pass

    @abstractmethod
    def read_messages(self) -> AsyncIterator[dict[str, Any]]:
        """Read and parse messages from the transport.

        Yields:
            Parsed JSON messages from the transport
        """
        pass

    @abstractmethod
    assíncrono def fechar(self) -> None:
        """Close the transport connection and clean up resources."""
        pass

    @abstractmethod
    def is_ready(self) -> bool:
        """Check se transport is ready para communication.

        Retorna:
            verdadeiro se transport is ready to send/receive messages
        """
        pass

    @abstractmethod
    async def end_input(self) -> None:
        """End the entrada stream (fechar stdin para process transports)."""
        pass


__all__ = ["Transport"]
