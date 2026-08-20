PHASE1_SYSTEM = """Jsi zkušený právní analytik specializující se na identifikaci slabin v právní argumentaci.
Dostaneš skutkový stav a argumentaci jedné strany. Tvým úkolem je identifikovat 3-5 nejslabších míst
v této argumentaci — nepodložená tvrzení, sporné právní kvalifikace, chybějící důkazy, alternativní
výklady právní normy. Nehodnoť, jestli má strana pravdu — jen hledej slabiny.

Vrať výhradně JSON objekt v přesně tomto tvaru, bez dalšího textu:
{"weaknesses": [{"weakness": "...", "description": "..."}]}"""


def build_phase1_user_prompt(fact_pattern: str, argument: str) -> str:
    return f"Skutkový stav: {fact_pattern}\n\nArgumentace: {argument}"


PHASE1_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "weaknesses": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "weakness": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["weakness", "description"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["weaknesses"],
    "additionalProperties": False,
}
