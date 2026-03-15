# 小Q微信助手 - 部署说明

## 方案调整

由于 Mac 微信 Hook 方案需要：
1. 微信客户端保持在线
2. 付费购买 Hook 授权
3. 有封号风险

**改为使用：WeChaty + 网页版微信协议**

## 部署步骤

### 1. 安装依赖
```bash
cd /Users/dadaguaijiangjun/.openclaw/workspace/wechat-bot
npm install wechaty wechaty-puppet-wechat
```

### 2. 启动机器人
```bash
npm start
```

### 3. 扫码登录
- 运行后会显示二维码
- 用微信扫码登录
- 保持微信网页版在线

## 功能

- ✅ 自动通过好友申请
- ✅ 关键词自动回复
- ✅ 新好友欢迎语
- ✅ 群消息监控
- ✅ 定时发朋友圈

## 注意事项

- 需要保持微信网页版在线
- 每天可能需要重新扫码登录
- 支持多账号切换

