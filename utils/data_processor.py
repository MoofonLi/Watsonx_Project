import requests
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from config import OpenScaleConfig

class DataProcessor:
    def __init__(self, apikey: str, instance_id: str):
        self.instance_id = instance_id
        self.authenticator = IAMAuthenticator(apikey)
        self.base_url = f"https://api.aiopenscale.cloud.ibm.com/{instance_id}/v2"
        self.config = OpenScaleConfig
        self.headers = None
        self._update_token()
        
    def _update_token(self):
        token = self.authenticator.token_manager.get_token()
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def _make_request(self, endpoint, params=None):
        """統一的請求處理方法"""
        try:
            url = f"{self.base_url}/{endpoint}"
            # 添加必要的參數
            if params is None:
                params = {}
            params.update({
                'version': self.config.API_VERSION
            })
            
            response = requests.get(url, headers=self.headers, params=params)
            
            # 打印請求信息用於調試
            print(f"Request URL: {response.url}")
            print(f"Response Status: {response.status_code}")
            print(f"Response Content: {response.text[:500]}...")  # 只打印前500字符
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Request Error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response Status Code: {e.response.status_code}")
                print(f"Response Content: {e.response.text}")
            raise Exception(f"API request failed: {str(e)}")

    def get_model_metrics(self):
        """獲取模型監控指標"""
        endpoint = f"subscriptions/{self.config.SUBSCRIPTION_ID}/monitors/metrics"
        return self._make_request(endpoint)
        
    def get_quality_metrics(self):
        """獲取品質指標"""
        endpoint = f"subscriptions/{self.config.SUBSCRIPTION_ID}/monitors/quality/measurements"
        return self._make_request(endpoint)
        
    def get_fairness_metrics(self):
        """獲取公平性指標"""
        endpoint = f"subscriptions/{self.config.SUBSCRIPTION_ID}/monitors/fairness/measurements"
        return self._make_request(endpoint)
        
    def get_deployment_info(self):
        """獲取部署信息"""
        endpoint = f"service_providers/{self.config.SERVICE_PROVIDER_ID}/deployments/{self.config.DEPLOYMENT_ID}"
        return self._make_request(endpoint)