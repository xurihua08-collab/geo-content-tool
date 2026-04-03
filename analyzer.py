import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class GEOAnalysisResult:
    """GEO分析结果数据类"""
    overall_score: float
    eeat_score: float
    citation_score: float
    structure_score: float
    readability_score: float
    suggestions: List[str]
    eeat_breakdown: Dict[str, float]
    details: Dict[str, Any]


class GEOAnalyzer:
    """GEO (Generative Engine Optimization) 内容分析器"""
    
    def __init__(self):
        self.eeat_indicators = {
            "experience": [
                "根据我的经验", "在实际工作中", "我曾遇到", "实践表明",
                "亲身经历", "实际操作", "实战中", "多年经验", "案例分享",
                "in my experience", "based on my", "practical experience",
                "real-world", "hands-on", "case study"
            ],
            "expertise": [
                "专业", "专家", "研究表明", "数据分析", "技术细节",
                "深入分析", "原理", "机制", "方法论", "系统性",
                "research shows", "according to experts", "technical analysis",
                "methodology", "systematic approach"
            ],
            "authority": [
                "引用", "参考文献", "权威", "公认", "标准",
                "行业规范", "权威机构", "认证", "资质",
                "citation", "reference", "authoritative", "industry standard",
                "certified", "recognized"
            ],
            "trustworthiness": [
                "数据来源", "可验证", "透明", "客观", "中立",
                "免责声明", "更新日期", "准确性",
                "data source", "verifiable", "transparent", "objective",
                "up-to-date", "accurate"
            ]
        }
        
        self.citation_patterns = [
            r'\[\d+\]',  # [1], [2], etc.
            r'\([^)]*\d{4}[^)]*\)',  # (Author, 2023)
            r'https?://\S+',  # URLs
            r'引用.*?:',  # 引用格式
            r'来源.*?:',  # 来源格式
            r'参考.*?：',  # 参考格式
        ]
        
        self.structure_elements = [
            "标题", "目录", "摘要", "引言", "结论",
            "h1", "h2", "h3", "h4", "h5", "h6",
            "bullet", "list", "table", "image", "quote"
        ]
    
    def analyze(self, content: str, title: str = "") -> GEOAnalysisResult:
        """
        分析内容的GEO优化度
        
        Args:
            content: 要分析的内容文本
            title: 内容标题
            
        Returns:
            GEOAnalysisResult: 分析结果
        """
        # 分析EEAT元素
        eeat_scores = self._analyze_eeat(content)
        eeat_score = sum(eeat_scores.values()) / len(eeat_scores)
        
        # 分析引用友好度
        citation_score = self._analyze_citations(content)
        
        # 分析内容结构
        structure_score = self._analyze_structure(content)
        
        # 分析可读性
        readability_score = self._analyze_readability(content)
        
        # 计算综合得分
        overall_score = (
            eeat_score * 0.35 +
            citation_score * 0.25 +
            structure_score * 0.20 +
            readability_score * 0.20
        )
        
        # 生成优化建议
        suggestions = self._generate_suggestions(
            content, eeat_scores, citation_score, structure_score, readability_score
        )
        
        return GEOAnalysisResult(
            overall_score=round(overall_score, 1),
            eeat_score=round(eeat_score, 1),
            citation_score=round(citation_score, 1),
            structure_score=round(structure_score, 1),
            readability_score=round(readability_score, 1),
            suggestions=suggestions,
            eeat_breakdown={k: round(v, 1) for k, v in eeat_scores.items()},
            details=self._generate_details(content, eeat_scores)
        )
    
    def _analyze_eeat(self, content: str) -> Dict[str, float]:
        """分析EEAT元素 (Experience, Expertise, Authoritativeness, Trustworthiness)"""
        content_lower = content.lower()
        scores = {}
        
        for dimension, indicators in self.eeat_indicators.items():
            count = 0
            for indicator in indicators:
                count += content_lower.count(indicator.lower())
            
            # 根据出现频率计算得分 (0-100)
            # 假设每500字出现2-3次为佳
            content_length = len(content)
            expected_count = max(1, content_length / 800)
            score = min(100, (count / expected_count) * 50)
            scores[dimension] = score
        
        return scores
    
    def _analyze_citations(self, content: str) -> float:
        """分析引用友好度"""
        citation_count = 0
        
        for pattern in self.citation_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            citation_count += len(matches)
        
        # 检查数据点
        data_patterns = [
            r'\d+%',  # 百分比
            r'\d+\.?\d*\s*(?:亿|万|千|百|million|billion|thousand)',  # 数量
            r'20\d{2}[-/年]',  # 年份
            r'(?:增加|减少|增长|下降).*?\d+',  # 变化幅度
        ]
        
        data_points = 0
        for pattern in data_patterns:
            matches = re.findall(pattern, content)
            data_points += len(matches)
        
        # 综合评分
        content_length = len(content)
        expected_citations = max(1, content_length / 1000)
        expected_data = max(1, content_length / 800)
        
        citation_score = min(50, (citation_count / expected_citations) * 25)
        data_score = min(50, (data_points / expected_data) * 25)
        
        return citation_score + data_score
    
    def _analyze_structure(self, content: str) -> float:
        """分析内容结构"""
        score = 50  # 基础分
        
        # 检查标题层次
        headers = re.findall(r'^#{1,6}\s', content, re.MULTILINE)
        if len(headers) >= 2:
            score += 15
        if len(headers) >= 4:
            score += 10
        
        # 检查列表使用
        lists = re.findall(r'^[\s]*[-*+]\s', content, re.MULTILINE)
        if len(lists) >= 3:
            score += 10
        
        # 检查段落长度
        paragraphs = content.split('\n\n')
        avg_para_length = sum(len(p) for p in paragraphs) / max(1, len(paragraphs))
        if 100 <= avg_para_length <= 500:
            score += 10
        
        # 检查是否有总结或结论
        conclusion_patterns = ['结论', '总结', 'conclusion', 'summary', 'in summary']
        for pattern in conclusion_patterns:
            if pattern in content.lower():
                score += 5
                break
        
        return min(100, score)
    
    def _analyze_readability(self, content: str) -> float:
        """分析可读性"""
        score = 70  # 基础分
        
        # 计算平均句长
        sentences = re.split(r'[。！？.!?]', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if sentences:
            avg_sentence_length = sum(len(s) for s in sentences) / len(sentences)
            # 中文句子长度在20-50字之间为佳
            if 15 <= avg_sentence_length <= 60:
                score += 15
            elif avg_sentence_length > 100:
                score -= 15
        
        # 检查段落数量
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if len(paragraphs) >= 3:
            score += 10
        
        # 检查是否有小标题
        if re.search(r'^#{2,6}\s', content, re.MULTILINE):
            score += 5
        
        return min(100, max(0, score))
    
    def _generate_suggestions(
        self, content: str, eeat_scores: Dict[str, float],
        citation_score: float, structure_score: float, readability_score: float
    ) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        # EEAT建议
        if eeat_scores.get("experience", 0) < 40:
            suggestions.append("💡 建议增加更多实践经验和案例分享，提升内容的真实感")
        
        if eeat_scores.get("expertise", 0) < 40:
            suggestions.append("💡 建议加入更多专业术语和深入分析，展示专业水平")
        
        if eeat_scores.get("authority", 0) < 40:
            suggestions.append("💡 建议添加权威引用和参考文献，增强内容可信度")
        
        if eeat_scores.get("trustworthiness", 0) < 40:
            suggestions.append("💡 建议标注数据来源和更新时间，提高透明度")
        
        # 引用建议
        if citation_score < 50:
            suggestions.append("💡 建议增加数据引用和来源标注，每500字至少1-2个引用")
        
        # 结构建议
        if structure_score < 60:
            suggestions.append("💡 建议使用更清晰的标题层次和列表格式，提升内容结构化")
        
        # 可读性建议
        if readability_score < 60:
            suggestions.append("💡 建议优化段落长度和句子结构，控制在20-50字/句")
        
        if not suggestions:
            suggestions.append("✅ 内容质量良好，继续保持！")
        
        return suggestions
    
    def _generate_details(self, content: str, eeat_scores: Dict[str, float]) -> Dict[str, Any]:
        """生成详细分析数据"""
        # 统计词数
        word_count = len(content.replace(' ', '').replace('\n', ''))
        
        # 统计段落数
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # 统计EEAT关键词出现次数
        keyword_counts = {}
        content_lower = content.lower()
        for dimension, indicators in self.eeat_indicators.items():
            count = 0
            for indicator in indicators:
                count += content_lower.count(indicator.lower())
            keyword_counts[dimension] = count
        
        return {
            "word_count": word_count,
            "paragraph_count": len(paragraphs),
            "eeat_keyword_counts": keyword_counts,
            "avg_paragraph_length": word_count / max(1, len(paragraphs))
        }
    
    def get_eeat_guidelines(self) -> str:
        """获取EEAT优化指南"""
        return """
# EEAT 优化指南

## Experience (经验)
- 分享第一手实践经验
- 使用具体案例说明
- 描述实际操作过程
- 加入个人见解和反思

## Expertise (专业性)
- 使用准确的行业术语
- 提供深入的技术分析
- 展示系统性的方法论
- 引用专业研究数据

## Authoritativeness (权威性)
- 引用权威来源
- 添加参考文献
- 引用行业标准
- 展示资质认证

## Trustworthiness (可信度)
- 标注数据来源
- 提供可验证的信息
- 保持客观中立
- 注明更新日期
        """


# 便捷函数
def analyze_content(content: str, title: str = "") -> GEOAnalysisResult:
    """
    快速分析内容的GEO优化度
    
    Args:
        content: 要分析的内容文本
        title: 内容标题
        
    Returns:
        GEOAnalysisResult: 分析结果
    """
    analyzer = GEOAnalyzer()
    return analyzer.analyze(content, title)


def get_score_emoji(score: float) -> str:
    """根据分数返回对应的表情符号"""
    if score >= 80:
        return "🟢"
    elif score >= 60:
        return "🟡"
    else:
        return "🔴"


def format_analysis_result(result: GEOAnalysisResult) -> str:
    """格式化分析结果为可读文本"""
    output = []
    output.append("=" * 50)
    output.append("📊 GEO 内容分析报告")
    output.append("=" * 50)
    output.append(f"\n综合得分: {result.overall_score}/100 {get_score_emoji(result.overall_score)}")
    output.append(f"\n详细评分:")
    output.append(f"  • EEAT得分: {result.eeat_score}/100 {get_score_emoji(result.eeat_score)}")
    output.append(f"    - 经验: {result.eeat_breakdown.get('experience', 0)}")
    output.append(f"    - 专业: {result.eeat_breakdown.get('expertise', 0)}")
    output.append(f"    - 权威: {result.eeat_breakdown.get('authority', 0)}")
    output.append(f"    - 可信: {result.eeat_breakdown.get('trustworthiness', 0)}")
    output.append(f"  • 引用友好度: {result.citation_score}/100 {get_score_emoji(result.citation_score)}")
    output.append(f"  • 结构优化: {result.structure_score}/100 {get_score_emoji(result.structure_score)}")
    output.append(f"  • 可读性: {result.readability_score}/100 {get_score_emoji(result.readability_score)}")
    
    output.append(f"\n优化建议:")
    for suggestion in result.suggestions:
        output.append(f"  {suggestion}")
    
    output.append(f"\n内容统计:")
    output.append(f"  • 总字数: {result.details.get('word_count', 0)}")
    output.append(f"  • 段落数: {result.details.get('paragraph_count', 0)}")
    output.append(f"  • 平均段落长度: {result.details.get('avg_paragraph_length', 0):.0f}字")
    
    output.append("=" * 50)
    
    return "\n".join(output)
