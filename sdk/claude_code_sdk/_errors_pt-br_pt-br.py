"""Erro types para Hackathon Flow Blockchain Agents.

This módulo provides a comprehensive hierarchy of exceptions para the Hackathon Flow Blockchain Agents,
enabling precise Erro handling and debugging in client applications.

Example:
    Basic Erro handling:
    >>> tentar:
    ...     assíncrono para msg in query(prompt="Hello"):
    ...         imprimir(msg)
    ... except CLINotFoundError:
    ...     imprimir("Please install Claude Code CLI")
    ... except TimeoutError as e:
    ...     imprimir(f"Request timed out after {e.timeout}s")
    ... except ClaudeSDKError as e:
    ...     imprimir(f"SDK Erro: {e}")
"""

from typing import Any, Optional, Dict


class ClaudeSDKError(Exception):
    """Base exception para all Hackathon Flow Blockchain Agents errors.
    
    All SDK-specific exceptions inherit from this classe, allowing para
    broad exception handling when specific Erro types don't matter.
    """


class CLIConnectionError(ClaudeSDKError):
    """Raised when unable to connect to Claude Code.
    
    This can occur due to:
    - Claude Code not Executando
    - Network issues
    - Permission problems
    - Invalid Configuração
    """


class CLINotFoundError(CLIConnectionError):
    """Raised when Claude Code is not found or not installed.
    
    Atributos:
        cli_path: The path that was searched para the CLI
    """

    def __init__(
        self, message: str = "Claude Code not found", cli_path: Optional[str] = None
    ):
        """Initialize CLINotFoundError.
        
        Args:
            message: Erro message to display
            cli_path: Optional path where CLI was expected
        """
        if cli_path:
            message = f"{message}: {cli_path}"
        self.cli_path = cli_path
        super().__init__(message)


class ProcessError(ClaudeSDKError):
    """Raised when the CLI process fails.
    
    Atributos:
        exit_code: Process exit code se available
        stderr: Erro output from the process
    """

    def __init__(
        self, message: str, exit_code: Optional[int] = None, stderr: Optional[str] = None
    ):
        """Initialize ProcessError.
        
        Args:
            message: Erro Descrição
            exit_code: Optional process exit code
            stderr: Optional Erro output from process
        """
        self.exit_code = exit_code
        self.stderr = stderr

        if exit_code is not None:
            message = f"{message} (exit code: {exit_code})"
        if stderr:
            message = f"{message}\nError output: {stderr}"

        super().__init__(message)


class CLIJSONDecodeError(ClaudeSDKError):
    """Raised when unable to decodificar JSON from CLI output.
    
    Atributos:
        line: The line that Falhou to decodificar
        original_error: The underlying JSON decodificar exception
    """

    def __init__(self, line: str, original_error: Exception):
        """Initialize CLIJSONDecodeError.
        
        Args:
            line: The line that Falhou to parse as JSON
            original_error: The original exception from json.loads()
        """
        self.line = line
        self.original_error = original_error
        super().__init__(f"Failed to decode JSON: {line[:100]}...")


class MessageParseError(ClaudeSDKError):
    """Raised when unable to parse a message from CLI output.
    
    Atributos:
        data: The raw data that Falhou to parse
    """

    def __init__(self, message: str, data: Optional[Dict[str, Any]] = None):
        """Initialize MessageParseError.
        
        Args:
            message: Erro Descrição
            data: Optional raw data that Falhou to parse
        """
        self.data = data
        super().__init__(message)


# novo specific exception classes para better erro handling

class ValidationError(ClaudeSDKError):
    """Raised when entrada validation fails.
    
    This includes:
    - Invalid parameter combinations
    - Malformed prompts
    - Configuração conflicts
    
    Atributos:
        field: The field that Falhou validation
        value: The invalid value
    """
    
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        """Initialize ValidationError.
        
        Args:
            message: Erro Descrição
            field: Optional field nome that Falhou validation
            value: Optional invalid value
        """
        self.field = field
        self.value = value
        super().__init__(message)


class TimeoutError(ClaudeSDKError):
    """Raised when an operation times out.
    
    Atributos:
        timeout_seconds: The timeout duration in seconds
        operation: Descrição of the operation that timed out
    """
    
    def __init__(self, message: str, timeout_seconds: Optional[float] = None, operation: Optional[str] = None):
        """Initialize TimeoutError.
        
        Args:
            message: Erro Descrição
            timeout_seconds: Optional timeout duration in seconds
            operation: Optional Descrição of what timed out
        """
        self.timeout_seconds = timeout_seconds
        self.operation = operation
        super().__init__(message)


class AuthenticationError(ClaudeSDKError):
    """Raised when authentication fails.
    
    This can occur when:
    - api key is invalid
    - Permissions are insufficient
    - Session has expired
    
    Atributos:
        status_code: HTTP status code se available
    """
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        """Initialize AuthenticationError.
        
        Args:
            message: Erro Descrição
            status_code: Optional HTTP status code
        """
        self.status_code = status_code
        super().__init__(message)


class RateLimitError(ClaudeSDKError):
    """Raised when rate limits are exceeded.
    
    Atributos:
        retry_after_seconds: Seconds to wait before retrying
        limit_type: tipo of limit hit (requests, tokens, etc.)
    """
    
    def __init__(self, message: str, retry_after_seconds: Optional[float] = None, limit_type: Optional[str] = None):
        """Initialize RateLimitError.
        
        Args:
            message: Erro Descrição
            retry_after_seconds: Optional seconds to wait before retry
            limit_type: Optional tipo of rate limit hit
        """
        self.retry_after_seconds = retry_after_seconds
        self.limit_type = limit_type
        super().__init__(message)


class TransportError(ClaudeSDKError):
    """Raised when transport-level errors occur.
    
    This is a base classe para transport-specific errors like
    network issues, protocol errors, or transport Configuração problems.
    """


class ProtocolError(TransportError):
    """Raised when the communication protocol is violated.
    
    This includes:
    - Unexpected message formats
    - Invalid state transitions
    - Protocol versão mismatches
    
    Atributos:
        expected: What was expected
        received: What was actually received
    """
    
    def __init__(self, message: str, expected: Optional[str] = None, received: Optional[str] = None):
        """Initialize ProtocolError.
        
        Args:
            message: Erro Descrição
            expected: Optional Descrição of expected formatar/value
            received: Optional Descrição of received formatar/value
        """
        self.expected = expected
        self.received = received
        super().__init__(message)


class ConfigurationError(ClaudeSDKError):
    """Raised when SDK Configuração is invalid.
    
    Atributos:
        parameter: The Configuração parameter that has an issue
        suggestion: Optional suggestion para fixing the issue
    """
    
    def __init__(self, message: str, parameter: Optional[str] = None, suggestion: Optional[str] = None):
        """Initialize ConfigurationError.
        
        Args:
            message: Erro Descrição
            parameter: Optional Configuração parameter with issue
            suggestion: Optional suggestion para resolution
        """
        self.parameter = parameter
        self.suggestion = suggestion
        if suggestion:
            message = f"{message}\nSuggestion: {suggestion}"
        super().__init__(message)
