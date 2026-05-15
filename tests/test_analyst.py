import json
from unittest.mock import MagicMock, patch
from models import Lead
from agents.analyst import diagnose_lead

MOCK_DIAGNOSIS = {
    "problema": "Alta reputação local, sem presença no Google",
    "servico_recomendado": "Landing Page",
    "pacote": "Presença Express",
    "faixa_preco": "R$1.000–R$1.700",
    "angulo_venda": "Você não aparece no Google quando alguém busca 'salão'",
    "prioridade": "hot"
}

def test_diagnose_lead_fills_all_fields():
    lead = Lead(name="Salão Glamour", rating=4.8, reviews=312, score_dor=7)
    with patch("agents.analyst.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0, stdout=json.dumps(MOCK_DIAGNOSIS)
        )
        result = diagnose_lead(lead)
    assert result.prioridade == "hot"
    assert result.problema == "Alta reputação local, sem presença no Google"
    assert result.pacote == "Presença Express"
    assert result.faixa_preco == "R$1.000–R$1.700"
    assert result.angulo_venda != ""

def test_diagnose_lead_claude_failure_returns_lead_unchanged():
    lead = Lead(name="Test", score_dor=7)
    with patch("agents.analyst.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        result = diagnose_lead(lead)
    assert result.prioridade == ""
    assert result.problema == ""

def test_diagnose_lead_invalid_json_returns_lead_unchanged():
    lead = Lead(name="Test", score_dor=7)
    with patch("agents.analyst.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="not valid json")
        result = diagnose_lead(lead)
    assert result.problema == ""

def test_diagnose_lead_passes_lead_data_to_claude():
    lead = Lead(name="Padaria Central", rating=4.2, reviews=89, score_dor=6)
    with patch("agents.analyst.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0, stdout=json.dumps(MOCK_DIAGNOSIS)
        )
        diagnose_lead(lead)
    call_args = mock_run.call_args
    prompt = call_args[0][0][2]  # third element of the command list ["claude", "-p", prompt]
    assert "Padaria Central" in prompt
    assert "4.2" in prompt
