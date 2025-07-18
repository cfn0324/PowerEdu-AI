"""
简化的RAG系统实现，避免sklearn依赖问题
"""
import os
import json
import logging
import hashlib
import asyncio
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import uuid

# 文档处理
try:
    import PyPDF2
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

try:
    import docx
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    from markdown import markdown
    from bs4 import BeautifulSoup
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False

# 向量化和检索
import numpy as np

# 文本处理
try:
    import jieba
    HAS_JIEBA = True
except ImportError:
    HAS_JIEBA = False

import re

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """文档处理器"""
    
    @staticmethod
    def process_file(file_path: str) -> Tuple[str, Dict]:
        """处理单个文件"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.txt':
            return DocumentProcessor._process_txt(file_path)
        elif file_ext == '.md':
            return DocumentProcessor._process_markdown(file_path)
        elif file_ext == '.pdf' and HAS_PDF:
            return DocumentProcessor._process_pdf(file_path)
        elif file_ext in ['.docx', '.doc'] and HAS_DOCX:
            return DocumentProcessor._process_docx(file_path)
        elif file_ext == '.html':
            return DocumentProcessor._process_html(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_ext}")
    
    @staticmethod
    def _process_txt(file_path: str) -> Tuple[str, Dict]:
        """处理TXT文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='gbk') as f:
                content = f.read()
        
        metadata = {
            'source': file_path,
            'type': 'txt',
            'size': len(content)
        }
        
        return content, metadata
    
    @staticmethod
    def _process_markdown(file_path: str) -> Tuple[str, Dict]:
        """处理Markdown文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取纯文本（移除markdown语法）
        if HAS_MARKDOWN:
            html = markdown(content)
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text()
        else:
            # 简单的markdown语法移除
            text = re.sub(r'[#*`_\[\]()]', '', content)
        
        metadata = {
            'source': file_path,
            'type': 'markdown',
            'size': len(text)
        }
        
        return text, metadata
    
    @staticmethod
    def _process_pdf(file_path: str) -> Tuple[str, Dict]:
        """处理PDF文件"""
        text = ""
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        
        metadata = {
            'source': file_path,
            'type': 'pdf',
            'pages': len(reader.pages),
            'size': len(text)
        }
        
        return text, metadata
    
    @staticmethod
    def _process_docx(file_path: str) -> Tuple[str, Dict]:
        """处理DOCX文件"""
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        metadata = {
            'source': file_path,
            'type': 'docx',
            'paragraphs': len(doc.paragraphs),
            'size': len(text)
        }
        
        return text, metadata
    
    @staticmethod
    def _process_html(file_path: str) -> Tuple[str, Dict]:
        """处理HTML文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if HAS_MARKDOWN:
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text()
        else:
            # 简单的HTML标签移除
            text = re.sub(r'<[^>]+>', '', content)
        
        metadata = {
            'source': file_path,
            'type': 'html',
            'size': len(text)
        }
        
        return text, metadata


class TextSplitter:
    """文本分块器"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """分割文本为块"""
        # 简单的文本分割
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            
            # 尝试在句号处分割
            if end < len(text):
                last_period = chunk.rfind('。')
                if last_period > self.chunk_size // 2:
                    chunk = chunk[:last_period + 1]
                    end = start + last_period + 1
            
            chunk_metadata = {
                'chunk_index': len(chunks),
                'chunk_size': len(chunk),
                'chunk_word_count': len(chunk.split()),
                **(metadata or {})
            }
            
            chunks.append({
                'content': chunk.strip(),
                'metadata': chunk_metadata
            })
            
            start = end - self.chunk_overlap
        
        return chunks


class SimpleEmbedding:
    """简单的嵌入模型实现"""
    
    def __init__(self):
        self.is_fitted = True  # 简化版本，不需要训练
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """编码文本为向量"""
        # 简单的字符级向量化
        vocab = set()
        for text in texts:
            vocab.update(text)
        vocab = sorted(list(vocab))
        
        vectors = []
        for text in texts:
            vector = [text.count(char) for char in vocab]
            vectors.append(vector)
        
        return np.array(vectors, dtype=float)


class VectorStore:
    """向量存储器"""
    
    def __init__(self, embedding_model=None):
        self.embedding_model = embedding_model or SimpleEmbedding()
        self.chunks = []
        self.vectors = None
        self.metadata = []
    
    def add_documents(self, chunks: List[Dict]):
        """添加文档块"""
        for chunk in chunks:
            self.chunks.append(chunk['content'])
            self.metadata.append(chunk['metadata'])
        
        # 重新计算向量
        self._update_vectors()
    
    def _update_vectors(self):
        """更新向量"""
        if self.chunks:
            self.vectors = self.embedding_model.encode(self.chunks)
    
    def similarity_search(self, query: str, top_k: int = 5, threshold: float = 0.1) -> List[Dict]:
        """相似度搜索"""
        if not self.chunks or self.vectors is None:
            return []
        
        # 编码查询
        query_vector = self.embedding_model.encode([query])
        
        # 简单的余弦相似度计算
        def cosine_sim(a, b):
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            if norm_a == 0 or norm_b == 0:
                return 0
            return dot_product / (norm_a * norm_b)
        
        similarities = []
        for vector in self.vectors:
            sim = cosine_sim(query_vector[0], vector)
            similarities.append(sim)
        similarities = np.array(similarities)
        
        # 获取top_k结果
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = similarities[idx]
            if score >= threshold:
                results.append({
                    'content': self.chunks[idx],
                    'score': float(score),
                    'metadata': self.metadata[idx],
                    'index': int(idx)
                })
        
        return results


class LLMInterface:
    """大语言模型接口"""
    
    def __init__(self, model_config):
        """初始化LLM接口
        
        Args:
            model_config: 可以是字典或ModelConfig对象
        """
        if hasattr(model_config, 'model_type'):
            # 如果是ModelConfig对象，转换为字典
            self.model_config = {
                'model_type': model_config.model_type,
                'model_name': model_config.model_name,
                'api_key': model_config.api_key,
                'api_base_url': model_config.api_base_url,
                'max_tokens': model_config.max_tokens,
                'temperature': model_config.temperature,
            }
        else:
            # 如果是字典，直接使用
            self.model_config = model_config
        
        self.model_type = self.model_config.get('model_type', 'mock')
        self.model_name = self.model_config.get('model_name', 'mock')
    
    async def generate(self, prompt: str, context: str = "") -> str:
        """生成回答"""
        if self.model_type == 'mock' or self.model_name == 'mock':
            return f"基于提供的上下文信息：{context[:100]}...\n\n对于问题「{prompt}」，这是一个模拟回答。请配置真实的大语言模型以获得准确回答。"
        
        # 真实API调用
        if self.model_type == 'api':
            try:
                return await self._call_real_api(prompt, context)
            except Exception as e:
                logger.error(f"API调用失败: {e}")
                return f"抱歉，调用AI模型时出现错误：{str(e)}"
        
        return "请配置大语言模型"
    
    async def _call_real_api(self, prompt: str, context: str = "") -> str:
        """调用真实的API"""
        import aiohttp
        import json
        
        api_key = self.model_config.get('api_key')
        api_base_url = self.model_config.get('api_base_url')
        model_name = self.model_config.get('model_name')
        
        if not api_key:
            return "错误：未配置API密钥"
        
        # 构建提示词
        if context:
            full_prompt = f"基于以下上下文信息回答问题：\n\n上下文：{context}\n\n问题：{prompt}\n\n请基于上下文信息给出准确、有帮助的回答。如果上下文中没有相关信息，请说明并基于你的知识给出合理的回答。"
        else:
            full_prompt = f"问题：{prompt}\n\n请给出准确、有帮助的回答。"
        
        try:
            # 支持不同的API格式
            if 'gemini' in model_name.lower() or 'google' in api_base_url.lower():
                return await self._call_gemini_api(full_prompt, api_key, api_base_url)
            elif 'openai' in api_base_url.lower():
                return await self._call_openai_api(full_prompt, api_key, api_base_url, model_name)
            else:
                return await self._call_generic_api(full_prompt, api_key, api_base_url, model_name)
        except Exception as e:
            logger.error(f"API调用异常: {e}")
            return f"API调用失败：{str(e)}"
    
    async def _call_gemini_api(self, prompt: str, api_key: str, api_base_url: str) -> str:
        """调用Gemini API - 使用同步方式确保稳定性"""
        import requests
        import json
        import asyncio
        
        # 在线程池中执行同步请求，避免阻塞事件循环
        def sync_request():
            # Gemini API URL格式 - 使用v1beta
            if not api_base_url.endswith('/'):
                api_base_url_fixed = api_base_url + '/'
            else:
                api_base_url_fixed = api_base_url
            
            # 使用配置中的模型名称
            model_name = self.model_config.get('model_name', 'gemini-pro')
            url = f"{api_base_url_fixed}v1beta/models/{model_name}:generateContent"
            
            # 正确的请求头格式 - 使用x-goog-api-key
            headers = {
                'Content-Type': 'application/json',
                'x-goog-api-key': api_key
            }
            
            # 正确的请求体格式
            data = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": self.model_config.get('temperature', 0.7),
                    "maxOutputTokens": self.model_config.get('max_tokens', 4096),
                }
            }
            
            logger.info(f"Gemini API URL: {url}")
            logger.info(f"Gemini API Headers: {headers}")
            
            try:
                response = requests.post(url, headers=headers, json=data, timeout=30)
                logger.info(f"Gemini API Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    candidates = result.get('candidates', [])
                    if candidates and candidates[0].get('content'):
                        parts = candidates[0]['content'].get('parts', [])
                        if parts:
                            answer = parts[0].get('text', '未获得有效回复')
                            logger.info(f"Gemini API Success: {answer[:100]}...")
                            return answer
                    logger.warning("Gemini API响应格式不正确")
                    return '未获得有效回复'
                else:
                    logger.error(f"Gemini API请求失败 ({response.status_code}): {response.text}")
                    raise Exception(f"API请求失败 ({response.status_code}): {response.text}")
                    
            except Exception as e:
                logger.error(f"Gemini API调用异常: {e}")
                raise e
        
        # 在线程池中执行同步请求
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, sync_request)
        return result
    
    async def _call_openai_api(self, prompt: str, api_key: str, api_base_url: str, model_name: str) -> str:
        """调用OpenAI API"""
        import aiohttp
        import json
        
        url = f"{api_base_url}/chat/completions"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        data = {
            "model": model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": self.model_config.get('temperature', 0.7),
            "max_tokens": self.model_config.get('max_tokens', 4096),
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    choices = result.get('choices', [])
                    if choices:
                        return choices[0]['message']['content']
                    return '未获得有效回复'
                else:
                    error_text = await response.text()
                    raise Exception(f"API请求失败 ({response.status}): {error_text}")
    
    async def _call_generic_api(self, prompt: str, api_key: str, api_base_url: str, model_name: str) -> str:
        """调用通用API"""
        import aiohttp
        import json
        
        # 尝试OpenAI格式
        try:
            return await self._call_openai_api(prompt, api_key, api_base_url, model_name)
        except Exception as e:
            logger.error(f"通用API调用失败: {e}")
            return f"API调用失败：{str(e)}"
    
    async def generate_response(self, prompt: str, context: str = "") -> Dict:
        """生成回答并返回详细信息"""
        import time
        start_time = time.time()
        
        try:
            answer = await self.generate(prompt, context)
            response_time = round((time.time() - start_time), 3)  # 保持为秒，保留3位小数
            
            return {
                'answer': answer,
                'response_time': response_time,
                'model_used': f"{self.model_name}",
                'success': True
            }
        except Exception as e:
            response_time = round((time.time() - start_time), 3)  # 保持为秒，保留3位小数
            return {
                'answer': f"生成回答时出错: {str(e)}",
                'response_time': response_time,
                'model_used': f"{self.model_name}",
                'success': False,
                'error': str(e)
            }


class RAGSystem:
    """RAG系统主类"""
    
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.text_splitter = TextSplitter()
        self.knowledge_bases = {}  # 存储每个知识库的向量存储
        self.llm_configs = {}  # 存储LLM配置
        
    def get_or_create_vector_store(self, kb_id: int) -> VectorStore:
        """获取或创建知识库的向量存储"""
        if kb_id not in self.knowledge_bases:
            self.knowledge_bases[kb_id] = VectorStore()
        return self.knowledge_bases[kb_id]
    
    def configure_llm(self, config_id: int, model_config: Dict):
        """配置大语言模型"""
        self.llm_configs[config_id] = LLMInterface(model_config)
    
    def process_document(self, kb_id: int, file_path: str, document_id: Optional[int] = None) -> Dict:
        """处理文档"""
        try:
            # 处理文档
            content, metadata = self.document_processor.process_file(file_path)
            
            # 分块
            chunks = self.text_splitter.split_text(content, metadata)
            
            # 获取向量存储并添加文档
            vector_store = self.get_or_create_vector_store(kb_id)
            vector_store.add_documents(chunks)
            
            return {
                'success': True,
                'chunk_count': len(chunks),
                'content_length': len(content),
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"处理文档失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'chunk_count': 0
            }
    
    async def ask_question(self, kb_id: int, question: str, config_id: Optional[int] = None, 
                          top_k: int = 5, threshold: float = 0.5) -> Dict:
        """智能问答"""
        import time
        start_time = time.time()
        
        try:
            # 获取向量存储
            vector_store = self.get_or_create_vector_store(kb_id)
            
            # 检索相关文档
            relevant_docs = vector_store.similarity_search(question, top_k=top_k, threshold=threshold)
            
            # 构建上下文
            if relevant_docs:
                context = "\n".join([doc['content'] for doc in relevant_docs])
                context_info = f"基于知识库中的 {len(relevant_docs)} 个相关文档片段："
            else:
                context = ""
                context_info = "知识库中没有找到相关信息，但我可以基于我的知识来回答："
            
            # 生成回答 - 无论是否找到相关文档都尝试调用大模型
            llm = self.llm_configs.get(config_id) if config_id else None
            if llm:
                llm_result = await llm.generate_response(question, context)
                answer = llm_result.get('answer', '生成回答失败')
                model_used = llm_result.get('model_used', f"config_{config_id}" if config_id else "default")
            else:
                # 如果没有配置LLM，才返回"未找到相关信息"的提示
                if not relevant_docs:
                    response_time = round((time.time() - start_time), 3)
                    return {
                        'answer': '抱歉，我在知识库中没有找到相关信息，且未配置大语言模型。请配置模型以获得智能回答。',
                        'sources': [],
                        'confidence': 0.0,
                        'retrieved_chunks': [],
                        'model_used': f"config_{config_id}" if config_id else "default",
                        'response_time': response_time
                    }
                else:
                    answer = f"基于知识库内容，找到了 {len(relevant_docs)} 个相关片段，但未配置大语言模型。请配置模型以获得智能回答。"
                    model_used = f"config_{config_id}" if config_id else "default"
            
            response_time = round((time.time() - start_time), 3)  # 保持为秒，保留3位小数
            
            return {
                'answer': answer,
                'sources': [
                    {
                        'content': doc['content'][:200] + '...' if len(doc['content']) > 200 else doc['content'],
                        'score': doc['score'],
                        'metadata': doc['metadata']
                    }
                    for doc in relevant_docs
                ],
                'confidence': relevant_docs[0]['score'] if relevant_docs else 0.0,
                'retrieved_chunks': relevant_docs,
                'model_used': model_used,
                'response_time': response_time
            }
            
        except Exception as e:
            logger.error(f"问答失败: {e}")
            response_time = round((time.time() - start_time), 3)  # 保持为秒，保留3位小数
            return {
                'answer': f'查询过程中出现错误: {str(e)}',
                'sources': [],
                'confidence': 0.0,
                'retrieved_chunks': [],
                'model_used': "error",
                'response_time': response_time
            }
    
    def get_knowledge_base_stats(self, kb_id: int) -> Dict:
        """获取知识库统计信息"""
        if kb_id in self.knowledge_bases:
            vector_store = self.knowledge_bases[kb_id]
            return {
                'total_chunks': len(vector_store.chunks),
                'total_documents': len(set(chunk.get('document_id', 0) for chunk in vector_store.metadata)),
                'vector_dimension': vector_store.vectors.shape[1] if vector_store.vectors is not None else 0
            }
        else:
            return {
                'total_chunks': 0,
                'total_documents': 0,
                'vector_dimension': 0
            }
