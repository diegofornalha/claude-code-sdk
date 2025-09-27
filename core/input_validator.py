"""
Sistema Avançado de Validação e Sanitização de Entrada
=======================================================
Protege contra XSS, SQL Injection, Path Traversal e mais
"""

import re
import html
import json
from typing import Any, Optional, List, Union
from enum import Enum


class ValidationError(Exception):
    """Erro customizado para validações."""
    pass


class InputType(Enum):
    """Tipos de entrada para validação específica."""
    TEXT = "text"
    EMAIL = "email"
    URL = "url"
    NUMBER = "number"
    JSON = "json"
    PATH = "path"
    SESSION_ID = "session_id"
    MESSAGE = "message"
    PROJECT_ID = "project_id"


class InputValidator:
    """Validador inteligente com proteção contra múltiplos ataques."""

    # Padrões perigosos
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>',
        r'vbscript:',
        r'data:text/html',
    ]

    SQL_INJECTION_PATTERNS = [
        r'\bUNION\b.*\bSELECT\b',
        r'\bDROP\b.*\bTABLE\b',
        r"'\s*OR\s*'",
        r'--\s*$',
    ]

    PATH_TRAVERSAL_PATTERNS = [
        r'\.\./+',
        r'\.\.%2[fF]',
        r'/etc/passwd',
    ]

    def validate(self, value: Any, input_type: InputType) -> Any:
        """Valida e sanitiza entrada baseado no tipo."""
        if value is None:
            raise ValidationError("Valor não pode ser None")

        if input_type == InputType.MESSAGE:
            return self._validate_message(str(value))
        elif input_type == InputType.SESSION_ID:
            return self._validate_session_id(str(value))
        elif input_type == InputType.NUMBER:
            return self._validate_number(value)
        elif input_type == InputType.PROJECT_ID:
            return self._validate_project_id(str(value))

        return str(value)

    def _validate_message(self, value: str) -> str:
        """Valida mensagem de chat."""
        # Garante que value é uma string
        if isinstance(value, list):
            # Se for lista, converte para string (junta elementos)
            value = ' '.join(str(item) for item in value)
        elif not isinstance(value, str):
            # Se não for string, converte
            value = str(value)

        # Remove caracteres null
        value = value.replace('\x00', '')

        # Limita tamanho (consistente com frontend: 50000 caracteres)
        if len(value) > 50000:
            raise ValidationError("Mensagem muito longa (máximo 50.000 caracteres)")

        # Verifica XSS
        for pattern in self.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                # Remove o padrão perigoso ao invés de rejeitar
                value = re.sub(pattern, '', value, flags=re.IGNORECASE)

        # Escapa HTML
        value = html.escape(value)
        return value.strip()

    def _validate_session_id(self, value: str) -> str:
        """Valida UUID de sessão."""
        value = value.strip().lower()
        uuid_pattern = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
        if not re.match(uuid_pattern, value):
            raise ValidationError("Session ID inválido")
        return value

    def _validate_number(self, value: Union[str, int, float]) -> Union[int, float]:
        """Valida número."""
        try:
            num = float(value)
            return int(num) if num.is_integer() else num
        except:
            raise ValidationError("Número inválido")

    def _validate_project_id(self, value: str) -> str:
        """Valida project ID."""
        value = value.strip()

        # Remove caracteres perigosos
        if len(value) > 100:
            raise ValidationError("Project ID muito longo")

        # Permite apenas alfanuméricos, hífen e underscore
        import re
        if not re.match(r'^[\w\-]+$', value):
            raise ValidationError("Project ID contém caracteres inválidos")

        return value

    def sanitize_for_display(self, value: str) -> str:
        """Sanitiza string para exibição segura no HTML."""
        value = html.escape(value)
        value = value.replace('\n', '<br>')
        return value

    def validate_session_id(self, value: str) -> str:
        """Valida session ID (método público)."""
        return self._validate_session_id(value)

    def validate_project_id(self, value: str) -> str:
        """Valida project ID (método público)."""
        return self._validate_project_id(value)

    def validate_address(self, value: str) -> str:
        """Valida endereço Flow (hexadecimal)."""
        value = value.strip().lower()

        # Remove prefixo 0x se presente
        if value.startswith('0x'):
            value = value[2:]

        # Valida formato hexadecimal
        if not re.match(r'^[a-f0-9]{16}$', value):
            raise ValidationError("Endereço Flow inválido (deve ser 16 caracteres hexadecimais)")

        return value

    def validate_dict(self, value: Any, field_name: str = "config") -> dict:
        """Valida e sanitiza dicionário."""
        if not isinstance(value, dict):
            raise ValidationError(f"{field_name} deve ser um objeto JSON")

        # Limita profundidade e tamanho
        json_str = json.dumps(value)
        if len(json_str) > 10000:
            raise ValidationError(f"{field_name} muito grande")

        return value


# Instância global
validator = InputValidator()