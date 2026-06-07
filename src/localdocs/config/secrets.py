cat > src/localdocs/config/__init__.py << 'EOF'
"""Configuration Module for LocalDocs AI"""

from .settings import (
    Settings,
    get_settings,
    app_settings
)
from .secrets import (
    SecretsManager,
    get_secrets_manager,
    get_api_key,
    get_llm_api_key,
    get_database_url,
    get_encryption_key
)

__all__ = [
    "Settings",
    "get_settings",
    "app_settings",
    "SecretsManager",
    "get_secrets_manager",
    "get_api_key",
    "get_llm_api_key",
    "get_database_url",
    "get_encryption_key"
]
EOF
