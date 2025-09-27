"""
Mocks para Claude SDK.
Simula comportamento do Claude Code SDK para testes.
"""

from typing import AsyncGenerator, List, Optional
from dataclasses import dataclass
from unittest.mock import AsyncMock


@dataclass
class MockTextBlock:
    """Mock de TextBlock do SDK."""
    text: str
    type: str = "text"


@dataclass
class MockToolUseBlock:
    """Mock de ToolUseBlock do SDK."""
    id: str
    name: str
    input: dict
    type: str = "tool_use"


@dataclass
class MockToolResultBlock:
    """Mock de ToolResultBlock do SDK."""
    tool_use_id: str
    content: str
    type: str = "tool_result"


@dataclass
class MockAssistantMessage:
    """Mock de AssistantMessage do SDK."""
    content: List
    role: str = "assistant"


@dataclass
class MockUserMessage:
    """Mock de UserMessage do SDK."""
    content: List
    role: str = "user"


@dataclass
class MockUsage:
    """Mock de Usage statistics."""
    input_tokens: int
    output_tokens: int


@dataclass
class MockResultMessage:
    """Mock de ResultMessage do SDK."""
    usage: Optional[MockUsage] = None
    total_cost_usd: float = 0.0


class MockClaudeSDKClient:
    """Mock completo do ClaudeSDKClient."""

    def __init__(self, options=None):
        self.options = options
        self._connected = False
        self.messages: List = []
        self.session_id: Optional[str] = None

    async def connect(self):
        """Simula conexão."""
        self._connected = True

    async def disconnect(self):
        """Simula desconexão."""
        self._connected = False

    async def query(self, message: str, session_id: Optional[str] = None):
        """Simula envio de query."""
        self.messages.append(message)
        self.session_id = session_id

    async def receive_response(self) -> AsyncGenerator:
        """Simula recebimento de resposta."""
        # Retorna resposta simulada
        yield MockAssistantMessage(
            content=[MockTextBlock(text="Esta é uma resposta simulada do Claude.")]
        )

        yield MockResultMessage(
            usage=MockUsage(input_tokens=10, output_tokens=20),
            total_cost_usd=0.001
        )

    async def interrupt(self):
        """Simula interrupção."""
        pass


class MockClaudeSDKClientWithTools(MockClaudeSDKClient):
    """Mock do SDK com suporte a tool use."""

    async def receive_response(self) -> AsyncGenerator:
        """Simula resposta com tool use."""
        # Primeira resposta: tool use
        yield MockAssistantMessage(
            content=[
                MockToolUseBlock(
                    id="tool_123",
                    name="bash",
                    input={"command": "ls -la"}
                )
            ]
        )

        # Segunda resposta: tool result
        yield MockUserMessage(
            content=[
                MockToolResultBlock(
                    tool_use_id="tool_123",
                    content="file1.txt\nfile2.txt"
                )
            ]
        )

        # Terceira resposta: texto final
        yield MockAssistantMessage(
            content=[MockTextBlock(text="Encontrei 2 arquivos.")]
        )

        # Resultado final
        yield MockResultMessage(
            usage=MockUsage(input_tokens=50, output_tokens=100),
            total_cost_usd=0.005
        )


class MockClaudeSDKClientError(MockClaudeSDKClient):
    """Mock do SDK que simula erro."""

    async def query(self, message: str, session_id: Optional[str] = None):
        """Simula erro ao enviar query."""
        raise Exception("Erro simulado de conexão")

    async def receive_response(self) -> AsyncGenerator:
        """Simula erro ao receber resposta."""
        raise Exception("Erro simulado ao receber resposta")
        yield  # Para satisfazer o tipo AsyncGenerator


def create_mock_client(client_type: str = "default"):
    """Factory para criar diferentes tipos de mock clients."""
    if client_type == "default":
        return MockClaudeSDKClient()
    elif client_type == "with_tools":
        return MockClaudeSDKClientWithTools()
    elif client_type == "error":
        return MockClaudeSDKClientError()
    else:
        raise ValueError(f"Unknown client type: {client_type}")