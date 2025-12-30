"""
服务器配置管理
"""
import json
import os
from typing import List, Dict, Optional

# 使用绝对路径
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "server_configs.json")


class ServerConfigManager:
    """服务器配置管理器"""
    
    def __init__(self, config_file: str = CONFIG_FILE):
        self.config_file = config_file
        self.configs = self._load_configs()
    
    def _load_configs(self) -> List[Dict]:
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []
    
    def _save_configs(self):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.configs, f, ensure_ascii=False, indent=2)
    
    def add_config(self, name: str, host: str, port: int, username: str, 
                   password: str = None, key_file: str = None, 
                   containers: List[str] = None) -> Dict:
        """添加配置"""
        config = {
            "id": len(self.configs) + 1,
            "name": name,
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "key_file": key_file,
            "containers": containers or []
        }
        self.configs.append(config)
        self._save_configs()
        return config
    
    def get_config(self, config_id: int) -> Optional[Dict]:
        """获取配置"""
        for config in self.configs:
            if config["id"] == config_id:
                return config
        return None
    
    def get_all_configs(self) -> List[Dict]:
        """获取所有配置"""
        # 返回时不包含密码
        return [
            {**config, "password": "******" if config.get("password") else None}
            for config in self.configs
        ]
    
    def update_config(self, config_id: int, **kwargs):
        """更新配置"""
        for config in self.configs:
            if config["id"] == config_id:
                config.update(kwargs)
                self._save_configs()
                return True
        return False
    
    def delete_config(self, config_id: int):
        """删除配置"""
        self.configs = [c for c in self.configs if c["id"] != config_id]
        self._save_configs()
