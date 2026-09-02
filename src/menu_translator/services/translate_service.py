"""service module for AWS Translate"""
from menu_translator.ai import translate


def get_supported_languages() -> list[dict]:
    """Return supported translation languages."""

    return translate.list_languages()