# 企业微信自动回复系统

基于企业微信API的智能自动回复系统，支持关键词触发、文档检索和历史聊天学习。

## ✨ 功能特性

- **关键词自动回复**：配置关键词→回复规则，立即生效
- **文档知识库检索**：从本地文档（PDF/Word/TXT/MD）中检索相关信息
- **历史聊天学习**：分析历史对话，学习回复模式
- **多级回复策略**：优先级：关键词 → 历史学习 → 文档检索 → 默认回复
- **企业微信官方API**：稳定可靠，无封号风险

## 📋 快速开始

### 1. 环境准备
```bash
# 克隆或下载项目
cd wechat-auto

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 企业微信配置
1. 登录[企业微信管理后台](https://work.weixin.qq.com/)
2. 进入「应用管理」→「自建应用」→「创建应用」
3. 获取以下信息：
   - **企业ID** (CorpID)
   - **应用Secret** (Secret)
   - **应用ID** (AgentId)

### 3. 配置文件
```bash
# 复制配置文件模板
cp config/config_template.yaml config/config.yaml

# 编辑配置文件，填入企业微信信息
```

### 4. 运行测试
```bash
python main.py
```

## ⚙️ 配置说明

### 基础配置
```yaml
wecom:
  corp_id: "你的企业ID"
  secret: "你的应用Secret"
  agent_id: 1000002
```

### 关键词触发规则
```yaml
keyword_triggers:
  - keywords: ["价格", "多少钱", "报价"]
    reply: "您好！价格信息如下..."
  - keywords: ["发货", "配送时间"]
    reply: "付款后24小时内发货..."
```

### 启用高级功能
```yaml
enable_document_retrieval: true
document_path: "./data/documents/"

enable_chat_history_learning: true  
chat_history_path: "./data/history/"
```

## 📁 项目结构
```
wechat-auto/
├── main.py                 # 主程序入口
├── config/
│   ├── config_template.yaml # 配置模板
│   └── config.yaml         # 实际配置（需创建）
├── modules/                # 功能模块
│   ├── wecom_client.py     # 企业微信客户端
│   ├── keyword_matcher.py  # 关键词匹配
│   ├── document_retriever.py # 文档检索
│   ├── history_learner.py  # 历史学习
│   └── message_processor.py # 消息处理器
├── data/                   # 数据目录
│   ├── documents/          # 知识库文档
│   └── history/            # 历史聊天记录
├── logs/                   # 日志目录
└── requirements.txt        # 依赖列表
```

## 📚 数据准备

### 1. 文档知识库
将产品文档、FAQ、说明文档放入 `data/documents/` 目录，支持格式：
- PDF (.pdf)
- Word (.docx, .doc)
- 纯文本 (.txt)
- Markdown (.md)

### 2. 历史聊天记录
将历史聊天记录放入 `data/history/` 目录，支持格式：
- JSON: `[{"question": "问题", "answer": "回复"}, ...]`
- CSV: 包含 question/answer 列的CSV文件
- 文本: Q: 问题 A: 回复 格式

## 🚀 运行模式

### 测试模式
```bash
python main.py
```
运行测试用例，验证所有组件是否正常工作。

### 生产模式
需要实现企业微信消息监听（待完善）：
- 回调模式：配置企业微信回调URL
- 轮询模式：定期拉取新消息

## 🔧 扩展开发

### 添加新的回复策略
1. 在 `modules/` 目录下创建新模块
2. 实现 `get_reply_from_xxx(message)` 方法
3. 在 `message_processor.py` 中集成

### 升级文档检索
1. 安装向量检索库：`pip install sentence-transformers chromadb`
2. 修改 `document_retriever.py` 使用向量相似度搜索

### 集成大模型
1. 安装OpenAI/Local LLM SDK
2. 创建 `llm_enhancer.py` 模块
3. 使用LLM润色回复或生成新回复

## 📊 监控与日志

- 日志文件：`logs/wechat_auto.log`
- 日志级别可在配置中调整
- 关键操作都会记录日志

## ⚠️ 注意事项

1. **企业微信API限制**：注意调用频率限制（约2000次/分钟）
2. **文档格式**：确保文档编码为UTF-8
3. **历史数据质量**：高质量的历史对话数据能显著提升学习效果
4. **测试环境**：建议先用测试应用进行开发测试

## 📞 支持与反馈

如有问题，请：
1. 检查日志文件 `logs/wechat_auto.log`
2. 确认企业微信配置正确
3. 确保依赖库已正确安装

---

**提示**：首次运行时，系统会进入测试模式。配置企业微信API后，才能使用真实消息处理功能。