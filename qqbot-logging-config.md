# 开启QQ聊天记录详细日志记录

## 配置说明
在 openclaw.json 中添加日志配置，记录所有收到的消息

## 配置项
```json
{
  "logging": {
    "level": "debug",
    "qqbot": {
      "logMessages": true,
      "logPath": "~/.openclaw/qqbot/logs/chat.log"
    }
  }
}
```

## 日志格式
```
[时间戳] [用户ID] [消息类型] [消息内容]
```

## 保存位置
- 日志文件：`~/.openclaw/qqbot/logs/chat.log`
- 每日归档：`~/.openclaw/qqbot/logs/chat-YYYY-MM-DD.log`

## 记忆库同步
- 定期将聊天记录同步到 `memory/daily/YYYY-MM-DD-chat.md`
- 重要信息提取到对应记忆文件
