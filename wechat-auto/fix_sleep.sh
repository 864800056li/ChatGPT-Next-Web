#!/bin/bash
# 一键解决OpenClaw睡眠问题
# 让电脑24小时在线，关屏后也能正常响应

echo "========================================"
echo "🛡️  OpenClaw 24小时在线配置"
echo "========================================"

echo ""
echo "🔧 正在检查当前电源设置..."
pmset -g | grep -E "(sleep|display|disk)" | head -5

echo ""
echo "📝 需要输入管理员密码来修改系统设置"
echo "   密码输入时不会显示，输完后按回车"

echo ""
echo "🚀 执行防睡眠配置..."
sudo pmset -a sleep 0
sudo pmset -a displaysleep 0
sudo pmset -a disksleep 0
sudo pmset -a womp 1
sudo pmset -a powernap 1
sudo pmset -a tcpkeepalive 1

echo ""
echo "✅ 配置完成！"
echo ""
echo "📊 新的电源设置："
pmset -g | grep -E "(sleep|display|disk)" | head -5

echo ""
echo "🔍 验证配置："
echo "   1. 电脑将永不睡眠"
echo "   2. 显示器关闭后仍保持运行"
echo "   3. 网络连接不会中断"
echo "   4. OpenClaw可24小时响应"

echo ""
echo "🧪 测试方法："
echo "   1. 关闭显示器或合上笔记本"
echo "   2. 等待2分钟"
echo "   3. 用手机飞书发消息测试"
echo "   4. 应该能收到自动回复"

echo ""
echo "⚠️  注意事项："
echo "   • 电脑会一直运行，耗电增加"
echo "   • 建议插电使用，避免电池耗尽"
echo "   • 可设置自动重启时间（如凌晨4点）"
echo ""
echo "🔄 恢复默认设置（如需）："
echo "   sudo pmset -a sleep 1 displaysleep 10 disksleep 10"
echo "========================================"

# 等待用户确认
read -p "按回车键退出..."