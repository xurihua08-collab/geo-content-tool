from playwright.sync_api import sync_playwright

def publish_article_with_playwright(platform_url, article_data):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=False 以便查看
        page = browser.new_page()
        page.goto(platform_url)
        
        # 登录流程
        page.fill('input[name="username"]', '你的用户名')
        page.fill('input[name="password"]', '你的密码')
        page.click('button[type="submit"]')
        
        # 等待登录完成
        page.wait_for_selector('selector_for_dashboard')  # 更新为实际选择器
        
        # 填写文章内容
        page.fill('input[name="title"]', article_data['title'])
        page.fill('textarea[name="content"]', article_data['content'])
        page.click('button[type="submit"]')  # 提交
        
        print("文章已发布！")
        browser.close()

# 示例调用
if __name__ == '__main__':
    sample_article = {
        'title': '示例文章标题',
        'content': '这是文章内容。'
    }
    publish_article_with_playwright('https://example.com/publish', sample_article)