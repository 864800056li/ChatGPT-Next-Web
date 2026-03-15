#!/usr/bin/env python3
"""
企业微信自动回复系统
支持：关键词触发 + 文档检索 + 历史聊天学习
"""

import yaml
import logging
import os
import sys
from pathlib import Path

# 添加模块路径
sys.path.append(str(Path(__file__).parent))

from modules.wecom_client import WeComClient
from modules.message_processor import MessageProcessor
from modules.keyword_matcher import KeywordMatcher
from modules.document_retriever import DocumentRetriever
from modules.history_learner import HistoryLearner


class WeChatAuto:
    def __init__(self, config_path="config/config.yaml"):
        """初始化自动回复系统"""
        self.config = self._load_config(config_path)
        self._setup_logging()
        
        # 初始化组件
        self.wecom = WeComClient(self.config['wecom'])
        self.keyword_matcher = KeywordMatcher(self.config['message']['keyword_triggers'])
        
        # 可选组件
        self.document_retriever = None
        if self.config['message']['enable_document_retrieval']:
            self.document_retriever = DocumentRetriever(self.config['message']['document_path'])
            
        self.history_learner = None
        if self.config['message']['enable_chat_history_learning']:
            self.history_learner = HistoryLearner(self.config['message']['chat_history_path'])
            
        self.message_processor = MessageProcessor(
            keyword_matcher=self.keyword_matcher,
            document_retriever=self.document_retriever,
            history_learner=self.history_learner
        )
        
        self.logger.info("企业微信自动回复系统初始化完成")
        
    def _load_config(self, config_path):
        """加载配置文件"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        # 创建必要目录
        os.makedirs(self.config['message']['document_path'], exist_ok=True)
        os.makedirs(self.config['message']['chat_history_path'], exist_ok=True)
        os.makedirs(os.path.dirname(self.config['logging']['file']), exist_ok=True)
        
        return config
    
    def _setup_logging(self):
        """配置日志"""
        log_config = self.config['logging']
        logging.basicConfig(
            level=getattr(logging, log_config['level']),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_config['file'], encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def process_message(self, user_id, message):
        """处理单条消息"""
        self.logger.info(f"收到消息 from {user_id}: {message}")
        
        # 安全检查
        if self._is_blacklisted(user_id):
            self.logger.warning(f"用户 {user_id} 在黑名单中，忽略消息")
            return None
            
        # 处理消息
        reply = self.message_processor.process(user_id, message)
        
        if reply:
            self.logger.info(f"生成回复 to {user_id}: {reply}")
            return reply
        else:
            self.logger.info(f"未触发回复规则 for {user_id}")
            return None
    
    def _is_blacklisted(self, user_id):
        """检查用户是否在黑名单中"""
        return user_id in self.config['security']['blacklist']
    
    def run(self):
        """运行主循环（监听消息）"""
        self.logger.info("开始监听企业微信消息...")
        
        # 这里将实现企业微信消息监听
        # 暂时使用模拟消息进行测试
        self._run_test_mode()
    
    def _run_test_mode(self):
        """测试模式：模拟消息处理"""
        self.logger.info("进入测试模式，请输入消息进行测试（输入 quit 退出）")
        
        test_cases = [
            ("user1", "这个产品多少钱？"),
            ("user1", "什么时候能发货？"),
            ("user2", "我想联系客服"),
            ("user3", "你们公司地址在哪里？")
        ]
        
        for user_id, message in test_cases:
            print(f"\n[测试] {user_id}: {message}")
            reply = self.process_message(user_id, message)
            if reply:
                print(f"[回复] {reply}")
            else:
                print(f"[无匹配] 未触发自动回复规则")
        
        print("\n测试完成！请配置企业微信API以使用真实消息监听。")


if __name__ == "__main__":
    try:
        # 先检查配置
        config_path = "config/config.yaml"
        if not os.path.exists(config_path):
            print(f"⚠️  配置文件不存在，请先复制 config_template.yaml 并填写企业微信API信息")
            print(f"   cp config/config_template.yaml config/config.yaml")
            print("   然后编辑 config.yaml 填写你的 CorpID, Secret, AgentId")
            sys.exit(1)
            
        app = WeChatAuto(config_path)
        app.run()
        
    except Exception as e:
        logging.error(f"程序启动失败: {e}", exc_info=True)
        sys.exit(1)