FamilyDataDaily/
├── app.py                      # 主程序入口
├── config.py                   # 配置文件
├── manage_password.py          # 密码管理工具（服务器端）
├── requirements.txt            # Python依赖
├── start.sh                    # 启动脚本
├── models/                     # 数据模型层
│   ├── __init__.py
│   ├── user_model.py          # 用户模型（hash加密）
│   └── diary_model.py         # 日记模型
├── routes/                     # 路由层
│   ├── __init__.py
│   ├── auth_routes.py         # 认证路由
│   └── diary_routes.py        # 日记路由
├── templates/                  # HTML模板
│   ├── login.html             # 登录页
│   ├── register.html          # 注册页
│   ├── forgot_password.html   # 忘记密码页
│   └── dashboard.html         # 主页面（4个标签）
├── static/                     # 静态资源
│   ├── css/style.css          # 响应式样式
│   └── js/
│       ├── auth.js            # 认证JS
│       └── diary.js           # 日记JS
└── data/                       # 数据存储（自动创建）
    ├── family_diary.db        # SQLite数据库
    └── uploads/               # 上传文件
