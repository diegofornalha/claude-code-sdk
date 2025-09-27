"""
Sistema de Configuração Dinâmica
================================
Gerencia configurações em tempo de execução com hot reload
"""

import json
import os
from typing import Any, Dict, Optional
from pathlib import Path
from datetime import datetime
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ConfigFileHandler(FileSystemEventHandler):
    """Monitor de mudanças no arquivo de configuração."""

    def __init__(self, config_manager):
        self.config_manager = config_manager

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('config.json'):
            print(f"🔄 Config file modified: {event.src_path}")
            self.config_manager.reload()


class ConfigManager:
    """Gerenciador de configuração com hot reload."""

    def __init__(self, config_path: str = None):
        """Inicializa o gerenciador de configuração."""
        self.config_path = config_path or os.getenv('CONFIG_PATH', 'api/config/config.json')
        self.config: Dict[str, Any] = {}
        self.defaults = self._get_defaults()
        self.lock = threading.RLock()
        self.observer = None

        # Carrega configuração inicial
        self.load()

        # Inicia monitoramento de mudanças
        self.start_watching()

    def _get_defaults(self) -> Dict[str, Any]:
        """Retorna configurações padrão."""
        return {
            "api": {
                "host": "0.0.0.0",
                "port": 8888,
                "debug": False,
                "cors_origins": ["http://localhost:3333", "http://localhost:3000"],
                "max_request_size": 10485760,  # 10MB
                "rate_limit": {
                    "enabled": True,
                    "requests_per_minute": 60,
                    "burst_size": 10
                }
            },
            "claude": {
                "model": "claude-3-5-sonnet-latest",
                "max_tokens": 4096,
                "temperature": 0.7,
                "timeout": 120,
                "retry_attempts": 3,
                "retry_delay": 1
            },
            "neo4j": {
                "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                "user": os.getenv("NEO4J_USER", "neo4j"),
                "password": os.getenv("NEO4J_PASSWORD", "password"),
                "database": "neo4j",
                "connection_pool_size": 50,
                "max_connection_lifetime": 3600,
                "connection_timeout": 30
            },
            "session": {
                "timeout": 3600,  # 1 hour
                "max_history": 100,
                "cleanup_interval": 300,  # 5 minutes
                "storage_path": "api/sessions"
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "api/logs/app.log",
                "max_size": 10485760,  # 10MB
                "backup_count": 5,
                "enable_telemetry": True
            },
            "security": {
                "enable_validation": True,
                "max_message_length": 4000,
                "allowed_origins": ["http://localhost:3333"],
                "enable_rate_limiting": True,
                "enable_csrf_protection": False,
                "session_secret": os.getenv("SESSION_SECRET", "change-me-in-production")
            },
            "features": {
                "enable_streaming": True,
                "enable_memory": True,
                "enable_analytics": True,
                "enable_error_tracking": True,
                "enable_auto_save": True
            },
            "performance": {
                "enable_caching": True,
                "cache_ttl": 300,
                "enable_compression": True,
                "worker_threads": 4,
                "queue_size": 1000
            }
        }

    def load(self) -> None:
        """Carrega configuração do arquivo."""
        try:
            with self.lock:
                if os.path.exists(self.config_path):
                    with open(self.config_path, 'r') as f:
                        loaded_config = json.load(f)
                        # Merge com defaults
                        self.config = self._deep_merge(self.defaults.copy(), loaded_config)
                        print(f"✅ Configuration loaded from {self.config_path}")
                else:
                    # Usa defaults e cria arquivo
                    self.config = self.defaults.copy()
                    self.save()
                    print(f"📝 Default configuration created at {self.config_path}")
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            self.config = self.defaults.copy()

    def save(self) -> None:
        """Salva configuração atual no arquivo."""
        try:
            with self.lock:
                # Cria diretório se não existir
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

                # Salva com indentação para legibilidade
                with open(self.config_path, 'w') as f:
                    json.dump(self.config, f, indent=2)

                print(f"💾 Configuration saved to {self.config_path}")
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")

    def reload(self) -> None:
        """Recarrega configuração do arquivo."""
        print("🔄 Reloading configuration...")
        old_config = self.config.copy()
        self.load()

        # Detecta mudanças
        changes = self._detect_changes(old_config, self.config)
        if changes:
            print(f"📝 Configuration changes detected: {changes}")
            # Aqui podemos emitir eventos para componentes interessados

    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém valor de configuração usando notação de ponto.

        Exemplo: config.get('api.port', 8080)
        """
        with self.lock:
            keys = key.split('.')
            value = self.config

            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default

            return value

    def set(self, key: str, value: Any, persist: bool = True) -> None:
        """
        Define valor de configuração usando notação de ponto.

        Args:
            key: Chave em notação de ponto
            value: Valor a definir
            persist: Se deve salvar no arquivo
        """
        with self.lock:
            keys = key.split('.')
            config = self.config

            # Navega até a chave pai
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]

            # Define o valor
            old_value = config.get(keys[-1])
            config[keys[-1]] = value

            print(f"⚙️ Config updated: {key} = {value} (was: {old_value})")

            # Persiste se solicitado
            if persist:
                self.save()

    def update(self, updates: Dict[str, Any], persist: bool = True) -> None:
        """Atualiza múltiplas configurações de uma vez."""
        with self.lock:
            for key, value in updates.items():
                self.set(key, value, persist=False)

            if persist:
                self.save()

    def reset(self, key: Optional[str] = None) -> None:
        """Reseta configuração para valores padrão."""
        with self.lock:
            if key:
                # Reseta chave específica
                default_value = self.get_from_dict(self.defaults, key)
                if default_value is not None:
                    self.set(key, default_value)
            else:
                # Reseta tudo
                self.config = self.defaults.copy()
                self.save()
                print("🔄 Configuration reset to defaults")

    def start_watching(self) -> None:
        """Inicia monitoramento de mudanças no arquivo."""
        try:
            if self.observer:
                self.observer.stop()

            self.observer = Observer()
            event_handler = ConfigFileHandler(self)

            # Monitora o diretório do arquivo
            watch_dir = os.path.dirname(os.path.abspath(self.config_path))
            self.observer.schedule(event_handler, watch_dir, recursive=False)
            self.observer.start()

            print(f"👁️ Watching configuration file for changes")
        except Exception as e:
            print(f"❌ Could not start config file watcher: {e}")

    def stop_watching(self) -> None:
        """Para o monitoramento de mudanças."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            print("⏹️ Stopped watching configuration file")

    def _deep_merge(self, dict1: dict, dict2: dict) -> dict:
        """Merge profundo de dois dicionários."""
        result = dict1.copy()

        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _detect_changes(self, old: dict, new: dict, path: str = "") -> list:
        """Detecta mudanças entre duas configurações."""
        changes = []

        # Checa valores modificados ou removidos
        for key, old_value in old.items():
            current_path = f"{path}.{key}" if path else key

            if key not in new:
                changes.append(f"Removed: {current_path}")
            elif isinstance(old_value, dict) and isinstance(new.get(key), dict):
                changes.extend(self._detect_changes(old_value, new[key], current_path))
            elif old_value != new.get(key):
                changes.append(f"Modified: {current_path}")

        # Checa valores adicionados
        for key in new:
            if key not in old:
                current_path = f"{path}.{key}" if path else key
                changes.append(f"Added: {current_path}")

        return changes

    def get_from_dict(self, data: dict, key: str) -> Any:
        """Obtém valor de um dicionário usando notação de ponto."""
        keys = key.split('.')
        value = data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None

        return value

    def export(self) -> str:
        """Exporta configuração como JSON string."""
        with self.lock:
            return json.dumps(self.config, indent=2)

    def validate(self) -> tuple[bool, list[str]]:
        """Valida configuração atual."""
        errors = []

        with self.lock:
            # Validações básicas
            if self.get('api.port', 0) < 1 or self.get('api.port', 0) > 65535:
                errors.append("API port must be between 1 and 65535")

            if self.get('claude.max_tokens', 0) < 1:
                errors.append("Claude max_tokens must be positive")

            if self.get('session.timeout', 0) < 60:
                errors.append("Session timeout must be at least 60 seconds")

            if not self.get('neo4j.uri'):
                errors.append("Neo4j URI is required")

        return (len(errors) == 0, errors)

    def __del__(self):
        """Cleanup ao destruir o objeto."""
        self.stop_watching()


# Instância global (singleton)
_config_instance = None

def get_config_instance():
    """Retorna instância singleton do ConfigManager."""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance

# Instância global
config = get_config_instance()


# Funções de conveniência
def get_config(key: str, default: Any = None) -> Any:
    """Obtém configuração."""
    return config.get(key, default)


def set_config(key: str, value: Any, persist: bool = True) -> None:
    """Define configuração."""
    config.set(key, value, persist)


def reload_config() -> None:
    """Recarrega configuração."""
    config.reload()