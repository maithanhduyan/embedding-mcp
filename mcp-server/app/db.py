
# -*- coding: utf-8 -*-
# File: app/db.py
# This module handles database connections and operations.

import os
import hashlib
import sqlite3
from app.logger import get_logger
from app.config import SQLITE_DB_CONFIG, DB_PATH

# Initialize the logger
logger = get_logger(__name__)


def get_db_connection():
    """Get database connection"""
    conn = None
    try:
        
        conn = sqlite3.connect(DB_PATH)

        conn.row_factory = sqlite3.Row  # Allows access to columns by name

        conn.execute("PRAGMA journal_mode=WAL")  # Use Write-Ahead Logging for better concurrency

        return conn 
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise

    return conn

def init_database():
    """Initialize database with users table."""
    conn = get_db_connection()
    try:
        # Create users table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create default admin user if not exists
        admin_password = hash_password("admin123")
        conn.execute('''
            INSERT OR IGNORE INTO users (username, password_hash) 
            VALUES (?, ?)
        ''', ("admin", admin_password))
        
        conn.commit()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        conn.rollback()
    finally:
        conn.close()

def mcp_db_init():
    """Initialize the MCP database with thinking-related tables."""
    conn = get_db_connection()
    try:
        # Create MCP queries table - lưu trữ các truy vấn MCP
        conn.execute('''
            CREATE TABLE IF NOT EXISTS mcp_queries (
                id TEXT PRIMARY KEY,
                tool_name TEXT NOT NULL,
                input_data TEXT NOT NULL,
                output_data TEXT NOT NULL,
                execution_time_ms INTEGER,
                success BOOLEAN NOT NULL,
                error_message TEXT,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better performance
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_mcp_queries_tool_name 
            ON mcp_queries(tool_name)
        ''')
        
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_mcp_queries_created_date 
            ON mcp_queries(created_date)
        ''')
        
        conn.commit()
        logger.info("MCP database tables initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing MCP database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def hash_password(password: str) -> str:
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash."""
    return hash_password(password) == password_hash