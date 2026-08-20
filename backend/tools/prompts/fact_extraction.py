EXTRACTION_SYSTEM = """Jsi asistent, který z přiloženého právního dokumentu (např. výpověď, smlouva,
žaloba) vytáhne stručný a věcný popis skutkového stavu. Piš jen fakta (kdo, co, kdy, jak) — žádné
právní hodnocení, žádnou argumentaci ani vlastní závěry. Piš česky, souvislým textem nebo v odrážkách,
v rozsahu několika odstavců.

Vrať výhradně samotný text skutkového stavu, bez úvodu, nadpisu nebo komentáře."""


def build_extraction_user_prompt(document_text: str) -> str:
    return f"Dokument:\n{document_text}"
