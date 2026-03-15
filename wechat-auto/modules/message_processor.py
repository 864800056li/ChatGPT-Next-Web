"""
消息处理器模块
整合所有组件，处理消息并生成回复
"""

import logging
from typing import Optional, Dict, Any
from .keyword_matcher import KeywordMatcher
from .document_retriever import DocumentRetriever
from .history_learner import HistoryLearner


class MessageProcessor:
    def __init__(self, keyword_matcher: KeywordMatcher,
                 document_retriever: Optional[DocumentRetriever] = None,
                 history_learner: Optional[HistoryLearner] = None):
        """
        初始化消息处理器
        
        Args:
            keyword_matcher: 关键词匹配器
            document_retriever: 文档检索器（可选）
            history_learner: 历史学习器（可选）
        """
        self.keyword_matcher = keyword_matcher
        self.document_retriever = document_retriever
        self.history_learner = history_learner
        
        self.logger = logging.getLogger(__name__)
        
        # 为组件设置日志
        self.keyword_matcher.logger = self.logger
        
        self.logger.info("消息处理器初始化完成")
    
    def process(self, user_id: str, message: str) -> Optional[str]:
        """
        处理消息并生成回复
        
        Args:
            user_id: 用户ID
            message: 用户消息
            
        Returns:
            回复内容，无回复则返回None
        """
        self.logger.debug(f"处理消息: user={user_id}, msg='{message}'")
        
        # 按优先级处理消息
        reply = None
        
        # 1. 关键词匹配（最高优先级）
        reply = self.keyword_matcher.match(message)
        if reply:
            self.logger.debug("通过关键词匹配生成回复")
            return reply
        
        # 2. 历史聊天记录学习（中优先级）
        if self.history_learner:
            reply = self.history_learner.get_reply_from_history(message)
            if reply:
                self.logger.debug("通过历史学习生成回复")
                return reply
        
        # 3. 文档检索（低优先级）
        if self.document_retriever:
            reply = self.document_retriever.get_reply_from_documents(message)
            if reply:
                self.logger.debug("通过文档检索生成回复")
                return reply
        
        # 4. 默认回复（如果都未匹配）
        if not reply:
            # 可以添加一些启发式规则
            reply = self._generate_default_reply(message)
            if reply:
                self.logger.debug("生成默认回复")
                return reply
        
        return None
    
    def _generate_default_reply(self, message: str) -> Optional[str]:
        """生成默认回复（一些启发式规则）"""
        message_lower = message.lower()
        
        # 检查是否包含问候语
        greetings = ['你好', '您好', 'hi', 'hello', '嗨', '在吗', '在吗？']
        if any(greet in message_lower for greet in greetings):
            return "您好！我是智能助手，有什么可以帮您？"
        
        # 检查是否包含感谢
        thanks = ['谢谢', '感谢', 'thanks', 'thank you']
        if any(t in message_lower for t in thanks):
            return "不客气！很高兴为您服务。"
        
        # 检查是否包含告别
        goodbyes = ['再见', '拜拜', '88', 'bye', 'goodbye']
        if any(g in message_lower for g in goodbyes):
            return "再见！有问题随时联系我。"
        
        # 检查是否是简单疑问句
        if any(marker in message for marker in ['吗？', '吗?', '？', '?']):
            return "请详细描述您的问题，我会尽力为您解答。"
        
        return None
    
    def add_keyword_trigger(self, keywords: list, reply: str):
        """动态添加关键词触发规则"""
        self.keyword_matcher.add_trigger(keywords, reply)
        self.logger.info(f"添加关键词触发规则: {keywords} -> {reply[:50]}...")
    
    def list_all_triggers(self) -> Dict:
        """列出所有触发规则"""
        result = {
            'keyword_triggers': self.keyword_matcher.list_triggers(),
            'document_retrieval_enabled': self.document_retriever is not None,
            'history_learning_enabled': self.history_learner is not None
        }
        
        if self.document_retriever:
            result['document_count'] = len(self.document_retriever.list_documents())
        
        if self.history_learner:
            stats = self.history_learner.get_stats()
            result['history_stats'] = stats
        
        return result
    
    def test_all_components(self, test_message: str = "测试") -> Dict[str, Any]:
        """测试所有组件是否正常工作"""
        results = {}
        
        # 测试关键词匹配
        keyword_reply = self.keyword_matcher.match(test_message)
        results['keyword_matcher'] = {
            'working': True,
            'reply': keyword_reply,
            'status': '匹配成功' if keyword_reply else '无匹配（正常）'
        }
        
        # 测试文档检索
        if self.document_retriever:
            try:
                doc_reply = self.document_retriever.get_reply_from_documents(test_message)
                results['document_retriever'] = {
                    'working': True,
                    'reply': doc_reply,
                    'document_count': len(self.document_retriever.list_documents())
                }
            except Exception as e:
                results['document_retriever'] = {
                    'working': False,
                    'error': str(e)
                }
        
        # 测试历史学习
        if self.history_learner:
            try:
                history_reply = self.history_learner.get_reply_from_history(test_message)
                stats = self.history_learner.get_stats()
                results['history_learner'] = {
                    'working': True,
                    'reply': history_reply,
                    'conversation_count': stats['conversation_count']
                }
            except Exception as e:
                results['history_learner'] = {
                    'working': False,
                    'error': str(e)
                }
        
        return results


# 测试函数
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    print("消息处理器测试")
    print("=" * 50)
    
    # 创建测试组件
    from keyword_matcher import KeywordMatcher
    
    # 关键词匹配器
    keyword_config = [
        {
            "keywords": ["测试", "test"],
            "reply": "收到测试消息，系统运行正常！"
        }
    ]
    
    matcher = KeywordMatcher(keyword_config)
    
    # 消息处理器
    processor = MessageProcessor(keyword_matcher=matcher)
    
    # 测试消息
    test_messages = [
        "测试一下",
        "你好",
        "这个产品怎么样？",
        "谢谢",
        "再见"
    ]
    
    print("处理测试消息:")
    for msg in test_messages:
        reply = processor.process("test_user", msg)
        if reply:
            print(f"  '{msg}' -> '{reply}'")
        else:
            print(f"  '{msg}' -> 无回复")
    
    # 测试组件状态
    print("\n组件状态测试:")
    status = processor.test_all_components()
    for component, info in status.items():
        print(f"  {component}: {'正常' if info['working'] else '异常'}")