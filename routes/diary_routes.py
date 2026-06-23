from flask import Blueprint, request, jsonify, session, render_template, send_from_directory
from models.diary_model import Diary
from models.user_model import User
from config import UPLOAD_DIR, DIARY_DIR
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from pathlib import Path

diary_bp = Blueprint('diary', __name__, url_prefix='/diary')
diary_model = Diary()
user_model = User()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg',
                       'mp4', 'avi', 'mov', 'mkv', 'webm', 'flv', 'wmv',
                       'mp3', 'wav', 'flac', 'aac', 'ogg', 'wma',
                       'pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx', 'ppt', 'pptx',
                       'zip', 'rar', '7z', 'gz', 'tar'}


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_file(file, subfolder):
    """保存上传的文件"""
    if not file or not file.filename:
        return None
    
    if not allowed_file(file.filename):
        print(f"  ✗ 文件类型不允许: {file.filename}")
        return None
    
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(filename)
    unique_filename = f"{name}_{timestamp}{ext}"
    
    save_path = UPLOAD_DIR / subfolder
    save_path.mkdir(parents=True, exist_ok=True)
    
    file_path = save_path / unique_filename
    file.save(str(file_path))
    
    print(f"  ✓ 保存成功: {file_path} ({file_path.stat().st_size} bytes)")
    
    return f"uploads/{subfolder}/{unique_filename}"


@diary_bp.route('/')
def dashboard():
    """日记主页"""
    if 'user_id' not in session:
        return render_template('login.html')
    
    is_admin = user_model.is_admin(session['user_id'])
    return render_template('dashboard.html', 
                         username=session['username'], 
                         is_admin=is_admin,
                         user_id=session['user_id'])


@diary_bp.route('/create', methods=['POST'])
def create_diary():
    """创建日记"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    diary_type = request.form.get('diary_type')
    date = request.form.get('date')
    content = request.form.get('content')
    
    print(f"\n=== 日记提交调试信息 ===")
    print(f"日记类型: {diary_type}")
    print(f"日期: {date}")
    print(f"内容长度: {len(content) if content else 0}")
    print(f"上传的文件: {request.files.keys()}")
    
    if not all([diary_type, date]):
        return jsonify({'success': False, 'message': '请填写日期'}), 400
    
    # 处理文件上传
    images = []
    videos = []
    files = []
    
    # 处理图片
    if 'images' in request.files:
        for image in request.files.getlist('images'):
            if image.filename:  # 检查是否有文件
                print(f"处理图片: {image.filename}")
                path = save_file(image, 'images')
                if path:
                    images.append(path)
                    print(f"  ✓ 保存成功: {path}")
                else:
                    print(f"  ✗ 保存失败")
    
    # 处理视频
    if 'videos' in request.files:
        for video in request.files.getlist('videos'):
            if video.filename:
                print(f"处理视频: {video.filename}")
                path = save_file(video, 'videos')
                if path:
                    videos.append(path)
                    print(f"  ✓ 保存成功: {path}")
                else:
                    print(f"  ✗ 保存失败")
    
    # 处理其他文件
    if 'files' in request.files:
        for file in request.files.getlist('files'):
            if file.filename:
                print(f"处理文件: {file.filename}")
                path = save_file(file, 'documents')
                if path:
                    files.append(path)
                    print(f"  ✓ 保存成功: {path}")
                else:
                    print(f"  ✗ 保存失败")
    
    print(f"图片列表: {images}")
    print(f"视频列表: {videos}")
    print(f"文件列表: {files}")
    print(f"========================\n")
    
    diary_model.create_diary(
        user_id=session['user_id'],
        username=session['username'],
        diary_type=diary_type,
        date=date,
        content=content or '',
        images=images if images else None,
        videos=videos if videos else None,
        files=files if files else None
    )
    
    return jsonify({'success': True, 'message': '日记保存成功'})


@diary_bp.route('/public', methods=['GET'])
def get_public_diaries():
    """获取公共日记"""
    diaries = diary_model.get_public_diaries()
    return jsonify({'success': True, 'diaries': diaries})


@diary_bp.route('/private', methods=['GET'])
def get_private_diaries():
    """获取个人日记"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    diaries = diary_model.get_private_diaries(session['user_id'])
    return jsonify({'success': True, 'diaries': diaries})


@diary_bp.route('/uploads/<path:filename>')
def serve_upload(filename):
    """提供上传文件访问"""
    return send_from_directory(UPLOAD_DIR, filename)


@diary_bp.route('/delete/<int:diary_id>', methods=['POST'])
def delete_diary(diary_id):
    """删除日记（普通用户只能删除自己的，管理员可以删除任何）"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    is_admin = user_model.is_admin(session['user_id'])
    
    if is_admin:
        diary_info = diary_model.delete_diary_as_admin(diary_id)
    else:
        diary_info = diary_model.delete_diary(diary_id, session['user_id'])
    
    if diary_info:
        _delete_files(diary_info)
        return jsonify({'success': True, 'message': '日记已删除'})
    
    return jsonify({'success': False, 'message': '日记不存在或无权限'}), 404


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