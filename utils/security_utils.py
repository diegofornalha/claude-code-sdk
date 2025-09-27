"""
Utilitários de segurança
"""
import html
import re

def sanitize_for_frontend(content: str) -> str:
    """
    Sanitiza conteúdo para envio seguro ao frontend.
    Remove ou escapa caracteres potencialmente perigosos.
    """
    if not content:
        return content

    # Escapar HTML
    content = html.escape(content)

    # Remover caracteres de controle
    content = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', content)

    return content

def get_security_headers():
    """Retorna headers de segurança para as respostas."""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=()"
    }

def get_cache_headers(file_type: str = "default"):
    """
    Retorna headers de cache otimizados por tipo de arquivo.
    """
    cache_config = {
        "static": "public, max-age=31536000, immutable",  # 1 ano para assets estáticos
        "html": "no-cache, must-revalidate",
        "api": "no-store",
        "default": "no-cache"
    }
    return {"Cache-Control": cache_config.get(file_type, cache_config["default"])}