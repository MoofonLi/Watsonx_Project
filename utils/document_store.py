import streamlit as st
import pandas as pd
import os
import io
import uuid
import json
import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

class DocumentStore:
    def __init__(self, storage_dir: str = "QA_files"):
        # Initialize document store
        self.storage_dir = storage_dir
        self._create_storage_dir()
        
        if 'doc_index' not in st.session_state:
            st.session_state.doc_index = self._load_document_index()
    
    def _create_storage_dir(self):
        # Create storage directory if needed
        os.makedirs(self.storage_dir, exist_ok=True)
        index_file = Path(self.storage_dir) / "document_index.json"
        if not index_file.exists():
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def _load_document_index(self) -> List[Dict[str, Any]]:
        # Load document index
        index_file = Path(self.storage_dir) / "document_index.json"
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    
    def _save_document_index(self):
        # Save document index
        index_file = Path(self.storage_dir) / "document_index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(st.session_state.doc_index, f, ensure_ascii=False)
    
    def read_csv(self, file_bytes) -> Optional[str]:
        try:
            csv_file = io.BytesIO(file_bytes)
            
            # Try different encodings
            encodings = ['utf-8', 'big5', 'gb18030']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(csv_file, encoding=encoding)
                    csv_file.seek(0)
                    break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    st.error(f"CSV read error: {str(e)}")
                    return None
            
            if df is None:
                st.error("Cannot identify CSV encoding")
                return None
                
            # Convert to text format
            text_content = []
            text_content.append(",".join(df.columns.astype(str)))
            
            for _, row in df.iterrows():
                text_content.append(",".join(row.astype(str)))
            
            return '\n'.join(text_content)
            
        except Exception as e:
            st.error(f"CSV processing error: {str(e)}")
            return None
    
    def add_document(self, file_name: str, file_content: str) -> str:
        # Generate unique ID
        doc_id = str(uuid.uuid4())
        
        # File content path
        content_path = Path(self.storage_dir) / f"{doc_id}.txt"
        
        # Save file content
        with open(content_path, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        # Add to index
        doc_info = {
            "id": doc_id,
            "name": file_name,
            "type": "csv",
            "added_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "size_kb": round(len(file_content) / 1024, 2)
        }
        
        st.session_state.doc_index.append(doc_info)
        self._save_document_index()
        
        return doc_id
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        return st.session_state.doc_index
    
    def get_document_content(self, doc_id: str) -> Optional[str]:
        content_path = Path(self.storage_dir) / f"{doc_id}.txt"
        try:
            with open(content_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            st.error(f"File read error: {str(e)}")
            return None
    
    def delete_document(self, doc_id: str) -> bool:
        try:
            # Delete file content
            content_path = Path(self.storage_dir) / f"{doc_id}.txt"
            if content_path.exists():
                os.remove(content_path)
            
            # Remove from index
            st.session_state.doc_index = [
                doc for doc in st.session_state.doc_index if doc["id"] != doc_id
            ]
            self._save_document_index()
            
            return True
        except Exception as e:
            st.error(f"Delete error: {str(e)}")
            return False
    
    def get_all_document_contents(self) -> str:
        all_contents = []
        
        for doc in st.session_state.doc_index:
            content = self.get_document_content(doc["id"])
            if content:
                all_contents.append(f"--- File: {doc['name']} ---\n{content}")
        
        return "\n\n".join(all_contents)