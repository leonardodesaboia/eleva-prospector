from pathlib import Path
from models import Lead
from output import generate_markdown, save_leads

def _lead(**kwargs):
    defaults = dict(
        name="Salão Glamour", rating=4.8, reviews=312, prioridade="hot",
        problema="Sem site", servico_recomendado="Landing Page",
        pacote="Presença Express", faixa_preco="R$1.000–R$1.700",
        angulo_venda="Você não aparece no Google", canal="whatsapp",
        phone="(85) 99999-9999", mensagem="Oi, vi o Salão Glamour no Google."
    )
    defaults.update(kwargs)
    return Lead(**defaults)

def test_markdown_contains_lead_name():
    assert "Salão Glamour" in generate_markdown([_lead()])

def test_markdown_contains_priority_uppercase():
    assert "HOT" in generate_markdown([_lead(prioridade="hot")])
    assert "WARM" in generate_markdown([_lead(prioridade="warm")])

def test_markdown_formats_message_as_blockquote():
    result = generate_markdown([_lead(mensagem="Linha um\nLinha dois")])
    assert "> Linha um" in result
    assert "> Linha dois" in result

def test_markdown_shows_contact():
    result = generate_markdown([_lead(canal="whatsapp", phone="(85) 99999-9999")])
    assert "(85) 99999-9999" in result

def test_markdown_uses_instagram_handle_when_no_phone():
    result = generate_markdown([_lead(canal="instagram_dm", phone="", instagram_handle="salao_glamour")])
    assert "salao_glamour" in result

def test_markdown_empty_leads_shows_zero():
    assert "Total: 0 leads" in generate_markdown([])

def test_save_leads_creates_file(tmp_path):
    filepath = save_leads([_lead()], output_dir=str(tmp_path))
    assert Path(filepath).exists()
    content = Path(filepath).read_text(encoding="utf-8")
    assert "Salão Glamour" in content
