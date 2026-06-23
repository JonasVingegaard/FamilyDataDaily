from flask import Flask, redirect, url_for
from config import Config
from routes.auth_routes import auth_bp
from routes.diary_routes import diary_bp
from routes.admin_routes import admin_bp
import os


def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(diary_bp)
    app.register_blueprint(admin_bp)
    
    # 根路由 - 重定向到登录页
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    # 获取本机局域网IP
    import socket
    def get_local_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip
    
    local_ip = get_local_ip()
    port = 5000
    
    print(f"\n{'='*60}")
    print(f"🏠 家庭日记系统启动成功！")
    print(f"{'='*60}")
    print(f"📍 本机访问: http://localhost:{port}")
    print(f"📍 局域网访问: http://{local_ip}:{port}")
    print(f"📱 手机/平板访问: http://{local_ip}:{port}")
    print(f"{'='*60}\n")
    
    # host='0.0.0.0' 允许局域网访问
    app.run(host='0.0.0.0', port=port, debug=True)