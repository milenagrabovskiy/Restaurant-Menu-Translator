
from menu_translator.ai.aws import get_client

def detect_language(text: str) -> str:

    response = get_client("comprehend").detect_dominant_language(Text=text)
    languages = response.get("Languages", [])
    if languages:
        return languages[0]["LanguageCode"]
    return "en"