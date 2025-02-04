import requests
import streamlit as st
from typing import Optional, Dict, Any, List
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import re
from dataclasses import dataclass

@dataclass
class Document:
    content: str
    metadata: Dict[str, Any]

class WatsonX:
    def __init__(self, api_key: str):
        """初始化 WatsonX API 和向量存儲"""
        # IBM Cloud API 初始化
        token_response = requests.post(
            'https://iam.cloud.ibm.com/identity/token',
            data={
                "apikey": api_key,
                "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'
            }
        )
        mltoken = token_response.json()["access_token"]
        
        self.url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {mltoken}"
        }
        
        # 向量存儲初始化
        self.embedding_model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
        self.vector_store = None
        self.chunks = []
        self.chunk_size = 500
        self.chunk_overlap = 50
        
    def process_document(self, content: str, metadata: Dict[str, Any] = None):
        """處理文檔並建立向量索引"""
        # 文檔分塊
        self.chunks = self._create_chunks(content)
        
        # 生成嵌入向量
        embeddings = self.embedding_model.encode(self.chunks)
        
        # 初始化 FAISS 索引
        dimension = embeddings.shape[1]
        self.vector_store = faiss.IndexFlatL2(dimension)
        
        # 添加向量到索引
        self.vector_store.add(np.array(embeddings).astype('float32'))
        
        return len(self.chunks)
        
    def _create_chunks(self, text: str) -> List[str]:
        """智能文檔分塊"""
        # 清理文本
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 先嘗試用【房貸】分割
        if '【房貸】' in text:
            sections = text.split('【房貸】')
            base_chunks = ['【房貸】' + s.strip() for s in sections if s.strip()]
        else:
            # 如果沒有特定標記，使用滑動窗口分塊
            base_chunks = []
            start = 0
            while start < len(text):
                end = start + self.chunk_size
                if end > len(text):
                    end = len(text)
                chunk = text[start:end]
                if chunk.strip():
                    base_chunks.append(chunk.strip())
                start = end - self.chunk_overlap
                
        return base_chunks

    def find_relevant_context(self, query: str, top_k: int = 3) -> str:
        """基於語義相似度搜索相關上下文"""
        if not self.vector_store or not self.chunks:
            return ""
            
        try:
            # 生成查詢向量
            query_vector = self.embedding_model.encode([query])
            
            # 執行向量搜索
            distances, indices = self.vector_store.search(
                np.array(query_vector).astype('float32'), 
                top_k
            )
            
            # 獲取最相關的文本片段
            relevant_chunks = [self.chunks[i] for i in indices[0]]
            
            return '\n\n'.join(relevant_chunks)
            
        except Exception as e:
            st.error(f"搜索錯誤: {str(e)}")
            return ""

    def generate_response(self, context: str, user_input: str) -> Optional[str]:
        """生成回應"""
        prompt = f"""<|start_of_role|>system<|end_of_role|>您是台新銀行的專業房貸助理，專門協助房貸業務人員處理客戶諮詢。\
您具備豐富的房貸產品知識、流程經驗和銀行內部規定的了解。您應該：
1. 使用專業但易懂的語言
2. 提供明確的解釋和建議
3. 必要時引用具體的政策或規定
4. 若沒有特定資訊，請提供一般性建議

以下是相關的參考資料：

{context}
<|end_of_text|>
<|start_of_role|>user<|end_of_role|>{user_input}<|end_of_text|>
<|start_of_role|>assistant<|end_of_role|>"""

        payload = {
            "input": prompt,
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": 500,
                "min_new_tokens": 0,
                "repetition_penalty": 1
            },
            "model_id": "ibm/granite-3-8b-instruct",
            "project_id": "d91fb3ca-54ec-462a-9a26-491104a1d49d"
        }

        try:
            response = requests.post(
                self.url,
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            
            return response.json().get('results', [{}])[0].get(
                'generated_text',
                None
            )
            
        except requests.exceptions.RequestException as e:
            st.error(f"API 請求失敗: {str(e)}")
            return None