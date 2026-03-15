"""
历史聊天记录学习模块
从历史聊天记录中学习回复模式
"""

import json
import csv
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging


class HistoryLearner:
    def __init__(self, history_path: str):
        """
        初始化历史学习器
        
        Args:
            history_path: 历史聊天记录目录路径
        """
        self.history_path = Path(history_path)
        self.conversations = []  # 聊天记录缓存
        self.reply_patterns = {}  # 学习到的回复模式
        
        self.logger = logging.getLogger(__name__)
        
        # 确保目录存在
        self.history_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"历史学习器初始化，路径: {history_path}")
    
    def load_history(self) -> bool:
        """加载所有历史聊天记录"""
        try:
            self.conversations = []
            
            for file_path in self.history_path.rglob('*'):
                if file_path.is_file():
                    if file_path.suffix.lower() == '.json':
                        self._load_json_history(file_path)
                    elif file_path.suffix.lower() == '.csv':
                        self._load_csv_history(file_path)
                    elif file_path.suffix.lower() == '.txt':
                        self._load_text_history(file_path)
            
            self.logger.info(f"已加载 {len(self.conversations)} 条历史对话")
            
            # 学习回复模式
            self._learn_patterns()
            
            return True
            
        except Exception as e:
            self.logger.error(f"加载历史记录失败: {e}")
            return False
    
    def _load_json_history(self, file_path: Path):
        """加载JSON格式的历史记录"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                for conv in data:
                    if isinstance(conv, dict) and 'question' in conv and 'answer' in conv:
                        self.conversations.append({
                            'question': conv['question'],
                            'answer': conv['answer'],
                            'source': file_path.name
                        })
        except Exception as e:
            self.logger.error(f"读取JSON文件失败 {file_path}: {e}")
    
    def _load_csv_history(self, file_path: Path):
        """加载CSV格式的历史记录"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 尝试常见列名
                    question = row.get('question') or row.get('Question') or row.get('用户') or row.get('客户')
                    answer = row.get('answer') or row.get('Answer') or row.get('回复') or row.get('客服')
                    
                    if question and answer:
                        self.conversations.append({
                            'question': question,
                            'answer': answer,
                            'source': file_path.name
                        })
        except Exception as e:
            self.logger.error(f"读取CSV文件失败 {file_path}: {e}")
    
    def _load_text_history(self, file_path: Path):
        """加载文本格式的历史记录（简单Q:A格式）"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 尝试解析 Q: ... A: ... 格式
            pattern = r'(?:Q:|问：|问题：|客户：)\s*(.*?)\s*(?:A:|答：|回答：|客服：)\s*(.*?)(?=\n\s*(?:Q:|问：|问题：|客户：)|$)'
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            
            for q, a in matches:
                if q.strip() and a.strip():
                    self.conversations.append({
                        'question': q.strip(),
                        'answer': a.strip(),
                        'source': file_path.name
                    })
        except Exception as e:
            self.logger.error(f"读取文本文件失败 {file_path}: {e}")
    
    def _learn_patterns(self):
        """从历史对话中学习回复模式"""
        self.reply_patterns = {}
        
        # 1. 关键词到回复的映射
        keyword_to_replies = {}
        
        for conv in self.conversations:
            question = conv['question'].lower()
            answer = conv['answer']
            
            # 提取关键词（简单版本：取重要词汇）
            words = re.findall(r'\b\w+\b', question)
            
            # 过滤停用词
            stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
            keywords = [w for w in words if w not in stop_words and len(w) > 1]
            
            for keyword in keywords:
                if keyword not in keyword_to_replies:
                    keyword_to_replies[keyword] = []
                keyword_to_replies[keyword].append(answer)
        
        # 2. 计算每个关键词的典型回复
        for keyword, replies in keyword_to_replies.items():
            if len(replies) >= 2:  # 至少出现2次才有统计意义
                # 简单去重并计数
                reply_counts = {}
                for reply in replies:
                    # 简化回复用于统计
                    simple_reply = reply[:50]  # 取前50字符
                    reply_counts[simple_reply] = reply_counts.get(simple_reply, 0) + 1
                
                # 取最常见的回复
                most_common = max(reply_counts.items(), key=lambda x: x[1])
                self.reply_patterns[keyword] = {
                    'reply': replies[0],  # 使用完整的第一条回复
                    'count': len(replies),
                    'confidence': min(1.0, len(replies) / 10)  # 置信度，最多1.0
                }
        
        self.logger.info(f"学习了 {len(self.reply_patterns)} 个回复模式")
    
    def find_similar_question(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        查找与查询最相似的历史问题
        
        Args:
            query: 用户查询
            top_k: 返回最相似的k个问题
            
        Returns:
            相似问题列表
        """
        if not self.conversations:
            self.load_history()
        
        query_lower = query.lower()
        similarities = []
        
        for conv in self.conversations:
            question_lower = conv['question'].lower()
            
            # 计算相似度（简单版本）
            score = self._calculate_similarity(query_lower, question_lower)
            
            if score > 0:
                similarities.append({
                    'question': conv['question'],
                    'answer': conv['answer'],
                    'score': score,
                    'source': conv['source']
                })
        
        # 按相似度排序
        similarities.sort(key=lambda x: x['score'], reverse=True)
        
        return similarities[:top_k]
    
    def _calculate_similarity(self, query: str, question: str) -> float:
        """计算两个问题的相似度"""
        # 1. 词重叠
        query_words = set(re.findall(r'\b\w+\b', query))
        question_words = set(re.findall(r'\b\w+\b', question))
        
        if not query_words or not question_words:
            return 0
        
        # Jaccard相似度
        intersection = query_words.intersection(question_words)
        union = query_words.union(question_words)
        
        jaccard = len(intersection) / len(union)
        
        # 2. 考虑词序相似性（简单版本）
        # 这里可以扩展更复杂的相似度计算
        
        return jaccard
    
    def get_reply_from_history(self, query: str) -> Optional[str]:
        """
        从历史记录中生成回复
        
        Args:
            query: 用户查询
            
        Returns:
            回复内容，未找到返回None
        """
        # 方法1：找最相似的历史问题
        similar = self.find_similar_question(query, top_k=1)
        
        if similar and similar[0]['score'] > 0.3:  # 相似度阈值
            best_match = similar[0]
            
            # 根据相似度调整回复
            if best_match['score'] > 0.7:
                # 高度相似，直接使用历史回复
                return best_match['answer']
            else:
                # 中等相似，提示参考
                return f"参考类似问题：{best_match['answer']}"
        
        # 方法2：使用学习到的关键词模式
        query_lower = query.lower()
        best_keyword = None
        best_score = 0
        
        for keyword, pattern in self.reply_patterns.items():
            if keyword in query_lower:
                # 关键词匹配，使用置信度作为分数
                score = pattern['confidence']
                if score > best_score:
                    best_score = score
                    best_keyword = keyword
        
        if best_keyword and best_score > 0.2:
            return self.reply_patterns[best_keyword]['reply']
        
        return None
    
    def add_conversation(self, question: str, answer: str, source: str = "manual"):
        """添加单条对话记录"""
        self.conversations.append({
            'question': question,
            'answer': answer,
            'source': source
        })
        
        # 重新学习模式
        self._learn_patterns()
        
        self.logger.info(f"对话记录添加成功: {question[:30]}...")
    
    def export_patterns(self, file_path: str) -> bool:
        """导出学习到的回复模式"""
        try:
            data = {
                'patterns': self.reply_patterns,
                'conversation_count': len(self.conversations),
                'learned_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"回复模式已导出到: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"导出模式失败: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """获取学习统计信息"""
        return {
            'conversation_count': len(self.conversations),
            'pattern_count': len(self.reply_patterns),
            'avg_pattern_confidence': sum(p['confidence'] for p in self.reply_patterns.values()) / len(self.reply_patterns) if self.reply_patterns else 0
        }


# 测试函数
if __name__ == "__main__":
    import time
    
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    print("历史学习模块测试")
    print("=" * 50)
    
    # 创建测试历史目录
    test_dir = Path("./test_history")
    test_dir.mkdir(exist_ok=True)
    
    # 创建测试历史文件
    test_history = test_dir / "test_conversations.json"
    test_history.write_text(json.dumps([
        {
            "question": "这个产品多少钱？",
            "answer": "基础版100元/月，专业版300元/月。"
        },
        {
            "question": "价格是多少？",
            "answer": "价格从100元到800元不等，具体看您需要的版本。"
        },
        {
            "question": "什么时候发货？",
            "answer": "付款后24小时内发货。"
        },
        {
            "question": "发货要多久？",
            "answer": "一般24小时内安排发货。"
        }
    ], ensure_ascii=False, indent=2), encoding='utf-8')
    
    # 测试学习器
    learner = HistoryLearner(str(test_dir))
    learner.load_history()
    
    test_queries = [
        "这个产品价格多少",
        "什么时候能发货",
        "有优惠吗"
    ]
    
    for query in test_queries:
        print(f"\n查询: '{query}'")
        reply = learner.get_reply_from_history(query)
        if reply:
            print(f"回复: {reply}")
        else:
            print("未找到相似历史")
    
    # 显示统计信息
    stats = learner.get_stats()
    print(f"\n学习统计:")
    print(f"  对话记录数: {stats['conversation_count']}")
    print(f"  回复模式数: {stats['pattern_count']}")
    print(f"  平均置信度: {stats['avg_pattern_confidence']:.2f}")
    
    # 清理测试目录
    import shutil
    shutil.rmtree(test_dir)