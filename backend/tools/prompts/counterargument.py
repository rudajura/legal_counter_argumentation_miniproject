import json

PHASE2_SYSTEM = """Jsi advokát zastupující protistranu. Dostaneš seznam slabin v argumentaci soupeře.
Ke každé slabině zformuluj nejsilnější možný protiargument, jak by ho reálně použil zkušený advokát
u soudu. Přidej odhad síly protiargumentu (low/medium/high) a stručné zdůvodnění, případně
odkaz na typ právní normy nebo judikatury, o kterou by se dal opřít (bez nutnosti reálné citace,
lze uvést obecně, např. "ustálená judikatura NS k § 2913 OZ").

Na závěr přidej celkové shrnutí (1-2 věty) hodnotící, jak silná je původní argumentace a jaké je
hlavní riziko.

Vrať výhradně JSON objekt v přesně tomto tvaru, bez dalšího textu:
{"items": [{"weakness": "...", "counterargument": "...", "strength": "low|medium|high", "reasoning": "..."}], "summary": "..."}"""


def build_phase2_user_prompt(
    weaknesses: list[dict], fact_pattern: str, argument: str
) -> str:
    return (
        f"Skutkový stav: {fact_pattern}\n\n"
        f"Argumentace protistrany: {argument}\n\n"
        f"Slabiny: {json.dumps(weaknesses, ensure_ascii=False)}"
    )


PHASE2_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "weakness": {"type": "string"},
                    "counterargument": {"type": "string"},
                    "strength": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                    },
                    "reasoning": {"type": "string"},
                },
                "required": [
                    "weakness",
                    "counterargument",
                    "strength",
                    "reasoning",
                ],
                "additionalProperties": False,
            },
        },
        "summary": {"type": "string"},
    },
    "required": ["summary", "items"],
    "additionalProperties": False,
}
