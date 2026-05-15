from datetime import date
from pathlib import Path
from models import Lead

PRIORITY_EMOJI = {"hot": "🔥", "warm": "⚡", "cold": "❄️"}

def generate_markdown(leads: list[Lead]) -> str:
    today = date.today().isoformat()
    sections = [f"# Leads — {today}\n\nTotal: {len(leads)} leads qualificados\n\n---\n"]

    for lead in leads:
        emoji = PRIORITY_EMOJI.get(lead.prioridade, "")
        contact = lead.phone if lead.phone else lead.instagram_handle
        canal_label = lead.canal.replace("_", " ").title()
        message_lines = "\n".join(
            f"> {line}" for line in lead.mensagem.split("\n") if line.strip()
        )

        sections.append(
            f"## {lead.name} ⭐ {lead.rating} ({lead.reviews} reviews)"
            f" | {lead.prioridade.upper()} {emoji}\n\n"
            f"**Problema:** {lead.problema}\n"
            f"**Serviço:** {lead.pacote} — {lead.servico_recomendado} ({lead.faixa_preco})\n"
            f"**Ângulo:** \"{lead.angulo_venda}\"\n\n"
            f"**Canal:** {canal_label} | {contact}\n"
            f"**Mensagem:**\n{message_lines}\n\n---\n"
        )

    return "\n".join(sections)

def save_leads(leads: list[Lead], output_dir: str = "leads") -> str:
    today = date.today().isoformat()
    Path(output_dir).mkdir(exist_ok=True)
    filepath = f"{output_dir}/{today}.md"
    Path(filepath).write_text(generate_markdown(leads), encoding="utf-8")
    return filepath
