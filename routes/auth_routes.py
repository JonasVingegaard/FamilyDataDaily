from flask import Blueprint, request, jsonify, session, render_template
from models.user_model import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
user_model = User()


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = user_model.verify_user(username, password)
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({'success': True, 'message': '登录成功'})
    
    return jsonify({'success': False, 'message': '用户名或密码错误'}), 401


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if request.method == 'GET':
        return render_template('register.html')
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not all([username, password, email]):
        return jsonify({'success': False, 'message': '请填写完整信息'}), 400
    
    if user_model.create_user(username, password, email):
        return jsonify({'success': True, 'message': '注册成功'})
    
    return jsonify({'success': False, 'message': '用户名或邮箱已存在'}), 400


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """忘记密码"""
    if request.method == 'GET':
        return render_template('forgot_password.html')
    
    data = request.get_json()
    username = data.get('username')
    
    user = user_model.get_user_by_username(username)
    if user:
        return jsonify({'success': True, 'message': '请联系管理员重置密码'})
    
    return jsonify({'success': False, 'message': '用户不存在'}), 404


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    session.clear()
    return jsonify({'success': True, 'message': '已退出登录'})


@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """检查登录状态"""
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'username': session['username']
        })
    return jsonify({'logged_in': False})