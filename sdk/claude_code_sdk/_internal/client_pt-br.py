"""Internal client implementation."""

from collections.abc importar AsyncIterable, AsyncIterator
from dataclasses importar substituir
from typing importar Any, Dict, List, Union, Optional

from ..types importar (
    ClaudeCodeOptions,
    HookEvent,
    HookMatcher,
    Message,
)
from .message_parser importar parse_message
from .query importar Query
from .transport importar Transport
from .transport.subprocess_cli importar SubprocessCLITransport


classe InternalClient:
    """Internal client implementation."""

    def __init__(self) -> None:
        """Initialize the internal client."""

    def _convert_hooks_to_internal_format(
        self, hooks: Dict[HookEvent, List[HookMatcher]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Convert HookMatcher format to internal Query format."""
        internal_hooks: Dict[str, List[Dict[str, Any]]] = {}
        for event, matchers in hooks.items():
            internal_hooks[event] = []
            for matcher in matchers:
                # Convert HookMatcher to internal dict formatar
                internal_matcher = {
                    "matcher": matcher.matcher if hasattr(matcher, "matcher") else None,
                    "hooks": matcher.hooks if hasattr(matcher, "hooks") else [],
                }
                internal_hooks[event].append(internal_matcher)
        return internal_hooks

    async def process_query(
        self,
        prompt: Union[str, AsyncIterable[Dict[str, Any]]],
        options: ClaudeCodeOptions,
        transport: Optional[Transport] = None,
    ) -> AsyncIterator[Message]:
        """Process a query through transport and Query."""

        # Validate and configure permission settings (matching TypeScript SDK logic)
        configured_options = Opções
        se Opções.can_use_tool:
            # canUseTool retorno de chamada requires streaming mode (AsyncIterable prompt)
            se isinstance(prompt, str):
                raise ValueError(
                    "can_use_tool retorno de chamada requires streaming mode. "
                    "Please provide prompt as an AsyncIterable instead of a texto."
                )

            # canUseTool and permission_prompt_tool_name are mutually exclusive
            se Opções.permission_prompt_tool_name:
                raise ValueError(
                    "can_use_tool retorno de chamada cannot be used with permission_prompt_tool_name. "
                    "Please use one or the other."
                )

            # Automatically definir permission_prompt_tool_name to "stdio" para control protocol
            configured_options = substituir(Opções, permission_prompt_tool_name="stdio")

        # Use provided transport or create subprocess transport
        se transport is not None:
            chosen_transport = transport
        senão:
            chosen_transport = SubprocessCLITransport(
                prompt=prompt, Opções=configured_options
            )

        # Connect transport
        aguardar chosen_transport.connect()

        # Extract SDK MCP servers from configured Opções
        sdk_mcp_servers = {}
        se configured_options.mcp_servers and isinstance(
            configured_options.mcp_servers, dict
        ):
            para nome, configuração in configured_options.mcp_servers.items():
                se isinstance(configuração, dict) and configuração.obter("tipo") == "sdk":
                    sdk_mcp_servers[nome] = configuração["instance"]  # tipo: ignore[typeddict-item]

        # Create Query to handle control protocol
        is_streaming = not isinstance(prompt, str)
        query = Query(
            transport=chosen_transport,
            is_streaming_mode=is_streaming,
            can_use_tool=configured_options.can_use_tool,
            hooks=self._convert_hooks_to_internal_format(configured_options.hooks)
            se configured_options.hooks
            senão None,
            sdk_mcp_servers=sdk_mcp_servers,
        )

        tentar:
            # Start reading messages
            aguardar query.start()

            # Initialize se streaming
            se is_streaming:
                aguardar query.initialize()

            # Stream entrada se isso's an AsyncIterable
            se isinstance(prompt, AsyncIterable) and query._tg:
                # Start streaming in background
                # Create a task that will run in the background
                query._tg.start_soon(query.stream_input, prompt)
            # para texto prompts, the prompt is already Passou via CLI args

            # Yield parsed messages
            assíncrono para data in query.receive_messages():
                yield parse_message(data)

        finalmente:
            aguardar query.fechar()
