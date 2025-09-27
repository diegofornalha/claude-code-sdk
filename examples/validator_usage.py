"""
Exemplos de uso do Input Validator
Demonstra como usar todas as funcionalidades de validação e sanitização
"""

from core.input_validator import (
    validator,
    InputSanitizer,
    ValidationError,
    sanitize_html,
    sanitize_for_frontend,
    get_security_headers,
    rate_limiter
)


def exemplo_1_validar_strings():
    """Exemplo 1: Validação de strings"""
    print("\n" + "=" * 70)
    print("EXEMPLO 1: Validação de Strings")
    print("=" * 70)

    # Texto normal
    try:
        texto = "Este é um texto normal e seguro"
        resultado = validator.validate_string(texto)
        print(f"✅ Texto válido: {resultado}")
    except ValidationError as e:
        print(f"❌ Erro: {e}")

    # Texto com HTML
    try:
        texto_html = "<script>alert('XSS')</script>Hello"
        resultado = validator.validate_string(texto_html, allow_html=False)
        print(f"✅ HTML sanitizado: {resultado}")
    except ValidationError as e:
        print(f"❌ Erro: {e}")

    # Texto muito longo
    try:
        texto_longo = "A" * 10001
        resultado = validator.validate_string(texto_longo, max_length=10000)
        print(f"✅ Texto: {resultado}")
    except ValidationError as e:
        print(f"❌ Texto muito longo bloqueado: {e}")


def exemplo_2_validar_mensagens():
    """Exemplo 2: Validação de mensagens de chat"""
    print("\n" + "=" * 70)
    print("EXEMPLO 2: Validação de Mensagens de Chat")
    print("=" * 70)

    mensagens = [
        "Olá, como você está?",
        "<script>alert('XSS')</script>",
        "' OR '1'='1' --",
        "; rm -rf /",
        "Mensagem normal com émojis 🎉",
    ]

    for msg in mensagens:
        try:
            resultado = validator.validate_message(msg)
            print(f"✅ Mensagem aceita: {msg[:30]}... → {resultado[:30]}...")
        except ValidationError as e:
            print(f"❌ Mensagem bloqueada: {msg[:30]}... → {e}")


def exemplo_3_validar_uuids():
    """Exemplo 3: Validação de UUIDs (Session IDs)"""
    print("\n" + "=" * 70)
    print("EXEMPLO 3: Validação de UUIDs")
    print("=" * 70)

    uuids = [
        "550e8400-e29b-41d4-a716-446655440000",  # UUID válido
        "not-a-uuid",
        "12345",
        "<script>alert('xss')</script>",
        "'; DROP TABLE sessions--",
    ]

    for uuid in uuids:
        try:
            resultado = validator.validate_session_id(uuid)
            print(f"✅ UUID válido: {uuid}")
        except ValidationError as e:
            print(f"❌ UUID inválido: {uuid} → {e}")


def exemplo_4_validar_enderecos():
    """Exemplo 4: Validação de endereços blockchain"""
    print("\n" + "=" * 70)
    print("EXEMPLO 4: Validação de Endereços Blockchain")
    print("=" * 70)

    enderecos = [
        "0x36395f9dde50ea27",  # Flow (16 chars)
        "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",  # Ethereum (40 chars)
        "not-an-address",
        "<script>alert('xss')</script>",
        "0xZZZZ",
    ]

    for addr in enderecos:
        try:
            resultado = validator.validate_address(addr)
            print(f"✅ Endereço válido: {addr} → {resultado}")
        except ValidationError as e:
            print(f"❌ Endereço inválido: {addr} → {e}")


def exemplo_5_validar_emails():
    """Exemplo 5: Validação de emails"""
    print("\n" + "=" * 70)
    print("EXEMPLO 5: Validação de Emails")
    print("=" * 70)

    emails = [
        "user@example.com",
        "valid.email+tag@domain.co.uk",
        "invalid-email",
        "user@",
        "@domain.com",
        "<script>alert('xss')</script>@test.com",
    ]

    for email in emails:
        try:
            resultado = validator.validate_email(email)
            print(f"✅ Email válido: {email} → {resultado}")
        except ValidationError as e:
            print(f"❌ Email inválido: {email} → {e}")


def exemplo_6_validar_numeros():
    """Exemplo 6: Validação de números"""
    print("\n" + "=" * 70)
    print("EXEMPLO 6: Validação de Números")
    print("=" * 70)

    # Validar inteiros
    print("\nInteiros:")
    valores_int = [42, "100", "not-a-number", 150, -10]
    for val in valores_int:
        try:
            resultado = validator.validate_integer(val, min_value=0, max_value=100)
            print(f"✅ Inteiro válido: {val} → {resultado}")
        except ValidationError as e:
            print(f"❌ Inteiro inválido: {val} → {e}")

    # Validar floats
    print("\nFloats:")
    valores_float = [3.14, "2.5", "not-a-number", 1.5, -0.5]
    for val in valores_float:
        try:
            resultado = validator.validate_float(val, min_value=0.0, max_value=10.0)
            print(f"✅ Float válido: {val} → {resultado}")
        except ValidationError as e:
            print(f"❌ Float inválido: {val} → {e}")


def exemplo_7_validar_listas_dicts():
    """Exemplo 7: Validação de listas e dicionários"""
    print("\n" + "=" * 70)
    print("EXEMPLO 7: Validação de Listas e Dicionários")
    print("=" * 70)

    # Validar listas
    print("\nListas:")
    listas = [
        [1, 2, 3],
        [],
        list(range(100)),
        "not-a-list",
    ]

    for lista in listas:
        try:
            resultado = validator.validate_list(lista, min_length=1, max_length=10)
            print(f"✅ Lista válida: {len(lista)} itens")
        except ValidationError as e:
            print(f"❌ Lista inválida: {e}")

    # Validar dicts
    print("\nDicionários:")
    dicts = [
        {"name": "John", "age": 30},
        {"name": "Jane"},
        {},
        "not-a-dict",
    ]

    for d in dicts:
        try:
            resultado = validator.validate_dict(d, required_keys=["name"])
            print(f"✅ Dict válido: {d}")
        except ValidationError as e:
            print(f"❌ Dict inválido: {e}")


def exemplo_8_sanitizacao():
    """Exemplo 8: Sanitização de conteúdo"""
    print("\n" + "=" * 70)
    print("EXEMPLO 8: Sanitização de Conteúdo")
    print("=" * 70)

    sanitizer = InputSanitizer()

    # Sanitizar HTML
    print("\nSanitizar HTML:")
    html_content = "<script>alert('XSS')</script><p>Texto normal</p><img src=x onerror=alert(1)>"
    safe_html = sanitizer.sanitize_html(html_content)
    print(f"Original: {html_content}")
    print(f"Sanitizado: {safe_html}")

    # Sanitizar SQL
    print("\nSanitizar SQL:")
    sql_content = "' OR '1'='1' -- DROP TABLE users"
    safe_sql = sanitizer.sanitize_sql(sql_content)
    print(f"Original: {sql_content}")
    print(f"Sanitizado: {safe_sql}")

    # Sanitizar comandos
    print("\nSanitizar Comandos:")
    cmd_content = "; rm -rf / && cat /etc/passwd"
    safe_cmd = sanitizer.sanitize_command(cmd_content)
    print(f"Original: {cmd_content}")
    print(f"Sanitizado: {safe_cmd}")

    # Sanitizar paths
    print("\nSanitizar Paths:")
    path_content = "../../etc/passwd"
    safe_path = sanitizer.sanitize_path(path_content)
    print(f"Original: {path_content}")
    print(f"Sanitizado: {safe_path}")

    # Sanitizar NoSQL
    print("\nSanitizar NoSQL:")
    nosql_content = '{"$ne": null, "$gt": ""}'
    safe_nosql = sanitizer.sanitize_nosql(nosql_content)
    print(f"Original: {nosql_content}")
    print(f"Sanitizado: {safe_nosql}")


def exemplo_9_detectar_padroes():
    """Exemplo 9: Detecção de padrões perigosos"""
    print("\n" + "=" * 70)
    print("EXEMPLO 9: Detecção de Padrões Perigosos")
    print("=" * 70)

    sanitizer = InputSanitizer()

    textos = [
        "Texto normal e seguro",
        "<script>alert('XSS')</script>",
        "' OR '1'='1' --",
        "; rm -rf /",
        "../../etc/passwd",
        '{"$ne": null}',
    ]

    for texto in textos:
        padroes = sanitizer.detect_dangerous_patterns(texto)
        if padroes:
            print(f"⚠️  Padrões perigosos em: {texto[:40]}")
            print(f"   Padrões: {padroes[:2]}")
        else:
            print(f"✅ Texto seguro: {texto[:40]}")


def exemplo_10_rate_limiting():
    """Exemplo 10: Rate Limiting"""
    print("\n" + "=" * 70)
    print("EXEMPLO 10: Rate Limiting")
    print("=" * 70)

    # Simular requisições de um IP
    ip = "192.168.1.1"

    print(f"\nTestando rate limit para IP: {ip}")
    print(f"Limite: 60 requisições por minuto")

    # Simular 65 requisições
    for i in range(1, 66):
        allowed = rate_limiter.check_rate_limit(ip)
        if i <= 60:
            if allowed:
                print(f"✅ Requisição {i}: PERMITIDA")
            else:
                print(f"❌ Requisição {i}: BLOQUEADA (inesperado)")
        else:
            if not allowed:
                print(f"🛑 Requisição {i}: BLOQUEADA (esperado)")
            else:
                print(f"⚠️  Requisição {i}: PERMITIDA (inesperado)")

        # Parar após primeiro bloqueio
        if i > 60 and not allowed:
            break


def exemplo_11_security_headers():
    """Exemplo 11: Headers de Segurança"""
    print("\n" + "=" * 70)
    print("EXEMPLO 11: Headers de Segurança")
    print("=" * 70)

    headers = get_security_headers()

    print("\nHeaders de segurança configurados:")
    for header, value in headers.items():
        print(f"• {header}")
        print(f"  {value[:80]}...")
        print()


def exemplo_12_sanitizacao_frontend():
    """Exemplo 12: Sanitização para Frontend"""
    print("\n" + "=" * 70)
    print("EXEMPLO 12: Sanitização para Frontend")
    print("=" * 70)

    conteudos = [
        "Texto normal",
        "<script>alert('XSS')</script>",
        "Texto com 'aspas' e \"aspas duplas\"",
        "Texto com\nquebras\nde linha",
        '<img src=x onerror="alert(1)">',
    ]

    for conteudo in conteudos:
        safe = sanitize_for_frontend(conteudo)
        print(f"\nOriginal: {conteudo}")
        print(f"Sanitizado: {safe}")


def main():
    """Função principal - executa todos os exemplos"""
    print("\n" + "=" * 70)
    print("🛡️  EXEMPLOS DE USO - INPUT VALIDATOR")
    print("=" * 70)

    try:
        exemplo_1_validar_strings()
        exemplo_2_validar_mensagens()
        exemplo_3_validar_uuids()
        exemplo_4_validar_enderecos()
        exemplo_5_validar_emails()
        exemplo_6_validar_numeros()
        exemplo_7_validar_listas_dicts()
        exemplo_8_sanitizacao()
        exemplo_9_detectar_padroes()
        exemplo_10_rate_limiting()
        exemplo_11_security_headers()
        exemplo_12_sanitizacao_frontend()

        print("\n" + "=" * 70)
        print("✅ Todos os exemplos executados com sucesso!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Erro ao executar exemplos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()