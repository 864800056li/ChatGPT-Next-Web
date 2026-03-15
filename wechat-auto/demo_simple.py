#!/usr/bin/env python3
"""
超简单演示脚本 - 无需任何配置
直接在命令行体验自动回复效果
"""

import sys
import os

print("=" * 60)
print("🤖 微信自动回复系统 - 即时演示")
print("=" * 60)
print("无需配置，立即体验关键词自动回复效果！")
print("输入客户问题，查看系统如何自动回复")
print("输入 'quit' 或 '退出' 结束演示")
print("=" * 60)

# 内置关键词回复规则
keyword_rules = {
    "价格": "💰 我们的产品价格：基础版100元/月，专业版300元/月，企业版800元/月",
    "多少钱": "💰 价格根据版本不同：100元到800元每月",
    "发货": "🚚 付款后24小时内发货，快递2-3天送达",
    "配送": "🚚 我们使用顺丰/京东快递，大部分地区2-3天",
    "客服": "👨‍💼 客服电话：400-xxx-xxxx（工作日9:00-18:00）",
    "联系": "👨‍💼 可以打电话400-xxx-xxxx或发邮件到support@example.com",
    "你好": "👋 您好！我是智能助手，有什么可以帮您？",
    "您好": "👋 您好！很高兴为您服务",
    "谢谢": "🙏 不客气！很高兴能帮助您",
    "再见": "👋 再见！有问题随时联系我",
    "功能": "🛠️ 主要功能：数据同步、团队协作、自动化工作流、数据分析",
    "优惠": "🎁 现有优惠：年付8折，企业版免费试用30天",
    "退款": "🔙 支持7天无理由退款（未使用服务）",
    "发票": "🧾 可以开发票，付款后联系客服提供开票信息",
}

def find_reply(question):
    """查找回复（简单关键词匹配）"""
    question_lower = question.lower()
    
    # 按关键词匹配
    for keyword, reply in keyword_rules.items():
        if keyword in question_lower:
            return reply
    
    # 默认回复
    if "吗" in question or "？" in question or "?" in question:
        return "🤔 请详细描述您的问题，我会尽力为您解答。"
    
    if any(word in question_lower for word in ["帮助", "帮忙", "help"]):
        return "🆘 请告诉我您遇到的具体问题，我会尽力帮助您解决。"
    
    return "🤖 我理解了您的意思，但需要更多信息来提供准确回答。能详细描述一下吗？"

def main():
    """主演示循环"""
    demo_count = 0
    
    while True:
        try:
            # 获取用户输入
            if demo_count == 0:
                question = input("\n💬 请输入客户问题（示例：这个产品多少钱？）： ")
            else:
                question = input("\n💬 请继续输入客户问题： ")
            
            # 检查退出命令
            if question.lower() in ["quit", "退出", "exit", "q"]:
                print("\n👋 演示结束！")
                break
            
            if not question.strip():
                print("⚠️  请输入有效的问题")
                continue
            
            # 查找回复
            reply = find_reply(question)
            
            # 显示结果
            print("\n" + "=" * 60)
            print(f"📱 客户问题：{question}")
            print(f"🤖 自动回复：{reply}")
            print("=" * 60)
            
            demo_count += 1
            
            # 显示提示
            if demo_count == 1:
                print("\n💡 提示：系统正在匹配关键词，您可以尝试：")
                print("   • '什么时候发货？'")
                print("   • '怎么联系客服？'")
                print("   • '有优惠吗？'")
                print("   • '这个产品有什么功能？'")
            
        except KeyboardInterrupt:
            print("\n\n👋 演示被中断")
            break
        except Exception as e:
            print(f"\n❌ 出现错误：{e}")
            break
    
    # 演示统计
    print(f"\n📊 演示统计：处理了 {demo_count} 个问题")
    
    # 显示系统能力
    print("\n🔧 完整系统功能：")
    print("   1. 关键词自动回复（已演示）")
    print("   2. 文档知识库检索（从PDF/Word等文件搜索答案）")
    print("   3. 历史聊天学习（从过往对话学习你的回复风格）")
    print("   4. 企业微信集成（官方API，零封号风险）")
    
    # 下一步建议
    print("\n🎯 下一步建议：")
    print("   想实际使用？请运行：python test_quick.py")
    print("   需要帮助配置？告诉我你的具体业务问题")
    
    # 快速启动提示
    print("\n⚡ 最快速启动：")
    print("   告诉我3个最常见的客户问题+你的回答")
    print("   我立刻帮你配置到完整系统中！")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"演示程序出错：{e}")
        import traceback
        traceback.print_exc()