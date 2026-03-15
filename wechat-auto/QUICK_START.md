# 🚀 5分钟快速启动指南

## 第一步：安装系统
```bash
# 进入项目目录
cd ~/.openclaw/workspace/wechat-auto

# 运行安装脚本
bash setup.sh  # Mac/Linux
# 或双击 setup.bat  # Windows

# 激活虚拟环境（安装完成后）
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows
```

## 第二步：配置企业微信（3分钟）
1. **登录** [企业微信管理后台](https://work.weixin.qq.com/)
2. **创建应用**：应用管理 → 自建应用 → 创建应用
3. **获取三个信息**：
   - **企业ID** (CorpID)：在"我的企业"-"企业信息"查看
   - **应用Secret** (Secret)：在应用详情页面
   - **应用ID** (AgentId)：应用详情页面的AgentId

## 第三步：填写配置文件（1分钟）
```bash
# 复制示例配置
cp config/config_example.yaml config/config.yaml

# 编辑配置文件，填入你的信息
# 使用你喜欢的编辑器：vi, nano, 或文本编辑器
```

**最少需要修改**：
```yaml
wecom:
  corp_id: "你的企业ID"          # ← 修改这里
  secret: "你的应用Secret"       # ← 修改这里  
  agent_id: 1000002             # ← 修改这里
```

## 第四步：添加你的业务关键词（1分钟）
编辑 `config/config.yaml` 中的 `keyword_triggers`，例如：
```yaml
keyword_triggers:
  - keywords: ["价格", "多少钱"]  # ← 你的客户常问的问题
    reply: "您好！我们的价格是..."  # ← 你的标准回答
```

## 第五步：运行测试
```bash
# 测试关键词匹配功能
python test_quick.py

# 运行主程序（测试模式）
python main.py
```

## 🎯 最简启动方案
如果觉得以上步骤复杂，只需做这两步：

### 方案A：先体验再配置
1. **直接运行测试**：`python test_quick.py`
2. **查看默认关键词回复效果**
3. **决定是否继续配置企业微信**

### 方案B：先配置关键词
1. **告诉我3个最常见客户问题+你的回答**
2. **我帮你配置到系统中**
3. **立即看到自动回复效果**

## 📞 需要帮助？
- **企业微信不会注册**：我可以截图指导
- **配置文件不会编辑**：发我信息，我帮你生成
- **想用个人微信**：有封号风险，需特殊配置
- **没有历史数据**：先用手动配置的关键词

## ⏱️ 时间估算
- 完全新手：15-20分钟（含学习时间）
- 有技术基础：5-10分钟
- 只想看效果：2分钟（运行测试脚本）

## 💡 提示
- 即使不配置企业微信，**关键词匹配功能也可独立使用**
- 可集成到其他平台（需简单适配）
- 系统已包含**示例数据和文档**，可直接参考

---

**现在就开始**：
```bash
cd ~/.openclaw/workspace/wechat-auto
python test_quick.py
```

运行后告诉我结果，我指导下一步！