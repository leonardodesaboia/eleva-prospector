import json
import subprocess
from models import Lead
from config import PACOTES_ELEVA

def diagnose_lead(lead: Lead) -> Lead:
    prompt = (
        f"Você é um consultor comercial da Eleva, agência de serviços digitais para negócios locais em Fortaleza.\n\n"
        f"Analise este lead e retorne um JSON com diagnóstico comercial.\n\n"
        f"DADOS DO LEAD:\n"
        f"- Nome: {lead.name}\n"
        f"- Rating Google: {lead.rating} ({lead.reviews} avaliações)\n"
        f"- Site: {lead.site_status}\n"
        f"- Instagram: {'sem perfil' if not lead.instagram_handle else '@' + lead.instagram_handle}\n"
        f"- Score de dor digital: {lead.score_dor}/10\n\n"
        f"{PACOTES_ELEVA}\n\n"
        f"Retorne APENAS JSON válido, sem markdown ou texto extra:\n"
        '{{\n'
        '  "problema": "frase curta descrevendo o problema principal",\n'
        '  "servico_recomendado": "nome do serviço da lista acima",\n'
        '  "pacote": "nome do pacote",\n'
        '  "faixa_preco": "R$ X–R$ Y",\n'
        '  "angulo_venda": "gancho específico para este tipo de negócio",\n'
        '  "prioridade": "hot|warm|cold"\n'
        '}}\n\n'
        f"Regras de prioridade:\n"
        f"- hot: score_dor >= 7 OU (sem site E rating > 4.5)\n"
        f"- warm: score_dor 4–6\n"
        f"- cold: score_dor < 4"
    )

    result = subprocess.run(
        ["claude", "-p", prompt],
        capture_output=True, text=True, timeout=60
    )

    if result.returncode != 0 or not result.stdout.strip():
        return lead

    try:
        data = json.loads(result.stdout.strip())
        lead.problema = data.get("problema", "")
        lead.servico_recomendado = data.get("servico_recomendado", "")
        lead.pacote = data.get("pacote", "")
        lead.faixa_preco = data.get("faixa_preco", "")
        lead.angulo_venda = data.get("angulo_venda", "")
        lead.prioridade = data.get("prioridade", "cold")
    except json.JSONDecodeError:
        pass

    return lead
