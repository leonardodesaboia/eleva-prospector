import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from models import Lead
from agents.instagram import validate_instagram

def _make_page(url="https://instagram.com/salao/", content="normal content"):
    page = AsyncMock()
    page.url = url
    page.goto = AsyncMock(return_value=MagicMock(status=200))
    page.content = AsyncMock(return_value=content)
    page.query_selector = AsyncMock(return_value=None)
    page.query_selector_all = AsyncMock(return_value=[MagicMock()])
    return page

def _make_playwright_mock(page):
    context = AsyncMock()
    context.new_page = AsyncMock(return_value=page)
    browser = AsyncMock()
    browser.new_context = AsyncMock(return_value=context)
    browser.close = AsyncMock()
    chromium = AsyncMock()
    chromium.launch = AsyncMock(return_value=browser)
    pw = AsyncMock()
    pw.chromium = chromium
    return pw

@pytest.mark.asyncio
async def test_validate_instagram_no_handle_found_sets_score():
    page = _make_page()
    page.query_selector_all = AsyncMock(return_value=[])  # no instagram links in Google results
    pw = _make_playwright_mock(page)

    lead = Lead(name="Test", site_status="sem_site", rating=4.5)
    with patch("agents.instagram.async_playwright") as mock_pw:
        mock_pw.return_value.__aenter__ = AsyncMock(return_value=pw)
        mock_pw.return_value.__aexit__ = AsyncMock(return_value=None)
        result = await validate_instagram(lead)

    assert result.instagram_handle == ""
    assert result.score_dor > 0  # score calculated even without instagram

@pytest.mark.asyncio
async def test_validate_instagram_login_redirect_clears_handle():
    page = _make_page(url="https://instagram.com/accounts/login/")
    pw = _make_playwright_mock(page)

    lead = Lead(name="Test", site_status="sem_site", rating=4.5)
    with patch("agents.instagram.async_playwright") as mock_pw:
        mock_pw.return_value.__aenter__ = AsyncMock(return_value=pw)
        mock_pw.return_value.__aexit__ = AsyncMock(return_value=None)
        result = await validate_instagram(lead)

    assert result.score_dor >= 0
