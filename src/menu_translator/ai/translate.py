
from menu_translator.ai.aws import get_client


def translate(text: str, source_lang: str, target_lang: str) -> dict:
    response = get_client("translate").translate_text(
        Text=text,
        SourceLanguageCode=source_lang,
        TargetLanguageCode=target_lang
    )

    return {
        "translated_text": response["TranslatedText"],
        "source_language": response["SourceLanguageCode"],
        "target_language": response["TargetLanguageCode"]
    }


if __name__ == "__main__":
    print(translate("hello", "en", "ru"))