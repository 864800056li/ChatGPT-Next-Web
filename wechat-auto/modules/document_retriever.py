"""
文档检索模块
基于RAG（检索增强生成）技术，从本地文档中检索相关信息
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional
import logging


class DocumentRetriever:
    def __init__(self, document_path: str):
        """
        初始化文档检索器
        
        Args:
            document_path: 文档目录路径
        """
        self.document_path = Path(document_path)
        self.documents = []  # 文档缓存
        self.logger = logging.getLogger(__name__)
        
        # 确保目录存在
        self.document_path.mkdir(parents=True, exist_ok=True)
        
        # 支持的文档格式
        self.supported_extensions = {'.txt', '.md', '.pdf', '.docx', '.doc'}
        
        self.logger.info(f"文档检索器初始化，路径: {document_path}")
    
    def load_documents(self) -> bool:
        """加载目录下所有文档"""
        try:
            self.documents = []
            
            for file_path in self.document_path.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                    content = self._read_document(file_path)
                    if content:
                        self.documents.append({
                            'path': str(file_path),
                            'name': file_path.name,
                            'content': content,
                            'chunks': self._chunk_document(content)
                        })
            
            self.logger.info(f"已加载 {len(self.documents)} 个文档")
            return True
            
        except Exception as e:
            self.logger.error(f"加载文档失败: {e}")
            return False
    
    def _read_document(self, file_path: Path) -> Optional[str]:
        """读取文档内容（根据格式）"""
        try:
            ext = file_path.suffix.lower()
            
            if ext in {'.txt', '.md'}:
                # 文本文件直接读取
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
                    
            elif ext == '.pdf':
                # PDF文件需要额外库
                try:
                    import PyPDF2
                    content = ""
                    with open(file_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        for page in pdf_reader.pages:
                            content += page.extract_text()
                    return content
                except ImportError:
                    self.logger.warning("未安装PyPDF2，无法读取PDF文件")
                    return None
                    
            elif ext in {'.docx', '.doc'}:
                # Word文档
                try:
                    import docx
                    doc = docx.Document(file_path)
                    content = '\n'.join([para.text for para in doc.paragraphs])
                    return content
                except ImportError:
                    self.logger.warning("未安装python-docx，无法读取Word文档")
                    return None
                    
            return None
            
        except Exception as e:
            self.logger.error(f"读取文档失败 {file_path}: {e}")
            return None
    
    def _chunk_document(self, content: str, chunk_size: int = 500) -> List[str]:
        """将文档切分成小块"""
        # 简单按段落切分
        paragraphs = re.split(r'\n\s*\n', content)
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            if len(current_chunk) + len(para) < chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        搜索相关文档内容
        
        Args:
            query: 查询文本
            top_k: 返回最相关的k个结果
            
        Returns:
            相关文档片段列表
        """
        if not self.documents:
            self.load_documents()
        
        # 简单关键词匹配（后续可升级为向量检索）
        query_lower = query.lower()
        results = []
        
        for doc in self.documents:
            for chunk in doc['chunks']:
                # 计算简单相关性分数
                score = self._calculate_similarity(chunk, query_lower)
                if score > 0:
                    results.append({
                        'document': doc['name'],
                        'content': chunk,
                        'score': score
                    })
        
        # 按分数排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # 返回前top_k个
        return results[:top_k]
    
    def _calculate_similarity(self, text: str, query: str) -> float:
        """计算文本与查询的相关性分数（简单版本）"""
        text_lower = text.lower()
        
        # 1. 精确匹配关键词
        query_words = set(query.split())
        text_words = set(text_lower.split())
        
        # 共同词数量
        common_words = query_words.intersection(text_words)
        
        if not common_words:
            return 0
        
        # 2. 考虑词频
        score = len(common_words) / len(query_words)
        
        # 3. 考虑位置（标题、开头等）
        # 这里简化处理
        if any(word in text_lower[:100] for word in common_words):
            score *= 1.2
        
        return score
    
    def get_reply_from_documents(self, query: str) -> Optional[str]:
        """
        从文档中生成回复
        
        Args:
            query: 用户查询
            
        Returns:
            回复内容，未找到返回None
        """
        results = self.search(query, top_k=1)
        
        if not results:
            return None
        
        best_result = results[0]
        
        # 简单提取最相关的部分作为回复
        content = best_result['content']
        
        # 如果内容太长，截取前200字符
        if len(content) > 200:
            content = content[:200] + "..."
        
        # 格式化回复
        reply = f"根据相关文档《{best_result['document']}》：\n{content}"
        
        return reply
    
    def add_document(self, file_path: str) -> bool:
        """添加单个文档"""
        try:
            path = Path(file_path)
            if not path.exists():
                self.logger.error(f"文件不存在: {file_path}")
                return False
            
            content = self._read_document(path)
            if not content:
                return False
            
            # 添加到文档列表
            self.documents.append({
                'path': str(path),
                'name': path.name,
                'content': content,
                'chunks': self._chunk_document(content)
            })
            
            self.logger.info(f"文档添加成功: {path.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"添加文档失败 {file_path}: {e}")
            return False
    
    def list_documents(self) -> List[Dict]:
        """列出所有文档信息"""
        return [
            {
                'name': doc['name'],
                'path': doc['path'],
                'chunk_count': len(doc['chunks'])
            }
            for doc in self.documents
        ]


# 测试函数
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    print("文档检索模块测试")
    print("=" * 50)
    
    # 创建测试文档目录
    test_dir = Path("./test_documents")
    test_dir.mkdir(exist_ok=True)
    
    # 创建测试文档
    test_doc = test_dir / "test_faq.md"
    test_doc.write_text("""
# 常见问题解答

## 产品价格
我们的产品分为三个版本：
- 基础版：100元/月
- 专业版：300元/月
- 企业版：800元/月

## 发货时间
付款后24小时内发货，快递一般2-3天送达。

## 售后服务
我们提供7天无理由退货，1年质保。
    """, encoding='utf-8')
    
    # 测试检索器
    retriever = DocumentRetriever(str(test_dir))
    retriever.load_documents()
    
    test_queries = [
        "产品多少钱",
        "发货要多久",
        "售后服务政策"
    ]
    
    for query in test_queries:
        print(f"\n查询: '{query}'")
        reply = retriever.get_reply_from_documents(query)
        if reply:
            print(f"回复: {reply}")
        else:
            print("未找到相关信息")
    
    # 清理测试目录
    import shutil
    shutil.rmtree(test_dir)