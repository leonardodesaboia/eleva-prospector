# tests/test_output_obsidian_mockup.py
from pathlib import Path
import output_obsidian
from output_obsidian import update_note_with_mockup, _note_content
from models import Lead


def _lead():
    return Lead(
        name="Delta Barbearia", canal="whatsapp", phone="85999",
        prioridade="hot", problema="Sem site", servico_recomendado="Landing Page",
        pacote="Presença Express", faixa_preco="R$1.000–R$1.700",
        angulo_venda="Você não aparece no Google", mensagem="Oi, vi a Delta..."
    )


def test_note_content_includes_mockup_command():
    content = _note_content(_lead(), "2026-05-15")
    assert "mockup.py" in content
    assert "Delta Barbearia" in content
    assert "Gerar mockup" in content


def test_update_note_adds_mockup_section(tmp_path):
    note = tmp_path / "(C) 2026-05-15 Lead - Delta Barbearia.md"
    note.write_text(
        "# Delta Barbearia\n\n## Diagnóstico\n\ntest\n",
        encoding="utf-8"
    )

    original = output_obsidian.CAPTACAO_DIR
    output_obsidian.CAPTACAO_DIR = tmp_path

    result = update_note_with_mockup("Delta Barbearia", "2026-05-15", "mockup.png")

    output_obsidian.CAPTACAO_DIR = original

    assert result is not None
    content = note.read_text(encoding="utf-8")
    assert "## Mockup" in content
    assert "mockup.png" in content


def test_update_note_is_idempotent(tmp_path):
    note = tmp_path / "(C) 2026-05-15 Lead - Delta Barbearia.md"
    note.write_text("# Delta Barbearia\n\n## Diagnóstico\n\ntest\n", encoding="utf-8")

    original = output_obsidian.CAPTACAO_DIR
    output_obsidian.CAPTACAO_DIR = tmp_path

    update_note_with_mockup("Delta Barbearia", "2026-05-15", "mockup.png")
    update_note_with_mockup("Delta Barbearia", "2026-05-15", "mockup2.png")

    output_obsidian.CAPTACAO_DIR = original

    content = note.read_text(encoding="utf-8")
    assert content.count("## Mockup") == 1
    assert "mockup2.png" in content


def test_update_note_returns_none_when_note_not_found(tmp_path):
    original = output_obsidian.CAPTACAO_DIR
    output_obsidian.CAPTACAO_DIR = tmp_path
    result = update_note_with_mockup("Inexistente", "2026-05-15", "mockup.png")
    output_obsidian.CAPTACAO_DIR = original
    assert result is None
