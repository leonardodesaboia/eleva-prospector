import argparse
import asyncio
import json
from datetime import date
from pathlib import Path

from agents.discovery import discover_leads
from agents.instagram import validate_instagram
from agents.analyst import diagnose_lead
from agents.messenger import generate_message
from output import save_leads
from config import DEFAULT_CIDADE, MIN_SCORE_DOR

def main():
    parser = argparse.ArgumentParser(description="Eleva Prospector — gerador de leads qualificados")
    parser.add_argument("--categoria", required=True, help="Ex: 'salão de beleza'")
    parser.add_argument("--cidade", default=DEFAULT_CIDADE, help="Ex: 'Fortaleza'")
    parser.add_argument("--limite", type=int, default=25, help="Máximo de negócios a analisar")
    args = parser.parse_args()

    print(f"\n[1/4] Descobrindo: {args.categoria} em {args.cidade} (limite: {args.limite})...")
    leads = asyncio.run(discover_leads(args.categoria, args.cidade, args.limite))
    print(f"  → {len(leads)} negócios coletados")

    print("[2/4] Validando Instagram e calculando score de dor...")
    leads = [asyncio.run(validate_instagram(lead)) for lead in leads]
    leads = [l for l in leads if l.score_dor >= MIN_SCORE_DOR]
    print(f"  → {len(leads)} leads qualificados (score_dor >= {MIN_SCORE_DOR})")

    if not leads:
        print("  Nenhum lead qualificado. Tente outra categoria ou cidade.")
        return

    print("[3/4] Gerando diagnóstico com Claude...")
    leads = [diagnose_lead(lead) for lead in leads]
    leads = [l for l in leads if l.prioridade in ("hot", "warm")]
    print(f"  → {len(leads)} leads hot/warm")

    print("[4/4] Gerando mensagens com Claude...")
    leads = [generate_message(lead) for lead in leads]
    leads = [l for l in leads if l.mensagem]

    Path("data").mkdir(exist_ok=True)
    session_file = f"data/{date.today().isoformat()}.json"
    with open(session_file, "w", encoding="utf-8") as f:
        json.dump([vars(l) for l in leads], f, ensure_ascii=False, indent=2)

    filepath = save_leads(leads)
    print(f"\n✓ Revisão pronta: {filepath}")
    print(f"  {len(leads)} leads com mensagem. Abra o arquivo e envie os aprovados.")

if __name__ == "__main__":
    main()
