import sqlite3
import json
import datetime
import os
import uuid

class DatabaseLogger:
    """Class to handle logging of chat interactions to a database."""
    
    def __init__(self, db_path="logs/chat_logs.db"):
        """Initialize the database connection and create tables if they don't exist."""
        # Ensure logs directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # Create tables if they don't exist
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        # Sessions table to track unique chat sessions
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            start_time TIMESTAMP,
            user_browser TEXT,
            user_ip TEXT
        )
        ''')
        
        # Interactions table to log all queries and responses
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            interaction_id TEXT PRIMARY KEY,
            session_id TEXT,
            timestamp TIMESTAMP,
            model_name TEXT,
            model_id TEXT,
            temperature REAL,
            max_tokens INTEGER,
            user_query TEXT,
            model_response TEXT,
            has_file BOOLEAN,
            file_name TEXT,
            has_image BOOLEAN,
            execution_time_ms INTEGER,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )
        ''')
        
        self.conn.commit()
    
    def log_session(self, session_id, user_browser=None, user_ip=None):
        """Log a new session."""
        self.cursor.execute(
            "INSERT OR IGNORE INTO sessions VALUES (?, ?, ?, ?)",
            (session_id, datetime.datetime.now(), user_browser, user_ip)
        )
        self.conn.commit()
    
    def log_interaction(self, session_id, model_name, model_id, temperature, max_tokens, 
                         user_query, model_response, has_file=False, file_name=None, 
                         has_image=False, execution_time_ms=0):
        """Log a chat interaction."""
        interaction_id = str(uuid.uuid4())
        
        self.cursor.execute(
            "INSERT INTO interactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                interaction_id,
                session_id,
                datetime.datetime.now(),
                model_name,
                model_id,
                temperature,
                max_tokens,
                user_query,
                model_response,
                has_file,
                file_name,
                has_image,
                execution_time_ms
            )
        )
        self.conn.commit()
        return interaction_id
    
    def get_session_interactions(self, session_id):
        """Get all interactions for a specific session."""
        self.cursor.execute(
            "SELECT * FROM interactions WHERE session_id = ? ORDER BY timestamp",
            (session_id,)
        )
        return self.cursor.fetchall()
    
    def get_all_sessions(self, limit=100):
        """Get all sessions with optional limit."""
        self.cursor.execute(
            "SELECT * FROM sessions ORDER BY start_time DESC LIMIT ?",
            (limit,)
        )
        return self.cursor.fetchall()
    
    def get_stats(self):
        """Get basic usage statistics."""
        stats = {}
        
        # Total number of sessions
        self.cursor.execute("SELECT COUNT(*) FROM sessions")
        stats["total_sessions"] = self.cursor.fetchone()[0]
        
        # Total number of interactions
        self.cursor.execute("SELECT COUNT(*) FROM interactions")
        stats["total_interactions"] = self.cursor.fetchone()[0]
        
        # Most popular model
        self.cursor.execute(
            "SELECT model_name, COUNT(*) as count FROM interactions GROUP BY model_name ORDER BY count DESC LIMIT 1"
        )
        result = self.cursor.fetchone()
        stats["most_popular_model"] = result[0] if result else None
        stats["most_popular_model_count"] = result[1] if result else 0
        
        return stats
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
