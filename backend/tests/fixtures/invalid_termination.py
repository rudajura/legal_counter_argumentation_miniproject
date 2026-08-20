"""Static fixture responses for the "Neplatná výpověď" demo case.

Mirrors the fact pattern/argument used in frontend/src/data/demoExamples.ts so
tests exercising this scenario can assert against realistic, pre-generated
model output without calling the OpenAI API.
"""

FACT_PATTERN = (
    "Zaměstnanci byla dána výpověď pro nadbytečnost dle § 52 písm. c) zákoníku "
    "práce s odůvodněním organizační změny. Zaměstnanec tvrdí, že na jeho místo "
    "byl do 14 dnů přijat nový pracovník na stejnou pozici."
)

ARGUMENT = (
    "Jako zaměstnanec tvrdím, že výpověď je neplatná, protože organizační změna "
    "byla pouze účelová a fiktivní — moje pracovní místo fakticky nezaniklo, "
    "jelikož zaměstnavatel na stejnou pozici téměř okamžitě přijal jinou osobu."
)

# Five independent, schema-valid AnalyzeResponse payloads (see app.schemas).
# Each represents a plausible full analysis for this scenario so a test can
# pick any one (or iterate over all) instead of hitting the real API.
INVALID_TERMINATION_RESPONSES = [
    {
        "summary": "Argumentace je středně silná, ale opírá se pouze o časovou "
        "shodu, kterou lze vysvětlit i jinak.",
        "items": [
            {
                "weakness": "Chybí důkaz o totožnosti pracovní pozice",
                "counterargument": "Zaměstnavatel namítne, že nově přijatý "
                "pracovník zastává jinou pracovní pozici s odlišnou náplní "
                "práce, byť formálně podobným označením, a organizační "
                "změna tedy byla skutečná.",
                "strength": "high",
                "reasoning": "Bez porovnání pracovních náplní a organizační "
                "struktury před a po změně jde jen o domněnku založenou na "
                "časové souvislosti, což soudy samo o sobě nepovažují za "
                "průkaz účelovosti.",
            },
            {
                "weakness": "Nedoložena existence a obsah organizační změny",
                "counterargument": "Zaměstnavatel doloží rozhodnutí o "
                "organizační změně přijaté před podáním výpovědi, čímž "
                "prokáže, že nešlo o fiktivní krok učiněný až dodatečně.",
                "strength": "medium",
                "reasoning": "Platnost výpovědi dle § 52 písm. c) zákoníku "
                "práce závisí na tom, že rozhodnutí o organizační změně "
                "skutečně předcházelo výpovědi; to však zaměstnanec ve svém "
                "vylíčení skutkového stavu nezpochybňuje.",
            },
        ],
    },
    {
        "summary": "Argumentace je slabá, protože opomíjí procesní podmínku "
        "pro uplatnění neplatnosti výpovědi.",
        "items": [
            {
                "weakness": "Neuvedena dvouměsíční lhůta k žalobě dle § 72 "
                "zákoníku práce",
                "counterargument": "Zaměstnavatel namítne, že pokud "
                "zaměstnanec nepodal žalobu na neplatnost výpovědi u soudu "
                "ve lhůtě dvou měsíců ode dne, kdy měl pracovní poměr "
                "skončit, k neplatnosti se nepřihlíží bez ohledu na to, jak "
                "silné jsou věcné argumenty.",
                "strength": "high",
                "reasoning": "Jde o prekluzivní lhůtu, kterou soud zkoumá "
                "jako první, dřív než se zabývá věcnou opodstatněností "
                "tvrzení o fiktivní organizační změně.",
            },
            {
                "weakness": "Chybí tvrzení o splnění nabídkové povinnosti",
                "counterargument": "Zaměstnavatel doloží, že zaměstnanci "
                "nemohl nabídnout jinou vhodnou práci dle § 61 odst. 1 "
                "zákoníku práce, protože žádná volná pozice v době výpovědi "
                "neexistovala.",
                "strength": "low",
                "reasoning": "Tato námitka se týká jiné podmínky platnosti "
                "výpovědi a nesouvisí přímo s tvrzenou fiktivností "
                "organizační změny, proto má nižší dopad na spor.",
            },
        ],
    },
    {
        "summary": "Argumentace je poměrně silná v jádru věci, ale chybí jí "
        "podpůrné důkazy.",
        "items": [
            {
                "weakness": "Tvrzení o přijetí nového pracovníka není nijak "
                "doloženo",
                "counterargument": "Zaměstnavatel zpochybní věrohodnost "
                "tvrzení a požádá soud, aby zaměstnanec prokázal, že nová "
                "osoba byla skutečně přijata na totéž pracovní místo, "
                "např. pracovní smlouvou nebo výpisem z vnitřního systému.",
                "strength": "medium",
                "reasoning": "Důkazní břemeno o okolnostech vzniku nároku "
                "leží na zaměstnanci; pouhé tvrzení bez důkazního návrhu "
                "oslabuje pozici u soudu.",
            },
            {
                "weakness": "Nezohledněna možnost legitimní následné potřeby "
                "obsadit místo",
                "counterargument": "Zaměstnavatel argumentuje, že i "
                "krátce po zrušení místa může vzniknout nová, obsahově "
                "odlišná potřeba přijmout pracovníka, aniž by to "
                "znamenalo, že původní organizační změna byla účelová.",
                "strength": "medium",
                "reasoning": "Ustálená judikatura Nejvyššího soudu "
                "připouští, že k obnovené personální potřebě může dojít i "
                "v krátkém časovém odstupu, pokud je věcně odůvodněná.",
            },
        ],
    },
    {
        "summary": "Argumentace je celkově středně silná, hlavním rizikem je "
        "nedostatečné vymezení příčinné souvislosti.",
        "items": [
            {
                "weakness": "Chybí vysvětlení, proč organizační změna byla "
                "účelová, nikoli jen shoda okolností",
                "counterargument": "Zaměstnavatel namítne, že zaměstnanec "
                "nepředložil žádný přímý důkaz o úmyslu obejít zákon "
                "(např. interní komunikaci), a proto jde jen o spekulaci.",
                "strength": "high",
                "reasoning": "Soudy vyžadují prokázání skutečného úmyslu "
                "nebo alespoň objektivních indicií nad rámec pouhé časové "
                "návaznosti, aby organizační změnu označily za fiktivní.",
            },
            {
                "weakness": "Neřešena otázka rozsahu pracovní pozice nového "
                "zaměstnance",
                "counterargument": "Zaměstnavatel uvede, že nový pracovník "
                "byl přijat na částečný úvazek nebo na dobu určitou k "
                "pokrytí přechodné agendy, což organizační změnu "
                "nezpochybňuje.",
                "strength": "low",
                "reasoning": "Jde o hypotetickou obranu, kterou musí "
                "zaměstnavatel teprve prokázat; sama o sobě argumentaci "
                "zaměstnance jen mírně oslabuje.",
            },
        ],
    },
    {
        "summary": "Argumentace je silná, pokud ji zaměstnanec podpoří "
        "konkrétními důkazy o obsazení pozice.",
        "items": [
            {
                "weakness": "Nejasné, zda šlo o totéž pracovní místo ve "
                "smyslu organizační struktury, nebo jen o podobný pracovní "
                "titul",
                "counterargument": "Zaměstnavatel předloží organizační "
                "schéma prokazující, že zrušené místo a nově obsazené "
                "místo jsou v organizační struktuře odlišná, byť mají "
                "podobný název pozice.",
                "strength": "medium",
                "reasoning": "Rozhodující je faktický obsah práce a "
                "zařazení v organizační struktuře, nikoli název pozice; "
                "argumentace zaměstnance toto rozlišení nezohledňuje.",
            },
            {
                "weakness": "Krátká lhůta 14 dnů nemusí sama o sobě "
                "prokazovat fiktivnost",
                "counterargument": "Zaměstnavatel namítne, že rychlé "
                "obsazení pozice může být důsledkem dlouhodobě plánovaného "
                "náboru zahájeného před výpovědí, nikoli důkazem účelovosti.",
                "strength": "low",
                "reasoning": "Samotná rychlost náboru je nepřímý důkaz a "
                "může mít i nevinné vysvětlení, pokud zaměstnavatel doloží "
                "časovou osu náborového procesu.",
            },
        ],
    },
]
