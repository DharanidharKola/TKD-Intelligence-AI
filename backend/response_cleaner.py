
import re


def clean_ai_response(text: str) -> str:
    """
    Remove internal PDF references and document citation markers
    from AI responses while preserving normal Markdown formatting.
    """

    if not isinstance(text, str) or not text.strip():
        return ""

    patterns = [
        # Examples: [PDF41.0], [PDF 41.0], [PDF Page 41]
        r"\[\s*PDF\s*(?:Page\s*)?[\d.]+\s*\]",

        # Examples: 【PDF41.0】, (PDF 41.0)
        r"【\s*PDF\s*(?:Page\s*)?[\d.]+\s*】",
        r"\(\s*PDF\s*(?:Page\s*)?[\d.]+\s*\)",

        # Examples: [Page 41], [p. 41]
        r"\[\s*Page\s+\d+(?:\.\d+)?\s*\]",
        r"\[\s*p\.?\s*\d+(?:\.\d+)?\s*\]",

        # Inline PDF references
        r"\bPDF\s*(?:Page\s*)?\d+(?:\.\d+)?\b",
    ]

    cleaned = text

    for pattern in patterns:
        cleaned = re.sub(
            pattern,
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

    # Remove empty brackets or parentheses left after cleaning.
    cleaned = re.sub(r"\[\s*\]", "", cleaned)
    cleaned = re.sub(r"\(\s*\)", "", cleaned)

    # Remove trailing spaces before punctuation.
    cleaned = re.sub(r"\s+([,.;:!?])", r"\1", cleaned)

    # Normalize excessive spaces and blank lines.
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = re.sub(r"\n[ \t]+", "\n", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    return cleaned.strip()
