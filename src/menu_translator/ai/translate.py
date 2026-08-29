from typing import Any

from menu_translator.ai.aws import get_client


def translate(text: str,
              source_lang: str,
              target_lang: str,
              client: Any | None = None
              ) -> dict:
    """Translate text from the source language to the target language."""

    translate_client = (
        client
        if client is not None
        else get_client("translate")
    )

    response = translate_client.translate_text(
        Text=text,
        SourceLanguageCode=source_lang,
        TargetLanguageCode=target_lang
    )

    return {
        "translated_text": response["TranslatedText"],
        "source_language": response["SourceLanguageCode"],
        "target_language": response["TargetLanguageCode"]
    }