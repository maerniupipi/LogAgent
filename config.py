"""配置文件 - 本地模型连接配置"""
import os
from dotenv import load_dotenv

load_dotenv()

# 本地模型配置（根据你的 DGX 部署调整）
LOCAL_MODEL_CONFIG = {
    "base_url": os.getenv("LOCAL_MODEL_URL", "http://localhost:8000/v1"),
    "api_key": os.getenv("LOCAL_MODEL_API_KEY", "not-needed"),
    "model_name": os.getenv("LOCAL_MODEL_NAME", "local-model"),
    "temperature": 0.7,
    "max_tokens": 2000,
}
