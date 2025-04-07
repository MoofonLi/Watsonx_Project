import requests
import json
from typing import Dict, List, Any, Optional
import streamlit as st

class AgentLabIntegration:
    """
    Agent Lab 集成類，用於與 Agent Lab API 交互
    """
    
    def __init__(self, token_manager=None):
        """
        初始化 Agent Lab 集成
        
        Args:
            token_manager: 負責管理 API token 的對象
        """
        self.token_manager = token_manager
        self.agent_url = "https://private.api.dataplatform.cloud.ibm.com/wx/v1/ai-runtime/prediction"
        self.space_id = "c9dc34b6-71dc-40b6-b0b6-481d50e34f18"  # 從 agent_lab.py 中獲取
    
    def _get_headers(self) -> Optional[Dict[str, str]]:
        """
        獲取帶有 token 的請求頭
        
        Returns:
            Dict[str, str]: 包含 token 的請求頭
        """
        token = self.token_manager.get_token() if self.token_manager else None
        
        if not token:
            st.error("無法獲取 Agent Lab API Token")
            return None
            
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
    
    def generate_response(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """
        透過 Agent Lab API 生成回應
        
        Args:
            messages: 對話歷史消息列表
            
        Returns:
            str: 生成的回應
        """
        headers = self._get_headers()
        if not headers:
            return "系統無法連接到 Agent Lab 服務。"
        
        payload = {
            "space_id": self.space_id,
            "input_data": [
                {
                    "fields": ["messages"],
                    "values": [[messages]]
                }
            ]
        }
        
        try:
            response = requests.post(
                self.agent_url,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            # 處理響應數據
            response_data = response.json()
            
            # 提取生成的文本回應
            generated_response = None
            try:
                outputs = response_data.get("predictions", [])[0].get("values", [])[0]
                choices = outputs.get("choices", [])
                if choices and len(choices) > 0:
                    generated_response = choices[0].get("message", {}).get("content", "")
            except (IndexError, KeyError) as e:
                st.error(f"無法解析 API 響應: {str(e)}")
            
            return generated_response or "無法從 API 獲取有效回應。"
            
        except requests.exceptions.RequestException as e:
            st.error(f"API 請求失敗: {str(e)}")
            return "API 請求失敗。請稍後再試。"
    
    def format_context_as_system_message(self, context: str) -> Dict[str, str]:
        """
        將上下文格式化為系統消息
        
        Args:
            context: 上下文文本
            
        Returns:
            Dict[str, str]: 系統消息
        """
        return {
            "role": "system",
            "content": f"""您是台新銀行的專業房貸助理，專門協助房貸業務人員處理客戶諮詢。
您具備豐富的房貸產品知識、流程經驗和銀行內部規定的了解。您應該：
1. 使用專業但易懂的語言
2. 提供明確的解釋和建議
3. 必要時引用具體的政策或規定
4. 若沒有特定資訊，請提供一般性建議

以下是相關的參考資料：

{context}"""
        }
    
    def prepare_messages(self, conversation_history: List[Dict[str, str]], context: str) -> List[Dict[str, str]]:
        """
        準備用於 Agent Lab API 的消息格式
        
        Args:
            conversation_history: 對話歷史
            context: 上下文信息
            
        Returns:
            List[Dict[str, str]]: 帶有系統消息的完整消息列表
        """
        system_message = self.format_context_as_system_message(context)
        
        # 合併系統消息和對話歷史
        messages = [system_message] + conversation_history
        
        return messages