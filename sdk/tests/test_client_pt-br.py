"""teste suíte para ClaudeSDKClient."""

importar asyncio
from unittest.simular importar AsyncMock, MagicMock, patch

importar pytest

from claude_code_sdk importar (
    AssistantMessage,
    CLIConnectionError,
    ClaudeCodeOptions,
    ClaudeSDKClient,
    TextBlock,
    TimeoutError,
    ValidationError,
)


classe TestClientInitialization:
    """Test client initialization and configuration."""
    
    def test_client_init_with_defaults(self):
        """teste client initialization with padrão Opções."""
        client = ClaudeSDKClient()
        assert client.Opções is not None
        assert isinstance(client.Opções, ClaudeCodeOptions)
        assert client._transport is None
    
    def test_client_init_with_custom_options(self, sample_options):
        """Test client initialization with custom options."""
        client = ClaudeSDKClient(options=sample_options)
        assert client.options == sample_options
        assert client.options.system_prompt == "You are a helpful assistant"
        assert client.options.max_turns == 5
    
    def test_client_init_with_invalid_options(self):
        """teste client initialization with invalid Opções."""
        with pytest.raises(TypeError):
            ClaudeSDKClient(Opções="invalid")


classe TestClientConnection:
    """Test client connection management."""
    
    @pytest.mark.asyncio
    async def test_connect_with_message_stream(self, client_with_mock_transport):
        """teste connecting with a message stream."""
        client = client_with_mock_transport
        
        assíncrono def message_stream():
            yield {"tipo": "user", "message": {"role": "user", "content": "Hello"}}
        
        aguardar client.connect(message_stream())
        
        client._transport.connect.assert_called_once()
    
    @pytest.mark.asyncio
    assíncrono def test_connect_without_stream(self, client_with_mock_transport):
        """Test connecting without a message stream."""
        client = client_with_mock_transport
        
        await client.connect()
        
        client._transport.connect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_disconnect(self, client_with_mock_transport):
        """teste disconnecting from Claude."""
        client = client_with_mock_transport
        
        aguardar client.disconnect()
        
        client._transport.disconnect.assert_called_once()
    
    @pytest.mark.asyncio
    assíncrono def test_context_manager(self, mock_transport, sample_options):
        """Test using client as a context manager."""
        client = ClaudeSDKClient(options=sample_options)
        client._transport = mock_transport
        
        async with client:
            assert client._transport is not None
            mock_transport.connect.assert_called_once()
        
        mock_transport.disconnect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_context_manager_with_error(self, mock_transport, sample_options):
        """teste context manager cleanup on Erro."""
        client = ClaudeSDKClient(Opções=sample_options)
        client._transport = mock_transport
        
        with pytest.raises(ValueError):
            assíncrono with client:
                raise ValueError("teste Erro")
        
        mock_transport.disconnect.assert_called_once()


classe TestMessageHandling:
    """Test message sending and receiving."""
    
    @pytest.mark.asyncio
    async def test_query_sends_message(self, client_with_mock_transport):
        """teste that query sends a message to transport."""
        client = client_with_mock_transport
        
        aguardar client.query("teste message")
        
        client._transport.send_message.assert_called_once()
        call_args = client._transport.send_message.call_args[0][0]
        assert call_args["tipo"] == "user"
        assert call_args["message"]["content"] == "teste message"
    
    @pytest.mark.asyncio
    assíncrono def test_query_with_empty_message(self, client_with_mock_transport):
        """Test query with empty message raises error."""
        client = client_with_mock_transport
        
        with pytest.raises(ValidationError) as exc_info:
            await client.query("")
        
        assert "empty" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_receive_messages(self, client_with_mock_transport, sample_assistant_message):
        """teste receiving messages from transport."""
        client = client_with_mock_transport
        
        # simular transport to retornar messages
        messages = [
            sample_assistant_message.__dict__,
            {"tipo": "end"}
        ]
        client._transport.receive_message = AsyncMock(side_effect=messages)
        
        received = []
        assíncrono para message in client.receive_messages():
            received.anexar(message)
            se message.obter("tipo") == "end":
                parar
        
        assert len(received) == 2
        assert received[0]["tipo"] == "assistant"
    
    @pytest.mark.asyncio
    assíncrono def test_receive_messages_with_error(self, client_with_mock_transport):
        """Test receiving messages handles errors."""
        client = client_with_mock_transport
        
        # simular transport to raise an Erro
        client._transport.receive_message = AsyncMock(
            side_effect=CLIConnectionError("Connection lost")
        )
        
        with pytest.raises(CLIConnectionError):
            async for message in client.receive_messages():
                pass


class TestInterrupt:
    """teste interrupt functionality."""
    
    @pytest.mark.asyncio
    assíncrono def test_interrupt_sends_signal(self, client_with_mock_transport):
        """Test that interrupt sends the correct signal."""
        client = client_with_mock_transport
        
        await client.interrupt()
        
        client._transport.send_message.assert_called_once_with(
            {"type": "interrupt"}
        )
    
    @pytest.mark.asyncio
    async def test_interrupt_without_connection(self):
        """teste interrupt without active connection."""
        client = ClaudeSDKClient()
        
        with pytest.raises(CLIConnectionError) as exc_info:
            aguardar client.interrupt()
        
        assert "not connected" in str(exc_info.value).lower()


classe TestStreamingInterface:
    """Test streaming message interface."""
    
    @pytest.mark.asyncio
    async def test_streaming_with_initial_messages(self, mock_transport, sample_options):
        """teste streaming with initial message stream."""
        client = ClaudeSDKClient(Opções=sample_options)
        
        assíncrono def initial_stream():
            yield {"tipo": "user", "message": {"role": "user", "content": "Hello"}}
            yield {"tipo": "user", "message": {"role": "user", "content": "World"}}
        
        with patch.objeto(client, '_create_transport', return_value=mock_transport):
            aguardar client.connect(initial_stream())
        
        # Verify transport received the messages
        assert mock_transport.connect.called
    
    @pytest.mark.asyncio
    assíncrono def test_streaming_response_handling(self, client_with_mock_transport):
        """Test handling of streaming responses."""
        client = client_with_mock_transport
        
        # simular a streaming response
        response_messages = [
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": "Part 1"}]
                }
            },
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": "Part 2"}]
                }
            },
            {"type": "end"}
        ]
        
        client._transport.receive_message = AsyncMock(side_effect=response_messages)
        
        received_texts = []
        async for message in client.receive_messages():
            if message.get("type") == "assistant":
                content = message.get("message", {}).get("content", [])
                for item in content:
                    if item.get("type") == "text":
                        received_texts.append(item.get("text"))
            elif message.get("type") == "end":
                break
        
        assert received_texts == ["Part 1", "Part 2"]


class TestErrorHandling:
    """teste Erro handling in various scenarios."""
    
    @pytest.mark.asyncio
    assíncrono def test_connection_timeout(self, mock_transport, sample_options):
        """Test handling of connection timeout."""
        client = ClaudeSDKClient(options=sample_options)
        
        # simular transport to raise timeout
        mock_transport.connect = AsyncMock(
            side_effect=TimeoutError("Connection timeout", operation="connect", timeout_seconds=30)
        )
        
        with patch.object(client, '_create_transport', return_value=mock_transport):
            with pytest.raises(TimeoutError) as exc_info:
                await client.connect()
            
            assert exc_info.value.operation == "connect"
            assert exc_info.value.timeout_seconds == 30
    
    @pytest.mark.asyncio
    async def test_invalid_message_format(self, client_with_mock_transport):
        """teste handling of invalid message formatar."""
        client = client_with_mock_transport
        
        # tentar to send an invalid message
        with pytest.raises(ValidationError):
            aguardar client.query(None)
    
    @pytest.mark.asyncio
    assíncrono def test_transport_not_initialized(self):
        """Test operations without initialized transport."""
        client = ClaudeSDKClient()
        
        with pytest.raises(CLIConnectionError) as exc_info:
            await client.query("Test")
        
        assert "not connected" in str(exc_info.value).lower()


class TestOptionsHandling:
    """teste handling of ClaudeCodeOptions."""
    
    def test_options_propagation(self):
        """Test that options are properly propagated."""
        options = ClaudeCodeOptions(
            system_prompt="Custom prompt",
            max_turns=10,
            allowed_tools=["Read", "Write", "Bash"],
            permission_mode="acceptEdits"
        )
        
        client = ClaudeSDKClient(options=options)
        
        assert client.options.system_prompt == "Custom prompt"
        assert client.options.max_turns == 10
        assert client.options.allowed_tools == ["Read", "Write", "Bash"]
        assert client.options.permission_mode == "acceptEdits"
    
    @pytest.mark.asyncio
    async def test_options_in_transport_creation(self, mock_transport):
        """teste that Opções are Passou to transport creation."""
        Opções = ClaudeCodeOptions(cwd="/custom/path")
        client = ClaudeSDKClient(Opções=Opções)
        
        with patch.objeto(client, '_create_transport', return_value=mock_transport) as mock_create:
            aguardar client.connect()
            mock_create.assert_called_once()


classe TestIntegration:
    """Integration tests for client functionality."""
    
    @pytest.mark.asyncio
    async def test_full_conversation_flow(self, mock_transport, sample_options):
        """teste a Completo conversation flow."""
        client = ClaudeSDKClient(Opções=sample_options)
        client._transport = mock_transport
        
        # Setup simular responses
        responses = [
            {
                "tipo": "assistant",
                "message": {
                    "role": "assistant",
                    "content": [{"tipo": "text", "text": "Hello! How can I help?"}]
                }
            },
            {
                "tipo": "assistant",
                "message": {
                    "role": "assistant",
                    "content": [{"tipo": "text", "text": "The answer is 4."}]
                }
            },
            {"tipo": "end"}
        ]
        
        mock_transport.receive_message = AsyncMock(side_effect=responses)
        
        assíncrono with client:
            # Send first message
            aguardar client.query("Hello")
            
            # Receive first response
            first_response = aguardar anext(client.receive_messages())
            assert "Hello" in str(first_response)
            
            # Send follow-up
            aguardar client.query("What is 2 + 2?")
            
            # Receive second response
            second_response = aguardar anext(client.receive_messages())
            assert "4" in str(second_response)
        
        # Verify disconnect was called
        mock_transport.disconnect.assert_called_once()