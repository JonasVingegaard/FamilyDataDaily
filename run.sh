#!/bin/bash

echo "=========================================="
echo "🏠 家庭日记系统 - 启动脚本"
echo "=========================================="

# 检查是否在conda环境
if command -v conda &> /dev/null; then
    echo "✓ 检测到 Conda 环境"
    
    # 检查是否已激活环境
    if [[ "$CONDA_DEFAULT_ENV" == "" ]]; then
        echo "⚠ 未激活conda环境，使用base环境"
    else
        echo "✓ 当前环境: $CONDA_DEFAULT_ENV"
    fi
fi

# 检查Flask是否安装
echo ""
echo "📦 检查依赖..."
if python -c "import flask" 2>/dev/null; then
    echo "✓ Flask 已安装"
else
    echo "⚠ Flask 未安装，正在安装..."
    pip install Flask==3.0.0 Werkzeug==3.0.1
fi

# 启动服务
echo ""
echo "🚀 启动服务..."
echo ""
python app.py