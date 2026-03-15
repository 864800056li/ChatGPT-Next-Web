#!/usr/bin/env python3
"""
快速测试脚本 - 无需企业微信配置
"""

import sys
import os
from pathlib import Path

# 添加模块路径
sys.path.append(str(Path(__file__).parent))

from modules.keyword_matcher import KeywordMatcher
from modules.message_processor import MessageProcessor


def test_keyword_matching():
    """测试关键词匹配功能"""
    print("=" * 60)
    print("关键词匹配测试")
    print("=" * 60)
    
    # 创建测试配置
    test_triggers = [
        {
            "keywords": ["价格", "多少钱", "报价", "cost", "price"],
            "reply": "💰 产品价格：基础版100元/月，专业版300元/月，企业版800元/月。"
        },
        {
            "keywords": ["发货", "配送", "多久到", "delivery", "shipping"],
            "reply": "🚚 发货时间：付款后24小时内发货，大部分地区2-3天送达。"
        },
        {
            "keywords": ["客服", "人工", "联系你们", "customer service"],
            "reply": "👨‍💼 客服支持：如需人工客服请拨打400-xxx-xxxx，或留言稍后回复。"
        },
        {
            "keywords": ["你好", "您好", "hello", "hi", "在吗"],
            "reply": "👋 您好！我是智能助手，有什么可以帮您？"
        }
    ]
    
    # 创建匹配器
    matcher = KeywordMatcher(test_triggers)
    processor = MessageProcessor(keyword_matcher=matcher)
    
    # 测试用例
    test_cases = [
        ("这个产品多少钱？", "💰 产品价格：基础版100元/月，专业版300元/月，企业版800元/月。"),
        ("价格是多少？", "💰 产品价格：基础版100元/月，专业版300元/月，企业版800元/月。"),
        ("什么时候发货？", "🚚 发货时间：付款后24小时内发货，大部分地区2-3天送达。"),
        ("delivery time?", "🚚 发货时间：付款后24小时内发货，大部分地区2-3天送达。"),
        ("你好", "👋 您好！我是智能助手，有什么可以帮您？"),
        ("怎么联系客服？", "👨‍💼 客服支持：如需人工客服请拨打400-xxx-xxxx，或留言稍后回复。"),
        ("这个产品有什么功能？", None),  # 无匹配
        ("谢谢", "不客气！很高兴为您服务。"),  # 默认回复
        ("再见", "再见！有问题随时联系我。"),  # 默认回复
    ]
    
    print("\n测试结果：")
    print("-" * 60)
    
    passed = 0
    total = len(test_cases)
    
    for i, (question, expected) in enumerate(test_cases, 1):
        reply = processor.process(f"test_user_{i}", question)
        
        if reply == expected:
            status = "✅ 通过"
            passed += 1
        elif expected is None and reply is None:
            status = "✅ 通过 (无匹配)"
            passed += 1
        elif expected is None and reply is not None:
            status = f"⚠️  注意 (期望无匹配，但得到: {reply[:30]}...)"
        else:
            status = f"❌ 失败 (期望: {expected[:30]}...，得到: {reply[:30]}...)"
        
        print(f"{i:2d}. {question:20s} -> {status}")
    
    print("-" * 60)
    print(f"测试完成: {passed}/{total} 通过 ({passed/total*100:.1f}%)")


def test_configuration_check():
    """检查配置文件"""
    print("\n" + "=" * 60)
    print("配置文件检查")
    print("=" * 60)
    
    config_path = Path("config/config.yaml")
    
    if config_path.exists():
        print("✅ 配置文件存在: config/config.yaml")
        
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 检查关键配置项
            wecom = config.get('wecom', {})
            
            checks = [
                ("corp_id", wecom.get('corp_id'), "你的企业ID"),
                ("secret", wecom.get('secret'), "你的应用Secret"),
                ("agent_id", wecom.get('agent_id'), "1000002"),
            ]
            
            all_valid = True
            for key, value, default in checks:
                if value == default:
                    print(f"❌ {key}: 仍为默认值 '{default}'，请修改")
                    all_valid = False
                elif not value:
                    print(f"❌ {key}: 未设置")
                    all_valid = False
                else:
                    print(f"✅ {key}: 已设置")
            
            if all_valid:
                print("\n🎉 所有配置项都已正确设置！")
            else:
                print("\n⚠️  请修改配置文件中的默认值")
                
        except Exception as e:
            print(f"❌ 读取配置文件失败: {e}")
    else:
        print("❌ 配置文件不存在")
        print("   请执行: cp config/config_template.yaml config/config.yaml")
        print("   然后编辑配置文件")


def show_next_steps():
    """显示下一步操作"""
    print("\n" + "=" * 60)
    print("下一步操作指南")
    print("=" * 60)
    
    steps = [
        ("1. 企业微信配置", [
            "登录企业微信管理后台",
            "应用管理 → 自建应用 → 创建应用",
            "获取 CorpID, Secret, AgentId"
        ]),
        ("2. 编辑配置文件", [
            "编辑 config/config.yaml",
            "填写 wecom 部分的三个参数",
            "可根据需要修改 keyword_triggers"
        ]),
        ("3. 准备数据", [
            "文档知识库: 放入 data/documents/",
            "历史聊天记录: 放入 data/history/",
            "支持格式: PDF, Word, TXT, MD, JSON, CSV"
        ]),
        ("4. 运行系统", [
            "测试模式: python main.py",
            "查看日志: logs/wechat_auto.log",
            "监控运行状态"
        ]),
        ("5. 扩展功能", [
            "添加更多关键词规则",
            "丰富文档知识库",
            "收集优质历史对话数据"
        ])
    ]
    
    for title, items in steps:
        print(f"\n{title}:")
        for item in items:
            print(f"  • {item}")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("企业微信自动回复系统 - 快速测试")
    print("=" * 60)
    
    # 测试关键词匹配
    test_keyword_matching()
    
    # 检查配置文件
    test_configuration_check()
    
    # 显示下一步
    show_next_steps()
    
    print("\n" + "=" * 60)
    print("💡 提示:")
    print("  - 即使没有企业微信API，关键词匹配功能也可独立使用")
    print("  - 可将此系统集成到其他平台（需适配消息接口）")
    print("  - 文档检索和历史学习功能需要相应数据文件")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试中断")
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()