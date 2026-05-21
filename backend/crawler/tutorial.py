"""
Playwright 入门教程 — 逐步运行，理解每个概念。

运行方式：
    python tutorial.py
"""

import asyncio
from playwright.async_api import async_playwright


# ─────────────────────────────────────────────
# 第 1 课：打开浏览器，访问一个页面，截图
# ─────────────────────────────────────────────
async def lesson_1_open_and_screenshot():
    print("\n=== 第1课：打开页面并截图 ===")

    async with async_playwright() as p:
        # 启动浏览器，headless=False 会弹出真实窗口方便观察
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto("https://www.google.com")
        print(f"页面标题：{await page.title()}")

        await page.screenshot(path="lesson1.png")
        print("截图已保存为 lesson1.png")

        await browser.close()


# ─────────────────────────────────────────────
# 第 2 课：找到元素，填写输入框，点击按钮
# ─────────────────────────────────────────────
async def lesson_2_interact():
    print("\n=== 第2课：填写搜索框并搜索 ===")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto("https://www.google.com", wait_until="domcontentloaded")

        # 找到搜索框并输入内容
        await page.fill("textarea[name='q']", "Playwright 教程")

        # 按回车搜索
        await page.keyboard.press("Enter")

        # 等待搜索结果出现
        await page.wait_for_selector("#search")
        print(f"搜索后标题：{await page.title()}")

        await page.screenshot(path="lesson2.png")
        await browser.close()


# ─────────────────────────────────────────────
# 第 3 课：等待元素出现，读取页面内容
# ─────────────────────────────────────────────
async def lesson_3_read_content():
    print("\n=== 第3课：读取页面文字内容 ===")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto("https://news.ycombinator.com")

        # 等待文章列表出现
        await page.wait_for_selector(".titleline")

        # 获取所有文章标题元素
        titles = await page.query_selector_all(".titleline > a")

        print("Hacker News 当前头条：")
        for i, title in enumerate(titles[:5], 1):
            text = await title.inner_text()
            href = await title.get_attribute("href")
            print(f"  {i}. {text}")
            print(f"     {href}")

        await browser.close()


# ─────────────────────────────────────────────
# 第 4 课：监听网络请求（fetch.py 的核心原理）
# ─────────────────────────────────────────────
async def lesson_4_intercept_requests():
    print("\n=== 第4课：拦截网络请求 ===")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # 注册监听器：每发出一个请求就打印 URL
        def on_request(request):
            # 只打印图片和 JS 文件
            if any(request.url.endswith(ext) for ext in [".js", ".png", ".jpg"]):
                print(f"  [{request.resource_type}] {request.url[:80]}")

        page.on("request", on_request)

        print("访问页面，监听请求中...")
        await page.goto("https://www.google.com")
        await asyncio.sleep(2)

        await browser.close()


# ─────────────────────────────────────────────
# 第 5 课：执行 JavaScript
# ─────────────────────────────────────────────
async def lesson_5_execute_js():
    print("\n=== 第5课：在页面中执行 JavaScript ===")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto("https://www.google.com")

        # 用 JS 读取页面信息
        title = await page.evaluate("document.title")
        url   = await page.evaluate("window.location.href")
        width = await page.evaluate("window.innerWidth")

        print(f"标题：{title}")
        print(f"URL：{url}")
        print(f"窗口宽度：{width}px")

        await browser.close()


async def lesson_6_m3u8():
    # 先做到读取网页的元素
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()


        # 跳到一级界面
        host = 'https://developer.apple.com'
        await page.goto(f'{host}/videos/')
        

        # 找到视频外部元素
        xpath = '//*[@id="main"]/div/section[2]/div/div[2]/div/a[2]'
        video_into_a_element = await page.query_selector(xpath)
        video_page_url = await video_into_a_element.get_attribute("href")
        print(f"视频界面链接：{host}{video_page_url}")

        # 跳到二级界面
        await page.goto(f"{host}{video_page_url}")
        xpath2 = '//*[@id="video"]'
        video_element = await page.query_selector(xpath2)
        video_m3u8_url = await video_element.get_attribute("src")
        print(f"视频 m3u8 链接：{video_m3u8_url}")

# ─────────────────────────────────────────────
# 主入口：逐课运行
# ─────────────────────────────────────────────
async def main():
    choose = int(input("请选择要运行的课程（1-5）："))

    if choose == 1:
        await lesson_1_open_and_screenshot()
    elif choose == 2:
        await lesson_2_interact()
    elif choose == 3:
        await lesson_3_read_content()
    elif choose == 4:
        await lesson_4_intercept_requests()
    elif choose == 5:
        await lesson_5_execute_js()
    elif choose == 6:
        await lesson_6_m3u8()
    else:
        print("无效选择！")


if __name__ == "__main__":
    asyncio.run(main())
