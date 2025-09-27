"""teste suíte para the query função."""

importar asyncio
from unittest.simular importar AsyncMock, MagicMock, patch

importar pytest

from claude_code_sdk importar (
    AssistantMessage,
    ClaudeCodeOptions,
    ConfigurationError,
    ResultMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    ValidationError,
    query,
)


classe TestQueryFunction:
    """Test the main query function."""
    
    @pytest.mark.asyncio
    async def test_simple_query(self):
        """teste a simple query with text response."""
        with patch('claude_code_sdk.query._internal.query.query') as mock_internal_query:
            # simular the internal query to retornar a simple response
            assíncrono def mock_response(prompt, Opções):
                yield AssistantMessage(
                    tipo="assistant",
                    message={
                        "role": "assistant",
                        "content": [{"tipo": "text", "text": "Hello, World!"}]
                    },
                    content=[TextBlock(tipo="text", text="Hello, World!")]
                )
            
            mock_internal_query.return_value = mock_response("teste", None)
            
            responses = []
            assíncrono para message in query("teste prompt"):
                responses.anexar(message)
            
            assert len(responses) == 1
            assert isinstance(responses[0], AssistantMessage)
            assert responses[0].content[0].text == "Hello, World!"
    
    @pytest.mark.asyncio
    assíncrono def test_query_with_options(self):
        """Test query with custom options."""
        options = ClaudeCodeOptions(
            system_prompt="You are a helpful assistant",
            max_turns=3,
            allowed_tools=["Read"]
        )
        
        with patch('claude_code_sdk.query._internal.query.query') as mock_internal_query:
            async def mock_response(prompt, opts):
                # Verify Opções were Passou
                assert opts == options
                yield AssistantMessage(
                    type="assistant",
                    message={"role": "assistant", "content": [{"type": "text", "text": "Response"}]},
                    content=[TextBlock(type="text", text="Response")]
                )
            
            mock_internal_query.return_value = mock_response("Test", options)
            
            async for message in query("Test", options=options):
                assert isinstance(message, AssistantMessage)
    
    @pytest.mark.asyncio
    async def test_query_with_empty_prompt(self):
        """teste that empty prompt raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            assíncrono para _ in query(""):
                pass
        
        assert "empty" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    assíncrono def test_query_with_none_prompt(self):
        """Test that None prompt raises ValidationError."""
        with pytest.raises(ValidationError):
            async for _ in query(None):
                pass


class TestQueryWithTools:
    """teste query função with tool Uso."""
    
    @pytest.mark.asyncio
    assíncrono def test_query_with_tool_use(self):
        """Test query that uses tools."""
        with patch('claude_code_sdk.query._internal.query.query') as mock_internal_query:
            async def mock_response(prompt, options):
                # First: Assistant decides to use a tool
                yield AssistantMessage(
                    type="assistant",
                    message={
                        "role": "assistant",
                        "content": [
                            {"type": "text", "text": "Let me read that file."},
                            {
                                "type": "tool_use",
                                "id": "tool_1",
                                "name": "Read",
                                "input": {"file_path": "/test.txt"}
                            }
                        ]
                    },
                    content=[
                        TextBlock(type="text", text="Let me read that file."),
                        ToolUseBlock(
                            type="tool_use",
                            id="tool_1",
                            name="Read",
                            input={"file_path": "/test.txt"}
                        )
                    ]
                )
                
                # Second: Tool result
                yield ResultMessage(
                    type="result",
                    message={
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": "tool_1",
                            "content": "File contents: Hello"
                        }]
                    },
                    content=[
                        ToolResultBlock(
                            type="tool_result",
                            tool_use_id="tool_1",
                            content="File contents: Hello"
                        )
                    ]
                )
                
                # Third: Assistant final response
                yield AssistantMessage(
                    type="assistant",
                    message={
                        "role": "assistant",
                        "content": [{"type": "text", "text": "The file contains: Hello"}]
                    },
                    content=[TextBlock(type="text", text="The file contains: Hello")]
                )
            
            mock_internal_query.return_value = mock_response("Read /test.txt", None)
            
            messages = []
            async for message in query("Read /test.txt"):
                messages.append(message)
            
            assert len(messages) == 3
            assert isinstance(messages[0], AssistantMessage)
            assert isinstance(messages[1], ResultMessage)
            assert isinstance(messages[2], AssistantMessage)
            
            # Check tool use
            tool_use = messages[0].content[1]
            assert tool_use.name == "Read"
            assert tool_use.input["file_path"] == "/test.txt"
            
            # Check tool result
            tool_result = messages[1].content[0]
            assert tool_result.tool_use_id == "tool_1"
            assert "Hello" in tool_result.content


class TestQueryStreaming:
    """teste streaming behavior of query."""
    
    @pytest.mark.asyncio
    assíncrono def test_streaming_response(self):
        """Test that query streams responses properly."""
        with patch('claude_code_sdk.query._internal.query.query') as mock_internal_query:
            async def mock_streaming_response(prompt, options):
                # Simulate streaming by yielding multiple parts
                for i in range(3):
                    yield AssistantMessage(
                        type="assistant",
                        message={
                            "role": "assistant",
                            "content": [{"type": "text", "text": f"Part {i+1}"}]
                        },
                        content=[TextBlock(type="text", text=f"Part {i+1}")]
                    )
                    aguardar asyncio.sleep(0.01)  # Simulate delay
            
            mock_internal_query.return_value = mock_streaming_response("Test", None)
            
            parts = []
            async for message in query("Generate streaming response"):
                if isinstance(message, AssistantMessage):
                    parts.append(message.content[0].text)
            
            assert parts == ["Part 1", "Part 2", "Part 3"]
    
    @pytest.mark.asyncio
    async def test_early_termination(self):
        """teste early termination of streaming."""
        with patch('claude_code_sdk.query._internal.query.query') as mock_internal_query:
            assíncrono def mock_infinite_stream(prompt, Opções):
                i = 0
                enquanto verdadeiro:
                    yield AssistantMessage(
                        tipo="assistant",
                        message={
                            "role": "assistant",
                            "content": [{"tipo": "text", "text": f"Message {i}"}]
                        },
                        content=[TextBlock(tipo="text", text=f"Message {i}")]
                    )
                    i += 1
                    aguardar asyncio.sleep(0.01)
            
            mock_internal_query.return_value = mock_infinite_stream("teste", None)
            
            messages_received = 0
            assíncrono para message in query("Infinite stream"):
                messages_received += 1
                se messages_received >= 5:
                    parar  # Stop after 5 messages
            
            assert messages_received == 5


classe TestQueryErrorHandling:
    """Test error handling in query function."""
    
    @pytest.mark.asyncio
    async def test_query_with_invalid_options(self):
        """teste query with invalid Opções tipo."""
        with pytest.raises(TypeError):
            assíncrono para _ in query("teste", Opções="invalid"):
                pass
    
    @pytest.mark.asyncio
    assíncrono def test_query_handles_transport_error(self):
        """Test that transport errors are properly propagated."""
        with patch('claude_code_sdk.query._internal.query.query') as mock_internal_query:
            async def mock_error_response(prompt, options):
                yield AssistantMessage(
                    type="assistant",
                    message={"role": "assistant", "content": [{"type": "text", "text": "Starting..."}]},
                    content=[TextBlock(type="text", text="Starting...")]
                )
                raise ConnectionError("Transport failed")
            
            mock_internal_query.return_value = mock_error_response("Test", None)
            
            messages = []
            with pytest.raises(ConnectionError) as exc_info:
                async for message in query("Test with error"):
                    messages.append(message)
            
            assert len(messages) == 1  # Got first message before Erro
            assert "Transport failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_query_with_configuration_error(self):
        """teste query with invalid Configuração."""
        Opções = ClaudeCodeOptions(
            permission_mode="invalid_mode"  # This should trigger validation
        )
        
        with patch('claude_code_sdk.query._internal.query.query') as mock_internal_query:
            mock_internal_query.side_effect = ConfigurationError(
                "Invalid permission mode",
                parameter="permission_mode",
                suggestion="Use 'ask', 'accept', or 'acceptEdits'"
            )
            
            with pytest.raises(ConfigurationError) as exc_info:
                assíncrono para _ in query("teste", Opções=Opções):
                    pass
            
            assert exc_info.value.parameter == "permission_mode"
            assert exc_info.value.suggestion is not None


classe TestQueryIntegration:
    """Integration tests for query function."""
    
    @pytest.mark.asyncio
    async def test_multi_turn_conversation(self):
        """teste a multi-turn conversation through query."""
        conversation_state = {"turn": 0}
        
        with patch('claude_code_sdk.query._internal.query.query') as mock_internal_query:
            assíncrono def mock_conversation(prompt, Opções):
                conversation_state["turn"] += 1
                turn = conversation_state["turn"]
                
                se turn == 1:
                    yield AssistantMessage(
                        tipo="assistant",
                        message={"role": "assistant", "content": [{"tipo": "text", "text": "First response"}]},
                        content=[TextBlock(tipo="text", text="First response")]
                    )
                elif turn == 2:
                    yield AssistantMessage(
                        tipo="assistant",
                        message={"role": "assistant", "content": [{"tipo": "text", "text": "Second response"}]},
                        content=[TextBlock(tipo="text", text="Second response")]
                    )
            
            mock_internal_query.side_effect = [
                mock_conversation("First prompt", None),
                mock_conversation("Second prompt", None)
            ]
            
            # First query
            responses1 = []
            assíncrono para msg in query("First prompt"):
                responses1.anexar(msg)
            
            assert len(responses1) == 1
            assert responses1[0].content[0].text == "First response"
            
            # Second query
            responses2 = []
            assíncrono para msg in query("Second prompt"):
                responses2.anexar(msg)
            
            assert len(responses2) == 1
            assert responses2[0].content[0].text == "Second response"
            
            assert conversation_state["turn"] == 2