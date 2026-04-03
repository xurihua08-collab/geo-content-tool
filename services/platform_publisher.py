"""
平台发布服务 - 浏览器自动化
支持：今日头条、百家号、知乎、福步论坛
"""
import asyncio
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import json
import os
from datetime import datetime

# 尝试导入 playwright
try:
    from playwright.async_api import async_playwright, Page, Browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("警告: playwright 未安装，请运行: pip install playwright")


class PublishStatus(Enum):
    """发布状态"""
    PENDING = "pending"
    LOGGING_IN = "logging_in"
    PUBLISHING = "publishing"
    SUCCESS = "success"
    FAILED = "failed"
    NEED_VERIFY = "need_verify"


@dataclass
class PublishResult:
    """发布结果"""
    platform: str
    status: PublishStatus
    article_url: str = ""
    error_message: str = ""
    screenshot_path: str = ""
    publish_time: str = ""


class BasePlatformPublisher:
    """平台发布基类"""
    
    def __init__(self, cookies_dir: str = "cookies"):
        self.cookies_dir = cookies_dir
        self.browser = None
        self.page = None
        
        # 确保 cookies 目录存在
        if not os.path.exists(cookies_dir):
            os.makedirs(cookies_dir)
    
    async def __aenter__(self):
        """异步上下文管理器"""
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright 未安装，自动发布功能不可用。请在本地环境安装: pip install playwright")
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,  # 调试时设为 False，生产环境设为 True
            slow_mo=100  # 减慢操作速度，模拟真人
        )
        self.page = await self.browser.new_page(
            viewport={'width': 1920, 'height': 1080}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """退出时关闭浏览器"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    def _get_cookies_path(self, platform: str, account: str) -> str:
        """获取 cookies 文件路径"""
        filename = f"{platform}_{account.replace('@', '_').replace('.', '_')}.json"
        return os.path.join(self.cookies_dir, filename)
    
    async def _load_cookies(self, platform: str, account: str) -> bool:
        """加载 cookies"""
        cookies_path = self._get_cookies_path(platform, account)
        if os.path.exists(cookies_path):
            with open(cookies_path, 'r') as f:
                cookies = json.load(f)
            await self.page.context.add_cookies(cookies)
            return True
        return False
    
    async def _save_cookies(self, platform: str, account: str):
        """保存 cookies"""
        cookies = await self.page.context.cookies()
        cookies_path = self._get_cookies_path(platform, account)
        with open(cookies_path, 'w') as f:
            json.dump(cookies, f)
    
    async def _take_screenshot(self, name: str) -> str:
        """截图保存"""
        screenshot_dir = "screenshots"
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"{screenshot_dir}/{name}_{timestamp}.png"
        await self.page.screenshot(path=path, full_page=True)
        return path


class ToutiaoPublisher(BasePlatformPublisher):
    """今日头条发布器"""
    
    PLATFORM_NAME = "toutiao"
    LOGIN_URL = "https://mp.toutiao.com"
    PUBLISH_URL = "https://mp.toutiao.com/profile_v4/graphic/publish"
    
    async def login(self, account: str, password: str = "", cookies: str = "") -> bool:
        """
        登录今日头条
        
        Args:
            account: 账号名/手机号
            password: 密码（可选，推荐使用扫码登录）
            cookies: 已有的 cookies 字符串（可选）
        
        Returns:
            bool: 是否登录成功
        """
        try:
            # 先尝试使用 cookies 登录
            if await self._load_cookies(self.PLATFORM_NAME, account):
                await self.page.goto(self.LOGIN_URL)
                await asyncio.sleep(2)
                
                # 检查是否已登录（通过检查页面元素）
                if await self._is_logged_in():
                    print(f"[{self.PLATFORM_NAME}] 使用 cookies 登录成功")
                    return True
            
            # 如果没有 cookies 或已过期，需要手动登录
            await self.page.goto(self.LOGIN_URL)
            await asyncio.sleep(3)
            
            print(f"[{self.PLATFORM_NAME}] 请手动扫码登录...")
            print(f"[{self.PLATFORM_NAME}] 等待30秒，请完成登录...")
            await asyncio.sleep(30)  # 等待30秒让用户完成登录
            
            # 保存 cookies
            await self._save_cookies(self.PLATFORM_NAME, account)
            print(f"[{self.PLATFORM_NAME}] 登录成功，cookies 已保存")
            return True
            
        except Exception as e:
            print(f"[{self.PLATFORM_NAME}] 登录失败: {e}")
            return False
    
    async def _is_logged_in(self) -> bool:
        """检查是否已登录"""
        try:
            # 检查是否有登录相关的元素
            # 例如：检查是否有用户头像、发布按钮等
            await self.page.wait_for_selector(".user-info", timeout=3000)
            return True
        except:
            return False
    
    async def publish_article(
        self,
        title: str,
        content: str,
        cover_image: str = "",
        tags: list = None
    ) -> PublishResult:
        """
        发布文章到今日头条
        
        Args:
            title: 文章标题
            content: 文章内容（HTML 或纯文本）
            cover_image: 封面图片路径（可选）
            tags: 标签列表（可选）
        
        Returns:
            PublishResult: 发布结果
        """
        result = PublishResult(
            platform=self.PLATFORM_NAME,
            status=PublishStatus.PENDING
        )
        
        try:
            # 1. 打开发布页面
            await self.page.goto(self.PUBLISH_URL)
            await asyncio.sleep(3)
            
            # 2. 填写标题
            title_input = await self.page.wait_for_selector(
                'input[placeholder*="标题"], textarea[placeholder*="标题"], #title',
                timeout=10000
            )
            await title_input.fill(title)
            await asyncio.sleep(1)
            
            # 3. 填写内容
            # 今日头条使用富文本编辑器，需要特殊处理
            content_editor = await self.page.wait_for_selector(
                '.editor-content, #editor, [contenteditable="true"]',
                timeout=10000
            )
            await content_editor.fill(content)
            await asyncio.sleep(2)
            
            # 4. 上传封面图（如果有）
            if cover_image and os.path.exists(cover_image):
                upload_btn = await self.page.query_selector('input[type="file"]')
                if upload_btn:
                    await upload_btn.set_input_files(cover_image)
                    await asyncio.sleep(3)
            
            # 5. 添加标签（如果有）
            if tags:
                for tag in tags[:5]:  # 最多5个标签
                    tag_input = await self.page.query_selector(
                        'input[placeholder*="标签"], input[placeholder*="话题"]'
                    )
                    if tag_input:
                        await tag_input.fill(tag)
                        await asyncio.sleep(0.5)
                        # 按回车确认
                        await self.page.keyboard.press('Enter')
                        await asyncio.sleep(0.5)
            
            # 6. 截图预览
            preview_path = await self._take_screenshot(f"{self.PLATFORM_NAME}_preview")
            result.screenshot_path = preview_path
            
            # 7. 发布
            publish_btn = await self.page.wait_for_selector(
                'button:has-text("发布"), button:has-text("发表"), .publish-btn',
                timeout=5000
            )
            await publish_btn.click()
            await asyncio.sleep(5)
            
            # 8. 检查发布结果
            result.status = PublishStatus.SUCCESS
            result.publish_time = datetime.now().isoformat()
            
            # 尝试获取文章链接
            try:
                # 等待发布成功提示
                await self.page.wait_for_selector(
                    '.success-message, .publish-success',
                    timeout=10000
                )
                
                # 获取文章链接（如果有）
                link_elem = await self.page.query_selector('a[href*="/article/"]')
                if link_elem:
                    result.article_url = await link_elem.get_attribute('href')
            except:
                pass
            
            # 保存成功截图
            success_path = await self._take_screenshot(f"{self.PLATFORM_NAME}_success")
            
            print(f"[{self.PLATFORM_NAME}] 文章发布成功!")
            print(f"[{self.PLATFORM_NAME}] 标题: {title}")
            if result.article_url:
                print(f"[{self.PLATFORM_NAME}] 链接: {result.article_url}")
            
            return result
            
        except Exception as e:
            result.status = PublishStatus.FAILED
            result.error_message = str(e)
            
            # 保存错误截图
            error_path = await self._take_screenshot(f"{self.PLATFORM_NAME}_error")
            print(f"[{self.PLATFORM_NAME}] 发布失败: {e}")
            print(f"[{self.PLATFORM_NAME}] 错误截图: {error_path}")
            
            return result


class BaijiahaoPublisher(BasePlatformPublisher):
    """百家号发布器"""
    
    PLATFORM_NAME = "baijiahao"
    LOGIN_URL = "https://baijiahao.baidu.com"
    PUBLISH_URL = "https://baijiahao.baidu.com/builderinnerpage/content/article"
    
    async def login(self, account: str, password: str = "", cookies: str = "") -> bool:
        """登录百家号"""
        try:
            if await self._load_cookies(self.PLATFORM_NAME, account):
                await self.page.goto(self.LOGIN_URL)
                await asyncio.sleep(2)
                
                if await self._is_logged_in():
                    print(f"[{self.PLATFORM_NAME}] 使用 cookies 登录成功")
                    return True
            
            await self.page.goto(self.LOGIN_URL)
            await asyncio.sleep(3)
            
            print(f"[{self.PLATFORM_NAME}] 请手动扫码登录...")
            input("登录成功后按 Enter 继续...")
            
            await self._save_cookies(self.PLATFORM_NAME, account)
            print(f"[{self.PLATFORM_NAME}] 登录成功，cookies 已保存")
            return True
            
        except Exception as e:
            print(f"[{self.PLATFORM_NAME}] 登录失败: {e}")
            return False
    
    async def _is_logged_in(self) -> bool:
        """检查是否已登录"""
        try:
            await self.page.wait_for_selector(".user-name, .avatar", timeout=3000)
            return True
        except:
            return False
    
    async def publish_article(
        self,
        title: str,
        content: str,
        cover_image: str = "",
        tags: list = None,
        category: str = "",
        original: bool = True
    ) -> PublishResult:
        """
        发布文章到百家号
        
        Args:
            title: 文章标题
            content: 文章内容
            cover_image: 封面图片路径
            tags: 标签列表
            category: 文章分类
            original: 是否原创
        """
        result = PublishResult(
            platform=self.PLATFORM_NAME,
            status=PublishStatus.PENDING
        )
        
        try:
            # 1. 打开发布页面
            await self.page.goto(self.PUBLISH_URL)
            await asyncio.sleep(3)
            
            # 2. 填写标题
            print(f"[{self.PLATFORM_NAME}] 填写标题...")
            title_input = await self.page.wait_for_selector(
                '#title, input[placeholder*="标题"], textarea[placeholder*="标题"]',
                timeout=10000
            )
            await title_input.fill(title)
            await asyncio.sleep(1)
            
            # 3. 填写内容（百家号使用富文本编辑器）
            print(f"[{self.PLATFORM_NAME}] 填写内容...")
            # 切换到内容编辑框
            content_frame = await self.page.wait_for_selector(
                'iframe#ueditor_0, .edui-editor-iframeholder iframe',
                timeout=10000
            )
            
            if content_frame:
                # 在 iframe 中填写内容
                frame = await content_frame.content_frame()
                if frame:
                    await frame.fill('body', content)
                else:
                    # 如果无法获取 frame，尝试直接填写
                    await self.page.fill('[contenteditable="true"]', content)
            else:
                # 备用方案
                await self.page.fill('[contenteditable="true"]', content)
            
            await asyncio.sleep(2)
            
            # 4. 上传封面图（如果有）
            if cover_image and os.path.exists(cover_image):
                print(f"[{self.PLATFORM_NAME}] 上传封面...")
                try:
                    # 点击上传封面按钮
                    upload_trigger = await self.page.query_selector(
                        '.cover-upload, .upload-btn, [class*="cover"]'
                    )
                    if upload_trigger:
                        await upload_trigger.click()
                        await asyncio.sleep(1)
                        
                        # 选择文件
                        file_input = await self.page.wait_for_selector(
                            'input[type="file"]',
                            timeout=5000
                        )
                        if file_input:
                            await file_input.set_input_files(cover_image)
                            await asyncio.sleep(3)
                except Exception as e:
                    print(f"[{self.PLATFORM_NAME}] 封面上传失败（非致命）: {e}")
            
            # 5. 选择分类（如果提供）
            if category:
                print(f"[{self.PLATFORM_NAME}] 选择分类...")
                try:
                    # 点击分类选择器
                    category_btn = await self.page.query_selector(
                        '.category-selector, [class*="category"], [placeholder*="分类"]'
                    )
                    if category_btn:
                        await category_btn.click()
                        await asyncio.sleep(1)
                        
                        # 选择具体分类
                        category_option = await self.page.wait_for_selector(
                            f'text={category}, [class*="category-item"]:has-text("{category}")',
                            timeout=5000
                        )
                        if category_option:
                            await category_option.click()
                            await asyncio.sleep(1)
                except Exception as e:
                    print(f"[{self.PLATFORM_NAME}] 分类选择失败（非致命）: {e}")
            
            # 6. 设置原创（百家号重视原创）
            if original:
                print(f"[{self.PLATFORM_NAME}] 设置原创...")
                try:
                    original_checkbox = await self.page.query_selector(
                        '.original-checkbox, [class*="original"], input[name*="original"]'
                    )
                    if original_checkbox:
                        await original_checkbox.click()
                        await asyncio.sleep(1)
                except Exception as e:
                    print(f"[{self.PLATFORM_NAME}] 原创设置失败（非致命）: {e}")
            
            # 7. 添加标签（如果有）
            if tags:
                print(f"[{self.PLATFORM_NAME}] 添加标签...")
                try:
                    tag_input = await self.page.query_selector(
                        'input[placeholder*="标签"], input[placeholder*="关键词"], .tag-input'
                    )
                    if tag_input:
                        for tag in tags[:5]:  # 最多5个标签
                            await tag_input.fill(tag)
                            await asyncio.sleep(0.5)
                            await self.page.keyboard.press('Enter')
                            await asyncio.sleep(0.5)
                except Exception as e:
                    print(f"[{self.PLATFORM_NAME}] 标签添加失败（非致命）: {e}")
            
            # 8. 截图预览
            print(f"[{self.PLATFORM_NAME}] 保存预览截图...")
            preview_path = await self._take_screenshot(f"{self.PLATFORM_NAME}_preview")
            result.screenshot_path = preview_path
            
            # 9. 发布
            print(f"[{self.PLATFORM_NAME}] 点击发布...")
            publish_btn = await self.page.wait_for_selector(
                '.publish-btn, button:has-text("发布"), button:has-text("立即发布"), [data-testid*="publish"]',
                timeout=5000
            )
            await publish_btn.click()
            await asyncio.sleep(5)
            
            # 10. 检查发布结果
            print(f"[{self.PLATFORM_NAME}] 检查发布结果...")
            
            # 等待成功提示或跳转
            try:
                # 检查成功提示
                success_indicator = await self.page.wait_for_selector(
                    '.success-message, .publish-success, [class*="success"], .toast-success',
                    timeout=10000
                )
                
                if success_indicator:
                    result.status = PublishStatus.SUCCESS
                    result.publish_time = datetime.now().isoformat()
                    
                    # 尝试获取文章链接
                    try:
                        # 查找文章链接
                        link_elem = await self.page.query_selector(
                            'a[href*="baijiahao.baidu.com/s?id="], a[href*="/article/"]'
                        )
                        if link_elem:
                            result.article_url = await link_elem.get_attribute('href')
                    except:
                        pass
                    
                    print(f"[{self.PLATFORM_NAME}] ✅ 文章发布成功!")
                    if result.article_url:
                        print(f"[{self.PLATFORM_NAME}] 链接: {result.article_url}")
                
            except Exception as e:
                # 可能没有明显的成功提示，检查页面URL变化
                current_url = self.page.url
                if "s?id=" in current_url or "article" in current_url:
                    result.status = PublishStatus.SUCCESS
                    result.article_url = current_url
                    result.publish_time = datetime.now().isoformat()
                    print(f"[{self.PLATFORM_NAME}] ✅ 文章发布成功!")
                    print(f"[{self.PLATFORM_NAME}] 链接: {result.article_url}")
                else:
                    raise Exception("未检测到发布成功标志")
            
            # 保存成功截图
            success_path = await self._take_screenshot(f"{self.PLATFORM_NAME}_success")
            
            return result
            
        except Exception as e:
            result.status = PublishStatus.FAILED
            result.error_message = str(e)
            
            # 保存错误截图
            error_path = await self._take_screenshot(f"{self.PLATFORM_NAME}_error")
            print(f"[{self.PLATFORM_NAME}] ❌ 发布失败: {e}")
            print(f"[{self.PLATFORM_NAME}] 错误截图: {error_path}")
            
            return result


# 发布器工厂
def get_publisher(platform: str):
    """获取对应平台的发布器"""
    if not PLAYWRIGHT_AVAILABLE:
        raise ImportError("Playwright 未安装，自动发布功能仅在本地环境可用。请在本地安装: pip install playwright")
    
    publishers = {
        "toutiao": ToutiaoPublisher,
        "baijiahao": BaijiahaoPublisher,
        # "zhihu": ZhihuPublisher,  # 待实现
        # "fob": FobPublisher,      # 待实现
    }
    
    publisher_class = publishers.get(platform)
    if not publisher_class:
        raise ValueError(f"不支持的平台: {platform}")
    
    return publisher_class()


# 使用示例
async def main():
    """测试发布"""
    # 今日头条发布示例
    async with ToutiaoPublisher() as publisher:
        # 登录
        login_success = await publisher.login(
            account="your_phone_number",
            password=""  # 推荐使用扫码登录
        )
        
        if login_success:
            # 发布文章
            result = await publisher.publish_article(
                title="测试文章标题",
                content="这是测试文章内容...",
                tags=["测试", "科技"]
            )
            
            print(f"发布状态: {result.status}")
            print(f"文章链接: {result.article_url}")


if __name__ == "__main__":
    asyncio.run(main())
