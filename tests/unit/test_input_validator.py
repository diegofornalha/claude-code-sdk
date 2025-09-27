"""
Testes unitários para InputValidator.
Valida proteção contra XSS, SQL Injection, Path Traversal.
"""

import pytest
from core.input_validator import InputValidator, ValidationError, InputType


@pytest.mark.unit
class TestInputValidator:
    """Suite de testes para InputValidator."""

    def test_validate_valid_message(self, input_validator):
        """Testa validação de mensagem válida."""
        message = "Esta é uma mensagem válida"
        result = input_validator.validate(message, InputType.MESSAGE)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_validate_message_too_long(self, input_validator):
        """Testa rejeição de mensagem muito longa."""
        long_message = "a" * 50001
        with pytest.raises(ValidationError) as exc:
            input_validator.validate(long_message, InputType.MESSAGE)
        assert "muito longa" in str(exc.value).lower()

    @pytest.mark.security
    def test_xss_protection_script_tag(self, input_validator):
        """Testa proteção contra XSS com script tag."""
        malicious = "<script>alert('XSS')</script>"
        result = input_validator.validate(malicious, InputType.MESSAGE)
        # Deve remover ou escapar o script
        assert "<script>" not in result.lower()

    @pytest.mark.security
    def test_xss_protection_javascript_protocol(self, input_validator):
        """Testa proteção contra javascript: protocol."""
        malicious = "javascript:alert(1)"
        result = input_validator.validate(malicious, InputType.MESSAGE)
        assert "javascript:" not in result.lower()

    @pytest.mark.security
    def test_xss_protection_iframe(self, input_validator):
        """Testa proteção contra iframe malicioso."""
        malicious = "<iframe src='evil.com'></iframe>"
        result = input_validator.validate(malicious, InputType.MESSAGE)
        assert "<iframe" not in result.lower()

    @pytest.mark.security
    def test_html_escape(self, input_validator):
        """Testa escape de caracteres HTML."""
        text = "Test <b>bold</b> & 'quotes'"
        result = input_validator.validate(text, InputType.MESSAGE)
        # Deve escapar HTML
        assert "&lt;" in result or "<b>" not in result

    def test_validate_valid_session_id(self, input_validator, valid_session_id):
        """Testa validação de UUID válido."""
        result = input_validator.validate(valid_session_id, InputType.SESSION_ID)
        assert result == valid_session_id.lower()

    def test_validate_invalid_session_id(self, input_validator):
        """Testa rejeição de UUID inválido."""
        invalid_ids = [
            "invalid-uuid",
            "12345",
            "not-a-uuid-at-all",
            "",
            "12345678-1234-1234-1234-12345678ZZZZ"  # contém caracteres inválidos
        ]
        for invalid_id in invalid_ids:
            with pytest.raises(ValidationError):
                input_validator.validate(invalid_id, InputType.SESSION_ID)

    def test_validate_valid_project_id(self, input_validator):
        """Testa validação de project ID válido."""
        valid_ids = ["neo4j-agent", "my_project", "test123", "project-name_123"]
        for project_id in valid_ids:
            result = input_validator.validate(project_id, InputType.PROJECT_ID)
            assert result == project_id.strip()

    def test_validate_invalid_project_id(self, input_validator):
        """Testa rejeição de project ID inválido."""
        invalid_ids = [
            "project with spaces",
            "project/with/slashes",
            "project<script>",
            "a" * 101,  # muito longo
        ]
        for invalid_id in invalid_ids:
            with pytest.raises(ValidationError):
                input_validator.validate(invalid_id, InputType.PROJECT_ID)

    def test_validate_number_int(self, input_validator):
        """Testa validação de número inteiro."""
        result = input_validator.validate("42", InputType.NUMBER)
        assert result == 42
        assert isinstance(result, int)

    def test_validate_number_float(self, input_validator):
        """Testa validação de número decimal."""
        result = input_validator.validate("3.14", InputType.NUMBER)
        assert result == 3.14
        assert isinstance(result, float)

    def test_validate_invalid_number(self, input_validator):
        """Testa rejeição de número inválido."""
        with pytest.raises(ValidationError):
            input_validator.validate("not-a-number", InputType.NUMBER)

    def test_validate_none_value(self, input_validator):
        """Testa rejeição de valor None."""
        with pytest.raises(ValidationError) as exc:
            input_validator.validate(None, InputType.MESSAGE)
        assert "None" in str(exc.value)

    def test_sanitize_for_display(self, input_validator):
        """Testa sanitização para exibição HTML."""
        text = "Line 1\nLine 2\nLine 3"
        result = input_validator.sanitize_for_display(text)
        assert "<br>" in result

    def test_validate_flow_address_valid(self, input_validator):
        """Testa validação de endereço Flow válido."""
        valid_addresses = [
            "0x36395f9dde50ea27",
            "36395f9dde50ea27",
            "0X36395F9DDE50EA27"
        ]
        for addr in valid_addresses:
            result = input_validator.validate_address(addr)
            assert len(result) == 16
            assert result.islower()

    def test_validate_flow_address_invalid(self, input_validator):
        """Testa rejeição de endereço Flow inválido."""
        invalid_addresses = [
            "invalid",
            "0x123",
            "ZZZZZZZZZZZZZZZZ",
            "0x36395f9dde50ea2",  # muito curto
            "0x36395f9dde50ea277",  # muito longo
        ]
        for addr in invalid_addresses:
            with pytest.raises(ValidationError):
                input_validator.validate_address(addr)

    def test_validate_dict_valid(self, input_validator):
        """Testa validação de dicionário válido."""
        valid_dict = {"key": "value", "number": 42}
        result = input_validator.validate_dict(valid_dict)
        assert result == valid_dict

    def test_validate_dict_invalid_type(self, input_validator):
        """Testa rejeição de tipo não-dict."""
        with pytest.raises(ValidationError):
            input_validator.validate_dict("not-a-dict")

    def test_validate_dict_too_large(self, input_validator):
        """Testa rejeição de dict muito grande."""
        large_dict = {f"key{i}": "value" * 100 for i in range(100)}
        with pytest.raises(ValidationError):
            input_validator.validate_dict(large_dict)

    @pytest.mark.security
    @pytest.mark.parametrize("malicious_input", [
        "<script>alert('XSS')</script>",
        "'; DROP TABLE users; --",
        "../../../etc/passwd",
        "javascript:alert(1)",
        "<iframe src='evil.com'></iframe>",
        "' OR '1'='1"
    ])
    def test_malicious_inputs_blocked(self, input_validator, malicious_input):
        """Testa bloqueio de múltiplas entradas maliciosas."""
        # Não deve lançar exceção, mas deve sanitizar
        result = input_validator.validate(malicious_input, InputType.MESSAGE)
        # Verifica que foi sanitizado de alguma forma
        assert result != malicious_input or len(result) == 0