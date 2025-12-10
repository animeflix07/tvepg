LANGUAGE_MAP = {
    "hindi": "HIN",
    "assamese": "ASM",
    "bengali": "BEN",
    "bodo": "BOD",
    "dogri": "DOG",
    "gujarati": "GUJ",
    "kannada": "KAN",
    "kashmiri": "KAS",
    "konkani": "KON",
    "maithili": "MAI",
    "malayalam": "MAL",
    "manipuri": "MAN",
    "marathi": "MAR",
    "nepali": "NEP",
    "odia": "ODI",
    "punjabi": "PUN",
    "sanskrit": "SAN",
    "santali": "SANL",
    "sindhi": "SIN",
    "tamil": "TAM",
    "telugu": "TEL",
    "urdu": "URD"
}

def map_languages(languages: list) -> list:
    """Map language names to ISO codes"""
    mapped = []
    for lang in languages:
        lang_lower = lang.lower()
        if lang_lower in LANGUAGE_MAP:
            mapped.append(LANGUAGE_MAP[lang_lower])
        else:
            mapped.append(lang.upper())
    return mapped
