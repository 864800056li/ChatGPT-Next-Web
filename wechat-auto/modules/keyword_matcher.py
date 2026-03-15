"""
关键词匹配模块
支持精确匹配、模糊匹配、正则表达式
"""

import re
from typing import List, Dict, Optional


class KeywordMatcher:
    def __init__(self, triggers_config: List[Dict]):
        """
        初始化关键词匹配器
        
        Args:
            triggers_config: 触发规则配置列表
                [
                    {
                        "keywords": ["价格", "多少钱"],
                        "reply": "回复内容"
                    },
                    ...
                ]
        """
        self.triggers = []
        for trigger in triggers_config:
            self.triggers.append({
                'patterns': [self._create_pattern(kw) for kw in trigger['keywords']],
                'reply': trigger['reply']
            })
        
        self.logger = None  # 将在外部设置
        
    def _create_pattern(self, keyword: str):
        """将关键词转换为匹配模式（支持简单模糊匹配）"""
        # 移除首尾空格
        keyword = keyword.strip()
        
        # 如果是正则表达式（以/开头结尾）
        if keyword.startswith('/') and keyword.endswith('/'):
            return re.compile(keyword[1:-1], re.IGNORECASE)
        
        # 普通关键词：转换为忽略大小写的正则
        # 允许关键词前后有少量其他字符（模糊匹配）
        escaped = re.escape(keyword)
        pattern = f".*{escaped}.*"
        return re.compile(pattern, re.IGNORECASE)
    
    def match(self, message: str) -> Optional[str]:
        """
        匹配消息中的关键词
        
        Args:
            message: 用户消息
            
        Returns:
            匹配到的回复内容，未匹配到则返回None
        """
        message = message.strip()
        
        for trigger in self.triggers:
            for pattern in trigger['patterns']:
                if pattern.search(message):
                    if self.logger:
                        self.logger.debug(f"关键词匹配成功: {pattern.pattern} -> {message}")
                    return trigger['reply']
        
        return None
    
    def add_trigger(self, keywords: List[str], reply: str):
        """动态添加触发规则"""
        self.triggers.append({
            'patterns': [self._create_pattern(kw) for kw in keywords],
            'reply': reply
        })
    
    def remove_trigger(self, index: int):
        """移除指定索引的触发规则"""
        if 0 <= index < len(self.triggers):
            self.triggers.pop(index)
    
    def list_triggers(self) -> List[Dict]:
        """列出所有触发规则"""
        result = []
        for i, trigger in enumerate(self.triggers):
            keywords = []
            for pattern in trigger['patterns']:
                # 从正则模式中提取原始关键词（简化显示）
                pattern_str = pattern.pattern
                if pattern_str.startswith('.*') and pattern_str.endswith('.*'):
                    keyword = pattern_str[2:-2]
                    keyword = re.sub(r'\\.', lambda m: m.group(0)[1], keyword)  # 取消转义
                    keywords.append(keyword)
                else:
                    keywords.append(f"/{pattern_str}/")
            
            result.append({
                'index': i,
                'keywords': keywords,
                'reply': trigger['reply']
            })
        
        return result


# 测试函数
if __name__ == "__main__":
    # 测试配置
    test_config = [
        {
            "keywords": ["价格", "多少钱", "报价"],
            "reply": "您好！价格信息如下..."
        },
        {
            "keywords": ["发货", "配送", "多久到"],
            "reply": "发货时间一般为24小时内..."
        }
    ]
    
    matcher = KeywordMatcher(test_config)
    
    # 测试用例
    test_messages = [
        "这个产品多少钱？",
        "请问价格是多少",
        "什么时候发货",
        "配送要多久",
        "你们公司地址在哪"
    ]
    
    print("关键词匹配测试：")
    for msg in test_messages:
        reply = matcher.match(msg)
        if reply:
            print(f"  '{msg}' -> '{reply}'")
        else:
            print(f"  '{msg}' -> 无匹配")