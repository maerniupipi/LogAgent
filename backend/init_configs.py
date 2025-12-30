"""
初始化服务器配置
"""
from server_config import ServerConfigManager

def init_default_configs():
    """初始化默认的三个环境配置"""
    config_manager = ServerConfigManager()
    
    # 清空现有配置（可选）
    # config_manager.configs = []
    
    # UAT 环境
    config_manager.add_config(
        name="UAT环境",
        host="192.168.100.127",
        port=22,
        username="root",
        password="Fytrd127",
        containers=["otc-market", "otc-api", "otc-web"]
    )
    
    # TEST 环境
    config_manager.add_config(
        name="TEST环境",
        host="192.168.100.126",
        port=22,
        username="root",
        password="Ayfgh126",
        containers=["otc-market", "otc-api", "otc-web"]
    )
    
    # DEV 环境
    config_manager.add_config(
        name="DEV环境",
        host="192.168.100.27",
        port=22,
        username="root",
        password="DR.otc@2022",
        containers=["otc-market", "otc-api", "otc-web"]
    )
    
    print("✅ 配置初始化完成！")
    print("\n已添加的配置：")
    for config in config_manager.get_all_configs():
        print(f"  - {config['name']}: {config['username']}@{config['host']}")
        if config['containers']:
            print(f"    容器: {', '.join(config['containers'])}")

if __name__ == "__main__":
    init_default_configs()
