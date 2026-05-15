from models import Lead
from agents.instagram import calculate_score

def test_sem_site_high_rating_no_instagram():
    # 4 (sem_site) + 3 (sem instagram, rating >= 4.0) = 7
    lead = Lead(site_status="sem_site", rating=4.5, instagram_handle="", phone="85999")
    assert calculate_score(lead) == 7

def test_sem_site_low_rating_no_instagram():
    # 4 (sem_site) only — rating < 4.0 doesn't trigger instagram bonus
    lead = Lead(site_status="sem_site", rating=3.8, instagram_handle="", phone="85999")
    assert calculate_score(lead) == 4

def test_site_ruim_instagram_sem_link():
    # 2 (site_ruim) + 2 (sem link) = 4
    lead = Lead(site_status="site_ruim", instagram_handle="salao",
                instagram_has_link=False, phone="85999")
    assert calculate_score(lead) == 4

def test_site_ruim_instagram_link_quebrado():
    # 2 (site_ruim) + 1 (link quebrado) = 3
    lead = Lead(site_status="site_ruim", instagram_handle="salao",
                instagram_has_link=True, instagram_link_works=False, phone="85999")
    assert calculate_score(lead) == 3

def test_sem_site_sem_instagram_sem_telefone():
    # 4 + 3 + 1 = 8
    lead = Lead(site_status="sem_site", rating=4.5, instagram_handle="", phone="")
    assert calculate_score(lead) == 8

def test_score_never_exceeds_10():
    lead = Lead(site_status="sem_site", rating=5.0, instagram_handle="", phone="")
    assert calculate_score(lead) <= 10

def test_site_ok_with_instagram_with_working_link():
    # 0 + 0 = 0
    lead = Lead(site_status="site_ok", instagram_handle="salao",
                instagram_has_link=True, instagram_link_works=True, phone="85999")
    assert calculate_score(lead) == 0
