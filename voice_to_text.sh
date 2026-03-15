#!/bin/bash
# Mac语音转文字快捷脚本
# 使用方法: ./voice_to_text.sh

echo "请说话，说完按回车结束..."
# 使用Mac的语音备忘录或听写功能
# 实际实现需要通过Automator或Shortcuts

# 临时方案：用ffmpeg录制音频，再用whisper本地识别
ffmpeg -f avfoundation -i ":0" -t 5 -acodec libopus /tmp/voice.ogg 2>/dev/null

echo "录音完成，识别中..."
# 这里调用whisper识别
python3 -c "
import sys
try:
    from faster_whisper import WhisperModel
    model = WhisperModel('tiny', device='cpu', compute_type='int8')
    segments, _ = model.transcribe('/tmp/voice.ogg', language='zh')
    for s in segments:
        print(s.text)
except Exception as e:
    print(f'错误: {e}')
"
