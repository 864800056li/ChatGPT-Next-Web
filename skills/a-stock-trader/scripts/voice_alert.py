#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音播报工具
大大怪将军为爸爸定制
"""

import sys
import os
import subprocess

def voice_alert(text, voice="Ting-Ting"):
    """语音播报"""
    try:
        # 生成AIFF
        aiff_path = "/tmp/voice_alert.aiff"
        subprocess.run([
            "say", 
            "-v", voice,
            text,
            "-o", aiff_path
        ], check=True)
        
        # 转换为MP3
        mp3_path = "/tmp/voice_alert.mp3"
        subprocess.run([
            "ffmpeg",
            "-i", aiff_path,
            mp3_path,
            "-y"
        ], check=True, capture_output=True)
        
        print(f"✅ 语音生成成功: {mp3_path}")
        print(f"🎙️ 播报内容: {text}")
        
        return mp3_path
        
    except Exception as e:
        print(f"❌ 语音生成失败: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python voice_alert.py <播报内容>")
        print("示例: python voice_alert.py '茅台涨到1800了！'")
        sys.exit(1)
    
    text = sys.argv[1]
    voice_alert(text)
