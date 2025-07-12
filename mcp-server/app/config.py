
import os



# Database configurations
SQLITE_DB_CONFIG = {
    "dbname": os.getenv("SQLITE_DB", "embedding.db"),
    "user": os.getenv("SQLITE_USER", ""),
    "password": os.getenv("SQLITE_PASSWORD", ""),
    "host": os.getenv("SQLITE_HOST", ""),
    "port": os.getenv("SQLITE_PORT", ""),
    "uri": os.getenv("SQLITE_URI", "sqlite:///embedding.db"),
}

# JWT Configuration
JWT_SECRET_KEY= os.getenv("JWT_SECRET_KEY","your-super-secret-jwt-key-change-in-production")

# MCP API Key for VS Code integration
MCP_API_KEY= os.getenv("MCP_API_KEY", "mcp-api-key-2025-super-secure-token")

# Default database path for SQLite
DB_PATH= os.getenv("DB_PATH", "embedding.db")