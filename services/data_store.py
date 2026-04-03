"""
数据存储服务
使用JSON文件存储数据
"""
import json
import os
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid

from models import Brand, Article, PublishRecord, PlatformAccount, Platform


class DataStore:
    """数据存储类"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self._ensure_data_dir()
        
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _get_file_path(self, filename: str) -> str:
        """获取文件路径"""
        return os.path.join(self.data_dir, filename)
    
    def _load_json(self, filename: str) -> List[Dict]:
        """加载JSON文件"""
        filepath = self._get_file_path(filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_json(self, filename: str, data: List[Dict]):
        """保存JSON文件"""
        filepath = self._get_file_path(filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # ========== 品牌管理 ==========
    
    def get_all_brands(self) -> List[Brand]:
        """获取所有品牌"""
        data = self._load_json('brands.json')
        brands = []
        for item in data:
            # 转换accounts字典
            accounts = {}
            for platform_name, account_data in item.get('accounts', {}).items():
                platform = Platform(platform_name)
                accounts[platform] = PlatformAccount(**account_data)
            item['accounts'] = accounts
            brands.append(Brand(**item))
        return brands
    
    def get_brand(self, brand_id: str) -> Optional[Brand]:
        """获取单个品牌"""
        brands = self.get_all_brands()
        for brand in brands:
            if brand.id == brand_id:
                return brand
        return None
    
    def save_brand(self, brand: Brand) -> Brand:
        """保存品牌"""
        brands = self.get_all_brands()
        
        # 转换accounts为可序列化的字典
        brand_dict = {
            'id': brand.id,
            'name': brand.name,
            'description': brand.description,
            'logo_url': brand.logo_url,
            'website': brand.website,
            'industry': brand.industry,
            'accounts': {},
            'created_at': brand.created_at,
            'updated_at': datetime.now().isoformat()
        }
        
        for platform, account in brand.accounts.items():
            brand_dict['accounts'][platform.value] = {
                'platform': platform.value,
                'account_name': account.account_name,
                'account_id': account.account_id,
                'api_key': account.api_key,
                'api_secret': account.api_secret,
                'cookies': account.cookies,
                'is_active': account.is_active,
                'notes': account.notes,
                'created_at': account.created_at
            }
        
        # 更新或添加
        found = False
        for i, b in enumerate(brands):
            if b.id == brand.id:
                brands[i] = brand
                found = True
                break
        
        if not found:
            brands.append(brand)
        
        # 保存
        brands_data = []
        for b in brands:
            b_dict = {
                'id': b.id,
                'name': b.name,
                'description': b.description,
                'logo_url': b.logo_url,
                'website': b.website,
                'industry': b.industry,
                'accounts': {},
                'created_at': b.created_at,
                'updated_at': b.updated_at
            }
            for platform, account in b.accounts.items():
                b_dict['accounts'][platform.value] = {
                    'platform': platform.value,
                    'account_name': account.account_name,
                    'account_id': account.account_id,
                    'api_key': account.api_key,
                    'api_secret': account.api_secret,
                    'cookies': account.cookies,
                    'is_active': account.is_active,
                    'notes': account.notes,
                    'created_at': account.created_at
                }
            brands_data.append(b_dict)
        
        self._save_json('brands.json', brands_data)
        return brand
    
    def delete_brand(self, brand_id: str) -> bool:
        """删除品牌"""
        brands = self.get_all_brands()
        brands = [b for b in brands if b.id != brand_id]
        
        brands_data = []
        for b in brands:
            b_dict = {
                'id': b.id,
                'name': b.name,
                'description': b.description,
                'logo_url': b.logo_url,
                'website': b.website,
                'industry': b.industry,
                'accounts': {},
                'created_at': b.created_at,
                'updated_at': b.updated_at
            }
            for platform, account in b.accounts.items():
                b_dict['accounts'][platform.value] = {
                    'platform': platform.value,
                    'account_name': account.account_name,
                    'account_id': account.account_id,
                    'api_key': account.api_key,
                    'api_secret': account.api_secret,
                    'cookies': account.cookies,
                    'is_active': account.is_active,
                    'notes': account.notes,
                    'created_at': account.created_at
                }
            brands_data.append(b_dict)
        
        self._save_json('brands.json', brands_data)
        return True
    
    # ========== 文章管理 ==========
    
    def get_all_articles(self) -> List[Article]:
        """获取所有文章"""
        data = self._load_json('articles.json')
        return [Article(**item) for item in data]
    
    def get_article(self, article_id: str) -> Optional[Article]:
        """获取单个文章"""
        articles = self.get_all_articles()
        for article in articles:
            if article.id == article_id:
                return article
        return None
    
    def save_article(self, article: Article) -> Article:
        """保存文章"""
        articles = self.get_all_articles()
        
        # 更新或添加
        found = False
        for i, a in enumerate(articles):
            if a.id == article.id:
                articles[i] = article
                found = True
                break
        
        if not found:
            articles.append(article)
        
        # 保存
        articles_data = [{
            'id': a.id,
            'title': a.title,
            'content': a.content,
            'brand_id': a.brand_id,
            'keywords': a.keywords,
            'status': a.status,
            'created_at': a.created_at,
            'updated_at': datetime.now().isoformat()
        } for a in articles]
        
        self._save_json('articles.json', articles_data)
        return article
    
    def delete_article(self, article_id: str) -> bool:
        """删除文章"""
        articles = self.get_all_articles()
        articles = [a for a in articles if a.id != article_id]
        
        articles_data = [{
            'id': a.id,
            'title': a.title,
            'content': a.content,
            'brand_id': a.brand_id,
            'keywords': a.keywords,
            'status': a.status,
            'created_at': a.created_at,
            'updated_at': a.updated_at
        } for a in articles]
        
        self._save_json('articles.json', articles_data)
        return True
    
    # ========== 发布记录管理 ==========
    
    def get_all_publish_records(self) -> List[PublishRecord]:
        """获取所有发布记录"""
        data = self._load_json('publish_records.json')
        records = []
        for item in data:
            # 转换platform字符串为枚举
            platform_value = item.get('platform')
            if isinstance(platform_value, str):
                try:
                    item['platform'] = Platform(platform_value)
                except ValueError:
                    # 如果值不匹配任何枚举，保留原值
                    pass
            records.append(PublishRecord(**item))
        return records
    
    def get_publish_records_by_article(self, article_id: str) -> List[PublishRecord]:
        """获取文章的发布记录"""
        records = self.get_all_publish_records()
        return [r for r in records if r.article_id == article_id]
    
    def save_publish_record(self, record: PublishRecord) -> PublishRecord:
        record.created_at = datetime.now().isoformat()
        """保存发布记录"""
        records = self.get_all_publish_records()
        
        # 更新或添加
        found = False
        for i, r in enumerate(records):
            if r.id == record.id:
                records[i] = record
                found = True
                break
        
        if not found:
            records.append(record)
        
        # 保存
        records_data = [{
            'id': r.id,
            'article_id': r.article_id,
            'brand_id': r.brand_id,
            'platform': r.platform.value if isinstance(r.platform, Platform) else r.platform,
            'platform_account': r.platform_account,
            'status': r.status,
            'publish_url': r.publish_url,
            'error_message': r.error_message,
            'created_at': r.created_at,
            'updated_at': datetime.now().isoformat()  # Ensure updated_at is set as current time
        } for r in records]
        
        self._save_json('publish_records.json', records_data)
        return record
    
    def delete_publish_record(self, record_id: str) -> bool:
        """删除发布记录"""
        records = self.get_all_publish_records()
        records = [r for r in records if r.id != record_id]
        
        records_data = [{
            'id': r.id,
            'article_id': r.article_id,
            'brand_id': r.brand_id,
            'platform': r.platform.value if isinstance(r.platform, Platform) else r.platform,
            'platform_account': r.platform_account,
            'status': r.status,
            'publish_url': r.publish_url,
            'error_message': r.error_message,
            'created_at': r.created_at,
            'updated_at': r.updated_at
        } for r in records]
        
        self._save_json('publish_records.json', records_data)
        return True
