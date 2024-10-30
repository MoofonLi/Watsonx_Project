import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    IAM_TOKEN = os.getenv("IAM_TOKEN", "your-iam-token")
    DEPLOYMENT_ID = os.getenv("DEPLOYMENT_ID", "your-deployment-id")