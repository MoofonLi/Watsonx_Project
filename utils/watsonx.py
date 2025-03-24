import requests
import streamlit as st
from typing import Optional, Dict, Any, List
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import re
from dataclasses import dataclass
import os


@dataclass
class Document:
    content: str
    metadata: Dict[str, Any]

class WatsonX:
    def __init__(self, token_manager=None):
        # Initialize WatsonX API and vector storage
        self.token_manager = token_manager
        
        # API settings
        self.url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
        
        # Vector storage initialization
        self.embedding_model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
        self.vector_store = None
        self.chunks = []
        self.chunk_size = 500
        self.chunk_overlap = 50
    
    def _get_headers(self):
        # Get headers with fresh token
        token = self.token_manager.get_token() if self.token_manager else None
        
        if not token:
            st.error("Unable to get WatsonX API Token")
            return None
            
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
    def process_document(self, content: str, metadata: Dict[str, Any] = None):
        # Process document and build vector index
        self.chunks = self._create_chunks(content)
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(self.chunks)
        
        # Initialize FAISS index
        dimension = embeddings.shape[1]
        self.vector_store = faiss.IndexFlatL2(dimension)
        
        # Add vectors to index
        self.vector_store.add(np.array(embeddings).astype('float32'))
        
        return len(self.chunks)
    
    def process_multiple_documents(self, documents: List[Document]):
        # Process multiple documents and build unified vector index
        all_chunks = []
        chunk_metadata = []
        
        # Create chunks for each document
        for doc in documents:
            doc_chunks = self._create_chunks(doc.content)
            all_chunks.extend(doc_chunks)
            
            # Add metadata for each chunk
            for _ in doc_chunks:
                chunk_metadata.append(doc.metadata)
        
        if not all_chunks:
            return 0
            
        # Generate embeddings
        embeddings = self.embedding_model.encode(all_chunks)
        
        # Initialize FAISS index
        dimension = embeddings.shape[1]
        self.vector_store = faiss.IndexFlatL2(dimension)
        
        # Add vectors to index
        self.vector_store.add(np.array(embeddings).astype('float32'))
        
        # Save chunks and metadata
        self.chunks = all_chunks
        self.chunks_metadata = chunk_metadata
        
        return len(all_chunks)
        
    def _create_chunks(self, text: str) -> List[str]:
        # Smart document chunking
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Try to split by 【房貸】 marker
        if '【房貸】' in text:
            sections = text.split('【房貸】')
            base_chunks = ['【房貸】' + s.strip() for s in sections if s.strip()]
        else:
            # Use sliding window chunking
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
        # Search for relevant context based on semantic similarity
        if not self.vector_store or not self.chunks:
            return ""
            
        try:
            # Generate query vector
            query_vector = self.embedding_model.encode([query])
            
            # Perform vector search
            distances, indices = self.vector_store.search(
                np.array(query_vector).astype('float32'), 
                top_k
            )
            
            # Get most relevant text chunks
            relevant_chunks = [self.chunks[i] for i in indices[0]]
            
            return '\n\n'.join(relevant_chunks)
            
        except Exception as e:
            st.error(f"Search error: {str(e)}")
            return ""

    def generate_response(self, context: str, user_input: str) -> Optional[str]:
        # Generate response
        headers = self._get_headers()
        if not headers:
            return "System cannot connect to WatsonX service."
            
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
                "max_new_tokens": 1000,
                "min_new_tokens": 0,
                "repetition_penalty": 1
            },
            "model_id": "ibm/",
            "project_id": "d91fb3ca-54ec-462a-9a26-491104a1d49d"
        }

        try:
            response = requests.post(
                self.url,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            return response.json().get('results', [{}])[0].get(
                'generated_text',
                None
            )
            
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {str(e)}")
            return "API request failed. Please try again later."