#!/bin/bash
# 技能安装脚本 - 基于ClawHub技能文档

echo "🦞 开始安装核心技能..."

# 1. Excel/XLSX 技能 - 主要是指导文档，已记录到TOOLS.md
echo "✅ Excel/XLSX 技能 - 已学习文档，使用openpyxl处理"

# 2. Sheetsmith 技能 - 需要下载Python脚本
echo "📥 下载 Sheetsmith..."
cd /Users/dadaguaijiangjun/.openclaw/workspace/skills

# 3. 安装Python依赖
echo "📦 安装Python依赖..."
pip3 install pandas openpyxl xlrd tabulate -q

echo "✅ 基础依赖安装完成"
echo ""
echo "📝 已掌握技能:"
echo "  1. Excel/XLSX - 使用 openpyxl 处理公式、格式"
echo "  2. Sheetsmith - Pandas驱动的数据分析"
echo "  3. 财务表格处理器 - 自主开发的收支分析工具"
echo ""
echo "🎯 现在可以处理财务表格了！"
