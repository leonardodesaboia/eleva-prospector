import json
import subprocess
from models import Lead

def generate_message(lead: Lead) -> Lead:
    canal = "whatsapp" if lead.phone else "instagram_dm"

    prompt = (
        f"Você escreve mensagens de prospecção humanas para a Eleva, agência de serviços digitais em Fortaleza.\n\n"
        f"Escreva UMA mensagem de abordagem fria. Retorne APENAS JSON válido, sem markdown.\n\n"
        f"DADOS:\n"
        f"- Nome do negócio: {lead.name}\n"
        f"- Rating Google: {lead.rating} ({lead.reviews} avaliações)\n"
        f"- Problema identificado: {lead.problema}\n"
        f"- Serviço a oferecer: {lead.servico_recomendado}\n"
        f"- Ângulo de venda: {lead.angulo_venda}\n"
        f"- Canal: {canal}\n\n"
        f"REGRAS OBRIGATÓRIAS:\n"
        f"- Máximo 5 linhas\n"
        f"- Mencione o nome do negócio e um dado específico (rating ou número de avaliações)\n"
        f"- NÃO mencione IA, automação ou que é freelancer/agência na primeira mensagem\n"
        f"- NÃO use saudações formais (Prezado, Boa tarde)\n"
        f"- NÃO termine com CTA agressivo (feche agora, aproveite, clique aqui)\n"
        f"- Termine com UMA pergunta simples e aberta\n"
        f"- Tom: direto, humano, curioso — não vendedor\n\n"
        f'Retorne APENAS: {{"canal": "{canal}", "mensagem": "texto aqui"}}'
    )

    result = subprocess.run(
        ["claude", "-p", prompt],
        capture_output=True, text=True, timeout=60
    )

    if result.returncode != 0 or not result.stdout.strip():
        return lead

    try:
        data = json.loads(result.stdout.strip())
        lead.canal = data.get("canal", canal)
        lead.mensagem = data.get("mensagem", "")
    except json.JSONDecodeError:
        pass

    return lead
