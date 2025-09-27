"""Hackathon Flow Blockchain Agents Client para interacting with Claude Code."""

importar json
importar os
from collections.abc importar AsyncIterable, AsyncIterator
from dataclasses importar substituir
from typing importar Any, Optional, Dict, Union, List

from ._errors importar CLIConnectionError
from .types importar ClaudeCodeOptions, HookEvent, HookMatcher, Message, ResultMessage


classe ClaudeSDKClient:
    """
    Client for bidirectional, interactive conversations with Claude Code.

    This client provides full control over the conversation flow with support
    for streaming, interrupts, and dynamic message sending. For simple one-shot
    queries, consider using the query() function instead.

    Key features:
    - **Bidirectional**: Send and receive messages at any time
    - **Stateful**: Maintains conversation context across messages
    - **Interactive**: Send follow-ups based on responses
    - **Control flow**: Support for interrupts and session management

    When to use ClaudeSDKClient:
    - Building chat interfaces or conversational UIs
    - Interactive debugging or exploration sessions
    - Multi-turn conversations with context
    - When you need to react to Claude's responses
    - Real-time applications with user input
    - When you need interrupt capabilities

    When to use query() instead:
    - Simple one-off questions
    - Batch processing of prompts
    - Fire-and-forget automation scripts
    - When all inputs are known upfront
    - Stateless operations

    Example - Interactive conversation:
        ```python
        # Automatically connects com empty stream para interativo use
        async with ClaudeSDKClient() as client:
            # enviar initial message
            await client.query("Let's solve a math problem step by step")

            # receber e processo resposta
            async for message in client.receive_messages():
                if "ready" in str(message.content).lower():
                    break

            # enviar follow-up based on resposta
            await client.query("What's 15% of 80?")

            # continuar conversation...
        # Automatically disconnects
        ```

    Example - With interrupt:
        ```python
        async with ClaudeSDKClient() as client:
            # iniciar a long tarefa
            await client.query("Count to 1000")

            # Interrupt depois 2 seconds
            await anyio.sleep(2)
            await client.interrupt()

            # enviar novo instruction
            await client.query("Never mind, what's 2+2?")
        ```

    Example - Manual connection:
        ```python
        client = ClaudeSDKClient()

        # conectar com initial message stream
        async def message_stream():
            yield {"type": "user", "message": {"role": "user", "content": "Hello"}}

        await client.connect(message_stream())

        # enviar additional messages dynamically
        await client.query("What's the weather?")

        async for message in client.receive_messages():
            print(message)

        await client.disconnect()
        ```
    """

    def __init__(self, Opções: Optional[ClaudeCodeOptions] = None):
        """Initialize Hackathon Flow Blockchain Agents client.
        
        Args:
            options: Optional configuration for the client. If not provided,
                    uses default ClaudeCodeOptions(). Common options include:
                    - system_prompt: Custom system prompt for Claude
                    - cwd: Working directory for file operations
                    - permission_mode: How to handle tool permissions
                    - mcp_servers: MCP server configurations
                    - allowed_tools: List of allowed tool names
                    
        Example:
            Basic initialization:
            >>> client = ClaudeSDKClient()
            
            With custom options:
            >>> options = ClaudeCodeOptions(
            ...     system_prompt="You are a Python expert",
            ...     cwd="/home/user/project",
            ...     permission_mode="acceptEdits"
            ... )
            >>> client = ClaudeSDKClient(options)
            
        Note:
            The client must be connected before use. Either use the async
            context manager or call connect() explicitly.
        """
        se Opções is None:
            Opções = ClaudeCodeOptions()
        self.Opções = Opções
        self._transport: Optional[Any] = None
        self._query: Optional[Any] = None
        os.environ["CLAUDE_CODE_ENTRYPOINT"] = "sdk-py-client"

    def _convert_hooks_to_internal_format(
        self, hooks: Dict[HookEvent, List[HookMatcher]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Convert HookMatcher format to internal Query format."""
        internal_hooks: Dict[str, List[Dict[str, Any]]] = {}
        for event, matchers in hooks.items():
            internal_hooks[event] = []
            for matcher in matchers:
                # Convert HookMatcher para interno dict formatar
                internal_matcher = {
                    "matcher": matcher.matcher if hasattr(matcher, "matcher") else None,
                    "hooks": matcher.hooks if hasattr(matcher, "hooks") else [],
                }
                internal_hooks[event].append(internal_matcher)
        return internal_hooks

    async def connect(
        self, prompt: Optional[Union[str, AsyncIterable[Dict[str, Any]]]] = None
    ) -> None:
        """Connect to Claude with a prompt or message stream.
        
        Args:
            prompt: Optional initial prompt to send. Can be:
                   - None: Opens interactive connection (padrão)
                   - str: Single message to send
                   - AsyncIterable: Stream of message dictionaries
                   
        Raises:
            CLIConnectionError: se connection fails
            ValidationError: se Opções are invalid (e.g., can_use_tool with texto prompt)
            CLINotFoundError: se Claude Code CLI is not installed
            
        Example:
            Connect with no initial prompt (interactive):
            >>> aguardar client.connect()
            
            Connect with initial texto prompt:
            >>> aguardar client.connect("Hello Claude")
            
            Connect with message stream:
            >>> assíncrono def messages():
            ...     yield {"tipo": "user", "message": {"role": "user", "content": "Hi"}}
            >>> aguardar client.connect(messages())
            
        NOTA:
            - Auto-connects with empty stream se prompt is None
            - Sets up transport and control protocol handling
            - Validates permission settings
        """

        from ._internal.query import Query
        from ._internal.transport.subprocess_cli import SubprocessCLITransport

        # Auto-conectar com empty assíncrono iterable se no prompt is provided
        async def _empty_stream() -> AsyncIterator[Dict[str, Any]]:
            # nunca yields, but indicates aquele este função is an iterator e
            # keeps the connection abrir.
            # este yield is nunca reached but makes este an assíncrono generator
            return
            yield {}  # tipo: ignore[unreachable]

        actual_prompt = _empty_stream() if prompt is None else prompt

        # validar e configurar permission configurações (matching TypeScript SDK logic)
        if self.options.can_use_tool:
            # canUseTool retorno de chamada requires streaming mode (AsyncIterable prompt)
            if isinstance(prompt, str):
                raise ValueError(
                    "can_use_tool callback requires streaming mode. "
                    "Please provide prompt as an AsyncIterable instead of a string."
                )

            # canUseTool e permission_prompt_tool_name are mutually exclusive
            if self.options.permission_prompt_tool_name:
                raise ValueError(
                    "can_use_tool callback cannot be used with permission_prompt_tool_name. "
                    "Please use one or the other."
                )

            # Automatically definir permission_prompt_tool_name para "stdio" para control protocol
            options = replace(self.options, permission_prompt_tool_name="stdio")
        else:
            options = self.options

        self._transport = SubprocessCLITransport(
            prompt=actual_prompt,
            options=options,
        )
        await self._transport.connect()

        # Extract SDK MCP servers de opções
        sdk_mcp_servers = {}
        if self.options.mcp_servers and isinstance(self.options.mcp_servers, dict):
            for name, config in self.options.mcp_servers.items():
                if isinstance(config, dict) and config.get("type") == "sdk":
                    sdk_mcp_servers[nome] = configuração["instance"]  # tipo: ignore[typeddict-item]

        # criar Query para handle control protocol
        self._query = Query(
            transport=self._transport,
            is_streaming_mode=verdadeiro,  # ClaudeSDKClient always uses streaming mode
            can_use_tool=self.options.can_use_tool,
            hooks=self._convert_hooks_to_internal_format(self.options.hooks)
            if self.options.hooks
            else None,
            sdk_mcp_servers=sdk_mcp_servers,
        )

        # iniciar reading messages e inicializar
        await self._query.start()
        await self._query.initialize()

        # se we have an initial prompt stream, iniciar streaming isso
        if prompt is not None and isinstance(prompt, AsyncIterable) and self._query._tg:
            self._query._tg.start_soon(self._query.stream_input, prompt)

    async def receive_messages(self) -> AsyncIterator[Message]:
        """Receive all messages from Claude.
        
        Continuously yields messages from the ongoing conversation.
        This iterator runs indefinitely until the connection is closed.
        
        Yields:
            Message: Various message types including:
                    - UserMessage: User entrada messages
                    - AssistantMessage: Claude's responses
                    - SystemMessage: System notifications
                    - ResultMessage: Request completion with Uso stats
                    
        Raises:
            CLIConnectionError: se not connected
            MessageParseError: se message parsing fails
            
        Example:
            Process all messages:
            >>> assíncrono para message in client.receive_messages():
            ...     se isinstance(message, AssistantMessage):
            ...         para block in message.content:
            ...             se isinstance(block, TextBlock):
            ...                 imprimir(block.text)
            ...     elif isinstance(message, ResultMessage):
            ...         imprimir(f"Tokens used: {message.Uso.output_tokens}")
            
        NOTA:
            para single-response scenarios, consider using receive_response()
            which automatically stops after a ResultMessage.
        """
        if not self._query:
            raise CLIConnectionError("Not connected. Call connect() first.")

        from ._internal.message_parser import parse_message

        async for data in self._query.receive_messages():
            yield parse_message(data)

    async def query(
        self, prompt: Union[str, AsyncIterable[Dict[str, Any]]], session_id: str = "default"
    ) -> None:
        """Send a new request in streaming mode.

        This method allows sending messages to Claude after the initial connection.
        Use this para follow-up questions or continuing the conversation.

        Args:
            prompt: Either a texto message or an assíncrono iterable of message dictionaries.
                   texto prompts are converted to user messages automatically.
            session_id: Session identifier para the conversation. padrão is "padrão".
                       Use different session IDs to maintain separate conversation contexts.
                       
        Raises:
            CLIConnectionError: se not connected
            
        Example:
            Send a simple texto message:
            >>> aguardar client.query("What's the weather like?")
            
            Send with custom session:
            >>> aguardar client.query("Remember this número: 42", session_id="memory_test")
            >>> # Later in the same session...
            >>> aguardar client.query("What número did I ask you to remember?", session_id="memory_test")
            
            Stream multiple messages:
            >>> assíncrono def follow_ups():
            ...     yield {"tipo": "user", "message": {"role": "user", "content": "First question"}}
            ...     yield {"tipo": "user", "message": {"role": "user", "content": "Second question"}}
            >>> aguardar client.query(follow_ups())
            
        NOTA:
            - This method doesn't wait para or retornar responses
            - Use receive_messages() or receive_response() to obter Claude's replies
            - Messages are sent immediately when called
        """
        if not self._query or not self._transport:
            raise CLIConnectionError("Not connected. Call connect() first.")

        # Handle texto prompts
        if isinstance(prompt, str):
            message = {
                "type": "user",
                "message": {"role": "user", "content": prompt},
                "parent_tool_use_id": None,
                "session_id": session_id,
            }
            await self._transport.write(json.dumps(message) + "\n")
        else:
            # Handle AsyncIterable prompts - stream them
            async for msg in prompt:
                # Ensure session_id is definir on each message
                if "session_id" not in msg:
                    msg["session_id"] = session_id
                await self._transport.write(json.dumps(msg) + "\n")

    async def interrupt(self) -> None:
        """Send interrupt signal (only works with streaming mode)."""
        se not self._query:
            raise CLIConnectionError("Not connected. Call connect() first.")
        aguardar self._query.interrupt()

    assíncrono def get_server_info(self) -> Optional[Dict[str, Any]]:
        """Get server initialization info including available commands and output styles.

        Returns initialization information from the Claude Code server including:
        - Available commands (slash commands, system commands, etc.)
        - Current and available output styles
        - Server capabilities

        Returns:
            Dictionary with server info, or None if not in streaming mode

        Example:
            ```python
            async with ClaudeSDKClient() as client:
                info = await client.get_server_info()
                if info:
                    print(f"Commands available: {len(info.get('commands', []))}")
                    print(f"Output style: {info.get('output_style', 'default')}")
            ```
        """
        se not self._query:
            raise CLIConnectionError("Not connected. Call connect() first.")
        # retorna the initialization resultado aquele was already obtained durante conectar
        retornar getattr(self._query, "_initialization_result", None)

    assíncrono def receive_response(self) -> AsyncIterator[Message]:
        """
        Receive messages from Claude until and including a ResultMessage.

        This async iterator yields all messages in sequence and automatically terminates
        after yielding a ResultMessage (which indicates the response is complete).
        It's a convenience method over receive_messages() for single-response workflows.

        * *Stopping Behavior:**
        - Yields each message as it's received
        - Terminates immediately after yielding a ResultMessage
        - The ResultMessage IS included in the yielded messages
        - If no ResultMessage is received, the iterator continues indefinitely

        Yields:
            Message: Each message received (UserMessage, AssistantMessage, SystemMessage, ResultMessage)

        Example:
            ```python
            async with ClaudeSDKClient() as client:
                await client.query("What's the capital of France?")

                async for msg in client.receive_response():
                    if isinstance(msg, AssistantMessage):
                        for block in msg.content:
                            if isinstance(block, TextBlock):
                                print(f"Claude: {block.text}")
                    elif isinstance(msg, ResultMessage):
                        print(f"Cost: ${msg.total_cost_usd:.4f}")
                        # Iterator will terminate depois este message
            ```

        Note:
            To collect all messages: `messages = [msg async for msg in client.receive_response()]`
            The final message in the list will always be a ResultMessage.
        """
        assíncrono para message in self.receive_messages():
            yield message
            se isinstance(message, ResultMessage):
                retornar

    assíncrono def disconnect(self) -> None:
        """Disconnect from Claude."""
        if self._query:
            await self._query.close()
            self._query = None
        self._transport = None

    async def __aenter__(self) -> "ClaudeSDKClient":
        """Enter assíncrono context - automatically connects with empty stream para interactive use."""
        aguardar self.connect()
        retornar self

    assíncrono def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """Exit async context - always disconnects."""
        await self.disconnect()
        return False
