#!/usr/bin/env python3
"""
新网合伙人小程序 - 图片获取脚本
⚠️ 高风险：微信自动化可能导致封号！仅用测试小号！
"""

import pyautogui
import time
import os
import sys
from datetime import datetime

print("=" * 70)
print("⚠️  ⚠️  ⚠️  高风险警告 ⚠️  ⚠️  ⚠️")
print("微信自动化可能导致永久封号！")
print("仅使用测试小号！不要用主账号！")
print("贷款业务账号监控更严格！")
print("=" * 70)

# 安全设置
pyautogui.FAILSAFE = True  # 鼠标移到左上角停止脚本
pyautogui.PAUSE = 1.0      # 每次操作间隔1秒

def check_prerequisites():
    """检查前提条件"""
    print("\n🔍 检查前提条件：")
    print("1. 微信是否已登录测试小号？")
    print("2. 是否已打开微信到主界面？")
    print("3. 屏幕是否未锁屏？")
    print("4. 是否准备好随时停止（鼠标移左上角）？")
    
    input("\n按回车键继续（Ctrl+C取消）...")

def locate_and_click(image_path, confidence=0.8, timeout=10):
    """定位图片并点击"""
    print(f"🔍 查找: {image_path}")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                print(f"✅ 找到，点击位置: {center}")
                pyautogui.click(center)
                return True
        except pyautogui.ImageNotFoundException:
            pass
        
        time.sleep(0.5)
    
    print(f"❌ 未找到: {image_path}")
    return False

def main():
    """主函数"""
    print("\n🎯 获取新网合伙人图片")
    print("=" * 70)
    
    # 步骤说明
    steps = [
        "1. 点击微信左侧「小程序」图标",
        "2. 搜索「新网合伙人」",
        "3. 进入小程序",
        "4. 查找「好人贷」产品",
        "5. 点击「当面邀请」",
        "6. 截图保存",
        "7. 查找「好人贷尊享版」产品",
        "8. 点击「当面邀请」",
        "9. 截图保存",
        "10. 发送到文件传输助手"
    ]
    
    print("\n📋 执行步骤：")
    for step in steps:
        print(f"  {step}")
    
    print("\n💡 提示：")
    print("  • 脚本将模拟鼠标移动和点击")
    print("  • 保持微信窗口在最前")
    print("  • 不要操作鼠标键盘干扰脚本")
    print("  • 随时可移动鼠标到屏幕左上角停止")
    
    # 确认执行
    confirm = input("\n🚨 确认执行？(y/N): ")
    if confirm.lower() != 'y':
        print("取消执行")
        return
    
    # 检查前提
    check_prerequisites()
    
    print("\n🚀 开始执行...")
    
    # 步骤1：点击小程序图标（假设在左侧）
    print("\n📱 步骤1: 点击小程序图标")
    # 这里需要实际的小程序图标截图
    # 暂时用坐标代替（需要用户校准）
    print("⚠️  需要先校准小程序图标位置")
    input("请手动将鼠标移到小程序图标上，按回车记录位置...")
    mini_program_pos = pyautogui.position()
    print(f"✅ 记录位置: {mini_program_pos}")
    pyautogui.click(mini_program_pos)
    time.sleep(2)
    
    # 步骤2：搜索新网合伙人
    print("\n🔍 步骤2: 搜索新网合伙人")
    # 点击搜索框
    print("⚠️  需要校准搜索框位置")
    input("请手动将鼠标移到搜索框上，按回车记录位置...")
    search_pos = pyautogui.position()
    pyautogui.click(search_pos)
    time.sleep(1)
    
    # 输入搜索词
    pyautogui.write('新网合伙人', interval=0.1)
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(3)
    
    # 步骤3：进入小程序
    print("\n📱 步骤3: 进入小程序")
    # 点击第一个结果
    print("⚠️  需要校准第一个结果位置")
    input("请手动将鼠标移到第一个结果上，按回车记录位置...")
    first_result_pos = pyautogui.position()
    pyautogui.click(first_result_pos)
    time.sleep(5)  # 等待小程序加载
    
    print("\n📋 后续步骤需要页面加载后继续...")
    print("由于页面动态变化，建议手动操作以下步骤：")
    print("1. 在小程序内找到「好人贷」")
    print("2. 找到「当面邀请」并截图")
    print("3. 找到「好人贷尊享版」")
    print("4. 找到「当面邀请」并截图")
    print("5. 发送到文件传输助手")
    
    print("\n🎯 脚本已完成基础导航，请手动完成后续操作")
    
    # 截图保存位置
    screenshot_dir = os.path.expanduser("~/Desktop/新网合伙人截图")
    os.makedirs(screenshot_dir, exist_ok=True)
    
    print(f"\n💾 截图将保存到: {screenshot_dir}")
    print("手动截图快捷键: Cmd+Shift+4")
    
    # 等待用户完成
    input("\n📝 手动操作完成后按回车结束脚本...")
    
    print("\n✅ 任务完成！")
    print(f"请检查桌面文件夹: {screenshot_dir}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🚫 脚本被用户中断")
    except Exception as e:
        print(f"\n❌ 脚本执行出错: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🔚 脚本结束")
    print("⚠️  建议删除此脚本，避免被微信检测")