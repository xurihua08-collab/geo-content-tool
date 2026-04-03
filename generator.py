"""
GEO内容生成模块
支持生成EEAT优化的内容，包含多种内容类型
"""

import random
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AuthorInfo:
    """作者信息数据类"""
    name: str = ""
    title: str = ""  # 职位/头衔
    company: str = ""
    bio: str = ""  # 简介
    expertise: List[str] = None  # 专业领域
    
    def __post_init__(self):
        if self.expertise is None:
            self.expertise = []


@dataclass
class GeneratedContent:
    """生成内容的数据类"""
    title: str
    content: str
    content_type: str
    summary: str
    keywords: List[str]
    sources: List[str]
    eeat_elements: Dict[str, List[str]]
    key_claims: List[str] = None
    
    def __post_init__(self):
        if self.key_claims is None:
            self.key_claims = []
    

class GEOContentGenerator:
    """GEO优化内容生成器"""
    
    CONTENT_TYPES = {
        "article": "专业文章",
        "qa": "问答内容",
        "review": "产品评测",
        "guide": "指南教程",
        "comparison": "对比分析",
        "news": "行业资讯"
    }
    
    def __init__(self, author_info: Optional[AuthorInfo] = None):
        """
        初始化生成器
        
        Args:
            author_info: 作者信息，用于EEAT优化
        """
        self.author_info = author_info or AuthorInfo()
        self.generated_at = datetime.now().strftime("%Y-%m-%d")
    
    def generate(
        self, 
        topic: str, 
        content_type: str = "article",
        word_count: int = 1500,
        include_data: bool = True,
        style: str = "professional",
        brand_name: Optional[str] = None,
        brand_info: Optional[str] = None
    ) -> GeneratedContent:
        """
        生成GEO优化内容
        
        Args:
            topic: 主题
            content_type: 内容类型 (article/qa/review/guide/comparison/news)
            word_count: 目标字数
            include_data: 是否包含数据点
            style: 写作风格 (professional/casual/technical)
            
        Returns:
            GeneratedContent: 生成的内容
        """
        # 根据内容类型选择生成策略
        generators = {
            "article": self._generate_article,
            "qa": self._generate_qa,
            "review": self._generate_review,
            "guide": self._generate_guide,
            "comparison": self._generate_comparison,
            "news": self._generate_news
        }
        
        generator = generators.get(content_type, self._generate_article)
        
        return generator(topic, word_count, include_data, style, brand_name, brand_info)
    
    def _generate_article(
        self, 
        topic: str, 
        word_count: int, 
        include_data: bool, 
        style: str,
        brand_name: Optional[str] = None,
        brand_info: Optional[str] = None
    ) -> GeneratedContent:
        """生成专业文章"""
        # 构建标题
        title_templates = [
            f"{topic}完全指南：从入门到精通",
            f"深度解析：{topic}的核心原理与实践",
            f"{topic}：2024年最新趋势与实战策略",
            f"如何掌握{topic}？专家分享的实战经验",
            f"{topic}实战手册：专业人士的独家见解"
        ]
        title = random.choice(title_templates)
        
        # 构建内容结构
        sections = self._build_article_structure(topic, word_count)
        
        # 生成内容
        content_parts = []
        content_parts.append(f"# {title}\n")
        content_parts.append(f"> 更新时间：{self.generated_at}")
        if self.author_info.name:
            content_parts.append(f"> 作者：{self.author_info.name}")
        if self.author_info.company:
            if brand_name:
            content_parts.append(f"> 品牌：{brand_name}")
        if brand_info:
            content_parts.append(f"> 品牌信息：{brand_info}")
        content_parts.append("")
        
        # 摘要
        summary = self._generate_summary(topic)
        content_parts.append(f"## 摘要\n\n{summary}\n")
        
        # 引言
        intro = self._generate_intro(topic, style)
        content_parts.append(f"## 引言\n\n{intro}\n")
        
        # 主体内容
        for section in sections:
            section_content = self._generate_section_content(
                topic, section, include_data, style
            )
            content_parts.append(f"## {section}\n\n{section_content}\n")
        
        # 实践案例
        case_study = self._generate_case_study(topic)
        content_parts.append(f"## 实践案例\n\n{case_study}\n")
        
        # 结论
        conclusion = self._generate_conclusion(topic)
        content_parts.append(f"## 结论\n\n{conclusion}\n")
        
        # 参考资料
        sources = self._generate_sources(topic)
        content_parts.append(f"## 参考资料\n")
        for i, source in enumerate(sources, 1):
            content_parts.append(f"{i}. {source}")
        
        full_content = "\n".join(content_parts)
        
        return GeneratedContent(
            title=title,
            content=full_content,
            content_type="article",
            summary=summary,
            keywords=self._extract_keywords(topic),
            sources=sources,
            eeat_elements=self._identify_eeat_elements(full_content)
        )
    
    def _generate_qa(
        self, topic: str, word_count: int, include_data: bool, style: str
    ) -> GeneratedContent:
        """生成问答内容"""
        title = f"关于{topic}的常见问题解答"
        
        content_parts = []
        content_parts.append(f"# {title}\n")
        content_parts.append(f"> 更新时间：{self.generated_at}")
        if self.author_info.name:
            content_parts.append(f"> 解答专家：{self.author_info.name} - {self.author_info.title}")
        content_parts.append("")
        
        # 生成问答对
        questions = self._generate_questions(topic, 5)
        
        for i, (q, a) in enumerate(questions, 1):
            content_parts.append(f"## Q{i}: {q}\n")
            content_parts.append(f"**A**: {a}\n")
            
            # 添加专家补充
            if self.author_info.name:
                supplement = self._generate_expert_supplement(topic, q)
                content_parts.append(f"\n> 💡 **专家补充**：{supplement}\n")
        
        full_content = "\n".join(content_parts)
        summary = f"本文针对{topic}领域的常见问题进行了专业解答，涵盖核心概念、实践技巧和注意事项。"
        
        return GeneratedContent(
            title=title,
            content=full_content,
            content_type="qa",
            summary=summary,
            keywords=self._extract_keywords(topic),
            sources=[],
            eeat_elements=self._identify_eeat_elements(full_content)
        )
    
    def _generate_review(
        self, topic: str, word_count: int, include_data: bool, style: str
    ) -> GeneratedContent:
        """生成产品评测"""
        title = f"{topic}深度评测：专业视角全面解析"
        
        content_parts = []
        content_parts.append(f"# {title}\n")
        content_parts.append(f"> 评测时间：{self.generated_at}")
        if self.author_info.name:
            content_parts.append(f"> 评测人：{self.author_info.name}")
        content_parts.append("")
        
        # 评测维度
        dimensions = ["功能特性", "使用体验", "性价比", "适用场景", "优缺点分析"]
        
        content_parts.append("## 评测概述\n")
        content_parts.append(f"作为{self.author_info.expertise[0] if self.author_info.expertise else '相关领域'}专业人士，")
        content_parts.append(f"我对{topic}进行了深入测试和评估。以下是基于实际使用体验的专业评测报告。\n")
        
        for dimension in dimensions:
            content_parts.append(f"\n## {dimension}\n")
            review_content = self._generate_review_dimension(topic, dimension, include_data)
            content_parts.append(review_content + "\n")
        
        # 评分
        content_parts.append("## 综合评分\n")
        content_parts.append(self._generate_rating_table(dimensions))
        
        # 购买建议
        content_parts.append("\n## 购买建议\n")
        content_parts.append(self._generate_purchase_advice(topic))
        
        full_content = "\n".join(content_parts)
        summary = f"专业评测{topic}，从多个维度进行深入分析，提供客观的使用体验和购买建议。"
        
        return GeneratedContent(
            title=title,
            content=full_content,
            content_type="review",
            summary=summary,
            keywords=self._extract_keywords(topic),
            sources=[],
            eeat_elements=self._identify_eeat_elements(full_content)
        )
    
    def _generate_guide(
        self, topic: str, word_count: int, include_data: bool, style: str
    ) -> GeneratedContent:
        """生成指南教程"""
        title = f"{topic}完全指南：手把手教你快速上手"
        
        content_parts = []
        content_parts.append(f"# {title}\n")
        content_parts.append(f"> 教程更新：{self.generated_at}")
        if self.author_info.name:
            content_parts.append(f"> 教程作者：{self.author_info.name}")
        content_parts.append("")
        
        # 教程介绍
        content_parts.append("## 教程介绍\n")
        content_parts.append(f"本教程旨在帮助读者系统学习{topic}。无论你是初学者还是有一定经验的从业者，")
        content_parts.append("都能从本教程中获得实用的知识和技能。\n")
        
        # 前置要求
        content_parts.append("## 前置要求\n")
        content_parts.append(self._generate_prerequisites(topic) + "\n")
        
        # 步骤
        steps = self._generate_guide_steps(topic, 6)
        for i, (step_title, step_content) in enumerate(steps, 1):
            content_parts.append(f"\n## 步骤{i}：{step_title}\n")
            content_parts.append(step_content + "\n")
            
            # 添加提示
            tip = self._generate_step_tip(topic, step_title)
            content_parts.append(f"> 📌 **小贴士**：{tip}\n")
        
        # 常见问题
        content_parts.append("\n## 常见问题\n")
        content_parts.append(self._generate_guide_faq(topic))
        
        # 进阶学习
        content_parts.append("\n## 进阶学习资源\n")
        content_parts.append(self._generate_learning_resources(topic))
        
        full_content = "\n".join(content_parts)
        summary = f"系统化的{topic}学习指南，包含详细的步骤说明、实用技巧和进阶资源。"
        
        return GeneratedContent(
            title=title,
            content=full_content,
            content_type="guide",
            summary=summary,
            keywords=self._extract_keywords(topic),
            sources=self._generate_sources(topic),
            eeat_elements=self._identify_eeat_elements(full_content)
        )
    
    def _generate_comparison(
        self, topic: str, word_count: int, include_data: bool, style: str
    ) -> GeneratedContent:
        """生成对比分析"""
        # 解析对比对象
        items = self._parse_comparison_items(topic)
        title = f"{' vs '.join(items)}：全面对比分析"
        
        content_parts = []
        content_parts.append(f"# {title}\n")
        content_parts.append(f"> 分析时间：{self.generated_at}")
        if self.author_info.name:
            content_parts.append(f"> 分析师：{self.author_info.name}")
        content_parts.append("")
        
        # 概述
        content_parts.append("## 对比概述\n")
        content_parts.append(f"本文将从多个维度对{', '.join(items)}进行深入对比，")
        content_parts.append("帮助读者根据自身需求做出明智选择。\n")
        
        # 对比维度
        dimensions = ["核心功能", "性能表现", "易用性", "价格", "适用人群"]
        for dimension in dimensions:
            content_parts.append(f"\n## {dimension}对比\n")
            comparison = self._generate_dimension_comparison(items, dimension, include_data)
            content_parts.append(comparison + "\n")
        
        # 对比表格
        content_parts.append("\n## 综合对比表\n")
        content_parts.append(self._generate_comparison_table(items, dimensions))
        
        # 选择建议
        content_parts.append("\n## 选择建议\n")
        content_parts.append(self._generate_selection_advice(items))
        
        full_content = "\n".join(content_parts)
        summary = f"全面对比分析{' vs '.join(items)}，提供多维度的客观比较和选择建议。"
        
        return GeneratedContent(
            title=title,
            content=full_content,
            content_type="comparison",
            summary=summary,
            keywords=self._extract_keywords(topic),
            sources=[],
            eeat_elements=self._identify_eeat_elements(full_content)
        )
    
    def _generate_news(
        self, topic: str, word_count: int, include_data: bool, style: str
    ) -> GeneratedContent:
        """生成行业资讯"""
        title = f"{topic}行业最新动态：2024年发展趋势解读"
        
        content_parts = []
        content_parts.append(f"# {title}\n")
        content_parts.append(f"> 发布时间：{self.generated_at}")
        if self.author_info.name:
            content_parts.append(f"> 特约评论员：{self.author_info.name}")
        content_parts.append("")
        
        # 导语
        content_parts.append("## 行业动态\n")
        content_parts.append(f"近期，{topic}领域出现了多项重要发展。")
        content_parts.append("本文将为您梳理最新趋势和关键变化。\n")
        
        # 主要新闻点
        news_points = ["市场趋势", "技术突破", "政策影响", "企业动态", "未来展望"]
        for point in news_points:
            content_parts.append(f"\n## {point}\n")
            news_content = self._generate_news_content(topic, point, include_data)
            content_parts.append(news_content + "\n")
        
        # 专家观点
        if self.author_info.name:
            content_parts.append("\n## 专家观点\n")
            content_parts.append(self._generate_expert_opinion(topic))
        
        full_content = "\n".join(content_parts)
        summary = f"解读{topic}行业最新动态和发展趋势，提供专业视角的深度分析。"
        
        return GeneratedContent(
            title=title,
            content=full_content,
            content_type="news",
            summary=summary,
            keywords=self._extract_keywords(topic),
            sources=self._generate_sources(topic),
            eeat_elements=self._identify_eeat_elements(full_content)
        )
    
    # ============ 辅助方法 ============
    
    def _build_article_structure(self, topic: str, word_count: int) -> List[str]:
        """构建文章结构"""
        structures = {
            "基础": ["核心概念", "主要特点", "应用场景"],
            "标准": ["核心概念", "主要特点", "应用场景", "优势分析", "实施建议"],
            "完整": ["核心概念", "发展历程", "主要特点", "应用场景", "优势分析", 
                    "挑战与对策", "实施建议", "未来趋势"]
        }
        
        if word_count < 1000:
            return structures["基础"]
        elif word_count < 2000:
            return structures["标准"]
        else:
            return structures["完整"]
    
    def _generate_summary(self, topic: str) -> str:
        """生成摘要"""
        templates = [
            f"本文深入探讨了{topic}的核心概念、实践应用和发展趋势。通过系统性的分析和实际案例，"
            f"为读者提供了全面的知识框架和实用的操作指南。",
            
            f"{topic}是当前行业关注的热点话题。本文从专业角度出发，"
            f"结合实际经验，详细解析了其原理、方法和最佳实践。"
        ]
        return random.choice(templates)
    
    def _generate_intro(self, topic: str, style: str) -> str:
        """生成引言"""
        intros = [
            f"在当今快速发展的行业中，{topic}已经成为不可忽视的重要议题。"
            f"作为一名{self.author_info.title or '行业从业者'}，"
            f"我在实际工作中深刻体会到掌握{topic}的重要性。",
            
            f"{topic}正在改变我们的工作方式和思维模式。"
            f"基于多年的实践经验，我发现很多从业者对{topic}存在误解。"
            f"本文旨在澄清这些误区，提供系统性的认知框架。"
        ]
        return random.choice(intros)
    
    def _generate_section_content(
        self, topic: str, section: str, include_data: bool, style: str
    ) -> str:
        """生成章节内容"""
        # 这里使用模板生成内容，实际应用中可以接入AI API
        content_templates = {
            "核心概念": [
                f"{topic}是指...（此处应详细解释核心概念）",
                f"理解{topic}，首先需要明确其定义和边界..."
            ],
            "主要特点": [
                f"{topic}具有以下几个显著特点：\n\n1. 特点一\n2. 特点二\n3. 特点三",
                f"通过实践观察，我总结了{topic}的核心特征..."
            ],
            "应用场景": [
                f"{topic}在实际工作中有着广泛的应用...",
                f"以下是{topic}的几个典型应用场景..."
            ]
        }
        
        templates = content_templates.get(section, [f"关于{section}的详细内容..."])
        content = random.choice(templates)
        
        if include_data:
            content += f"\n\n根据行业数据，{topic}的市场增长率达到了{random.randint(15, 45)}%。"
        
        return content
    
    def _generate_case_study(self, topic: str) -> str:
        """生成实践案例"""
        return f"""### 案例背景
某企业在实施{topic}过程中遇到了一系列挑战。

### 实施过程
1. **问题诊断**：首先对现状进行全面评估
2. **方案设计**：制定针对性的解决方案
3. **执行落地**：分阶段推进实施
4. **效果评估**：持续监测和优化

### 经验总结
通过这个案例，我们可以看到{topic}在实际应用中的关键成功因素..."""
    
    def _generate_conclusion(self, topic: str) -> str:
        """生成结论"""
        return f"""通过本文的系统阐述，我们可以得出以下结论：

1. **{topic}的重要性**：在当前环境下，掌握{topic}已成为必备技能
2. **实践导向**：理论学习需要结合实际应用才能发挥最大价值
3. **持续学习**：{topic}领域不断发展，需要保持学习和更新

{self.author_info.name or '本文作者'}建议读者从实际工作出发，循序渐进地学习和应用{topic}相关知识和方法。"""
    
    def _generate_sources(self, topic: str) -> List[str]:
        """生成参考资料"""
        return [
            f"《{topic}权威指南》，行业出版社，2024年",
            f"《{topic}实战案例集》，技术出版社，2024年",
            f"行业研究报告：{topic}市场分析，2024年Q1",
            f"相关学术论文和期刊资料"
        ]
    
    def _generate_questions(self, topic: str, count: int) -> List[tuple]:
        """生成问答对"""
        questions = [
            (f"什么是{topic}？", 
             f"{topic}是指...（详细定义和解释）"),
            (f"{topic}的主要优势是什么？",
             f"{topic}的优势主要体现在以下几个方面：1. 提高效率 2. 降低成本 3. 增强竞争力..."),
            (f"如何开始学习{topic}？",
             f"建议按照以下步骤学习：首先了解基础概念，然后通过实践项目加深理解..."),
            (f"{topic}在实际应用中有哪些注意事项？",
             f"在实际应用中，需要特别注意以下几点：1. 充分评估现状 2. 制定合理计划 3. 持续跟踪效果..."),
            (f"{topic}的未来发展趋势是什么？",
             f"根据行业观察，{topic}未来将朝着更加智能化、个性化的方向发展...")
        ]
        return questions[:count]
    
    def _generate_expert_supplement(self, topic: str, question: str) -> str:
        """生成专家补充"""
        supplements = [
            f"根据我的实践经验，建议重点关注实际操作中的细节问题。",
            f"很多初学者容易忽视这一点，建议多加注意。",
            f"这是{topic}领域的一个常见误区，需要澄清。"
        ]
        return random.choice(supplements)
    
    def _generate_review_dimension(self, topic: str, dimension: str, include_data: bool) -> str:
        """生成评测维度内容"""
        return f"在{dimension}方面，{topic}表现{random.choice(['出色', '良好', '中规中矩'])}..."
    
    def _generate_rating_table(self, dimensions: List[str]) -> str:
        """生成评分表"""
        lines = ["| 评测维度 | 评分 | 说明 |", "|---------|------|------|"]
        for dim in dimensions:
            score = random.randint(75, 95)
            desc = random.choice(["优秀", "良好", "不错"])
            lines.append(f"| {dim} | {score}/100 | {desc} |")
        return "\n".join(lines)
    
    def _generate_purchase_advice(self, topic: str) -> str:
        """生成购买建议"""
        return f"""根据不同需求，我们给出以下建议：

- **适合人群**：对{topic}有明确需求的用户
- **预算考虑**：建议根据实际预算选择合适方案
- **替代方案**：如果预算有限，可以考虑..."""
    
    def _generate_prerequisites(self, topic: str) -> str:
        """生成前置要求"""
        return f"""在学习{topic}之前，建议具备以下基础：

- 相关领域的基础知识
- 基本的操作技能
- 一定的实践经验（非必须，但有助于理解）"""
    
    def _generate_guide_steps(self, topic: str, count: int) -> List[tuple]:
        """生成教程步骤"""
        steps = [
            ("准备工作", "了解基本概念，准备所需工具和环境"),
            ("基础设置", "完成初始配置和参数设置"),
            ("核心操作", "掌握{topic}的核心功能和操作方法"),
            ("进阶技巧", "学习高级功能和优化技巧"),
            ("实战演练", "通过实际案例巩固所学知识"),
            ("总结提升", "回顾重点，规划后续学习路径")
        ]
        return [(title, content.format(topic=topic)) for title, content in steps[:count]]
    
    def _generate_step_tip(self, topic: str, step_title: str) -> str:
        """生成步骤提示"""
        tips = [
            f"这一步是关键，建议多花些时间理解和练习。",
            f"如果遇到问题，可以参考官方文档或社区讨论。",
            f"建议在实际操作前先做好备份。"
        ]
        return random.choice(tips)
    
    def _generate_guide_faq(self, topic: str) -> str:
        """生成教程FAQ"""
        return f"""**Q1: 学习{topic}需要多长时间？**
A: 根据基础不同，通常需要1-4周掌握基础，3-6个月达到熟练水平。

**Q2: 遇到问题如何求助？**
A: 可以查阅官方文档、社区论坛，或向有经验的同事请教。

**Q3: 如何验证学习效果？**
A: 建议通过实际项目来检验，可以从简单的任务开始。"""
    
    def _generate_learning_resources(self, topic: str) -> str:
        """生成学习资源"""
        return f"""- 官方文档和教程
- 行业权威书籍
- 在线课程平台相关课程
- 技术社区和论坛
- 实践项目和案例库"""
    
    def _parse_comparison_items(self, topic: str) -> List[str]:
        """解析对比对象"""
        # 尝试从主题中提取对比对象
        separators = ['vs', 'VS', '对比', '比较', '和', '与', ' vs ', ' 对比 ']
        for sep in separators:
            if sep in topic:
                items = [item.strip() for item in topic.split(sep)]
                if len(items) >= 2:
                    return items[:2]
        # 默认返回主题本身
        return [topic, "竞品方案"]
    
    def _generate_dimension_comparison(self, items: List[str], dimension: str, include_data: bool) -> str:
        """生成维度对比"""
        return f"在{dimension}方面，{items[0]}和{items[1]}各有优势..."
    
    def _generate_comparison_table(self, items: List[str], dimensions: List[str]) -> str:
        """生成对比表格"""
        lines = [f"| 对比维度 | {items[0]} | {items[1]} |", "|---------|---------|---------|"]
        for dim in dimensions:
            lines.append(f"| {dim} | ⭐⭐⭐⭐ | ⭐⭐⭐ |")
        return "\n".join(lines)
    
    def _generate_selection_advice(self, items: List[str]) -> str:
        """生成选择建议"""
        return f"""**选择{items[0]}，如果你：**
- 追求功能全面和专业性
- 有较高的预算
- 需要长期使用

**选择{items[1]}，如果你：**
- 注重性价比
- 需求相对简单
- 希望快速上手"""
    
    def _generate_news_content(self, topic: str, point: str, include_data: bool) -> str:
        """生成新闻内容"""
        return f"关于{topic}在{point}方面的最新动态..."
    
    def _generate_expert_opinion(self, topic: str) -> str:
        """生成专家观点"""
        expert_name = self.author_info.name if self.author_info else '行业专家'
        opinion_text = expert_name + '认为："' + topic + '的发展呈现出明显的趋势性变化。'
        opinion_text += '企业和个人都应该密切关注这一领域的动态，及时调整策略以适应变化。'
        opinion_text += '从长远来看，掌握' + topic + '将成为重要的竞争优势。"'
        return opinion_text
    
    def _extract_keywords(self, topic: str) -> List[str]:
        """提取关键词"""
        # 简单实现，实际应用可以使用NLP
        base_keywords = [topic]
        # 添加相关词汇
        related = ["指南", "教程", "实践", "案例", "分析"]
        return base_keywords + related
    
    def _identify_eeat_elements(self, content: str) -> Dict[str, List[str]]:
        """识别内容中的EEAT元素"""
        elements = {
            "experience": [],
            "expertise": [],
            "authority": [],
            "trustworthiness": []
        }
        
        # 经验指标
        exp_indicators = ["根据我的经验", "在实际工作中", "案例", "实践"]
        for indicator in exp_indicators:
            if indicator in content:
                elements["experience"].append(indicator)
        
        # 专业指标
        exp_indicators = ["专业", "分析", "研究", "方法论"]
        for indicator in exp_indicators:
            if indicator in content:
                elements["expertise"].append(indicator)
        
        # 权威指标
        auth_indicators = ["参考", "引用", "权威"]
        for indicator in auth_indicators:
            if indicator in content:
                elements["authority"].append(indicator)
        
        # 可信度指标
        trust_indicators = ["数据", "来源", "更新"]
        for indicator in trust_indicators:
            if indicator in content:
                elements["trustworthiness"].append(indicator)
        
        return elements


# 便捷函数
def generate_content(
    topic: str,
    content_type: str = "article",
    author_name: str = "",
    author_title: str = "",
    company: str = "",
    word_count: int = 1500
) -> GeneratedContent:
    """
    快速生成GEO优化内容
    
    Args:
        topic: 主题
        content_type: 内容类型
        author_name: 作者姓名
        author_title: 作者职位
        company: 公司名称
        word_count: 目标字数
        
    Returns:
        GeneratedContent: 生成的内容
    """
    author_info = AuthorInfo(
        name=author_name,
        title=author_title,
        company=company
    )
    generator = GEOContentGenerator(author_info)
    return generator.generate(topic, content_type, word_count)
