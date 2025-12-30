"""
日志存储模块 - 使用SQLite存储解析后的日志
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class LogStorage:
    """日志存储"""
    
    def __init__(self, db_path: str = "logs.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                container_name TEXT NOT NULL,
                timestamp TEXT,
                line_number INTEGER,
                error_content TEXT NOT NULL,
                context TEXT,
                analysis TEXT,
                severity TEXT,
                status TEXT DEFAULT 'new',
                created_at TEXT NOT NULL,
                analyzed_at TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collection_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                container_name TEXT NOT NULL,
                collected_at TEXT NOT NULL,
                log_lines INTEGER,
                error_count INTEGER
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("数据库初始化完成")
    
    def save_error(self, container_name: str, error_data: Dict) -> int:
        """保存单个错误日志"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        original = error_data.get('original', {})
        
        cursor.execute("""
            INSERT INTO error_logs 
            (container_name, timestamp, line_number, error_content, context, 
             analysis, analyzed_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            container_name,
            original.get('timestamp'),
            original.get('line_number'),
            original.get('content', ''),
            json.dumps(original.get('context', []), ensure_ascii=False),
            error_data.get('analysis', ''),
            error_data.get('analyzed_at'),
            datetime.now().isoformat()
        ))
        
        error_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return error_id
    
    def save_collection_history(self, container_name: str, log_lines: int, error_count: int):
        """保存采集历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO collection_history 
            (container_name, collected_at, log_lines, error_count)
            VALUES (?, ?, ?, ?)
        """, (
            container_name,
            datetime.now().isoformat(),
            log_lines,
            error_count
        ))
        
        conn.commit()
        conn.close()
    
    def get_errors(self, container_name: Optional[str] = None, 
                   status: Optional[str] = None, 
                   limit: int = 100) -> List[Dict]:
        """获取错误日志列表"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM error_logs WHERE 1=1"
        params = []
        
        if container_name:
            query += " AND container_name = ?"
            params.append(container_name)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        errors = []
        for row in rows:
            error = dict(row)
            if error.get('context'):
                try:
                    error['context'] = json.loads(error['context'])
                except (json.JSONDecodeError, TypeError):
                    error['context'] = []
            else:
                error['context'] = []
            errors.append(error)
        
        conn.close()
        return errors
    
    def get_error_by_id(self, error_id: int) -> Optional[Dict]:
        """获取单个错误详情"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM error_logs WHERE id = ?", (error_id,))
        row = cursor.fetchone()
        
        if row:
            error = dict(row)
            if error.get('context'):
                try:
                    error['context'] = json.loads(error['context'])
                except (json.JSONDecodeError, TypeError):
                    error['context'] = []
            else:
                error['context'] = []
            conn.close()
            return error
        
        conn.close()
        return None
    
    def update_error_status(self, error_id: int, status: str):
        """更新错误状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE error_logs SET status = ? WHERE id = ?
        """, (status, error_id))
        
        conn.commit()
        conn.close()
    
    def get_collection_history(self, limit: int = 50) -> List[Dict]:
        """获取采集历史"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM collection_history 
            ORDER BY collected_at DESC LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
