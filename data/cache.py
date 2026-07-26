import sqlite3
import json
import os
from datetime import datetime, timedelta
from config import CACHE_DB_PATH, CACHE_MAX_AGE_DAYS

class LocalCache:
    def __init__(self, db_path: str = CACHE_DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._create_table()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TEXT
                )
            """)
            conn.commit()

    def get(self, key: str, max_age_days: float = CACHE_MAX_AGE_DAYS) -> dict:
        """
        Retrieve data from the cache.
        Returns None if cache is missing or expired.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value, updated_at FROM cache WHERE key = ?", (key,))
                row = cursor.fetchone()
                if not row:
                    return None
                
                value_str, updated_at_str = row
                updated_at = datetime.fromisoformat(updated_at_str)
                
                # Check expiration
                if datetime.now() - updated_at > timedelta(days=max_age_days):
                    return None
                    
                return json.loads(value_str)
        except Exception:
            return None

    def set(self, key: str, data: dict):
        """
        Store data in the cache.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                value_str = json.dumps(data)
                updated_at_str = datetime.now().isoformat()
                cursor.execute("""
                    INSERT OR REPLACE INTO cache (key, value, updated_at)
                    VALUES (?, ?, ?)
                """, (key, value_str, updated_at_str))
                conn.commit()
        except Exception as e:
            print(f"Error writing to cache: {e}")

    def close(self):
        pass
