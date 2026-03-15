#!/usr/bin/env python3
"""
QQ音乐自动化 - 使用 ctypes 直接控制鼠标
作者：小小怪下士
"""

import ctypes
import ctypes.util
import time
import os

# 加载 Carbon 框架（Mac 原生 API）
carbon = ctypes.CDLL(ctypes.util.find_library('Carbon'))

# 定义鼠标事件常量
kCGMouseButtonLeft = 0
kCGEventMouseMoved = 5
kCGEventLeftMouseDown = 1
kCGEventLeftMouseUp = 2

# 获取屏幕尺寸
def get_screen_size():
    # 使用 Quartz 获取屏幕尺寸
    try:
        from Quartz import CGMainDisplayID, CGDisplayPixelsWide, CGDisplayPixelsHigh
        main_display = CGMainDisplayID()
        width = CGDisplayPixelsWide(main_display)
        height = CGDisplayPixelsHigh(main_display)
        return width, height
    except:
        # 如果 Quartz 不可用，使用默认值
        return 1920, 1080

def mouse_move(x, y):
    """移动鼠标"""
    # 使用 AppleScript 移动鼠标
    os.system(f'osascript -e "tell application \\"System Events\\" to tell process \\"QQMusic\\" to click at {{{x}, {y}}}"')

def mouse_click(x, y):
    """点击鼠标"""
    mouse_move(x, y)
    time.sleep(0.1)
    # 使用 AppleScript 点击
    os.system(f'osascript -e "tell application \\"System Events\\" to tell process \\"QQMusic\\" to click at {{{x}, {y}}}"')

def play_qq_music():
    """主函数"""
    print("=" * 50)
    print("QQ音乐自动化 - 直接鼠标控制")
    print("=" * 50)
    
    # 窗口位置和大小（从 AppleScript 获取）
    win_x, win_y = 271, 39
    win_w, win_h = 1280, 874
    
    # 1. 启动 QQ 音乐
    print("\n1. 启动 QQ 音乐...")
    os.system('open -a QQMusic.app')
    time.sleep(5)
    
    # 2. 点击搜索框（相对窗口位置）
    print("\n2. 点击搜索框...")
    search_x = win_x + win_w // 2
    search_y = win_y + 60
    mouse_click(search_x, search_y)
    time.sleep(0.5)
    
    # 3. 使用 AppleScript 输入文字
    print("\n3. 输入《心痛2009》...")
    os.system('osascript -e "tell application \\"System Events\\" to keystroke \\"心痛2009\\""')
    time.sleep(0.5)
    os.system('osascript -e "tell application \\"System Events\\" to key code 36"')
    time.sleep(3)
    
    # 4. 点击播放按钮（歌曲列表第一行）
    print("\n4. 点击播放...")
    # 播放按钮在歌曲列表左侧，大约在窗口左 1/4 处
    play_x = win_x + 200
    play_y = win_y + 200
    mouse_click(play_x, play_y)
    time.sleep(0.2)
    mouse_click(play_x, play_y)
    time.sleep(0.5)
    
    # 5. 调音量
    print("\n5. 音量调到100%...")
    for _ in range(15):
        os.system('osascript -e "tell application \\"System Events\\" to key code 144"')
        time.sleep(0.1)
    
    print("\n" + "=" * 50)
    print("✅ 执行完成！")
    print("=" * 50)

if __name__ == "__main__":
    print("\n⚠️  5秒后开始...")
    time.sleep(5)
    play_qq_music()
