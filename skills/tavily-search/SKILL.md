# SKILL.md - Tavily Search

## Description
联网搜索技能，实时检索全网最新资讯。

## When to Use
- 需要搜索新闻、价格、方案时
- 实时获取互联网信息
- 替代Brave搜索

## Usage

### 搜索
```
使用web_search工具进行搜索
query: 搜索关键词
count: 结果数量
```

### Example
搜索最新股票信息：
```
web_search query="三房巷 股票 最新消息" count=5
```

## Note
当前使用系统内置的web_search工具（Brave搜索），无需额外安装。
如需Tavily API，需配置TAVILY_API_KEY。
