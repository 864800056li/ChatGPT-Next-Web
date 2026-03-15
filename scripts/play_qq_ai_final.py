#!/usr/bin/env python3
"""
QQ音乐自动化 - 图像识别版
作者：小小怪下士
功能：通过截图识别播放按钮位置并点击
"""

import pyautogui
import cv2
import numpy as np
import time
import os

# 安全设置
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

def capture_screen():
    """截图"""
    screenshot = pyautogui.screenshot()
    screenshot.save('/tmp/qqmusic_screen.png')
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

def find_play_button(screen_img):
    """在屏幕上找到播放按钮"""
    # 转换为灰度图
    gray = cv2.cvtColor(screen_img, cv2.COLOR_BGR2GRAY)
    
    # 使用模板匹配查找播放按钮（三角形图标）
    # 这里需要有一个播放按钮的模板图片
    template_path = '/tmp/play_button_template.png'
    
    if not os.path.exists(template_path):
        print("模板图片不存在，使用坐标点击")
        return None
    
    template = cv2.imread(template_path, 0)
    if template is None:
        return None
    
    # 模板匹配
    result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    # 如果匹配度大于0.8，认为找到了
    if max_val > 0.8:
        h, w = template.shape
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        return (center_x, center_y)
    
    return None

def play_qq_music():
    """主函数"""
    print("=" * 50)
    print("QQ音乐自动化 - 图像识别版")
    print("=" * 50)
    
    # 1. 启动 QQ 音乐
    print("\n1. 启动 QQ 音乐...")
    os.system('open -a QQMusic.app')
    time.sleep(5)
    
    # 2. 搜索歌曲
    print("\n2. 搜索《心痛2009》...")
    screen_width, screen_height = pyautogui.size()
    
    # 点击搜索框
    pyautogui.click(screen_width // 2, 60)
    time.sleep(0.5)
    
    # 输入歌曲名
    pyautogui.hotkey('command', 'a')
    pyautogui.typewrite("心痛2009", interval=0.1)
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(3)
    
    # 3. 截图并查找播放按钮
    print("\n3. 截图查找播放按钮...")
    screen = capture_screen()
    
    # 4. 尝试找到播放按钮
    play_pos = find_play_button(screen)
    
    if play_pos:
        print(f"\n4. 找到播放按钮，位置: {play_pos}")
        pyautogui.click(play_pos)
        time.sleep(0.3)
        pyautogui.click(play_pos)
    else:
        print("\n4. 未找到播放按钮，使用默认坐标...")
        # 使用默认坐标（歌曲列表第一行）
        pyautogui.click(screen_width // 2 - 200, screen_height // 2 - 50)
        time.sleep(0.3)
        pyautogui.doubleClick(screen_width // 2 - 200, screen_height // 2 - 50)
    
    # 5. 调音量
    print("\n5. 音量调到100%...")
    for _ in range(15):
        pyautogui.press('volumeup')
        time.sleep(0.1)
    
    print("\n" + "=" * 50)
    print("✅ 执行完成！")
    print("=" * 50)

if __name__ == "__main__":
    print("\n⚠️  5秒后开始，鼠标移到左上角停止")
    time.sleep(5)
    play_qq_music()
