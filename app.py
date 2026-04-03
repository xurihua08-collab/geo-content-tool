"""
内容管理系统 - 主应用
支持多品牌管理、平台账号绑定、文章发布追踪
"""
import streamlit as st
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import Brand, Article, PublishRecord, PlatformAccount, Platform
from services.data_store import DataStore
import uuid
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="内容分发管理系统",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化数据存储
if 'data_store' not in st.session_state:
    st.session_state['data_store'] = DataStore()

# CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .brand-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .platform-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.85rem;
        margin: 0.25rem;
    }
    .status-success {
        background: #d4edda;
        color: #155724;
    }
    .status-failed {
        background: #f8d7da;
        color: #721c24;
    }
    .status-pending {
        background: #fff3cd;
        color: #856404;
    }
    .article-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def get_platform_name(platform: Platform) -> str:
    """获取平台显示名称"""
    platform_names = {
        Platform.GOOGLE_SEO: "🔍 Google SEO",
        Platform.ZHIHU: "💡 知乎",
        Platform.TOUTIAO: "📰 今日头条",
        Platform.BAIJIAHAO: "📝 百家号",
        Platform.FOB: "🌐 福步论坛"
    }
    return platform_names.get(platform, platform.value)


def get_platform_color(platform: Platform) -> str:
    """获取平台颜色"""
    platform_colors = {
        Platform.GOOGLE_SEO: "#4285F4",
        Platform.ZHIHU: "#0084FF",
        Platform.TOUTIAO: "#F04142",
        Platform.BAIJIAHAO: "#2932E1",
        Platform.FOB: "#FF6B35"
    }
    return platform_colors.get(platform, "#666")


def show_brand_management():
    """品牌管理页面"""
    st.markdown("### 🏢 品牌管理")
    
    data_store = st.session_state['data_store']
    brands = data_store.get_all_brands()
    
    # 显示现有品牌
    if brands:
        st.markdown("#### 已有品牌")
        for brand in brands:
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.markdown(f"**{brand.name}**")
                    if brand.description:
                        st.caption(brand.description)
                with col2:
                    # 显示已绑定的平台
                    for platform in brand.accounts.keys():
                        st.markdown(
                            f'<span class="platform-badge" style="background: {get_platform_color(platform)}20; color: {get_platform_color(platform)}; border: 1px solid {get_platform_color(platform)};">{get_platform_name(platform)}</span>',
                            unsafe_allow_html=True
                        )
                with col3:
                    if st.button("编辑", key=f"edit_brand_{brand.id}"):
                        st.session_state['editing_brand'] = brand.id
                        st.rerun()
                    if st.button("删除", key=f"delete_brand_{brand.id}"):
                        data_store.delete_brand(brand.id)
                        st.success(f"已删除品牌: {brand.name}")
                        st.rerun()
                st.markdown("---")
    else:
        st.info("暂无品牌，请添加第一个品牌")
    
    # 添加/编辑品牌
    st.markdown("#### 添加新品牌")
    
    editing_brand_id = st.session_state.get('editing_brand')
    editing_brand = None
    if editing_brand_id:
        editing_brand = data_store.get_brand(editing_brand_id)
    
    with st.form("brand_form"):
        brand_name = st.text_input(
            "品牌名称 *",
            value=editing_brand.name if editing_brand else "",
            placeholder="例如：科技创新有限公司"
        )
        brand_description = st.text_area(
            "品牌描述",
            value=editing_brand.description if editing_brand else "",
            placeholder="简要描述品牌..."
        )
        brand_website = st.text_input(
            "品牌官网",
            value=editing_brand.website if editing_brand else "",
            placeholder="https://www.example.com"
        )
        brand_industry = st.text_input(
            "所属行业",
            value=editing_brand.industry if editing_brand else "",
            placeholder="例如：科技、贸易、教育"
        )
        
        submitted = st.form_submit_button("保存品牌")
        
        if submitted:
            if not brand_name:
                st.error("品牌名称不能为空")
            else:
                if editing_brand:
                    # 更新现有品牌
                    editing_brand.name = brand_name
                    editing_brand.description = brand_description
                    editing_brand.website = brand_website
                    editing_brand.industry = brand_industry
                    data_store.save_brand(editing_brand)
                    st.success(f"已更新品牌: {brand_name}")
                    del st.session_state['editing_brand']
                else:
                    # 创建新品牌
                    new_brand = Brand(
                        id=str(uuid.uuid4()),
                        name=brand_name,
                        description=brand_description,
                        website=brand_website,
                        industry=brand_industry
                    )
                    data_store.save_brand(new_brand)
                    st.success(f"已创建品牌: {brand_name}")
                st.rerun()


def show_platform_accounts():
    """平台账号管理页面"""
    st.markdown("### 🔗 平台账号管理")
    
    data_store = st.session_state['data_store']
    brands = data_store.get_all_brands()
    
    if not brands:
        st.warning("请先创建品牌")
        return
    
    # 选择品牌
    brand_options = {b.name: b for b in brands}
    selected_brand_name = st.selectbox(
        "选择品牌",
        options=list(brand_options.keys())
    )
    selected_brand = brand_options[selected_brand_name]
    
    st.markdown(f"#### 为「{selected_brand.name}」配置平台账号")
    
    # 显示已配置的账号
    if selected_brand.accounts:
        st.markdown("**已配置的账号：**")
        for platform, account in selected_brand.accounts.items():
            with st.expander(f"{get_platform_name(platform)} - {account.account_name}"):
                st.text_input(
                    "账号名称",
                    value=account.account_name,
                    key=f"acc_name_{platform.value}",
                    disabled=True
                )
                st.text_input(
                    "账号ID",
                    value=account.account_id,
                    key=f"acc_id_{platform.value}",
                    disabled=True
                )
                if st.button("删除账号", key=f"del_acc_{platform.value}"):
                    del selected_brand.accounts[platform]
                    data_store.save_brand(selected_brand)
                    st.success("已删除账号")
                    st.rerun()
    
    # 添加新账号
    st.markdown("**添加新平台账号：**")
    
    available_platforms = [p for p in Platform if p not in selected_brand.accounts]
    
    if not available_platforms:
        st.info("已为该品牌配置所有平台账号")
        return
    
    platform_options = {get_platform_name(p): p for p in available_platforms}
    selected_platform_name = st.selectbox(
        "选择平台",
        options=list(platform_options.keys())
    )
    selected_platform = platform_options[selected_platform_name]
    
    with st.form("account_form"):
        account_name = st.text_input(
            "账号名称 *",
            placeholder="例如：张三"
        )
        account_id = st.text_input(
            "账号ID/用户名",
            placeholder="例如：zhangsan123"
        )
        api_key = st.text_input(
            "API Key（如有）",
            type="password",
            placeholder="可选"
        )
        api_secret = st.text_input(
            "API Secret（如有）",
            type="password",
            placeholder="可选"
        )
        cookies = st.text_area(
            "Cookies（用于模拟登录）",
            placeholder="可选，用于需要登录的平台",
            help="某些平台需要cookies来保持登录状态"
        )
        notes = st.text_area(
            "备注",
            placeholder="其他信息..."
        )
        
        submitted = st.form_submit_button("保存账号")
        
        if submitted:
            if not account_name:
                st.error("账号名称不能为空")
            else:
                new_account = PlatformAccount(
                    platform=selected_platform,
                    account_name=account_name,
                    account_id=account_id,
                    api_key=api_key,
                    api_secret=api_secret,
                    cookies=cookies,
                    notes=notes
                )
                selected_brand.accounts[selected_platform] = new_account
                data_store.save_brand(selected_brand)
                st.success(f"已为 {selected_brand.name} 添加 {get_platform_name(selected_platform)} 账号")
                st.rerun()


def show_article_management():
    """文章管理页面"""
    st.markdown("### 📝 文章管理")
    
    data_store = st.session_state['data_store']
    brands = data_store.get_all_brands()
    
    if not brands:
        st.warning("请先创建品牌")
        return
    
    # 选择品牌
    brand_options = {b.name: b for b in brands}
    selected_brand_name = st.selectbox(
        "选择品牌",
        options=list(brand_options.keys()),
        key="article_brand_select"
    )
    selected_brand = brand_options[selected_brand_name]
    
    # 显示该品牌的文章
    articles = [a for a in data_store.get_all_articles() if a.brand_id == selected_brand.id]
    
    if articles:
        st.markdown(f"#### {selected_brand.name} 的文章 ({len(articles)}篇)")
        
        for article in articles:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{article.title}**")
                    st.caption(f"状态: {article.status} | 创建时间: {article.created_at[:10]}")
                with col2:
                    if st.button("查看/编辑", key=f"edit_article_{article.id}"):
                        st.session_state['editing_article'] = article.id
                        st.rerun()
                with col3:
                    if st.button("发布", key=f"publish_article_{article.id}"):
                        st.session_state['publishing_article'] = article.id
                        st.rerun()
                st.markdown("---")
    else:
        st.info(f"{selected_brand.name} 暂无文章")
    
    # 创建新文章
    st.markdown("#### 创建新文章")
    
    # AI生成区域
    with st.expander("🤖 AI生成文章", expanded=False):
        st.markdown("**AI生成设置**")
        ai_topic = st.text_input("输入主题/关键词", placeholder="例如：跨境电商注册公司流程", key="ai_topic_article")
        ai_content_type = st.selectbox(
            "内容类型",
            options=["article", "guide", "qa", "news"],
            format_func=lambda x: {
                "article": "专业文章",
                "guide": "指南教程",
                "qa": "问答内容",
                "news": "行业资讯"
            }.get(x, x),
            key="ai_type_article"
        )
        ai_word_count = st.slider("目标字数", min_value=500, max_value=3000, value=1500, step=100, key="ai_words_article")
        
        if st.button("✨ AI生成文章", key="ai_gen_article_btn"):
            if not ai_topic:
                st.error("请输入主题")
            else:
                with st.spinner("AI正在生成文章..."):
                    try:
                        from generator import GEOContentGenerator
                        generator = GEOContentGenerator()
                        result = generator.generate(
                            topic=ai_topic,
                            content_type=ai_content_type,
                            word_count=ai_word_count
                        )
                        
                        # 保存到session
                        st.session_state['ai_generated_article'] = {
                            'title': result.title,
                            'content': result.content,
                            'keywords': result.keywords
                        }
                        
                        st.success("✅ 文章生成成功！已填充到下方表单")
                        
                    except Exception as e:
                        st.error(f"生成失败: {e}")
    
    # 获取AI生成的内容
    ai_data = st.session_state.get('ai_generated_article', {})
    default_title = ai_data.get('title', '')
    default_content = ai_data.get('content', '')
    default_keywords = ', '.join(ai_data.get('keywords', []))
    
    with st.form("article_form"):
        article_title = st.text_input(
            "文章标题 *",
            value=default_title,
            placeholder="输入文章标题"
        )
        article_content = st.text_area(
            "文章内容 *",
            value=default_content,
            height=300,
            placeholder="输入文章内容..."
        )
        article_keywords = st.text_input(
            "关键词（用逗号分隔）",
            value=default_keywords,
            placeholder="关键词1, 关键词2, 关键词3"
        )
        
        submitted = st.form_submit_button("保存文章")
        
        if submitted:
            if not article_title or not article_content:
                st.error("标题和内容不能为空")
            else:
                keywords = [k.strip() for k in article_keywords.split(",") if k.strip()]
                new_article = Article(
                    id=str(uuid.uuid4()),
                    title=article_title,
                    content=article_content,
                    brand_id=selected_brand.id,
                    keywords=keywords,
                    status="draft"
                )
                data_store.save_article(new_article)
                st.success(f"已保存文章: {article_title}")
                # 清除AI生成缓存
                if 'ai_generated_article' in st.session_state:
                    del st.session_state['ai_generated_article']
                st.rerun()


def show_publish_management():
    """发布管理页面"""
    st.markdown("### 📤 发布管理")
    
    data_store = st.session_state['data_store']
    
    # 获取所有发布记录
    records = data_store.get_all_publish_records()
    
    if records:
        st.markdown(f"#### 发布记录 ({len(records)}条)")
        
        # 按状态筛选
        status_filter = st.selectbox(
            "筛选状态",
            options=["全部", "success", "failed", "pending"],
            format_func=lambda x: {
                "全部": "全部",
                "success": "发布成功",
                "failed": "发布失败",
                "pending": "发布中"
            }.get(x, x)
        )
        
        filtered_records = records
        if status_filter != "全部":
            filtered_records = [r for r in records if r.status == status_filter]
        
        # 显示记录
        for record in filtered_records:
            article = data_store.get_article(record.article_id)
            brand = data_store.get_brand(record.brand_id)
            
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                
                with col1:
                    if article:
                        st.markdown(f"**{article.title[:20]}...**" if len(article.title) > 20 else f"**{article.title}**")
                    if brand:
                        st.caption(f"品牌: {brand.name}")
                
                with col2:
                    st.markdown(get_platform_name(Platform(record.platform)))
                    st.caption(f"账号: {record.platform_account}")
                
                with col3:
                    status_class = {
                        "success": "status-success",
                        "failed": "status-failed",
                        "pending": "status-pending"
                    }.get(record.status, "status-pending")
                    
                    status_text = {
                        "success": "✅ 成功",
                        "failed": "❌ 失败",
                        "pending": "⏳ 发布中"
                    }.get(record.status, record.status)
                    
                    st.markdown(
                        f'<span class="platform-badge {status_class}">{status_text}</span>',
                        unsafe_allow_html=True
                    )
                
                with col4:
                    if record.publish_url:
                        st.markdown(f"[查看文章]({record.publish_url})")
                    if record.error_message:
                        st.caption(f"错误: {record.error_message[:30]}...")
                
                st.markdown("---")
    else:
        st.info("暂无发布记录")


def main():
    """主函数"""
    # 侧边栏导航
    with st.sidebar:
        st.markdown("### 🚀 内容分发管理系统")
        
        page = st.radio(
            "选择功能:",
            ["🏢 品牌管理", "🔗 平台账号", "📝 文章管理", "🤖 自动发布", "📤 发布记录"]
        )
        
        st.markdown("---")
        st.markdown("### 📊 统计")
        
        data_store = st.session_state['data_store']
        brands_count = len(data_store.get_all_brands())
        articles_count = len(data_store.get_all_articles())
        records_count = len(data_store.get_all_publish_records())
        
        st.markdown(f"品牌数: **{brands_count}**")
        st.markdown(f"文章数: **{articles_count}**")
        st.markdown(f"发布记录: **{records_count}**")
    
    # 主标题
    st.markdown('<div class="main-header">🚀 内容分发管理系统</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">多品牌 · 多平台 · 一键分发</div>', unsafe_allow_html=True)
    
    # 页面路由
    if page == "🏢 品牌管理":
        show_brand_management()
    elif page == "🔗 平台账号":
        show_platform_accounts()
    elif page == "📝 文章管理":
        show_article_management()
    elif page == "🤖 自动发布":
        # 导入并显示自动发布页面
        from pages.auto_publish import main as auto_publish_main
        auto_publish_main()
    elif page == "📤 发布记录":
        show_publish_management()


if __name__ == "__main__":
    main()
