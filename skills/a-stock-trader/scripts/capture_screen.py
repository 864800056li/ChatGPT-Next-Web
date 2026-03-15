#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动截图工具
大大怪将军为爸爸定制
"""

import sys
import pyautogui
import os
from datetime import datetime

def capture_screen(save_path=None):
    """截取屏幕"""
    try:
        # 截图
        screenshot = pyautogui.screenshot()
        
        # 生成文件名
        if save_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = f"~/Desktop/stock_screenshot_{timestamp}.png"
        
        # 展开路径
        save_path = os.path.expanduser(save_path)
        
        # 保存
        screenshot.save(save_path)
        
        print(f"✅ 截图保存成功: {save_path}")
        print(f"📐 图片尺寸: {screenshot.size}")
        print(f"📁 文件大小: {os.path.getsize(save_path)/1024/1024:.2f} MB")
        
        return save_path
        
    except Exception as e:
        print(f"❌ 截图失败: {e}")
        return None

if __name__ == "__main__":
    save_path = sys.argv[1] if len(sys.argv) > 1 else None
    capture_screen(save_path)
