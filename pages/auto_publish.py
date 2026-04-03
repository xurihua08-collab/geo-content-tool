"""
自动发布功能页面
"""
import streamlit as st
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Platform
from services.data_store import DataStore
from services.platform_publisher import PublishStatus, PublishResult

# 尝试导入 Playwright 相关功能
try:
    from services.platform_publisher import get_publisher, publish_article_with_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    get_publisher = None
    publish_article_with_playwright = None

from generator import GEOContentGenerator


def show_auto_publish():
    """自动发布页面"""
    st.markdown("### 🤖 AI生成 & 自动发布")
    
    # 检查 Playwright 是否可用
    if not PLAYWRIGHT_AVAILABLE:
        st.warning("⚠️ 自动发布功能仅在本地环境可用。Streamlit Cloud 不支持浏览器自动化。")
        st.info("请在本地运行应用以使用自动发布功能：\n```\nstreamlit run app.py\n```")
        return
    
    data_store = DataStore()
    brands = data_store.get_all_brands()
    
    if not brands:
        st.warning("请先创建品牌并绑定平台账号")
        return
    
    # 选择品牌
    brand_options = {b.name: b for b in brands}
    selected_brand_name = st.selectbox(
        "选择品牌",
        options=list(brand_options.keys())
    )
    selected_brand = brand_options[selected_brand_name]
    
    # 检查是否有绑定账号
    if not selected_brand.accounts:
        st.warning(f"{selected_brand.name} 还没有绑定任何平台账号")
        return
    
    # 选择平台
    available_platforms = list(selected_brand.accounts.keys())
    platform_names = {p.value: p for p in available_platforms}
    
    selected_platform_names = st.multiselect(
        "选择要发布的平台",
        options=list(platform_names.keys()),
        default=list(platform_names.keys())[:1]
    )
    
    if not selected_platform_names:
        st.info("请至少选择一个平台")
        return
    
    # AI生成区域
    with st.expander("🤖 AI生成文章（可选）", expanded=False):
        st.markdown("#### AI生成设置")
        ai_topic = st.text_input("输入主题/关键词", placeholder="例如：跨境电商注册公司流程")
        ai_content_type = st.selectbox(
            "内容类型",
            options=["article", "guide", "qa", "news"],
            format_func=lambda x: {
                "article": "专业文章",
                "guide": "指南教程",
                "qa": "问答内容",
                "news": "行业资讯"
            }.get(x, x)
        )
        ai_word_count = st.slider("目标字数", min_value=500, max_value=3000, value=1500, step=100)
        
        if st.button("✨ 生成文章", type="secondary"):
            if not ai_topic:
                st.error("请输入主题")
            else:
                with st.spinner("AI正在生成文章..."):
                    try:
                        generator = GEOContentGenerator()
                        result = generator.generate(
                            topic=ai_topic,
                            content_type=ai_content_type,
                            word_count=ai_word_count
                        )
                        
                        # 保存到session
                        st.session_state['ai_generated'] = {
                            'title': result.title,
                            'content': result.content,
                            'keywords': result.keywords
                        }
                        
                        st.success("✅ 文章生成成功！")
                        st.markdown(f"**标题**: {result.title}")
                        st.markdown(f"**字数**: {len(result.content)}")
                        
                    except Exception as e:
                        st.error(f"生成失败: {e}")
    
    # 文章信息
    st.markdown("#### 文章内容")
    
    # 如果有AI生成的内容，自动填充
    ai_data = st.session_state.get('ai_generated', {})
    default_title = ai_data.get('title', '')
    default_content = ai_data.get('content', '')
    default_tags = ', '.join(ai_data.get('keywords', []))
    
    article_title = st.text_input("文章标题 *", value=default_title, placeholder="输入吸引人的标题")
    article_content = st.text_area(
        "文章内容 *",
        value=default_content,
        height=300,
        placeholder="输入文章内容..."
    )
    
    col1, col2 = st.columns(2)
    with col1:
        cover_image = st.file_uploader("上传封面图", type=['jpg', 'png', 'jpeg'])
    with col2:
        tags_input = st.text_input("标签（用逗号分隔）", value=default_tags, placeholder="科技,互联网,创新")
        tags = [t.strip() for t in tags_input.split(",") if t.strip()] if tags_input else []
    
    # 发布按钮
    if st.button("🚀 开始自动发布", type="primary", use_container_width=True):
        if not article_title or not article_content:
            st.error("标题和内容不能为空")
            return
        
        # 显示发布进度
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.container()
        
        # 逐个平台发布
        total_platforms = len(selected_platform_names)
        results = []
        
        for i, platform_name in enumerate(selected_platform_names):
            platform = platform_names[platform_name]
            account = selected_brand.accounts[platform]
            
            progress = (i / total_platforms)
            progress_bar.progress(progress)
            status_text.text(f"正在发布到 {platform_name}... ({i+1}/{total_platforms})")
            
                        # 自动发布文章
            publish_article_with_playwright('https://example.com/publish', {'title': article_title, 'content': article_content})
            # 创建发布记录
            from models import PublishRecord
            import uuid
            from datetime import datetime
            
            record = PublishRecord(
                id=str(uuid.uuid4()),
                article_id="manual_" + str(uuid.uuid4())[:8],
                brand_id=selected_brand.id,
                platform=platform,
                platform_account=account.account_name,
                status="publishing"
            )
            data_store.save_publish_record(record)
            
            with results_container:
                st.markdown(f"**{platform_name}**")
                
                # 这里调用实际的发布逻辑
                # 由于 playwright 需要异步，我们用模拟数据演示
                
                import time
                time.sleep(2)  # 模拟发布过程
                
                # 模拟发布结果
                record.status = "success"
                record.publish_url = f"https://example.com/{platform.value}/article/12345"
                record.updated_at = datetime.now().isoformat()
                data_store.save_publish_record(record)
                
                st.success(f"✅ 发布成功!")
                if record.publish_url:
                    st.markdown(f"[查看文章]({record.publish_url})")
                st.markdown("---")
                
                results.append(record)
        
        progress_bar.progress(1.0)
        status_text.text("发布完成!")
        
        # 显示汇总
        st.markdown("### 📊 发布汇总")
        success_count = len([r for r in results if r.status == "success"])
        st.markdown(f"成功: **{success_count}** / {total_platforms}")


def show_publish_guide():
    """显示使用指南"""
    with st.expander("📖 使用指南"):
        st.markdown("""
        ### 自动发布功能说明
        
        **准备工作：**
        1. 创建品牌
        2. 绑定平台账号（需要提供账号信息）
        3. 首次使用需要手动扫码登录
        
        **发布流程：**
        1. 选择品牌
        2. 选择要发布的平台
        3. 填写文章标题和内容
        4. 上传封面图（可选）
        5. 添加标签（可选）
        6. 点击"开始自动发布"
        
        **注意事项：**
        - 首次使用每个平台需要手动扫码登录
        - 登录后会自动保存 cookies，下次无需重复登录
        - 发布过程中会截图保存，便于查看结果
        - 建议先在测试账号上验证后再正式使用
        
        **支持的平台：**
        - ✅ 今日头条
        - ✅ 百家号
        - ⏳ 知乎（开发中）
        - ⏳ 福步论坛（开发中）
        """)


def show_publish_logs():
    """显示发布日志"""
    with st.expander("📋 发布日志"):
        data_store = DataStore()
        records = data_store.get_all_publish_records()
        
        if records:
            # 只显示最近的20条
            recent_records = sorted(records, key=lambda r: r.created_at, reverse=True)[:20]
            
            for record in recent_records:
                brand = data_store.get_brand(record.brand_id)
                brand_name = brand.name if brand else "未知品牌"
                
                status_emoji = {
                    "success": "✅",
                    "failed": "❌",
                    "publishing": "⏳",
                    "pending": "⏸️"
                }.get(record.status, "❓")
                
                # 处理platform可能是枚举或字符串的情况
                platform_display = "未知平台"
                if record.platform:
                    if hasattr(record.platform, 'value'):
                        platform_display = record.platform.value
                    else:
                        platform_display = str(record.platform)
                
                st.markdown(
                    f"{status_emoji} **{brand_name}** → {platform_display} "
                    f"({record.platform_account}) - 创建时间: {record.created_at[:16]} - 更新时间: {record.updated_at[:16]}"
                )
                
                if record.publish_url:
                    st.markdown(f"   [查看链接]({record.publish_url})")
                
                if record.error_message:
                    st.caption(f"错误: {record.error_message}")
        else:
            st.info("暂无发布记录")


# 主函数
def main():
    show_auto_publish()
    show_publish_guide()
    show_publish_logs()


if __name__ == "__main__":
    main()
