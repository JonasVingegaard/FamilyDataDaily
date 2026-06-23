import os
from pathlib import Path

# 基础路径
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
DB_PATH = DATA_DIR / 'family_diary.db'
DATABASE = DB_PATH  # 添加 DATABASE 别名
UPLOAD_DIR = DATA_DIR / 'uploads'
DIARY_DIR = DATA_DIR / 'diaries'

# 确保目录存在
for dir_path in [DATA_DIR, UPLOAD_DIR, DIARY_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Flask配置
class Config:
    SECRET_KEY = 'family-diary-secret-key-2026'  # 生产环境请更换
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB上传限制
    
    # 上传配置
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'pdf', 'doc', 'docx', 'txt'}
    UPLOAD_FOLDER = str(UPLOAD_DIR)