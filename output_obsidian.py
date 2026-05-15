import re
from datetime import date
from pathlib import Path
from models import Lead

CAPTACAO_DIR = Path(__file__).parent.parent / "00 Captação"
PRIORITY_EMOJI = {"hot": "🔥", "warm": "⚡", "cold": "❄️"}


def _slugify(name: str) -> str:
    name = re.sub(r'[^\w\s-]', '', name)
    return name.strip()


def _mockup_command_section(lead_name: str) -> str:
    return (
        "\n## Gerar mockup\n\n"
        "Rode do diretório `prospector/` quando o lead responder:\n\n"
        f'```bash\npython3 mockup.py --lead "{lead_name}"\n```\n'
    )


def _note_content(lead: Lead, today: str) -> str:
    emoji = PRIORITY_EMOJI.get(lead.prioridade, "")
    canal_label = lead.canal.replace("_", " ").title()
    contact = lead.phone if lead.phone else lead.instagram_handle
    message_lines = "\n".join(f"> {line}" for line in lead.mensagem.split("\n") if line.strip())

    return f"""---
type: lead
status: novo
canal: {lead.canal}
prioridade: {lead.prioridade}
data: {today}
---

# {lead.name}

**Origem:** Prospecção ativa (eleva-prospector)
**Canal:** {canal_label} | {contact}
**Rating:** ⭐ {lead.rating} ({lead.reviews} avaliações)
**Prioridade:** {lead.prioridade.upper()} {emoji}

## Diagnóstico

**Problema:** {lead.problema}
**Serviço:** {lead.pacote} — {lead.servico_recomendado} ({lead.faixa_preco})
**Ângulo:** "{lead.angulo_venda}"

## Mensagem

{message_lines}

## Próxima ação

- [ ] Enviar mensagem pelo {canal_label}
- [ ] Follow-up em 3 dias se não responder
{_mockup_command_section(lead.name)}
## Conexões

- [[Eleva]]
- [[Eleva - freelancer]]
"""


def save_to_obsidian(leads: list[Lead]) -> list[str]:
    today = date.today().isoformat()
    CAPTACAO_DIR.mkdir(parents=True, exist_ok=True)
    created = []

    for lead in leads:
        filename = f"(C) {today} Lead - {_slugify(lead.name)}.md"
        filepath = CAPTACAO_DIR / filename

        if filepath.exists():
            continue

        filepath.write_text(_note_content(lead, today), encoding="utf-8")
        created.append(filename)

    return created


def update_note_with_mockup(lead_name: str, data_date: str, png_name: str) -> str | None:
    filename = f"(C) {data_date} Lead - {_slugify(lead_name)}.md"
    note_path = CAPTACAO_DIR / filename

    if not note_path.exists():
        return None

    content = note_path.read_text(encoding="utf-8")
    mockup_section = f"\n## Mockup\n\n![[mockups/{png_name}]]\n"

    if "## Mockup" in content:
        content = re.sub(
            r'\n## Mockup\n[\s\S]*?(?=\n## |\Z)',
            mockup_section,
            content
        )
    else:
        content = content.rstrip() + "\n" + mockup_section

    note_path.write_text(content, encoding="utf-8")
    return filename
