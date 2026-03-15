#!/usr/bin/env python3
"""
私人微信自动化测试脚本
⚠️ 高风险警告：仅使用测试小号，主号必封！
"""

import pyautogui
import time
import os
import sys
from datetime import datetime

print("=" * 70)
print("🚨 🚨 🚨 高风险警告 🚨 🚨 🚨")
print("个人微信自动化可能导致永久封号！")
print("腾讯严格禁止自动化操作")
print("金融贷款业务账号监控更加严格！")
print("=" * 70)
print("⚠️  ⚠️  ⚠️  必须使用测试小号！ ⚠️  ⚠️  ⚠️")
print("绝对不要用主号！主号被封客户渠道全断！")
print("=" * 70)

# 安全设置
pyautogui.FAILSAFE = True  # 鼠标移到屏幕左上角停止脚本
pyautogui.PAUSE = 1.5      # 每次操作间隔1.5秒

def check_prerequisites():
    """检查前提条件"""
    print("\n🔍 检查前提条件：")
    print("1. ✅ 防睡眠设置已执行？（sudo pmset -a sleep 0 displaysleep 0）")
    print("2. ✅ 微信测试小号已登录？")
    print("3. ✅ 微信窗口在最前，主界面可见？")
    print("4. ✅ 屏幕不锁屏？")
    print("5. ✅ 准备好随时停止（鼠标移左上角）？")
    
    confirm = input("\n以上条件都满足？(y/N): ")
    if confirm.lower() != 'y':
        print("❌ 请先满足所有前提条件再继续")
        return False
    
    print("\n📱 请确保微信窗口：")
    print("• 在屏幕左侧，可见联系人列表")
    print("• 窗口未最小化")
    print("• 主界面显示正常")
    
    input("\n按回车键继续测试（Ctrl+C取消）...")
    return True

def calibrate_positions():
    """校准关键位置点"""
    print("\n🎯 校准阶段 - 请按照提示移动鼠标")
    
    positions = {}
    
    # 校准微信窗口区域
    print("\n1. 📱 微信窗口左上角")
    input("   请将鼠标移到微信窗口左上角（标题栏左上），按回车...")
    positions['window_top_left'] = pyautogui.position()
    print(f"   ✅ 记录位置: {positions['window_top_left']}")
    
    # 校准联系人列表
    print("\n2. 👥 联系人列表区域（任意联系人）")
    input("   请将鼠标移到左侧联系人列表的任意联系人上，按回车...")
    positions['contact_area'] = pyautogui.position()
    print(f"   ✅ 记录位置: {positions['contact_area']}")
    
    # 校准聊天输入框
    print("\n3. 💬 聊天输入框（底部输入区域）")
    input("   请将鼠标移到聊天窗口底部的输入框上，按回车...")
    positions['input_box'] = pyautogui.position()
    print(f"   ✅ 记录位置: {positions['input_box']}")
    
    # 校准发送按钮
    print("\n4. 📤 发送按钮（输入框右侧）")
    input("   请将鼠标移到输入框右侧的发送按钮上，按回车...")
    positions['send_button'] = pyautogui.position()
    print(f"   ✅ 记录位置: {positions['send_button']}")
    
    return positions

def test_file_transfer_assistant(positions):
    """测试向文件传输助手发送消息"""
    print("\n📤 测试1：向文件传输助手发送消息")
    
    # 先确保在微信主界面
    pyautogui.click(positions['window_top_left'])
    time.sleep(1)
    
    # 点击搜索框
    # 假设搜索框在顶部中间（可能需要额外校准）
    print("   🔍 请手动将鼠标移到搜索框上，按回车...")
    search_pos = pyautogui.position()
    pyautogui.click(search_pos)
    time.sleep(1)
    
    # 搜索文件传输助手
    pyautogui.write('文件传输助手', interval=0.1)
    time.sleep(2)
    
    # 点击搜索结果
    pyautogui.press('enter')
    time.sleep(3)
    
    # 点击输入框
    pyautogui.click(positions['input_box'])
    time.sleep(1)
    
    # 输入测试消息
    test_msg = f"微信自动化测试 {datetime.now().strftime('%H:%M:%S')}"
    pyautogui.write(test_msg, interval=0.05)
    time.sleep(1)
    
    # 点击发送
    pyautogui.click(positions['send_button'])
    time.sleep(2)
    
    print(f"   ✅ 已发送测试消息: '{test_msg}'")
    print("   📋 请检查文件传输助手是否收到")
    
    return True

def test_auto_reply_simulation(positions):
    """测试自动回复模拟"""
    print("\n🤖 测试2：自动回复模拟演示")
    
    print("   演示流程：")
    print("   1. 模拟客户发送'利率多少？'")
    print("   2. 系统自动回复利率信息")
    print("   3. 演示自动回复逻辑")
    
    # 这里只是演示，实际需要完整的消息处理系统
    from modules.keyword_matcher import KeywordMatcher
    from modules.message_processor import MessageProcessor
    
    # 加载贷款业务关键词
    loan_triggers = [
        {
            "keywords": ["利率", "利息", "年化", "费率"],
            "reply": "📊 利率根据您的资质浮动：\n• 优质客户：年化4.5%-6.8%\n• 普通客户：年化7.2%-9.6%\n• 需要根据您的征信具体评估"
        },
        {
            "keywords": ["额度", "能贷多少", "最高", "最多"],
            "reply": "💳 贷款额度：1万 - 50万元\n根据以下因素确定：\n1. 征信记录\n2. 收入证明\n3. 负债情况\n4. 工作稳定性"
        },
        {
            "keywords": ["期限", "多久", "多长时间", "几年"],
            "reply": "⏰ 贷款期限灵活：\n• 短期：3-12个月\n• 中期：1-3年\n• 长期：3-5年\n可根据您的还款能力选择"
        }
    ]
    
    matcher = KeywordMatcher(loan_triggers)
    processor = MessageProcessor(keyword_matcher=matcher)
    
    test_cases = [
        "利率多少？",
        "能贷多少钱？",
        "贷款期限多长？",
        "需要什么条件？"
    ]
    
    print("\n   自动回复演示：")
    for question in test_cases:
        reply = processor.process("test_user", question)
        print(f"   👤 客户: {question}")
        print(f"   🤖 回复: {reply[:50]}...")
        print()
    
    return True

def main():
    """主测试函数"""
    print("\n🎯 私人微信自动化测试")
    print("=" * 70)
    
    # 警告确认
    print("\n🚨 最后一次风险确认：")
    print("• 你是否使用测试小号？")
    print("• 你是否接受可能封号的风险？")
    print("• 你是否会立即停止如果出现异常？")
    
    confirm = input("\n确认以上三条？(y/N): ")
    if confirm.lower() != 'y':
        print("❌ 测试取消")
        return
    
    # 检查前提条件
    if not check_prerequisites():
        return
    
    # 校准位置
    positions = calibrate_positions()
    
    # 保存校准结果
    calibration_file = os.path.expanduser("~/wechat_calibration.txt")
    with open(calibration_file, 'w') as f:
        f.write(f"校准时间: {datetime.now()}\n")
        for key, pos in positions.items():
            f.write(f"{key}: {pos}\n")
    
    print(f"\n💾 校准结果已保存到: {calibration_file}")
    
    # 测试阶段1：基础发送
    print("\n📋 测试阶段1：基础功能测试")
    try:
        test_file_transfer_assistant(positions)
        print("✅ 阶段1完成")
    except Exception as e:
        print(f"❌ 阶段1失败: {e}")
        print("   建议检查微信窗口位置和权限")
        return
    
    # 测试阶段2：自动回复演示
    print("\n📋 测试阶段2：自动回复演示")
    try:
        test_auto_reply_simulation(positions)
        print("✅ 阶段2完成")
    except Exception as e:
        print(f"⚠️  阶段2演示失败（不影响基础功能）: {e}")
    
    # 后续建议
    print("\n" + "=" * 70)
    print("📋 测试完成建议")
    print("=" * 70)
    print("\n🎯 下一步测试计划：")
    print("1. 📅 今天：仅测试文件传输助手")
    print("2. 📅 明天：向测试好友发送消息（需准备测试好友）")
    print("3. 📅 第3天：简单自动回复测试")
    print("4. 📅 第1周：观察账号状态，确认安全")
    
    print("\n⚠️  重要提醒：")
    print("• 每天检查测试小号状态")
    print("• 发现任何异常（登录验证、功能限制）立即停止")
    print("• 准备至少3个备用测试小号")
    
    print("\n🔧 技术建议：")
    print("• 每次操作间隔至少1.5秒")
    print("• 避免高峰时段测试（上午10-12点，下午2-5点）")
    print("• 测试期间不要手动操作微信")
    
    print("\n💼 业务建议：")
    print("• 考虑使用企业微信（零风险，今天可上线）")
    print("• 如需个人微信自动化，建议使用专用业务号")
    print("• 重要客户建议人工维护")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🚫 测试被用户中断")
    except pyautogui.FailSafeException:
        print("\n\n🛑 鼠标移到屏幕左上角，测试已停止")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🔚 测试结束")
    print("📝 建议：删除校准文件和脚本，避免被检测")