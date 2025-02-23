import yaml
import os

def load_config():
    """加载配置文件"""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'config',
        'config.yaml'
    )
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)