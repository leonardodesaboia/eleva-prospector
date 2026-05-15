import asyncio
from playwright.async_api import async_playwright

async def debug_maps():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = await context.new_page()
        await page.goto("https://www.google.com/maps/search/barbearia+em+Fortaleza", timeout=15000)
        await page.wait_for_timeout(4000)

        feed = await page.query_selector('[role="feed"]')
        print("feed encontrado:", feed is not None)

        articles = await page.query_selector_all('[role="article"]')
        print("articles encontrados:", len(articles))

        # Pega o HTML da área de resultados para inspecionar
        html = await page.content()
        # Salva pra inspecionar
        with open("debug_maps.html", "w") as f:
            f.write(html)
        print("HTML salvo em debug_maps.html")

        await browser.close()

asyncio.run(debug_maps())
