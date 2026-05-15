import re
import asyncio
from urllib.parse import quote
from playwright.async_api import async_playwright
from models import Lead

MOBILE_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
)
EXCLUDED_HANDLES = {"p", "explore", "accounts", "stories", "reels", "tv", "direct"}

def calculate_score(lead: Lead) -> int:
    score = 0

    if lead.site_status == "sem_site":
        score += 4
    elif lead.site_status == "site_ruim":
        score += 2

    if not lead.instagram_handle and lead.rating >= 4.0:
        score += 3
    elif lead.instagram_handle:
        if not lead.instagram_has_link:
            score += 2
        elif not lead.instagram_link_works:
            score += 1

    if not lead.phone:
        score += 1

    return min(score, 10)

async def validate_instagram(lead: Lead) -> Lead:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=MOBILE_UA)
        page = await context.new_page()

        try:
            search_query = quote(f'"{lead.name}" site:instagram.com')
            await page.goto(
                f"https://www.google.com/search?q={search_query}",
                timeout=10000
            )
            await page.wait_for_timeout(2000)

            links = await page.query_selector_all('a[href*="instagram.com"]')
            handle = ""
            for link in links:
                href = await link.get_attribute("href") or ""
                match = re.search(r'instagram\.com/([^/?&\s]+)', href)
                if match:
                    candidate = match.group(1).strip("/")
                    if candidate and candidate not in EXCLUDED_HANDLES:
                        handle = candidate
                        break

            if not handle:
                lead.score_dor = calculate_score(lead)
                await browser.close()
                return lead

            lead.instagram_handle = handle

            await page.goto(
                f"https://www.instagram.com/{handle}/",
                timeout=10000
            )
            await page.wait_for_timeout(3000)

            if "login" in page.url or "Sorry, this page" in await page.content():
                lead.instagram_handle = ""
                lead.score_dor = calculate_score(lead)
                await browser.close()
                return lead

            link_el = await page.query_selector(
                'a[href*="linkin.bio"], a[href*="linktr.ee"], '
                'a[href*="bio.link"], a[href*="beacons.ai"]'
            )
            if link_el:
                lead.instagram_has_link = True
                link_url = await link_el.get_attribute("href") or ""
                if link_url:
                    try:
                        link_page = await context.new_page()
                        resp = await link_page.goto(link_url, timeout=5000)
                        lead.instagram_link_works = bool(resp and resp.status < 400)
                        await link_page.close()
                    except Exception:
                        lead.instagram_link_works = False

            time_els = await page.query_selector_all("time")
            lead.instagram_active = len(time_els) > 0

        except Exception:
            lead.instagram_handle = ""

        await browser.close()

    lead.score_dor = calculate_score(lead)
    return lead
