#!/usr/bin/env python3
"""
密码管理工具 - 服务器端使用
用法:
    python manage_password.py list          # 列出所有用户
    python manage_password.py reset <用户名> <新密码>  # 重置密码
    python manage_password.py get <用户名>   # 查看用户信息
"""

from models.user_model import User
import sys

user_model = User()


def list_users():
    """列出所有用户"""
    print("\n=== 所有用户列表 ===")
    with user_model._get_connection() as conn:
        users = conn.execute('SELECT id, username, email, is_admin, created_at FROM users').fetchall()
        
        if not users:
            print("暂无用户")
            return
        
        for user in users:
            print(f"ID: {user['id']}")
            print(f"用户名: {user['username']}")
            print(f"邮箱: {user['email']}")
            print(f"管理员: {'是' if user['is_admin'] else '否'}")
            print(f"注册时间: {user['created_at']}")
            print("-" * 40)


def reset_password(username, new_password):
    """重置用户密码"""
    success = user_model.reset_password(username, new_password)
    
    if success:
        print(f"\n✓ 用户 '{username}' 的密码已重置为: {new_password}")
    else:
        print(f"\n✗ 用户 '{username}' 不存在")


def get_user(username):
    """查看用户信息"""
    user = user_model.get_user_by_username(username)
    
    if user:
        print("\n=== 用户信息 ===")
        print(f"ID: {user['id']}")
        print(f"用户名: {user['username']}")
        print(f"邮箱: {user['email']}")
        print(f"管理员: {'是' if user.get('is_admin') else '否'}")
        print(f"注册时间: {user['created_at']}")
    else:
        print(f"\n✗ 用户 '{username}' 不存在")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'list':
        list_users()
    elif command == 'reset' and len(sys.argv) == 4:
        reset_password(sys.argv[2], sys.argv[3])
    elif command == 'get' and len(sys.argv) == 3:
        get_user(sys.argv[2])
    else:
        print(__doc__)