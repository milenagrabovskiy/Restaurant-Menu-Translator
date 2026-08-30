from typing import Any

from menu_translator.ai.aws import get_client


def detect_language(text: str, client: Any | None = None) -> tuple[str | None, float]:
    """Detect the dominant language and confidence score"""

    comprehend_client = client if client is not None else get_client("comprehend")

    response = comprehend_client.detect_dominant_language(Text=text)

    languages = response.get("Languages", [])

    if not languages:
        return None, 0.0

    language = languages[0] #dom language will be first in the list

    return language["LanguageCode"], language["Score"]