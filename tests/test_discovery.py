import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.discovery import _check_site

@pytest.mark.asyncio
async def test_check_site_empty_url_returns_sem_site():
    page = AsyncMock()
    assert await _check_site(page, "") == "sem_site"

@pytest.mark.asyncio
async def test_check_site_http_404_returns_site_ruim():
    page = AsyncMock()
    response = MagicMock()
    response.status = 404
    page.goto = AsyncMock(return_value=response)
    assert await _check_site(page, "http://example.com") == "site_ruim"

@pytest.mark.asyncio
async def test_check_site_http_500_returns_site_ruim():
    page = AsyncMock()
    response = MagicMock()
    response.status = 500
    page.goto = AsyncMock(return_value=response)
    assert await _check_site(page, "http://example.com") == "site_ruim"

@pytest.mark.asyncio
async def test_check_site_exception_returns_site_ruim():
    page = AsyncMock()
    page.goto = AsyncMock(side_effect=Exception("connection timeout"))
    assert await _check_site(page, "http://example.com") == "site_ruim"

@pytest.mark.asyncio
async def test_check_site_200_with_content_returns_site_ok():
    page = AsyncMock()
    response = MagicMock()
    response.status = 200
    page.goto = AsyncMock(return_value=response)
    page.inner_text = AsyncMock(return_value="a" * 200)
    assert await _check_site(page, "http://example.com") == "site_ok"

@pytest.mark.asyncio
async def test_check_site_200_empty_body_returns_site_ruim():
    page = AsyncMock()
    response = MagicMock()
    response.status = 200
    page.goto = AsyncMock(return_value=response)
    page.inner_text = AsyncMock(return_value="short")
    assert await _check_site(page, "http://example.com") == "site_ruim"

@pytest.mark.asyncio
async def test_check_site_none_response_returns_site_ruim():
    page = AsyncMock()
    page.goto = AsyncMock(return_value=None)
    assert await _check_site(page, "http://example.com") == "site_ruim"

from unittest.mock import patch
from agents.discovery import discover_leads

@pytest.mark.asyncio
async def test_discover_leads_returns_empty_list_when_no_feed():
    with patch("agents.discovery.async_playwright") as mock_pw:
        mock_context = AsyncMock()
        mock_browser = AsyncMock()
        mock_page = AsyncMock()

        inner_pw = AsyncMock()
        inner_pw.chromium = AsyncMock()
        inner_pw.chromium.launch = AsyncMock(return_value=mock_browser)

        mock_pw.return_value.__aenter__ = AsyncMock(return_value=inner_pw)
        mock_pw.return_value.__aexit__ = AsyncMock(return_value=None)

        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_page.query_selector = AsyncMock(return_value=None)  # no feed panel

        result = await discover_leads("salão", "Fortaleza", 5)
        assert isinstance(result, list)
        assert len(result) == 0
