import json
from unittest.mock import MagicMock, patch
from models import Lead
from agents.mockup_generator import generate_html

def _lead():
    return Lead(
        name="Delta Barbearia", phone="(85) 99217-9655",
        problema="Sem site, invisível no Google",
        servico_recomendado="Landing Page",
        prioridade="hot"
    )

def test_generate_html_returns_doctype_string():
    with patch("agents.mockup_generator.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="<!DOCTYPE html><html><body>Barbearia</body></html>"
        )
        result = generate_html(_lead())
    assert result.startswith("<!DOCTYPE html")

def test_generate_html_strips_markdown_code_block():
    with patch("agents.mockup_generator.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="```html\n<!DOCTYPE html><html><body>ok</body></html>\n```"
        )
        result = generate_html(_lead())
    assert result.startswith("<!DOCTYPE html")
    assert "```" not in result

def test_generate_html_raises_on_claude_failure():
    with patch("agents.mockup_generator.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
        raised = False
        try:
            generate_html(_lead())
        except RuntimeError:
            raised = True
    assert raised

def test_generate_html_passes_lead_name_and_phone_to_prompt():
    with patch("agents.mockup_generator.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0, stdout="<!DOCTYPE html><html></html>"
        )
        generate_html(_lead())
    prompt = mock_run.call_args[0][0][2]
    assert "Delta Barbearia" in prompt
    assert "99217" in prompt
