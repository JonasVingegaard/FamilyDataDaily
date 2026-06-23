from flask import Blueprint, request, jsonify, session, render_template
from models.user_model import User
from models.diary_model import Diary
import os
from config import UPLOAD_DIR
from pathlib import Path
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
user_model = User()
diary_model = Diary()


def require_admin(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        if not user_model.is_admin(session['user_id']):
            return jsonify({'success': False, 'message': '需要管理员权限'}), 403
        
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@require_admin
def admin_dashboard():
    """管理员后台页面"""
    return render_template('admin.html', username=session['username'])


@admin_bp.route('/users', methods=['GET'])
@require_admin
def get_users():
    """获取所有用户"""
    users = user_model.get_all_users()
    return jsonify({'success': True, 'users': users})


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@require_admin
def delete_user(user_id):
    """删除用户"""
    if user_id == session['user_id']:
        return jsonify({'success': False, 'message': '不能删除自己'}), 400
    
    user_model.delete_user(user_id)
    return jsonify({'success': True, 'message': '用户已删除'})


@admin_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@require_admin
def reset_password(user_id):
    """重置用户密码"""
    from werkzeug.security import generate_password_hash
    import sqlite3
    from config import DATABASE
    
    data = request.get_json()
    new_password = data.get('password')
    
    if not new_password:
        return jsonify({'success': False, 'message': '请提供新密码'}), 400
    
    password_hash = generate_password_hash(new_password)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': '密码已重置'})


@admin_bp.route('/diaries', methods=['GET'])
@require_admin
def get_all_diaries():
    """获取所有日记"""
    diaries = diary_model.get_all_diaries()
    return jsonify({'success': True, 'diaries': diaries})


@admin_bp.route('/diaries/<int:diary_id>', methods=['DELETE'])
@require_admin
def delete_diary(diary_id):
    """管理员删除日记"""
    diary_info = diary_model.delete_diary_as_admin(diary_id)
    
    if diary_info:
        _delete_files(diary_info)
        return jsonify({'success': True, 'message': '日记已删除'})
    
    return jsonify({'success': False, 'message': '日记不存在'}), 404


@admin_bp.route('/files', methods=['GET'])
@require_admin
def list_files():
    """列出所有上传的文件"""
    files = []
    
    for subfolder in ['images', 'videos', 'documents']:
        folder_path = UPLOAD_DIR / subfolder
        if folder_path.exists():
            for file_path in folder_path.rglob('*'):
                if file_path.is_file():
                    rel_path = file_path.relative_to(UPLOAD_DIR)
                    size = file_path.stat().st_size
                    files.append({
                        'path': str(rel_path),
                        'name': file_path.name,
                        'size': size,
                        'size_human': _format_size(size),
                        'type': subfolder
                    })
    
    return jsonify({'success': True, 'files': files})


@admin_bp.route('/files/<path:filename>', methods=['DELETE'])
@require_admin
def delete_file(filename):
    """删除文件"""
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        return jsonify({'success': False, 'message': '文件不存在'}), 404
    
    try:
        file_path.unlink()
        return jsonify({'success': True, 'message': '文件已删除'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500


def _delete_files(diary_info):
    """删除日记关联的文件"""
    import json
    
    for file_list_key in ['images', 'videos', 'files']:
        file_list = diary_info.get(file_list_key)
        if file_list:
            if isinstance(file_list, str):
                file_list = json.loads(file_list)
            
            for file_path in file_list:
                full_path = UPLOAD_DIR / file_path.replace('uploads/', '')
                if full_path.exists():
                    try:
                        full_path.unlink()
                        print(f"✓ 已删除文件: {full_path}")
                    except Exception as e:
                        print(f"✗ 删除文件失败: {full_path}, 错误: {e}")


def _format_size(size_bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"