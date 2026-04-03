"""
内容分发模块
支持多平台内容适配和分发
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class Platform(Enum):
    """支持的平台"""
    GOOGLE_SEO = "google_seo"    # Google SEO
    ZHIHU = "zhihu"              # 知乎
    TOUTIAO = "toutiao"          # 今日头条
    BAIJIAHAO = "baijiahao"      # 百家号
    FOB = "fob"                  # 福步论坛


@dataclass
class PlatformContent:
    """平台适配后的内容"""
    platform: str
    title: str
    content: str
    tags: List[str]
    extras: Dict[str, Any]  # 平台特定元素
    character_count: int
    

class ContentPublisher:
    """内容分发器"""
    
    # 平台配置
    PLATFORM_CONFIG = {
        Platform.GOOGLE_SEO: {
            "name": "Google SEO",
            "max_title": 60,
            "max_content": 50000,
            "max_tags": 0,
            "style": "SEO文章",
            "features": ["meta_description", "headers", "keywords", "internal_links"]
        },
        Platform.ZHIHU: {
            "name": "知乎",
            "max_title": 50,
            "max_content": 20000,
            "max_tags": 5,
            "style": "问答/文章",
            "features": ["reference", "cta", "topic"]
        },
        Platform.TOUTIAO: {
            "name": "今日头条",
            "max_title": 30,
            "max_content": 20000,
            "max_tags": 5,
            "style": "资讯文章",
            "features": ["headline", "summary", "cover", "category"]
        },
        Platform.BAIJIAHAO: {
            "name": "百家号",
            "max_title": 40,
            "max_content": 50000,
            "max_tags": 5,
            "style": "自媒体文章",
            "features": ["headline", "summary", "cover", "column", "original"]
        },
        Platform.FOB: {
            "name": "福步论坛",
            "max_title": 100,
            "max_content": 100000,
            "max_tags": 0,
            "style": "外贸论坛帖子",
            "features": ["trade_focus", "practical", "discussion"]
        }
    }
    
    def __init__(self):
        self.adapters = {
            Platform.GOOGLE_SEO: self._adapt_google_seo,
            Platform.ZHIHU: self._adapt_zhihu,
            Platform.TOUTIAO: self._adapt_toutiao,
            Platform.BAIJIAHAO: self._adapt_baijiahao,
            Platform.FOB: self._adapt_fob
        }
    
    def publish(
        self, 
        content: str, 
        title: str, 
        platform: Platform,
        author_info: Optional[Dict[str, str]] = None
    ) -> PlatformContent:
        """
        将内容适配到指定平台
        
        Args:
            content: 原始内容
            title: 原始标题
            platform: 目标平台
            author_info: 作者信息
            
        Returns:
            PlatformContent: 适配后的内容
        """
        adapter = self.adapters.get(platform)
        if not adapter:
            raise ValueError(f"不支持的平台: {platform}")
        
        return adapter(content, title, author_info)
    
    def publish_all(
        self, 
        content: str, 
        title: str,
        author_info: Optional[Dict[str, str]] = None
    ) -> Dict[str, PlatformContent]:
        """
        将内容适配到所有平台
        
        Args:
            content: 原始内容
            title: 原始标题
            author_info: 作者信息
            
        Returns:
            Dict[str, PlatformContent]: 各平台的适配内容
        """
        results = {}
        for platform in Platform:
            try:
                result = self.publish(content, title, platform, author_info)
                results[platform.value] = result
            except Exception as e:
                results[platform.value] = None
        
        return results
    
    def _adapt_google_seo(
        self, 
        content: str, 
        title: str, 
        author_info: Optional[Dict[str, str]]
    ) -> PlatformContent:
        """适配Google SEO格式"""
        config = self.PLATFORM_CONFIG[Platform.GOOGLE_SEO]
        
        # 处理标题 - SEO优化
        adapted_title = self._optimize_seo_title(title)
        adapted_title = self._truncate_text(adapted_title, config["max_title"])
        
        # 处理内容 - 保持完整结构
        adapted_content = content
        
        # 生成meta description
        meta_desc = self._generate_meta_description(content)
        
        # 提取关键词
        keywords = self._extract_keywords_for_seo(content, title)
        
        # 优化标题层级
        adapted_content = self._optimize_headers(adapted_content)
        
        # 添加作者信息
        if author_info:
            author_box = self._generate_author_box(author_info)
            adapted_content += f"\n\n{author_box}"
        
        extras = {
            "meta_description": meta_desc,
            "keywords": keywords,
            "slug": self._generate_slug(title),
            "reading_time": f"{len(content) // 500} 分钟",
            "schema_type": "Article"
        }
        
        return PlatformContent(
            platform=config["name"],
            title=adapted_title,
            content=adapted_content,
            tags=keywords,
            extras=extras,
            character_count=len(adapted_content)
        )
    
    def _adapt_zhihu(
        self, 
        content: str, 
        title: str, 
        author_info: Optional[Dict[str, str]]
    ) -> PlatformContent:
        """适配知乎格式"""
        config = self.PLATFORM_CONFIG[Platform.ZHIHU]
        
        # 处理标题 - 知乎风格
        adapted_title = self._optimize_zhihu_title(title)
        adapted_title = self._truncate_text(adapted_title, config["max_title"])
        
        # 处理内容
        adapted_content = content
        
        # 知乎风格优化
        adapted_content = self._optimize_zhihu_content(adapted_content)
        
        # 添加引用
        adapted_content = self._add_references_zhihu(adapted_content)
        
        # 添加互动引导
        cta = "\n\n---\n\n**如果本文对你有帮助，欢迎点赞、收藏、关注！**\n\n"
        if author_info and author_info.get("name"):
            cta += f"我是{author_info['name']}，{author_info.get('title', '行业从业者')}，"
            cta += "会持续分享相关领域的干货内容。"
        
        adapted_content += cta
        
        # 生成话题标签
        tags = self._generate_tags(content, config["max_tags"])
        tags = [f"{tag}" for tag in tags]
        
        extras = {
            "回答结构": "总-分-总",
            "引用规范": "需标注来源",
            "图片建议": "配图增加可信度",
            "话题选择": "选择相关问题"
        }
        
        return PlatformContent(
            platform=config["name"],
            title=adapted_title,
            content=adapted_content,
            tags=tags,
            extras=extras,
            character_count=len(adapted_content)
        )
    
    # ============ 辅助方法 ============
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """截断文本到指定长度"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    def _clean_markdown(self, content: str) -> str:
        """清理Markdown标记"""
        # 移除标题标记
        content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)
        # 移除粗体/斜体
        content = re.sub(r'\*\*?|\_\_?', '', content)
        # 移除链接
        content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
        # 移除代码块
        content = re.sub(r'```[\s\S]*?```', '', content)
        content = re.sub(r'`([^`]+)`', r'\1', content)
        return content.strip()
    
    def _extract_key_points(self, content: str, count: int) -> List[str]:
        """提取关键要点"""
        # 按句子分割
        sentences = re.split(r'[。！？\n]', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        # 选择最长的几个句子作为要点
        sentences.sort(key=len, reverse=True)
        return sentences[:count]
    
    def _generate_tags(self, content: str, max_tags: int) -> List[str]:
        """生成标签"""
        # 简单实现：从内容中提取关键词
        common_tags = [
            "干货分享", "经验总结", "实用技巧", "行业洞察",
            "新手必看", "进阶指南", "避坑指南", "最新趋势"
        ]
        
        import random
        selected = random.sample(common_tags, min(max_tags, len(common_tags)))
        return selected
    
    def _generate_cta(self, topic: str, platform: str) -> str:
        """生成行动号召"""
        return "感谢阅读！"
    
    def _optimize_seo_title(self, title: str) -> str:
        """优化SEO标题"""
        # 添加年份增强时效性
        if "202" not in title:
            title = f"2024年{title}"
        
        # 添加修饰词
        modifiers = ["完整指南", "最佳实践", "专家分享"]
        import random
        modifier = random.choice(modifiers)
        
        if modifier not in title:
            title = f"{title} - {modifier}"
        
        return title
    
    def _generate_meta_description(self, content: str) -> str:
        """生成Meta Description"""
        # 提取前150个字符
        desc = content[:150].replace('\n', ' ').strip()
        if len(desc) >= 147:
            desc = desc[:147] + "..."
        return desc
    
    def _extract_keywords_for_seo(self, content: str, title: str) -> List[str]:
        """提取SEO关键词"""
        # 简单实现
        words = re.findall(r'[\u4e00-\u9fa5]{2,6}', content)
        word_freq = {}
        for word in words:
            if len(word) >= 2:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 返回频率最高的词
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:10]]
    
    def _optimize_headers(self, content: str) -> str:
        """优化标题层级"""
        # 确保只有一个H1
        h1_count = content.count('\n# ')
        if h1_count > 1:
            # 将额外的H1转换为H2
            lines = content.split('\n')
            h1_found = False
            for i, line in enumerate(lines):
                if line.startswith('# ') and not line.startswith('##'):
                    if h1_found:
                        lines[i] = '#' + line
                    else:
                        h1_found = True
            content = '\n'.join(lines)
        
        return content
    
    def _generate_author_box(self, author_info: Dict[str, str]) -> str:
        """生成作者信息框"""
        box = "\n\n---\n\n## 关于作者\n\n"
        if author_info.get("name"):
            box += f"**{author_info['name']}**"
        if author_info.get("title"):
            box += f" - {author_info['title']}"
        box += "\n\n"
        if author_info.get("bio"):
            box += f"{author_info['bio']}\n\n"
        if author_info.get("company"):
            box += f"📍 {author_info['company']}"
        
        return box
    
    def _generate_slug(self, title: str) -> str:
        """生成URL slug"""
        # 简单的slug生成
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug[:50]
    
    def _optimize_zhihu_title(self, title: str) -> str:
        """优化知乎标题"""
        # 知乎风格：疑问式或经验分享式
        patterns = [
            f"如何评价{title}？",
            f"{title}是一种怎样的体验？",
            f"从事{title}多年，分享一些经验",
            f"{title}：从入门到精通"
        ]
        import random
        return random.choice(patterns)
    
    def _optimize_zhihu_content(self, content: str) -> str:
        """优化知乎内容格式"""
        # 添加引用块
        content = re.sub(
            r'([^\n]+(?:数据|研究|调查)[^\n]+)',
            r'> \1\n> ——数据来源：行业报告',
            content
        )
        
        return content
    
    def _add_references_zhihu(self, content: str) -> str:
        """为知乎内容添加参考文献"""
        references = [
            "[1] 行业研究报告，2024年",
            "[2] 相关专业书籍和文献",
            "[3] 实践经验总结"
        ]
        
        ref_section = "\n\n## 参考来源\n\n" + "\n".join(references)
        return content + ref_section

    def _adapt_toutiao(
        self, 
        content: str, 
        title: str, 
        author_info: Optional[Dict[str, str]]
    ) -> PlatformContent:
        """适配今日头条格式"""
        config = self.PLATFORM_CONFIG[Platform.TOUTIAO]
        
        # 处理标题 - 今日头条风格：悬念+数字
        adapted_title = self._optimize_toutiao_title(title)
        adapted_title = self._truncate_text(adapted_title, config["max_title"])
        
        # 处理内容
        adapted_content = self._clean_markdown(content)
        
        # 生成摘要（今日头条需要）
        summary = self._generate_toutiao_summary(adapted_content)
        
        # 优化内容结构
        adapted_content = self._optimize_toutiao_content(adapted_content)
        
        # 添加引导
        cta = self._generate_toutiao_cta()
        adapted_content += cta
        
        adapted_content = self._truncate_text(adapted_content, config["max_content"])
        
        # 生成标签
        tags = self._generate_tags(content, config["max_tags"])
        
        extras = {
            "摘要": summary,
            "封面建议": "选择高清、有吸引力的图片，比例16:9",
            "发布时间": "7:00-9:00, 12:00-14:00, 18:00-22:00",
            "分类建议": "根据内容选择合适分类",
            "原创声明": "建议勾选原创，提升推荐权重",
            "投放设置": "可设置投放范围和目标人群"
        }
        
        return PlatformContent(
            platform=config["name"],
            title=adapted_title,
            content=adapted_content,
            tags=tags,
            extras=extras,
            character_count=len(adapted_content)
        )

    def _adapt_baijiahao(
        self, 
        content: str, 
        title: str, 
        author_info: Optional[Dict[str, str]]
    ) -> PlatformContent:
        """适配百家号格式"""
        config = self.PLATFORM_CONFIG[Platform.BAIJIAHAO]
        
        # 处理标题 - 百家号风格：权威+价值
        adapted_title = self._optimize_baijiahao_title(title)
        adapted_title = self._truncate_text(adapted_title, config["max_title"])
        
        # 处理内容
        adapted_content = content
        
        # 生成摘要
        summary = self._generate_meta_description(content)
        
        # 优化内容结构
        adapted_content = self._optimize_baijiahao_content(adapted_content)
        
        # 添加作者信息框
        if author_info:
            author_box = self._generate_baijiahao_author_box(author_info)
            adapted_content += author_box
        
        adapted_content = self._truncate_text(adapted_content, config["max_content"])
        
        # 生成标签
        tags = self._generate_tags(content, config["max_tags"])
        
        extras = {
            "摘要": summary,
            "封面要求": "高清大图，比例3:2或16:9",
            "专栏选择": "选择相关专栏，提升垂直度",
            "原创设置": "勾选原创，获取更高收益",
            "话题标签": tags,
            "发布时间": "工作日9:00-11:00, 14:00-16:00效果较好"
        }
        
        return PlatformContent(
            platform=config["name"],
            title=adapted_title,
            content=adapted_content,
            tags=tags,
            extras=extras,
            character_count=len(adapted_content)
        )

    def _adapt_fob(
        self, 
        content: str, 
        title: str, 
        author_info: Optional[Dict[str, str]]
    ) -> PlatformContent:
        """适配福步论坛格式"""
        config = self.PLATFORM_CONFIG[Platform.FOB]
        
        # 处理标题 - 福步论坛风格：直接+实用
        adapted_title = self._optimize_fob_title(title)
        adapted_title = self._truncate_text(adapted_title, config["max_title"])
        
        # 处理内容 - 保持Markdown格式，外贸人习惯
        adapted_content = content
        
        # 优化内容结构
        adapted_content = self._optimize_fob_content(adapted_content)
        
        # 添加签名档
        signature = self._generate_fob_signature(author_info)
        adapted_content += signature
        
        adapted_content = self._truncate_text(adapted_content, config["max_content"])
        
        extras = {
            "板块选择": "根据内容选择：外贸交流、出口交流、进口交流等",
            "帖子类型": "经验分享/求助讨论/资源分享",
            "互动建议": "积极回复评论，建立专业形象",
            "注意事项": "遵守论坛规则，避免广告硬广",
            "签名设置": "完善个人签名，展示公司信息"
        }
        
        return PlatformContent(
            platform=config["name"],
            title=adapted_title,
            content=adapted_content,
            tags=[],
            extras=extras,
            character_count=len(adapted_content)
        )

    # ============ 今日头条专用方法 ============
    
    def _optimize_toutiao_title(self, title: str) -> str:
        """优化今日头条标题"""
        patterns = [
            f"震惊！{title}",
            f"必看：{title}",
            f"揭秘：{title}",
            f"【干货】{title}",
            f"深度解析：{title}",
            f"2024年最新：{title}"
        ]
        import random
        return random.choice(patterns)
    
    def _generate_toutiao_summary(self, content: str) -> str:
        """生成今日头条摘要"""
        # 提取前100字作为摘要
        summary = content[:100].replace('\n', ' ').strip()
        if len(summary) >= 97:
            summary = summary[:97] + "..."
        return summary
    
    def _optimize_toutiao_content(self, content: str) -> str:
        """优化今日头条内容"""
        # 添加小标题
        lines = content.split('\n')
        optimized = []
        
        for line in lines:
            if len(line) > 20 and not line.startswith('#') and not line.startswith('【'):
                # 长段落前加小标题
                optimized.append(f"【{line[:10]}...】")
            optimized.append(line)
        
        return '\n'.join(optimized)
    
    def _generate_toutiao_cta(self) -> str:
        """生成今日头条引导"""
        ctas = [
            "\n\n👆 觉得有用就点个赞吧！\n💬 有问题欢迎在评论区留言讨论~",
            "\n\n📌 收藏起来，需要的时候随时查看！\n👉 关注我，获取更多实用干货",
            "\n\n❤️ 感谢阅读！\n🔄 转发给需要的朋友"
        ]
        import random
        return random.choice(ctas)
    
    # ============ 百家号专用方法 ============
    
    def _optimize_baijiahao_title(self, title: str) -> str:
        """优化百家号标题"""
        patterns = [
            f"深度解读：{title}",
            f"专业分析｜{title}",
            f"行业洞察：{title}",
            f"独家观点：{title}",
            f"权威解读｜{title}"
        ]
        import random
        return random.choice(patterns)
    
    def _optimize_baijiahao_content(self, content: str) -> str:
        """优化百家号内容"""
        # 确保有清晰的结构
        if not content.startswith('#'):
            content = f"# {content.split(chr(10))[0]}\n\n{content}"
        
        # 添加段落分隔
        content = content.replace('\n\n', '\n\n---\n\n')
        
        return content
    
    def _generate_baijiahao_author_box(self, author_info: Dict[str, str]) -> str:
        """生成百家号作者信息框"""
        box = "\n\n---\n\n**关于作者**\n\n"
        if author_info.get("name"):
            box += f"👤 {author_info['name']}"
        if author_info.get("title"):
            box += f" | {author_info['title']}"
        box += "\n\n"
        if author_info.get("company"):
            box += f"🏢 {author_info['company']}\n\n"
        if author_info.get("bio"):
            box += f"💡 {author_info['bio']}\n\n"
        
        box += "📢 关注作者，获取更多行业干货"
        return box
    
    # ============ 福步论坛专用方法 ============
    
    def _optimize_fob_title(self, title: str) -> str:
        """优化福步论坛标题"""
        patterns = [
            f"[经验分享] {title}",
            f"[实操干货] {title}",
            f"[案例分析] {title}",
            f"[行业探讨] {title}",
            f"[新手必读] {title}"
        ]
        import random
        return random.choice(patterns)
    
    def _optimize_fob_content(self, content: str) -> str:
        """优化福步论坛内容"""
        # 福步用户喜欢实用、直接的内容
        # 保留Markdown格式，但确保结构清晰
        
        # 添加楼层标记
        lines = content.split('\n')
        optimized = ["【楼主分享】\n"]
        
        for line in lines:
            optimized.append(line)
        
        return '\n'.join(optimized)
    
    def _generate_fob_signature(self, author_info: Optional[Dict[str, str]]) -> str:
        """生成福步论坛签名档"""
        sig = "\n\n" + "="*50 + "\n\n"
        sig += "【签名档】\n\n"
        
        if author_info:
            if author_info.get("name"):
                sig += f"ID: {author_info['name']}\n"
            if author_info.get("company"):
                sig += f"公司: {author_info['company']}\n"
            if author_info.get("title"):
                sig += f"职位: {author_info['title']}\n"
        
        sig += "\n欢迎交流，共同进步！"
        sig += "\n\n" + "="*50
        
        return sig


# 便捷函数
def adapt_for_platform(
    content: str,
    title: str,
    platform: str,
    author_info: Optional[Dict[str, str]] = None
) -> PlatformContent:
    """
    快速适配内容到指定平台
    
    Args:
        content: 原始内容
        title: 标题
        platform: 平台名称 (xiaohongshu/douyin/shipinhao/google_seo/zhihu)
        author_info: 作者信息
        
    Returns:
        PlatformContent: 适配后的内容
    """
    platform_map = {
        "google_seo": Platform.GOOGLE_SEO,
        "zhihu": Platform.ZHIHU,
        "toutiao": Platform.TOUTIAO,
        "baijiahao": Platform.BAIJIAHAO,
        "fob": Platform.FOB
    }
    
    platform_enum = platform_map.get(platform.lower())
    if not platform_enum:
        raise ValueError(f"不支持的平台: {platform}")
    
    publisher = ContentPublisher()
    return publisher.publish(content, title, platform_enum, author_info)


def adapt_for_all_platforms(
    content: str,
    title: str,
    author_info: Optional[Dict[str, str]] = None
) -> Dict[str, PlatformContent]:
    """
    快速适配内容到所有平台
    
    Args:
        content: 原始内容
        title: 标题
        author_info: 作者信息
        
    Returns:
        Dict[str, PlatformContent]: 各平台的适配内容
    """
    publisher = ContentPublisher()
    return publisher.publish_all(content, title, author_info)
