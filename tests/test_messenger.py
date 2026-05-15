import json
from unittest.mock import MagicMock, patch
from models import Lead
from agents.messenger import generate_message

def _lead_with_phone():
    return Lead(
        name="Salão Glamour", phone="(85) 99999-9999", rating=4.8, reviews=312,
        problema="Sem site", servico_recomendado="Landing Page",
        angulo_venda="Você não aparece no Google"
    )

def _lead_no_phone():
    return Lead(
        name="Salão Glamour", phone="", instagram_handle="salao_glamour",
        rating=4.8, reviews=312, problema="Sem site",
        servico_recomendado="Landing Page", angulo_venda="Você não aparece no Google"
    )

def test_generate_message_fills_canal_and_mensagem():
    mock_resp = json.dumps({"canal": "whatsapp", "mensagem": "Oi, vi o Salão Glamour..."})
    with patch("agents.messenger.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout=mock_resp)
        result = generate_message(_lead_with_phone())
    assert result.canal == "whatsapp"
    assert result.mensagem == "Oi, vi o Salão Glamour..."

def test_generate_message_uses_instagram_dm_when_no_phone():
    mock_resp = json.dumps({"canal": "instagram_dm", "mensagem": "Oi via Instagram"})
    with patch("agents.messenger.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout=mock_resp)
        result = generate_message(_lead_no_phone())
    assert result.canal == "instagram_dm"

def test_generate_message_failure_leaves_fields_empty():
    with patch("agents.messenger.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        result = generate_message(_lead_with_phone())
    assert result.mensagem == ""
    assert result.canal == ""

def test_generate_message_invalid_json_leaves_fields_empty():
    with patch("agents.messenger.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="not json")
        result = generate_message(_lead_with_phone())
    assert result.mensagem == ""

def test_generate_message_passes_lead_data_to_claude():
    mock_resp = json.dumps({"canal": "whatsapp", "mensagem": "test"})
    with patch("agents.messenger.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout=mock_resp)
        generate_message(_lead_with_phone())
    prompt = mock_run.call_args[0][0][2]
    assert "Salão Glamour" in prompt
    assert "Você não aparece no Google" in prompt
