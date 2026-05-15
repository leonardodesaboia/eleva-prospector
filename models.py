from dataclasses import dataclass

@dataclass
class Lead:
    name: str = ""
    address: str = ""
    phone: str = ""
    rating: float = 0.0
    reviews: int = 0
    website: str = ""
    site_status: str = "sem_site"  # sem_site | site_ruim | site_ok
    instagram_handle: str = ""
    instagram_active: bool = False
    instagram_has_link: bool = False
    instagram_link_works: bool = False
    score_dor: int = 0
    problema: str = ""
    servico_recomendado: str = ""
    pacote: str = ""
    faixa_preco: str = ""
    angulo_venda: str = ""
    prioridade: str = ""  # hot | warm | cold
    canal: str = ""       # whatsapp | instagram_dm
    mensagem: str = ""
