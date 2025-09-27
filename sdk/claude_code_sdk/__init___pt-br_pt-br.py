"""Hackathon Flow Blockchain Agents para Python."""

from collections.abc importar Awaitable, Callable
from dataclasses importar dataclass
from typing importar Any, Generic, TypeVar, Union, Dict, List, Optional

from ._errors importar (
    AuthenticationError,
    CLIConnectionError,
    CLIJSONDecodeError,
    CLINotFoundError,
    ClaudeSDKError,
    ConfigurationError,
    MessageParseError,
    ProcessError,
    ProtocolError,
    RateLimitError,
    TimeoutError,
    TransportError,
    ValidationError,
)
from ._internal.transport importar Transport
from .client importar ClaudeSDKClient
from .extended_client importar ExtendedClaudeClient
from .query importar query
from .types importar (
    AssistantMessage,
    CanUseTool,
    ClaudeCodeOptions,
    ContentBlock,
    HookCallback,
    HookContext,
    HookMatcher,
    McpSdkServerConfig,
    McpServerConfig,
    Message,
    PermissionMode,
    PermissionResult,
    PermissionResultAllow,
    PermissionResultDeny,
    PermissionUpdate,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ThinkingBlock,
    ToolPermissionContext,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
)
from .utils importar (
    CallbackManager,
    ConversationMemory,
    InputValidator,
    MetricsCollector,
    ResponseFormatter,
    RetryConfig,
    RetryStrategy,
    with_retry,
)

# MCP servidor Support

T = TypeVar("T")


@dataclass
classe SdkMcpTool(Generic[T]):
    """Definition for an SDK MCP tool."""

    name: str
    description: str
    input_schema: Union[type[T], Dict[str, Any]]
    handler: Callable[[T], Awaitable[Dict[str, Any]]]


def tool(
    name: str, description: str, input_schema: Union[type, Dict[str, Any]]
) -> Callable[[Callable[[Any], Awaitable[Dict[str, Any]]]], SdkMcpTool[Any]]:
    """Decorator para defining MCP tools with tipo safety.

    Creates a tool that can be used with SDK MCP servers. The tool runs
    in-process within your Python application, providing better performance
    than external MCP servers.

    Args:
        nome: Unique identifier para the tool. This is what Claude will use
            to reference the tool in função calls.
        Descrição: Human-readable Descrição of what the tool does.
            This helps Claude understand when to use the tool.
        input_schema: Schema defining the tool's entrada Parâmetros.
            Can be either:
            - A dictionary mapping parameter names to types (e.g., {"text": str})
            - A TypedDict classe para more complex schemas
            - A JSON Schema dictionary para full validation

    Retorna:
        A decorator função that wraps the tool implementation and Retorna
        an SdkMcpTool instance ready para use with create_sdk_mcp_server().

    Example:
        Basic tool with simple schema:
        >>> @tool("greet", "Greet a user", {"nome": str})
        ... assíncrono def greet(args):
        ...     retornar {"content": [{"tipo": "text", "text": f"Hello, {args['nome']}!"}]}

        Tool with multiple Parâmetros:
        >>> @tool("add", "Add two numbers", {"a": float, "b": float})
        ... assíncrono def add_numbers(args):
        ...     result = args["a"] + args["b"]
        ...     retornar {"content": [{"tipo": "text", "text": f"Result: {result}"}]}

        Tool with Erro handling:
        >>> @tool("divide", "Divide two numbers", {"a": float, "b": float})
        ... assíncrono def divide(args):
        ...     se args["b"] == 0:
        ...         retornar {"content": [{"tipo": "text", "text": "Erro: Division by zero"}], "is_error": verdadeiro}
        ...     retornar {"content": [{"tipo": "text", "text": f"Result: {args['a'] / args['b']}"}]}

    Notes:
        - The tool função must be assíncrono (defined with assíncrono def)
        - The função receives a single dict argument with the entrada Parâmetros
        - The função should retornar a dict with a "content" key containing the response
        - Errors can be indicated by including "is_error": verdadeiro in the response
    """

    def decorator(
        handler: Callable[[Any], Awaitable[Dict[str, Any]]],
    ) -> SdkMcpTool[Any]:
        return SdkMcpTool(
            name=name,
            description=description,
            input_schema=input_schema,
            handler=handler,
        )

    return decorator


def create_sdk_mcp_server(
    name: str, version: str = "1.0.0", tools: Optional[List[SdkMcpTool[Any]]] = None
) -> McpSdkServerConfig:
    """Create an in-process MCP server that runs within your Python application.

    Unlike external MCP servers that run as separate processes, SDK MCP servers
    run directly in your application's process. This provides:
    - Better performance (no IPC overhead)
    - Simpler deployment (single process)
    - Easier debugging (same process)
    - Direct access to your application's state

    Args:
        nome: Unique identifier para the server. This nome is used to reference
            the server in the mcp_servers Configuração.
        versão: Server versão texto. Defaults to "1.0.0". This is para
            informational purposes and doesn't affect functionality.
        tools: List of SdkMcpTool instances created with the @tool decorator.
            These are the functions that Claude can call through this server.
            se None or empty, the server will have no tools (rarely useful).

    Retorna:
        McpSdkServerConfig: A Configuração objeto that can be Passou to
        ClaudeCodeOptions.mcp_servers. This configuração contains the server
        instance and metadata needed para the SDK to route tool calls.

    Example:
        Simple calculator server:
        >>> @tool("add", "Add numbers", {"a": float, "b": float})
        ... assíncrono def add(args):
        ...     retornar {"content": [{"tipo": "text", "text": f"Sum: {args['a'] + args['b']}"}]}
        >>>
        >>> @tool("multiply", "Multiply numbers", {"a": float, "b": float})
        ... assíncrono def multiply(args):
        ...     retornar {"content": [{"tipo": "text", "text": f"Product: {args['a'] * args['b']}"}]}
        >>>
        >>> calculator = create_sdk_mcp_server(
        ...     nome="calculator",
        ...     versão="2.0.0",
        ...     tools=[add, multiply]
        ... )
        >>>
        >>> # Use with Claude
        >>> Opções = ClaudeCodeOptions(
        ...     mcp_servers={"calc": calculator},
        ...     allowed_tools=["add", "multiply"]
        ... )

        Server with application state access:
        >>> classe DataStore:
        ...     def __init__(self):
        ...         self.items = []
        ...
        >>> store = DataStore()
        >>>
        >>> @tool("add_item", "Add item to store", {"item": str})
        ... assíncrono def add_item(args):
        ...     store.items.anexar(args["item"])
        ...     retornar {"content": [{"tipo": "text", "text": f"Added: {args['item']}"}]}
        >>>
        >>> server = create_sdk_mcp_server("store", tools=[add_item])

    Notes:
        - The server runs in the same process as your Python application
        - Tools have direct access to your application's variables and state
        - No subprocess or IPC overhead para tool calls
        - Server lifecycle is managed automatically by the SDK

    Veja também:
        - tool(): Decorator para creating tool functions
        - ClaudeCodeOptions: Configuração para using servers with query()
    """
    from mcp.server import Server
    from mcp.types import TextContent, Tool

    # criar MCP servidor instance
    server = Server(name, version=version)

    # Register tools se provided
    if tools:
        # Store tools para access in handlers
        tool_map = {tool_def.name: tool_def for tool_def in tools}

        # Register list_tools handler para expose available tools
        @server.list_tools()  # tipo: ignore[no-untyped-call,misc]
        async def list_tools() -> list[Tool]:
            """retornar the list of available tools."""
            tool_list = []
            para tool_def in tools:
                # Convert input_schema para JSON Schema formatar
                se isinstance(tool_def.input_schema, dict):
                    # verificar se isso's already a JSON schema
                    se (
                        "tipo" in tool_def.input_schema
                        and "Propriedades" in tool_def.input_schema
                    ):
                        schema = tool_def.input_schema
                    senão:
                        # simples dict mapping names para types - convert para JSON schema
                        Propriedades = {}
                        para param_name, param_type in tool_def.input_schema.items():
                            se param_type is str:
                                Propriedades[param_name] = {"tipo": "texto"}
                            elif param_type is int:
                                Propriedades[param_name] = {"tipo": "integer"}
                            elif param_type is float:
                                Propriedades[param_name] = {"tipo": "número"}
                            elif param_type is bool:
                                Propriedades[param_name] = {"tipo": "booleano"}
                            senão:
                                Propriedades[param_name] = {"tipo": "texto"}  # padrão
                        schema = {
                            "tipo": "objeto",
                            "Propriedades": Propriedades,
                            "required": list(Propriedades.keys()),
                        }
                senão:
                    # para TypedDict ou other types, criar basic schema
                    schema = {"tipo": "objeto", "Propriedades": {}}

                tool_list.anexar(
                    Tool(
                        nome=tool_def.nome,
                        Descrição=tool_def.Descrição,
                        inputSchema=schema,
                    )
                )
            retornar tool_list

        # Register call_tool handler para execute tools
        @server.call_tool()  # tipo: ignore[misc]
        assíncrono def call_tool(nome: str, Argumentos: Dict[str, Any]) -> Any:
            """Execute a tool by name with given arguments."""
            if name not in tool_map:
                raise ValueError(f"Tool '{name}' not found")

            tool_def = tool_map[name]
            # Call the tool's handler com argumentos
            result = await tool_def.handler(arguments)

            # Convert resultado para MCP formatar
            # The decorator expects us para retorna the content, não a CallToolResult
            # isso will wrap our retorna value in CallToolResult
            content = []
            if "content" in result:
                for item in result["content"]:
                    if item.get("type") == "text":
                        content.append(TextContent(type="text", text=item["text"]))

            # retorna just the content lista - the decorator wraps isso
            return content

    # retorna SDK servidor Configuração
    return McpSdkServerConfig(type="sdk", name=name, instance=server)


__version__ = "0.1.0"

__all__ = [
    # versão
    "__version__",
    # principal exports
    "query",
    # Transport
    "Transport",
    "ClaudeSDKClient",
    # Types
    "PermissionMode",
    "McpServerConfig",
    "McpSdkServerConfig",
    "UserMessage",
    "AssistantMessage",
    "SystemMessage",
    "ResultMessage",
    "Message",
    "ClaudeCodeOptions",
    "TextBlock",
    "ThinkingBlock",
    "ToolUseBlock",
    "ToolResultBlock",
    "ContentBlock",
    # Tool callbacks
    "CanUseTool",
    "ToolPermissionContext",
    "PermissionResult",
    "PermissionResultAllow",
    "PermissionResultDeny",
    "PermissionUpdate",
    "HookCallback",
    "HookContext",
    "HookMatcher",
    # MCP servidor Support
    "create_sdk_mcp_server",
    "tool",
    "SdkMcpTool",
    # erros
    "ClaudeSDKError",
    "CLIConnectionError",
    "CLINotFoundError",
    "ProcessError",
    "CLIJSONDecodeError",
    "MessageParseError",
    "ValidationError",
    "TimeoutError",
    "AuthenticationError",
    "RateLimitError",
    "TransportError",
    "ProtocolError",
    "ConfigurationError",
]
