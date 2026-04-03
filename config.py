"""
GEO 工具配置文件
管理各平台的配置和全局设置
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class PlatformConfig:
    """平台配置基类"""
    enabled: bool = True
    api_key: str = ""
    api_secret: str = ""
    access_token: str = ""
    refresh_token: str = ""
    extra_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class XiaohongshuConfig(PlatformConfig):
    """小红书配置"""
    app_id: str = ""
    app_secret: str = ""
    user_id: str = ""
    default_tags: list = field(default_factory=lambda: ['干货分享', '知识科普'])


@dataclass
class DouyinConfig(PlatformConfig):
    """抖音配置"""
    app_id: str = ""
    app_secret: str = ""
    open_id: str = ""
    default_music_id: str = ""


@dataclass
class WechatVideoConfig(PlatformConfig):
    """微信视频号配置"""
    app_id: str = ""
    app_secret: str = ""
    mch_id: str = ""


@dataclass
class GoogleSEOConfig(PlatformConfig):
    """Google SEO 配置"""
    brand_name: str = ""
    site_url: str = ""
    default_author: str = ""
    google_analytics_id: str = ""
    search_console_api_key: str = ""


@dataclass
class ZhihuConfig(PlatformConfig):
    """知乎配置"""
    client_id: str = ""
    client_secret: str = ""
    username: str = ""


@dataclass
class GeneratorConfig:
    """内容生成配置"""
    default_language: str = "zh"
    default_content_type: str = "article"
    default_target_length: int = 1500
    include_eeat: bool = True
    include_data_points: bool = True
    max_keywords: int = 8
    min_paragraphs: int = 3
    max_paragraphs: int = 10


@dataclass
class AnalyzerConfig:
    """分析器配置"""
    min_content_length: int = 50
    max_content_length: int = 50000
    enable_url_fetch: bool = True
    analysis_depth: str = "standard"  # quick, standard, deep


@dataclass
class AppConfig:
    """应用全局配置"""
    app_name: str = "GEO 内容分析工具"
    app_version: str = "2.0.0"
    debug: bool = False
    log_level: str = "INFO"
    data_dir: str = "./data"
    output_dir: str = "./output"
    max_history_items: int = 100


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or os.path.join(
            os.path.dirname(__file__), 'config.json'
        )
        
        # 初始化配置
        self.app = AppConfig()
        self.generator = GeneratorConfig()
        self.analyzer = AnalyzerConfig()
        
        # 平台配置
        self.xiaohongshu = XiaohongshuConfig()
        self.douyin = DouyinConfig()
        self.wechat_video = WechatVideoConfig()
        self.google_seo = GoogleSEOConfig()
        self.zhihu = ZhihuConfig()
        
        # 加载配置
        self.load()
    
    def load(self):
        """从文件加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 加载应用配置
                if 'app' in data:
                    self.app = AppConfig(**data['app'])
                
                # 加载生成器配置
                if 'generator' in data:
                    self.generator = GeneratorConfig(**data['generator'])
                
                # 加载分析器配置
                if 'analyzer' in data:
                    self.analyzer = AnalyzerConfig(**data['analyzer'])
                
                # 加载平台配置
                if 'xiaohongshu' in data:
                    self.xiaohongshu = XiaohongshuConfig(**data['xiaohongshu'])
                if 'douyin' in data:
                    self.douyin = DouyinConfig(**data['douyin'])
                if 'wechat_video' in data:
                    self.wechat_video = WechatVideoConfig(**data['wechat_video'])
                if 'google_seo' in data:
                    self.google_seo = GoogleSEOConfig(**data['google_seo'])
                if 'zhihu' in data:
                    self.zhihu = ZhihuConfig(**data['zhihu'])
                
            except Exception as e:
                print(f"加载配置文件失败: {e}")
    
    def save(self):
        """保存配置到文件"""
        data = {
            'app': asdict(self.app),
            'generator': asdict(self.generator),
            'analyzer': asdict(self.analyzer),
            'xiaohongshu': asdict(self.xiaohongshu),
            'douyin': asdict(self.douyin),
            'wechat_video': asdict(self.wechat_video),
            'google_seo': asdict(self.google_seo),
            'zhihu': asdict(self.zhihu)
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get_platform_config(self, platform: str) -> Dict[str, Any]:
        """获取指定平台的配置"""
        platform_map = {
            'xiaohongshu': self.xiaohongshu,
            'douyin': self.douyin,
            'wechat_video': self.wechat_video,
            'google_seo': self.google_seo,
            'zhihu': self.zhihu
        }
        
        config = platform_map.get(platform)
        if config:
            return asdict(config)
        return {}
    
    def update_platform_config(self, platform: str, config: Dict[str, Any]):
        """更新平台配置"""
        platform_map = {
            'xiaohongshu': ('xiaohongshu', XiaohongshuConfig),
            'douyin': ('douyin', DouyinConfig),
            'wechat_video': ('wechat_video', WechatVideoConfig),
            'google_seo': ('google_seo', GoogleSEOConfig),
            'zhihu': ('zhihu', ZhihuConfig)
        }
        
        if platform in platform_map:
            attr_name, config_class = platform_map[platform]
            current = getattr(self, attr_name)
            
            # 更新现有配置
            for key, value in config.items():
                if hasattr(current, key):
                    setattr(current, key, value)
            
            self.save()
    
    def get_all_platforms_config(self) -> Dict[str, Dict[str, Any]]:
        """获取所有平台配置"""
        return {
            'xiaohongshu': asdict(self.xiaohongshu),
            'douyin': asdict(self.douyin),
            'wechat_video': asdict(self.wechat_video),
            'google_seo': asdict(self.google_seo),
            'zhihu': asdict(self.zhihu)
        }
    
    def get_publisher_config(self) -> Dict[str, Dict[str, Any]]:
        """获取发布器配置 (用于 publisher.py)"""
        return {
            'xiaohongshu': asdict(self.xiaohongshu),
            'douyin': asdict(self.douyin),
            'wechat_video': asdict(self.wechat_video),
            'google_seo': asdict(self.google_seo),
            'zhihu': asdict(self.zhihu)
        }
    
    def get_generator_config(self) -> Dict[str, Any]:
        """获取生成器配置"""
        return asdict(self.generator)
    
    def get_analyzer_config(self) -> Dict[str, Any]:
        """获取分析器配置"""
        return asdict(self.analyzer)
    
    def reset_to_default(self):
        """重置为默认配置"""
        self.app = AppConfig()
        self.generator = GeneratorConfig()
        self.analyzer = AnalyzerConfig()
        self.xiaohongshu = XiaohongshuConfig()
        self.douyin = DouyinConfig()
        self.wechat_video = WechatVideoConfig()
        self.google_seo = GoogleSEOConfig()
        self.zhihu = ZhihuConfig()
        self.save()


# 全局配置实例
_config_instance: Optional[ConfigManager] = None


def get_config(config_file: str = None) -> ConfigManager:
    """获取全局配置实例"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager(config_file)
    return _config_instance


def init_config(config_file: str = None) -> ConfigManager:
    """初始化配置"""
    global _config_instance
    _config_instance = ConfigManager(config_file)
    return _config_instance


# 默认配置模板
DEFAULT_CONFIG_TEMPLATE = {
    "app": {
        "app_name": "GEO 内容分析工具",
        "app_version": "2.0.0",
        "debug": False,
        "log_level": "INFO",
        "data_dir": "./data",
        "output_dir": "./output",
        "max_history_items": 100
    },
    "generator": {
        "default_language": "zh",
        "default_content_type": "article",
        "default_target_length": 1500,
        "include_eeat": True,
        "include_data_points": True,
        "max_keywords": 8,
        "min_paragraphs": 3,
        "max_paragraphs": 10
    },
    "analyzer": {
        "min_content_length": 50,
        "max_content_length": 50000,
        "enable_url_fetch": True,
        "analysis_depth": "standard"
    },
    "xiaohongshu": {
        "enabled": True,
        "api_key": "",
        "api_secret": "",
        "access_token": "",
        "app_id": "",
        "app_secret": "",
        "user_id": "",
        "default_tags": ["干货分享", "知识科普"]
    },
    "douyin": {
        "enabled": True,
        "api_key": "",
        "api_secret": "",
        "access_token": "",
        "app_id": "",
        "app_secret": "",
        "open_id": "",
        "default_music_id": ""
    },
    "wechat_video": {
        "enabled": True,
        "api_key": "",
        "api_secret": "",
        "access_token": "",
        "app_id": "",
        "app_secret": "",
        "mch_id": ""
    },
    "google_seo": {
        "enabled": True,
        "brand_name": "",
        "site_url": "",
        "default_author": "",
        "google_analytics_id": "",
        "search_console_api_key": ""
    },
    "zhihu": {
        "enabled": True,
        "api_key": "",
        "api_secret": "",
        "access_token": "",
        "client_id": "",
        "client_secret": "",
        "username": ""
    }
}


def create_default_config_file(filepath: str):
    """创建默认配置文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(DEFAULT_CONFIG_TEMPLATE, f, ensure_ascii=False, indent=2)
