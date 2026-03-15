#!/usr/bin/env python3
"""
QQ音乐自动化 - 使用图像识别定位按钮
作者：小小怪下士
"""

import pyautogui
import time
import os

# 安全设置
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

def take_screenshot():
    """截图保存"""
    screenshot = pyautogui.screenshot()
    screenshot.save('/tmp/qqmusic_screenshot.png')
    return screenshot

def find_and_click(image_path, confidence=0.8):
    """在屏幕上查找图像并点击"""
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if location:
            center = pyautogui.center(location)
            pyautogui.click(center)
            return True
    except Exception as e:
        print(f"查找失败: {e}")
    return False

def play_qq_music():
    """主函数"""
    print("=" * 50)
    print("QQ音乐自动化 - 图像识别版")
    print("=" * 50)
    
    # 1. 启动 QQ 音乐
    print("\n1. 启动 QQ 音乐...")
    os.system('open -a QQMusic.app')
    time.sleep(5)
    
    # 2. 截图查看当前状态
    print("\n2. 截图...")
    take_screenshot()
    
    # 3. 点击搜索框（使用坐标，因为搜索框位置固定）
    print("\n3. 点击搜索框...")
    screen_width, screen_height = pyautogui.size()
    search_x = screen_width // 2
    search_y = 60
    pyautogui.click(search_x, search_y)
    time.sleep(0.5)
    
    # 4. 输入歌曲名
    print("\n4. 输入 '心痛2009'...")
    pyautogui.hotkey('command', 'a')
    pyautogui.typewrite("心痛2009", interval=0.1)
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(3)
    
    # 5. 截图查看搜索结果
    print("\n5. 截图查看搜索结果...")
    take_screenshot()
    
    # 6. 尝试点击播放按钮（使用相对坐标）
    print("\n6. 尝试点击播放按钮...")
    # 播放按钮通常在搜索结果左侧
    play_x = screen_width // 2 - 200
    play_y = screen_height // 2 - 100
    pyautogui.click(play_x, play_y)
    time.sleep(0.5)
    pyautogui.doubleClick(play_x, play_y)
    
    # 7. 音量最大
    print("\n7. 音量调到最大...")
    for _ in range(15):
        pyautogui.press('volumeup')
        time.sleep(0.1)
    
    print("\n" + "=" * 50)
    print("✅ 执行完成！")
    print("截图保存在: /tmp/qqmusic_screenshot.png")
    print("=" * 50)

if __name__ == "__main__":
    print("\n⚠️  5秒后开始执行，请将鼠标移到左上角停止")
    time.sleep(5)
    play_qq_music()
