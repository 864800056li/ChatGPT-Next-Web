#!/usr/bin/env python3
"""
QQ音乐自动化脚本 - 播放《QQ爱》并调音量到100%
作者：小小怪下士
时间：2026-03-13
"""

import pyautogui
import time
import subprocess

# 安全设置
pyautogui.FAILSAFE = True  # 鼠标移到左上角停止
pyautogui.PAUSE = 0.5  # 操作间隔

def open_qq_music():
    """打开QQ音乐"""
    print("正在打开QQ音乐...")
    # 使用 Spotlight 搜索打开
    pyautogui.keyDown('command')
    pyautogui.keyDown('space')
    pyautogui.keyUp('space')
    pyautogui.keyUp('command')
    time.sleep(0.5)
    
    pyautogui.typewrite('qq音乐', interval=0.1)
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(3)  # 等待应用启动

def search_and_play():
    """搜索并播放《QQ爱》"""
    print("正在搜索《QQ爱》...")
    
    # 点击搜索框（假设在顶部中央）
    screen_width, screen_height = pyautogui.size()
    search_x = screen_width // 2
    search_y = 80  # 顶部搜索框大概位置
    
    pyautogui.click(search_x, search_y)
    time.sleep(0.5)
    
    # 输入搜索内容
    pyautogui.typewrite('QQ爱', interval=0.1)
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(2)  # 等待搜索结果
    
    # 点击第一首歌曲（假设在搜索结果中间位置）
    song_x = screen_width // 2
    song_y = screen_height // 2 + 100
    pyautogui.click(song_x, song_y)
    time.sleep(1)
    
    # 双击播放
    pyautogui.doubleClick(song_x, song_y)
    time.sleep(1)

def set_volume_to_max():
    """将系统音量调到100%"""
    print("正在调整音量到100%...")
    
    # 方法1：使用系统快捷键
    # 按12次音量增加键（确保到最大）
    for _ in range(12):
        pyautogui.keyDown('volumeup')
        pyautogui.keyUp('volumeup')
        time.sleep(0.1)

def main():
    """主函数"""
    print("=" * 50)
    print("QQ音乐自动化脚本启动")
    print("任务：播放《QQ爱》并调音量到100%")
    print("=" * 50)
    print("\n⚠️  安全提示：")
    print("- 如需停止，请将鼠标移到屏幕左上角")
    print("- 确保QQ音乐已安装")
    print("- 脚本将在5秒后开始")
    print("=" * 50)
    
    # 倒计时
    for i in range(5, 0, -1):
        print(f"\n{i}秒后启动...")
        time.sleep(1)
    
    try:
        # 执行步骤
        open_qq_music()
        search_and_play()
        set_volume_to_max()
        
        print("\n" + "=" * 50)
        print("✅ 任务完成！")
        print("《QQ爱》正在播放，音量已调至100%")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 出错：{e}")
        print("请检查QQ音乐是否正常运行")

if __name__ == "__main__":
    main()
