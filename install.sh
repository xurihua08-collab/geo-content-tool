#!/bin/bash
# 安装依赖脚本

echo "安装内容管理系统依赖..."

# 安装 Python 依赖
pip install streamlit>=1.28.0 playwright>=1.40.0 asyncio

# 安装 playwright 浏览器
echo "安装 Playwright 浏览器..."
playwright install chromium

echo "✅ 安装完成"
echo ""
echo "启动应用:"
echo "  streamlit run app.py"
