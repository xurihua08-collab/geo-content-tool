"""
数据模型定义
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class Platform(Enum):
    """支持的平台"""
    GOOGLE_SEO = "google_seo"
    ZHIHU = "zhihu"
    TOUTIAO = "toutiao"
    BAIJIAHAO = "baijiahao"
    FOB = "fob"


@dataclass
class PlatformAccount:
    """平台账号信息"""
    platform: Platform
    account_name: str
    account_id: str = ""
    api_key: str = ""
    api_secret: str = ""
    cookies: str = ""
    is_active: bool = True
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Brand:
    """品牌信息"""
    id: str
    name: str
    description: str = ""
    logo_url: str = ""
    website: str = ""
    industry: str = ""
    accounts: Dict[Platform, PlatformAccount] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Article:
    """文章信息"""
    id: str
    title: str
    content: str
    brand_id: str
    keywords: List[str] = field(default_factory=list)
    status: str = "draft"  # draft, publishing, published, failed
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class PublishRecord:
    """发布记录"""
    id: str
    article_id: str
    brand_id: str
    platform: Platform
    platform_account: str
    status: str  # pending, publishing, success, failed
    publish_url: str = ""
    error_message: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class UserSettings:
    """用户设置"""
    brands: List[Brand] = field(default_factory=list)
    default_brand_id: str = ""
    theme: str = "light"
    language: str = "zh"
