from fpdf import FPDF

from app.pdf_extract import extract_text_from_pdf


def _build_sample_pdf_bytes(text: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, text)
    return bytes(pdf.output())


def test_extract_text_from_pdf_returns_page_text():
    pdf_bytes = _build_sample_pdf_bytes("Sample contract text")
    result = extract_text_from_pdf(pdf_bytes)
    assert "Sample" in result
