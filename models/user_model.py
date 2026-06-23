from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime
from config import DATABASE


class User:
    """用户模型"""
    
    def __init__(self):
        self.init_db()
        self.create_admin_if_not_exists()
    
    def init_db(self):
        """初始化数据库"""
        os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 兼容旧表：如果缺少 is_admin 列，自动添加
        try:
            cursor.execute('SELECT is_admin FROM users LIMIT 1')
        except sqlite3.OperationalError:
            cursor.execute('ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE')
            print("✓ 已自动迁移数据库：添加 is_admin 列")
        
        conn.commit()
        conn.close()
    
    def create_admin_if_not_exists(self):
        """如果不存在管理员，则创建默认管理员账号"""
        admin_username = 'admin'
        admin_password = 'admin123'  # 默认密码
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # 检查是否已有管理员
        cursor.execute('SELECT id FROM users WHERE username = ?', (admin_username,))
        if not cursor.fetchone():
            password_hash = generate_password_hash(admin_password)
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, is_admin)
                VALUES (?, ?, ?, ?)
            ''', (admin_username, password_hash, 'admin@family.com', True))
            conn.commit()
            print(f"✓ 已创建默认管理员账号: {admin_username} / {admin_password}")
        
        conn.close()
    
    def create_user(self, username, password, email):
        """创建新用户"""
        try:
            password_hash = generate_password_hash(password)
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, email)
                VALUES (?, ?, ?)
            ''', (username, password_hash, email))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def verify_user(self, username, password):
        """验证用户"""
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            return dict(user)
        return None
    
    def get_user_by_username(self, username):
        """根据用户名获取用户"""
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        conn.close()
        return dict(user) if user else None
    
    def get_all_users(self):
        """获取所有用户（管理员用）"""
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, username, email, is_admin, created_at FROM users ORDER BY created_at DESC')
        users = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return users
    
    def delete_user(self, user_id):
        """删除用户"""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # 删除用户的日记
        cursor.execute('DELETE FROM diaries WHERE user_id = ?', (user_id,))
        # 删除用户
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        return True
    
    def is_admin(self, user_id):
        """检查用户是否是管理员"""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT is_admin FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result and result[0]
    
    def _get_connection(self):
        """获取数据库连接（供 manage_password.py 使用）"""
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    
    def reset_password(self, username, new_password):
        """重置用户密码"""
        user = self.get_user_by_username(username)
        if not user:
            return False
        
        password_hash = generate_password_hash(new_password)
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?', (password_hash, username))
        conn.commit()
        conn.close()
        return True