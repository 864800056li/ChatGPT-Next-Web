"""
企业微信客户端模块
基于企业微信官方API：https://developer.work.weixin.qq.com/document/path/90236
"""

import requests
import json
import time
import logging
from typing import Optional, Dict, Any


class WeComClient:
    def __init__(self, config: Dict[str, Any]):
        """
        初始化企业微信客户端
        
        Args:
            config: 配置字典，包含 corp_id, secret, agent_id
        """
        self.corp_id = config['corp_id']
        self.secret = config['secret']
        self.agent_id = config['agent_id']
        
        self.access_token = None
        self.token_expires_at = 0
        
        self.base_url = "https://qyapi.weixin.qq.com/cgi-bin"
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        
    def _get_access_token(self) -> str:
        """获取或刷新Access Token"""
        now = time.time()
        
        # 如果token有效且未过期（提前5分钟刷新）
        if self.access_token and now < self.token_expires_at - 300:
            return self.access_token
        
        url = f"{self.base_url}/gettoken"
        params = {
            "corpid": self.corp_id,
            "corpsecret": self.secret
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['errcode'] == 0:
                self.access_token = data['access_token']
                self.token_expires_at = now + data['expires_in']
                self.logger.info("Access Token获取成功")
                return self.access_token
            else:
                self.logger.error(f"获取Access Token失败: {data}")
                raise Exception(f"企业微信API错误: {data['errmsg']}")
                
        except requests.RequestException as e:
            self.logger.error(f"请求Access Token失败: {e}")
            raise
    
    def send_message(self, user_id: str, content: str, msg_type: str = "text") -> bool:
        """
        发送消息给指定用户
        
        Args:
            user_id: 用户ID（企业微信中的UserID）
            content: 消息内容
            msg_type: 消息类型，支持：text, markdown, image等
            
        Returns:
            是否发送成功
        """
        token = self._get_access_token()
        url = f"{self.base_url}/message/send?access_token={token}"
        
        # 构建消息体
        message = {
            "touser": user_id,
            "msgtype": msg_type,
            "agentid": self.agent_id,
            msg_type: {
                "content": content
            }
        }
        
        try:
            response = requests.post(url, json=message, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['errcode'] == 0:
                self.logger.info(f"消息发送成功 to {user_id}: {content[:50]}...")
                return True
            else:
                self.logger.error(f"消息发送失败: {data}")
                return False
                
        except requests.RequestException as e:
            self.logger.error(f"发送消息请求失败: {e}")
            return False
    
    def get_user_info(self, user_id: str) -> Optional[Dict]:
        """获取用户信息"""
        token = self._get_access_token()
        url = f"{self.base_url}/user/get?access_token={token}"
        params = {"userid": user_id}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['errcode'] == 0:
                return data
            else:
                self.logger.error(f"获取用户信息失败: {data}")
                return None
                
        except requests.RequestException as e:
            self.logger.error(f"请求用户信息失败: {e}")
            return None
    
    def reply_callback_message(self, sdk_param: Dict, reply_content: str) -> Dict:
        """
        回复回调消息（用于企微回调模式）
        
        Args:
            sdk_param: 企业微信回调SDK参数
            reply_content: 回复内容
            
        Returns:
            回复消息体
        """
        # 企业微信回调消息回复格式
        return {
            "ToUserName": sdk_param.get("FromUserName", ""),
            "FromUserName": sdk_param.get("ToUserName", ""),
            "CreateTime": int(time.time()),
            "MsgType": "text",
            "Content": reply_content
        }
    
    def validate_callback(self, msg_signature: str, timestamp: str, 
                         nonce: str, echostr: str) -> Optional[str]:
        """
        验证回调URL（用于企微配置回调模式）
        
        Returns:
            解密后的echostr，验证失败返回None
        """
        # 这里需要实现企业微信回调验证逻辑
        # 由于需要encodingAESKey，暂时留空
        self.logger.warning("回调验证功能需要encodingAESKey，请参考企业微信文档配置")
        return None
    
    def test_connection(self) -> bool:
        """测试连接是否正常"""
        try:
            token = self._get_access_token()
            self.logger.info(f"连接测试成功，Access Token: {token[:20]}...")
            return True
        except Exception as e:
            self.logger.error(f"连接测试失败: {e}")
            return False


# 测试函数
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    print("企业微信客户端模块测试")
    print("=" * 50)
    
    # 需要真实配置才能测试
    print("⚠️  需要真实的企业微信配置才能进行完整测试")
    print("   请填写 config.yaml 中的 wecom 配置项")
    
    # 模拟测试
    print("\n模拟测试关键词匹配模块：")
    from keyword_matcher import KeywordMatcher
    
    test_config = [
        {
            "keywords": ["测试", "test"],
            "reply": "收到测试消息，系统运行正常！"
        }
    ]
    
    matcher = KeywordMatcher(test_config)
    test_msg = "这是一个测试消息"
    reply = matcher.match(test_msg)
    
    if reply:
        print(f"  消息: '{test_msg}'")
        print(f"  回复: '{reply}'")
    else:
        print(f"  消息: '{test_msg}'")
        print("  无匹配（正常，因为关键词不匹配）")