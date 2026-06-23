from config import DB_PATH, DIARY_DIR
import sqlite3
import json
from datetime import datetime
from pathlib import Path


class Diary:
    """日记模型类"""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.diary_dir = DIARY_DIR
        self._init_db()
    
    def _get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self):
        """初始化日记表"""
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS diaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    diary_type TEXT NOT NULL CHECK(diary_type IN ('public', 'private')),
                    date TEXT NOT NULL,
                    content TEXT,
                    images TEXT,  -- JSON数组存储图片路径
                    videos TEXT,  -- JSON数组存储视频路径
                    files TEXT,   -- JSON数组存储文件路径
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            conn.commit()
    
    def create_diary(self, user_id, username, diary_type, date, content, images=None, videos=None, files=None):
        """创建日记"""
        images_json = json.dumps(images) if images else '[]'
        videos_json = json.dumps(videos) if videos else '[]'
        files_json = json.dumps(files) if files else '[]'
        
        with self._get_connection() as conn:
            conn.execute(
                '''INSERT INTO diaries (user_id, username, diary_type, date, content, images, videos, files)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (user_id, username, diary_type, date, content, images_json, videos_json, files_json)
            )
            conn.commit()
            return True
    
    def get_public_diaries(self, limit=50):
        """获取所有公共日记"""
        with self._get_connection() as conn:
            diaries = conn.execute(
                'SELECT * FROM diaries WHERE diary_type = ? ORDER BY date DESC, created_at DESC LIMIT ?',
                ('public', limit)
            ).fetchall()
            return [self._parse_diary(dict(d)) for d in diaries]
    
    def get_private_diaries(self, user_id, limit=50):
        """获取个人私密日记"""
        with self._get_connection() as conn:
            diaries = conn.execute(
                'SELECT * FROM diaries WHERE diary_type = ? AND user_id = ? ORDER BY date DESC, created_at DESC LIMIT ?',
                ('private', user_id, limit)
            ).fetchall()
            return [self._parse_diary(dict(d)) for d in diaries]
    
    def _parse_diary(self, diary_dict):
        """解析日记数据"""
        import json as json_module
        for key in ['images', 'videos', 'files']:
            try:
                val = diary_dict.get(key)
                if val and isinstance(val, str):
                    diary_dict[key] = json_module.loads(val)
                elif not val:
                    diary_dict[key] = []
            except (json_module.JSONDecodeError, TypeError):
                diary_dict[key] = []
        diary_dict['user_id'] = int(diary_dict['user_id'])
        return diary_dict
    
    def get_diary_by_id(self, diary_id, user_id):
        """根据ID获取日记（验证权限）"""
        with self._get_connection() as conn:
            diary = conn.execute(
                'SELECT * FROM diaries WHERE id = ? AND user_id = ?',
                (diary_id, user_id)
            ).fetchone()
            return self._parse_diary(dict(diary)) if diary else None
    
    def delete_diary(self, diary_id, user_id):
        """删除日记（只能删除自己的）"""
        with self._get_connection() as conn:
            # 先获取日记信息（用于删除文件）
            diary = conn.execute(
                'SELECT * FROM diaries WHERE id = ? AND user_id = ?',
                (diary_id, user_id)
            ).fetchone()
            
            if not diary:
                return False
            
            diary_dict = dict(diary)
            
            # 删除日记记录
            conn.execute('DELETE FROM diaries WHERE id = ? AND user_id = ?', (diary_id, user_id))
            conn.commit()
            
            return diary_dict
    
    def delete_diary_as_admin(self, diary_id):
        """管理员删除日记"""
        with self._get_connection() as conn:
            # 先获取日记信息
            diary = conn.execute(
                'SELECT * FROM diaries WHERE id = ?',
                (diary_id,)
            ).fetchone()
            
            if not diary:
                return False
            
            diary_dict = dict(diary)
            
            # 删除日记记录
            conn.execute('DELETE FROM diaries WHERE id = ?', (diary_id,))
            conn.commit()
            
            return diary_dict
    
    def get_all_diaries(self):
        """获取所有日记（管理员用）"""
        with self._get_connection() as conn:
            diaries = conn.execute(
                'SELECT * FROM diaries ORDER BY created_at DESC'
            ).fetchall()
            return [self._parse_diary(dict(d)) for d in diaries]