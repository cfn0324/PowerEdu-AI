"""
RAG (Retrieval-Augmented Generation) 系统核心服务
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
import PyPDF2
import docx
from markdown import markdown
from bs4 import BeautifulSoup

# 向量化和检索
import numpy as np
try:
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.feature_extraction.text import TfidfVectorizer
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    print("Warning: sklearn not available, using simple similarity")

# 文本处理
import jieba
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """文档处理器"""
    
    def __init__(self):
        self.supported_formats = ['.md', '.pdf', '.txt', '.docx', '.html']
        
    def load_document(self, file_path: str) -> Tuple[str, Dict]:
        """加载文档内容"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.md':
            return self._load_markdown(file_path)
        elif file_ext == '.pdf':
            return self._load_pdf(file_path)
        elif file_ext == '.txt':
            return self._load_text(file_path)
        elif file_ext == '.docx':
            return self._load_docx(file_path)
        elif file_ext == '.html':
            return self._load_html(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_ext}")
    
    def _load_markdown(self, file_path: str) -> Tuple[str, Dict]:
        """加载Markdown文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 转换为HTML然后提取纯文本
        html = markdown(content)
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        
        metadata = {
            'format': 'markdown',
            'file_size': os.path.getsize(file_path),
            'char_count': len(text),
            'word_count': len(text.split())
        }
        
        return text, metadata
    
    def _load_pdf(self, file_path: str) -> Tuple[str, Dict]:
        """加载PDF文件"""
        text = ""
        page_count = 0
        
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            page_count = len(pdf_reader.pages)
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        
        metadata = {
            'format': 'pdf',
            'file_size': os.path.getsize(file_path),
            'page_count': page_count,
            'char_count': len(text),
            'word_count': len(text.split())
        }
        
        return text, metadata
    
    def _load_text(self, file_path: str) -> Tuple[str, Dict]:
        """加载纯文本文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        metadata = {
            'format': 'text',
            'file_size': os.path.getsize(file_path),
            'char_count': len(text),
            'word_count': len(text.split()),
            'line_count': len(text.split('\n'))
        }
        
        return text, metadata
    
    def _load_docx(self, file_path: str) -> Tuple[str, Dict]:
        """加载Word文档"""
        doc = docx.Document(file_path)
        text = ""
        paragraph_count = 0
        
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
            paragraph_count += 1
        
        metadata = {
            'format': 'docx',
            'file_size': os.path.getsize(file_path),
            'paragraph_count': paragraph_count,
            'char_count': len(text),
            'word_count': len(text.split())
        }
        
        return text, metadata
    
    def _load_html(self, file_path: str) -> Tuple[str, Dict]:
        """加载HTML文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()
        
        metadata = {
            'format': 'html',
            'file_size': os.path.getsize(file_path),
            'char_count': len(text),
            'word_count': len(text.split())
        }
        
        return text, metadata


class TextSplitter:
    """文本分块器"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""]
        )
    
    def split_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """分割文本为块"""
        chunks = self.splitter.split_text(text)
        
        chunk_list = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                'chunk_index': i,
                'chunk_size': len(chunk),
                'chunk_word_count': len(chunk.split()),
                **(metadata or {})
            }
            
            chunk_list.append({
                'content': chunk.strip(),
                'metadata': chunk_metadata
            })
        
        return chunk_list


class SimpleEmbedding:
    """简单的嵌入模型实现"""
    
    def __init__(self):
        if HAS_SKLEARN:
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words=self._get_stop_words(),
                ngram_range=(1, 2)
            )
        else:
            self.vectorizer = None
        self.is_fitted = False
    
    def _get_stop_words(self) -> List[str]:
        """获取中文停用词"""
        stop_words = [
            '的', '了', '在', '是', '我', '有', '和', '就', 
            '不', '人', '都', '一', '一个', '上', '也', '很', 
            '到', '说', '要', '去', '你', '会', '着', '没有',
            '看', '好', '自己', '这'
        ]
        return stop_words
    
    def fit(self, texts: List[str]):
        """训练向量器"""
        if not HAS_SKLEARN:
            self.is_fitted = True
            return
        
        # 预处理文本
        processed_texts = [self._preprocess_text(text) for text in texts]
        self.vectorizer.fit(processed_texts)
        self.is_fitted = True
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """编码文本为向量"""
        if not HAS_SKLEARN:
            # 简单的词频统计向量化
            vocab = set()
            for text in texts:
                vocab.update(text.split())
            vocab = list(vocab)
            
            vectors = []
            for text in texts:
                words = text.split()
                vector = [words.count(word) for word in vocab]
                vectors.append(vector)
            return np.array(vectors, dtype=float)
        
        if not self.is_fitted:
            self.fit(texts)
        
        processed_texts = [self._preprocess_text(text) for text in texts]
        vectors = self.vectorizer.transform(processed_texts)
        return vectors.toarray()
    
    def _preprocess_text(self, text: str) -> str:
        """预处理文本"""
        # 去除特殊字符
        text = re.sub(r'[^\w\s]', '', text)
        # 中文分词
        words = jieba.cut(text)
        return ' '.join(words)


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
    
    def similarity_search(self, query: str, top_k: int = 5, threshold: float = 0.5) -> List[Dict]:
        """相似度搜索"""
        if not self.chunks or self.vectors is None:
            return []
        
        # 编码查询
        query_vector = self.embedding_model.encode([query])
        
        # 计算相似度
        if HAS_SKLEARN:
            similarities = cosine_similarity(query_vector, self.vectors)[0]
        else:
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
    
    def save(self, file_path: str):
        """保存向量存储"""
        data = {
            'chunks': self.chunks,
            'vectors': self.vectors.tolist() if self.vectors is not None else None,
            'metadata': self.metadata
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load(self, file_path: str):
        """加载向量存储"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.chunks = data['chunks']
        self.metadata = data['metadata']
        if data['vectors']:
            self.vectors = np.array(data['vectors'])


class LLMInterface:
    """大语言模型接口"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.model_type = config.get('model_type', 'api')
        self.provider = config.get('provider', 'openai')
        
    async def generate_response(self, prompt: str, context: str = "", **kwargs) -> Dict:
        """生成回答"""
        if self.model_type == 'api':
            return await self._api_generate(prompt, context, **kwargs)
        else:
            return await self._local_generate(prompt, context, **kwargs)
    
    async def _api_generate(self, prompt: str, context: str = "", **kwargs) -> Dict:
        """API模式生成"""
        # 这里可以集成各种API
        if self.provider == 'openai':
            return await self._openai_generate(prompt, context, **kwargs)
        elif self.provider == 'anthropic':
            return await self._anthropic_generate(prompt, context, **kwargs)
        elif self.provider == 'zhipu':
            return await self._zhipu_generate(prompt, context, **kwargs)
        else:
            # 简单的模拟回答
            return await self._mock_generate(prompt, context, **kwargs)
    
    async def _local_generate(self, prompt: str, context: str = "", **kwargs) -> Dict:
        """本地模式生成"""
        # 本地模型推理逻辑
        return await self._mock_generate(prompt, context, **kwargs)
    
    async def _mock_generate(self, prompt: str, context: str = "", **kwargs) -> Dict:
        """模拟生成回答"""
        # 简单的基于关键词的回答
        response_time = 1.5
        tokens_used = 150
        
        answer = self._generate_mock_answer(prompt, context)
        
        return {
            'answer': answer,
            'model_used': f"{self.provider}_{self.config.get('model_name', 'default')}",
            'response_time': response_time,
            'tokens_used': tokens_used
        }
    
    def _generate_mock_answer(self, prompt: str, context: str) -> str:
        """生成模拟回答"""
        if not context.strip():
            return "抱歉，我没有找到相关的知识库内容来回答您的问题。请尝试重新表述您的问题或检查知识库是否包含相关信息。"
        
        # 简单的基于上下文的回答
        answer = f"""基于知识库内容，我为您提供以下回答：

{context[:500]}...

以上信息来源于知识库文档。如果您需要更详细的信息，请告诉我具体想了解的方面。"""
        
        return answer
    
    async def _openai_generate(self, prompt: str, context: str = "", **kwargs) -> Dict:
        """OpenAI API生成"""
        # 实际的OpenAI API调用逻辑
        # 这里需要安装openai库并实现实际的API调用
        return await self._mock_generate(prompt, context, **kwargs)
    
    async def _anthropic_generate(self, prompt: str, context: str = "", **kwargs) -> Dict:
        """Anthropic API生成"""
        # 实际的Anthropic API调用逻辑
        return await self._mock_generate(prompt, context, **kwargs)
    
    async def _zhipu_generate(self, prompt: str, context: str = "", **kwargs) -> Dict:
        """智谱AI API生成"""
        # 实际的智谱AI API调用逻辑
        return await self._mock_generate(prompt, context, **kwargs)


class RAGSystem:
    """RAG系统主类"""
    
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.text_splitter = TextSplitter()
        self.vector_stores = {}  # knowledge_base_id -> VectorStore
        self.llm_configs = {}    # config_id -> LLMInterface
        
    def create_knowledge_base(self, kb_id: int, documents_dir: str = None) -> bool:
        """创建知识库"""
        try:
            vector_store = VectorStore()
            self.vector_stores[kb_id] = vector_store
            
            if documents_dir and os.path.exists(documents_dir):
                self.load_documents_from_directory(kb_id, documents_dir)
            
            logger.info(f"知识库 {kb_id} 创建成功")
            return True
        except Exception as e:
            logger.error(f"创建知识库失败: {e}")
            return False
    
    def load_documents_from_directory(self, kb_id: int, directory: str) -> List[Dict]:
        """从目录加载文档"""
        if kb_id not in self.vector_stores:
            raise ValueError(f"知识库 {kb_id} 不存在")
        
        results = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                if file_ext in self.document_processor.supported_formats:
                    try:
                        result = self.process_document(kb_id, file_path)
                        results.append({
                            'file_path': file_path,
                            'status': 'success',
                            'chunks': result['chunk_count']
                        })
                    except Exception as e:
                        results.append({
                            'file_path': file_path,
                            'status': 'error',
                            'error': str(e)
                        })
        
        return results
    
    def process_document(self, kb_id: int, file_path: str, chunk_size: int = 1000, 
                        chunk_overlap: int = 200) -> Dict:
        """处理单个文档"""
        if kb_id not in self.vector_stores:
            raise ValueError(f"知识库 {kb_id} 不存在")
        
        # 加载文档
        content, metadata = self.document_processor.load_document(file_path)
        
        # 分块
        self.text_splitter.chunk_size = chunk_size
        self.text_splitter.chunk_overlap = chunk_overlap
        chunks = self.text_splitter.split_text(content, metadata)
        
        # 添加到向量存储
        self.vector_stores[kb_id].add_documents(chunks)
        
        return {
            'chunk_count': len(chunks),
            'content_length': len(content),
            'metadata': metadata
        }
    
    def configure_llm(self, config_id: int, config: Dict):
        """配置LLM"""
        self.llm_configs[config_id] = LLMInterface(config)
    
    async def ask_question(self, kb_id: int, question: str, config_id: int = None, 
                          top_k: int = 5, threshold: float = 0.5) -> Dict:
        """问答"""
        if kb_id not in self.vector_stores:
            raise ValueError(f"知识库 {kb_id} 不存在")
        
        # 检索相关文档
        vector_store = self.vector_stores[kb_id]
        retrieved_chunks = vector_store.similarity_search(
            question, top_k=top_k, threshold=threshold
        )
        
        # 构建上下文
        context = "\n\n".join([chunk['content'] for chunk in retrieved_chunks])
        
        # 构建提示词
        prompt = self._build_prompt(question, context)
        
        # 获取LLM配置
        if config_id and config_id in self.llm_configs:
            llm = self.llm_configs[config_id]
        elif self.llm_configs:
            # 使用第一个可用的配置
            llm = list(self.llm_configs.values())[0]
        else:
            # 使用默认配置
            llm = LLMInterface({'model_type': 'mock', 'provider': 'default'})
        
        # 生成回答
        start_time = datetime.now()
        result = await llm.generate_response(prompt, context)
        response_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'answer': result['answer'],
            'retrieved_chunks': retrieved_chunks,
            'model_used': result['model_used'],
            'response_time': response_time,
            'tokens_used': result.get('tokens_used', 0),
            'sources': self._extract_sources(retrieved_chunks)
        }
    
    def _build_prompt(self, question: str, context: str) -> str:
        """构建提示词"""
        prompt = f"""你是一个专业的电力知识库助手。请基于以下知识库内容回答用户的问题。

知识库内容：
{context}

用户问题：{question}

请根据知识库内容提供准确、详细的回答。如果知识库中没有相关信息，请明确说明。回答要专业、清晰，并且要结合具体的知识库内容。"""
        
        return prompt
    
    def _extract_sources(self, chunks: List[Dict]) -> List[Dict]:
        """提取文档来源"""
        sources = []
        for chunk in chunks:
            metadata = chunk.get('metadata', {})
            sources.append({
                'document_title': metadata.get('document_title', '未知文档'),
                'chunk_index': metadata.get('chunk_index', 0),
                'score': chunk.get('score', 0.0)
            })
        return sources
    
    def save_knowledge_base(self, kb_id: int, file_path: str):
        """保存知识库"""
        if kb_id in self.vector_stores:
            self.vector_stores[kb_id].save(file_path)
    
    def load_knowledge_base(self, kb_id: int, file_path: str):
        """加载知识库"""
        vector_store = VectorStore()
        vector_store.load(file_path)
        self.vector_stores[kb_id] = vector_store
    
    def get_knowledge_base_stats(self, kb_id: int) -> Dict:
        """获取知识库统计信息"""
        if kb_id not in self.vector_stores:
            return {}
        
        vector_store = self.vector_stores[kb_id]
        return {
            'chunk_count': len(vector_store.chunks),
            'vector_dimension': vector_store.vectors.shape[1] if vector_store.vectors is not None else 0,
            'total_characters': sum(len(chunk) for chunk in vector_store.chunks),
            'average_chunk_size': np.mean([len(chunk) for chunk in vector_store.chunks]) if vector_store.chunks else 0
        }
