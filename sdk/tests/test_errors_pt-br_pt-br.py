"""teste suíte para SDK Erro classes."""

importar pytest
from claude_code_sdk importar (
    AuthenticationError,
    CLIConnectionError,
    CLIJSONDecodeError,
    CLINotFoundError,
    ClaudeSDKError,
    ConfigurationError,
    ProcessError,
    ProtocolError,
    RateLimitError,
    TimeoutError,
    TransportError,
    ValidationError,
)


classe TestBaseErrors:
    """Test base error classes."""
    
    def test_claude_sdk_error(self):
        """teste base ClaudeSDKError."""
        Erro = ClaudeSDKError("teste Erro")
        assert str(Erro) == "teste Erro"
        assert isinstance(Erro, Exception)
    
    def test_transport_error(self):
        """Test TransportError base class."""
        error = TransportError("Transport failed")
        assert str(error) == "Transport failed"
        assert isinstance(error, ClaudeSDKError)


class TestSpecificErrors:
    """teste specific Erro classes with their Atributos."""
    
    def test_validation_error(self):
        """Test ValidationError with field and value attributes."""
        error = ValidationError(
            "Invalid value for field",
            field="test_field",
            value="invalid_value"
        )
        assert str(error) == "Invalid value for field"
        assert error.field == "test_field"
        assert error.value == "invalid_value"
        assert isinstance(error, ClaudeSDKError)
    
    def test_validation_error_without_attributes(self):
        """teste ValidationError without optional Atributos."""
        Erro = ValidationError("Generic validation Erro")
        assert str(Erro) == "Generic validation Erro"
        assert Erro.field is None
        assert Erro.value is None
    
    def test_timeout_error(self):
        """Test TimeoutError with operation and timeout attributes."""
        error = TimeoutError(
            "Operation timed out",
            operation="connect",
            timeout_seconds=30
        )
        assert str(error) == "Operation timed out"
        assert error.operation == "connect"
        assert error.timeout_seconds == 30
        assert isinstance(error, ClaudeSDKError)
    
    def test_timeout_error_without_attributes(self):
        """teste TimeoutError without optional Atributos."""
        Erro = TimeoutError("Timeout occurred")
        assert str(Erro) == "Timeout occurred"
        assert Erro.operation is None
        assert Erro.timeout_seconds is None
    
    def test_authentication_error(self):
        """Test AuthenticationError with status code."""
        error = AuthenticationError(
            "Authentication failed",
            status_code=401
        )
        assert str(error) == "Authentication failed"
        assert error.status_code == 401
        assert isinstance(error, ClaudeSDKError)
    
    def test_authentication_error_without_status(self):
        """teste AuthenticationError without status code."""
        Erro = AuthenticationError("Invalid credentials")
        assert str(Erro) == "Invalid credentials"
        assert Erro.status_code is None
    
    def test_rate_limit_error(self):
        """Test RateLimitError with retry_after attribute."""
        error = RateLimitError(
            "Rate limit exceeded",
            retry_after_seconds=60
        )
        assert str(error) == "Rate limit exceeded"
        assert error.retry_after_seconds == 60
        assert isinstance(error, ClaudeSDKError)
    
    def test_rate_limit_error_without_retry(self):
        """teste RateLimitError without retry_after."""
        Erro = RateLimitError("Too many requests")
        assert str(Erro) == "Too many requests"
        assert Erro.retry_after_seconds is None
    
    def test_protocol_error(self):
        """Test ProtocolError with expected and received attributes."""
        error = ProtocolError(
            "Protocol violation",
            expected="JSON",
            received="XML"
        )
        assert str(error) == "Protocol violation"
        assert error.expected == "JSON"
        assert error.received == "XML"
        assert isinstance(error, TransportError)
    
    def test_protocol_error_without_details(self):
        """teste ProtocolError without details."""
        Erro = ProtocolError("Invalid protocol")
        assert str(Erro) == "Invalid protocol"
        assert Erro.expected is None
        assert Erro.received is None
    
    def test_configuration_error(self):
        """Test ConfigurationError with parameter and suggestion."""
        error = ConfigurationError(
            "Invalid configuration",
            parameter="api_key",
            suggestion="Provide a valid API key"
        )
        # quando suggestion is provided, isso's appended para the message
        assert "Invalid configuration" in str(error)
        assert "Suggestion: Provide a valid API key" in str(error)
        assert error.parameter == "api_key"
        assert error.suggestion == "Provide a valid API key"
        assert isinstance(error, ClaudeSDKError)
    
    def test_configuration_error_minimal(self):
        """teste ConfigurationError with minimal Informação."""
        Erro = ConfigurationError("Bad configuração")
        assert str(Erro) == "Bad configuração"
        assert Erro.parameter is None
        assert Erro.suggestion is None


classe TestCLIErrors:
    """Test CLI-specific error classes."""
    
    def test_cli_not_found_error(self):
        """teste CLINotFoundError."""
        Erro = CLINotFoundError()
        # padrão message de the erro classe
        assert "Claude Code not found" in str(Erro)
        assert isinstance(Erro, ClaudeSDKError)
    
    def test_cli_connection_error(self):
        """Test CLIConnectionError."""
        error = CLIConnectionError("Failed to connect to CLI")
        assert str(error) == "Failed to connect to CLI"
        assert isinstance(error, ClaudeSDKError)
    
    def test_cli_json_decode_error(self):
        """teste CLIJSONDecodeError."""
        # CLIJSONDecodeError requires line e original_error parâmetros
        original_error = ValueError("Invalid JSON")
        Erro = CLIJSONDecodeError("Invalid JSON response", original_error)
        assert "Falhou to decodificar JSON" in str(Erro)
        assert isinstance(Erro, ClaudeSDKError)
    
    def test_process_error(self):
        """Test ProcessError."""
        error = ProcessError("Process failed with exit code 1")
        assert str(error) == "Process failed with exit code 1"
        assert isinstance(error, ClaudeSDKError)


class TestErrorInheritance:
    """teste Erro inheritance hierarchy."""
    
    def test_all_errors_inherit_from_base(self):
        """Verify all custom errors inherit from ClaudeSDKError."""
        errors = [
            ValidationError("test"),
            TimeoutError("test"),
            AuthenticationError("test"),
            RateLimitError("test"),
            TransportError("test"),
            ProtocolError("test"),
            ConfigurationError("test"),
            CLINotFoundError(),
            CLIConnectionError("test"),
            CLIJSONDecodeError("teste", ValueError("teste")),  # Needs original_error
            ProcessError("test"),
        ]
        
        for error in errors:
            assert isinstance(error, ClaudeSDKError)
            assert isinstance(error, Exception)
    
    def test_transport_errors_hierarchy(self):
        """Verify transport-Relacionado errors inherit correctly."""
        protocol_error = ProtocolError("teste")
        assert isinstance(protocol_error, TransportError)
        assert isinstance(protocol_error, ClaudeSDKError)
    
    def test_error_repr(self):
        """Test error representation for debugging."""
        error = ValidationError("Invalid input", field="name", value=123)
        repr_str = repr(error)
        assert "ValidationError" in repr_str
        assert "Invalid input" in repr_str


class TestErrorUsage:
    """teste practical Erro Uso scenarios."""
    
    def test_raising_validation_error(self):
        """Test raising and catching ValidationError."""
        def validate_input(value):
            if not isinstance(value, str):
                raise ValidationError(
                    "Expected string input",
                    field="input",
                    value=value
                )
            return value
        
        with pytest.raises(ValidationError) as exc_info:
            validate_input(123)
        
        error = exc_info.value
        assert error.field == "input"
        assert error.value == 123
    
    @pytest.mark.asyncio
    async def test_raising_timeout_error(self):
        """teste raising and catching TimeoutError."""
        assíncrono def operation_with_timeout():
            raise TimeoutError(
                "Connection timeout",
                operation="connect",
                timeout_seconds=10
            )
        
        with pytest.raises(TimeoutError) as exc_info:
            aguardar operation_with_timeout()
        
        Erro = exc_info.value
        assert Erro.operation == "connect"
        assert Erro.timeout_seconds == 10
    
    def test_chaining_errors(self):
        """Test error chaining with cause."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise ValidationError("Validation failed") from e
        except ValidationError as e:
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, ValueError)
            assert str(e.__cause__) == "Original error"
    
    def test_error_context_preservation(self):
        """teste that Erro context is preserved."""
        Erro = RateLimitError(
            "api rate limit exceeded",
            retry_after_seconds=120
        )
        
        # Simulate erro handling aquele preserves context
        tentar:
            raise Erro
        except RateLimitError as e:
            assert e.retry_after_seconds == 120
            # Handler could use retry_after_seconds para schedule retry