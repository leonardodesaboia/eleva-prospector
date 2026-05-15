import re
import subprocess
from models import Lead


def generate_html(lead: Lead) -> str:
    phone_digits = re.sub(r'\D', '', lead.phone or "")
    whatsapp_url = f"https://wa.me/55{phone_digits}" if phone_digits else "#"

    prompt = (
        f"Gere uma landing page HTML completa e profissional para o seguinte negócio.\n\n"
        f"DADOS DO NEGÓCIO:\n"
        f"- Nome: {lead.name}\n"
        f"- Telefone WhatsApp: {lead.phone} (link: {whatsapp_url})\n"
        f"- Problema digital: {lead.problema}\n"
        f"- Serviço que vamos entregar: {lead.servico_recomendado}\n\n"
        f"REQUISITOS:\n"
        f"1. HTML completo com CSS inline — sem arquivos externos exceto Unsplash para imagem do hero\n"
        f"2. Totalmente responsivo\n"
        f"3. Estilo limpo e profissional: fundo branco, cores neutras, fonte system-ui\n\n"
        f"SEÇÕES (nesta ordem exata):\n"
        f"1. HERO: imagem de fundo do Unsplash relacionada ao negócio "
        f"(ex: https://source.unsplash.com/1600x900/?barbershop), "
        f"overlay escuro semitransparente, nome do negócio em destaque, "
        f"subtítulo com proposta de valor, botão WhatsApp verde\n"
        f"2. SERVIÇOS: 3-4 cards com emoji + título + descrição curta e plausível\n"
        f"3. POR QUE NOS ESCOLHER: 3 diferenciais com emoji e texto curto\n"
        f"4. DEPOIMENTOS: 2 cards com nome fictício, cidade e texto (sem foto)\n"
        f"5. CTA FINAL: fundo com accent color, título de fechamento, botão WhatsApp grande\n\n"
        f"BOTÃO WHATSAPP (link: {whatsapp_url}):\n"
        f"- No hero\n"
        f"- No CTA final\n"
        f"- Flutuante fixo no canto inferior direito (position: fixed, z-index: 9999, "
        f"background: #25D366, border-radius: 50%, padding: 14px, bottom: 20px, right: 20px)\n\n"
        f"RODAPÉ: 'Esta é uma prévia conceitual criada pela Eleva — eleva.ce'\n\n"
        f"Retorne APENAS o HTML completo começando com <!DOCTYPE html>. "
        f"Sem explicações, sem markdown, sem ```."
    )

    result = subprocess.run(
        ["claude", "-p", prompt],
        capture_output=True, text=True, timeout=120
    )

    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError(f"Claude falhou ao gerar HTML: {result.stderr[:200]}")

    html = result.stdout.strip()
    match = re.search(r'```(?:html)?\s*([\s\S]*?)\s*```', html)
    if match:
        html = match.group(1).strip()

    return html
