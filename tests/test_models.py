from models import Lead

def test_lead_default_values():
    lead = Lead()
    assert lead.name == ""
    assert lead.site_status == "sem_site"
    assert lead.score_dor == 0
    assert lead.prioridade == ""
    assert lead.mensagem == ""

def test_lead_with_values():
    lead = Lead(name="Salão Glamour", rating=4.8, reviews=312)
    assert lead.name == "Salão Glamour"
    assert lead.rating == 4.8
    assert lead.reviews == 312
    assert lead.site_status == "sem_site"

def test_lead_all_fields_present():
    lead = Lead()
    required = [
        "name", "address", "phone", "rating", "reviews", "website",
        "site_status", "instagram_handle", "instagram_active",
        "instagram_has_link", "instagram_link_works", "score_dor",
        "problema", "servico_recomendado", "pacote", "faixa_preco",
        "angulo_venda", "prioridade", "canal", "mensagem"
    ]
    for field in required:
        assert hasattr(lead, field), f"Missing field: {field}"
