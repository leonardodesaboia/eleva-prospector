# mockup.py
import argparse
import asyncio
import json
import re
from datetime import date
from pathlib import Path

from agents.mockup_generator import generate_html
from models import Lead
from output_obsidian import update_note_with_mockup, CAPTACAO_DIR

DATA_DIR = Path(__file__).parent / "data"
MOCKUPS_HTML_DIR = Path(__file__).parent / "data" / "mockups"


def _slugify_simple(name: str) -> str:
    name = re.sub(r'[^\w\s-]', '', name)
    return name.strip().replace(" ", "-").lower()


def _find_lead(name_query: str, data_date: str) -> dict:
    json_file = DATA_DIR / f"{data_date}.json"
    if not json_file.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {json_file}\n"
            f"Rode o prospector primeiro: python3 prospect.py --categoria ..."
        )

    with open(json_file, encoding="utf-8") as f:
        leads = json.load(f)

    query = name_query.lower()
    matches = [l for l in leads if query in l["name"].lower()]

    if not matches:
        available = [l["name"] for l in leads]
        raise ValueError(
            f"Lead '{name_query}' não encontrado em {json_file.name}.\n"
            f"Disponíveis: {available}"
        )

    if len(matches) > 1:
        print(f"  Múltiplos matches — usando o primeiro: {matches[0]['name']}")

    return matches[0]


async def _screenshot(html_path: Path, png_path: Path) -> None:
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto(f"file://{html_path.resolve()}")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=str(png_path), full_page=False)
        await browser.close()


def main():
    parser = argparse.ArgumentParser(
        description="Eleva Mockup — gera landing page para lead que respondeu"
    )
    parser.add_argument("--lead", required=True, help="Nome do lead (parcial, case-insensitive)")
    parser.add_argument(
        "--data", default=date.today().isoformat(),
        help="Data do arquivo de leads YYYY-MM-DD (default: hoje)"
    )
    args = parser.parse_args()

    lead_data = _find_lead(args.lead, args.data)
    print(f"\n✓ Lead encontrado: {lead_data['name']}")

    lead = Lead(**lead_data)
    html = generate_html(lead)
    print(f"✓ HTML gerado ({len(html)} bytes)")

    MOCKUPS_HTML_DIR.mkdir(parents=True, exist_ok=True)
    slug = _slugify_simple(lead_data["name"])
    html_path = MOCKUPS_HTML_DIR / f"{slug}.html"
    html_path.write_text(html, encoding="utf-8")

    mockups_img_dir = CAPTACAO_DIR / "mockups"
    mockups_img_dir.mkdir(parents=True, exist_ok=True)
    png_name = f"(C) {args.data} Mockup - {lead_data['name']}.png"
    png_path = mockups_img_dir / png_name

    asyncio.run(_screenshot(html_path, png_path))
    print(f"✓ Screenshot salvo: {png_path.name}")

    updated = update_note_with_mockup(lead_data["name"], args.data, png_name)
    if updated:
        print(f"✓ Nota atualizada: {updated}")
    else:
        print("  Nota não encontrada — screenshot salvo mas nota não atualizada")


if __name__ == "__main__":
    main()
