import re
import subprocess
from models import Lead


def generate_html(lead: Lead) -> str:
    # Strip non-ASCII and non-digit chars before extracting phone digits
    clean_phone = re.sub(r'[^\x00-\x7F]', '', lead.phone or "")
    phone_digits = re.sub(r'\D', '', clean_phone)
    whatsapp_url = f"https://wa.me/55{phone_digits}" if phone_digits else "#"

    prompt = (
        f"Crie uma landing page HTML moderna, visualmente impressionante e profissional para o seguinte negócio local.\n\n"
        f"DADOS DO NEGÓCIO:\n"
        f"- Nome: {lead.name}\n"
        f"- WhatsApp: {whatsapp_url}\n"
        f"- Problema digital que resolve: {lead.problema}\n"
        f"- Serviço entregue: {lead.servico_recomendado}\n\n"
        f"DESIGN — siga estes padrões de sites modernos de 2024:\n"
        f"- Tipografia grande e bold no hero (font-size: 4rem+, font-weight: 800)\n"
        f"- Hero com altura 100vh, imagem Unsplash de fundo + overlay gradiente escuro (não só preto sólido)\n"
        f"- Paleta: escolha uma cor de destaque vibrante (ex: #FF6B35 para barbearia, #6C63FF para tech, #00B894 para saúde) — use ela como accent em botões, bordas e highlights\n"
        f"- Cards com border-radius: 16px, box-shadow suave, hover com transform: translateY(-4px)\n"
        f"- Seções com padding generoso (80px vertical), alternando fundo branco e cinza claro (#F8F9FA)\n"
        f"- Navbar fixo no topo, fundo semitransparente com backdrop-filter: blur(10px)\n"
        f"- Animações CSS suaves: fade-in no scroll via @keyframes\n"
        f"- Botões arredondados (border-radius: 50px) com gradient no accent color\n"
        f"- Fonte: importar Inter do Google Fonts\n"
        f"- Ícones: usar Lucide Icons via CDN (https://unpkg.com/lucide@latest/dist/umd/lucide.min.js) — substituir todos os emojis por ícones Lucide relevantes (ex: <i data-lucide='scissors'></i> para barbearia, <i data-lucide='star'></i> para avaliações). Chamar lucide.createIcons() no final do body.\n\n"
        f"SEÇÕES (nesta ordem):\n"
        f"1. NAVBAR: logo (nome do negócio), link 'Serviços', botão WhatsApp no canto direito\n"
        f"2. HERO (100vh): imagem Unsplash relacionada (ex: https://source.unsplash.com/1600x900/?barbershop,men), "
        f"overlay gradiente, título grande bold, subtítulo, dois botões (WhatsApp + 'Ver serviços')\n"
        f"3. SERVIÇOS: grid 2x2 de cards modernos com ícone emoji grande, título bold, descrição\n"
        f"4. POR QUE NOS ESCOLHER: 3 colunas com número grande (01, 02, 03) + título + texto\n"
        f"5. DEPOIMENTOS: 2 cards com aspas estilizadas, texto, nome e cidade\n"
        f"6. CTA FINAL: fundo com gradient do accent color, título grande, botão WhatsApp\n"
        f"7. FOOTER: nome do negócio, telefone, 'Prévia conceitual criada pela Eleva — eleva.ce'\n\n"
        f"BOTÃO WHATSAPP flutuante: position fixed, bottom 24px, right 24px, z-index 9999, "
        f"background #25D366, border-radius 50%, width 60px, height 60px, box-shadow 0 4px 20px rgba(37,211,102,0.4), "
        f"ícone SVG do WhatsApp branco centralizado\n\n"
        f"Retorne APENAS o HTML completo começando com <!DOCTYPE html>. Sem explicações, sem markdown, sem ```."
    )

    result = subprocess.run(
        ["claude", "-p", prompt],
        capture_output=True, text=True, timeout=300
    )

    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError(f"Claude falhou ao gerar HTML: {result.stderr[:200]}")

    html = result.stdout.strip()
    match = re.search(r'```(?:html)?\s*([\s\S]*?)\s*```', html)
    if match:
        html = match.group(1).strip()

    return html
