#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小Q微信助手 - Python版
使用 itchat 库
"""

import itchat
import time
import json
import os
from datetime import datetime

# 配置
CONFIG = {
    "welcome_message": """你好！我是李志强的助手小Q🤖

志强正在忙，我先来接待你～

请告诉我：
1. 你怎么认识志强的？
2. 有什么我可以转达的？

我会第一时间通知他！""",
    
    "keywords": {
        "价格": "关于价格/合作，请留下你的联系方式，志强会亲自联系你。",
        "合作": "感谢关注！请简单介绍你的项目和需求，我转达给志强。",
        "产品": "我们的产品资料正在整理中，请留下邮箱，我发给你。",
        "在吗": "在的！志强忙的时候我会先回复，重要事情我会立刻转达。",
        "你好": "你好！我是小Q，志强的AI助手。有什么可以帮你的？",
        "您好": "您好！我是小Q，志强的AI助手。有什么可以帮你的？",
    },
    
    "default_reply": "收到！我会转达给志强，他忙完会回复你。",
    
    "group_keywords": ["志强", "李总", "合作", "紧急", "小Q"]
}

def log(msg):
    """记录日志"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{now}] {msg}"
    print(log_msg)
    
    # 写入文件
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    with open(os.path.join(log_dir, "bot.log"), "a", encoding="utf-8") as f:
        f.write(log_msg + "\n")

def get_keyword_reply(content):
    """获取关键词回复"""
    if not content:
        return None
    
    content_lower = content.lower()
    for keyword, reply in CONFIG["keywords"].items():
        if keyword in content_lower:
            return reply
    return None

@itchat.msg_register(itchat.content.TEXT)
def handle_text(msg):
    """处理文本消息"""
    from_user = msg["FromUserName"]
    content = msg["Content"]
    
    # 跳过自己的消息
    if msg["FromUserName"] == itchat.get_friends()[0]["UserName"]:
        return
    
    # 群消息
    if msg["FromUserName"].startswith("@@"):
        handle_group_msg(msg)
        return
    
    # 私聊消息
    user_info = itchat.search_friends(userName=from_user)
    nickname = user_info[0]["NickName"] if user_info else "Unknown"
    log(f"[私聊] {nickname}: {content}")
    
    # 关键词回复
    reply = get_keyword_reply(content)
    if reply:
        itchat.send(reply, from_user)
        log(f"🤖 回复: {reply[:30]}...")
    else:
        itchat.send(CONFIG["default_reply"], from_user)
        log("🤖 默认回复")

def handle_group_msg(msg):
    """处理群消息"""
    from_user = msg["FromUserName"]
    content = msg["Content"]
    
    # 获取群信息
    group_info = itchat.search_chatrooms(userName=from_user)
    group_name = group_info[0]["NickName"] if group_info else "Unknown"
    
    # 获取发送者
    actual_user = msg.get("ActualUserName", "")
    actual_nick = msg.get("ActualNickName", "Unknown")
    
    log(f"[群:{group_name}] {actual_nick}: {content}")
    
    # 监控关键词
    for keyword in CONFIG["group_keywords"]:
        if keyword in content:
            alert = f"【群监控】群'{group_name}' 中 {actual_nick} 提到'{keyword}': {content}"
            log(f"🔔 {alert}")
            
            # 转发到文件传输助手
            itchat.send(alert, "filehelper")

@itchat.msg_register(itchat.content.FRIENDS)
def handle_friend_request(msg):
    """处理好友申请"""
    log(f"📝 收到好友申请")
    
    # 自动通过
    try:
        itchat.add_friend(msg["RecommendInfo"]["UserName"], status=3)
        log("✅ 已通过好友申请")
        
        # 等待一下
        time.sleep(2)
        
        # 发送欢迎语
        itchat.send(CONFIG["welcome_message"], msg["RecommendInfo"]["UserName"])
        log("💬 已发送欢迎语")
        
        # 通知我
        itchat.send(f"🎉 新好友添加成功！", "filehelper")
    except Exception as e:
        log(f"❌ 处理好友申请失败: {e}")

def main():
    """主函数"""
    log("🤖 小Q微信助手启动中...")
    log("📱 请扫码登录")
    
    # 启动
    itchat.auto_login(
        hotReload=True,  # 热登录，短时间重连不需要扫码
        enableCmdQR=2    # 在终端显示二维码
    )
    
    log("✅ 登录成功！")
    log("🚀 机器人开始运行...")
    
    # 发送启动通知
    itchat.send("🤖 小Q已上线！\n功能：\n- 自动通过好友\n- 关键词回复\n- 群监控\n- 每日股票简报", "filehelper")
    
    # 保持运行
    itchat.run()

if __name__ == "__main__":
    main()
