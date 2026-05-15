import re
import asyncio
from playwright.async_api import async_playwright
from models import Lead

DESKTOP_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

async def _check_site(page, url: str) -> str:
    if not url:
        return "sem_site"
    try:
        response = await page.goto(url, timeout=5000, wait_until="domcontentloaded")
        if not response or response.status >= 400:
            return "site_ruim"
        content = await page.inner_text("body")
        if len(content.strip()) < 100:
            return "site_ruim"
        return "site_ok"
    except Exception:
        return "site_ruim"


async def discover_leads(categoria: str, cidade: str, limite: int) -> list[Lead]:
    leads = []
    query = f"{categoria} em {cidade}"
    encoded = query.replace(" ", "+")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=DESKTOP_UA)
        page = await context.new_page()

        await page.goto(
            f"https://www.google.com/maps/search/{encoded}",
            timeout=15000
        )
        await page.wait_for_timeout(3000)

        results_panel = await page.query_selector('[role="feed"]')
        if not results_panel:
            await browser.close()
            return leads

        collected = 0
        scroll_count = 0
        max_scrolls = 15

        while collected < limite and scroll_count < max_scrolls:
            items = await page.query_selector_all('[role="article"]')

            for item in items[collected:]:
                if collected >= limite:
                    break
                try:
                    await item.click()
                    await page.wait_for_timeout(2000)

                    name_el = await page.query_selector('h1.DUwDvf')
                    name = (await name_el.inner_text()).strip() if name_el else ""
                    if not name:
                        collected += 1
                        continue

                    rating_el = await page.query_selector('[class*="fontDisplayLarge"]')
                    rating_text = (await rating_el.inner_text()).replace(",", ".") if rating_el else "0"
                    try:
                        rating = float(rating_text)
                    except ValueError:
                        rating = 0.0

                    reviews_el = await page.query_selector('[aria-label*="avalia"]')
                    reviews_label = (
                        await reviews_el.get_attribute("aria-label") or "0"
                    ) if reviews_el else "0"
                    reviews_match = re.search(r'([\d.]+)', reviews_label.replace(".", ""))
                    reviews = int(reviews_match.group(1)) if reviews_match else 0

                    phone_el = await page.query_selector(
                        '[data-tooltip="Copiar número de telefone"]'
                    )
                    phone = (await phone_el.inner_text()).strip() if phone_el else ""

                    website_el = await page.query_selector('[data-item-id="authority"] [href]')
                    website = (
                        await website_el.get_attribute("href") or ""
                    ) if website_el else ""

                    site_page = await context.new_page()
                    site_status = await _check_site(site_page, website)
                    await site_page.close()

                    if site_status == "site_ok" and reviews > 500:
                        collected += 1
                        await page.wait_for_timeout(500)
                        continue

                    leads.append(Lead(
                        name=name, phone=phone, rating=rating,
                        reviews=reviews, website=website, site_status=site_status
                    ))
                    collected += 1
                    await page.wait_for_timeout(1000)

                except Exception:
                    collected += 1
                    continue

            await results_panel.evaluate("el => el.scrollBy(0, 600)")
            await page.wait_for_timeout(2000)
            scroll_count += 1

        await browser.close()

    return leads
