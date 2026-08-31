"""
Text Normalization Service.

Cleans up text artifacts without destructively altering legal or procurement language.
Maintains separate raw_text and normalized_text.
"""
import re
import unicodedata
import structlog

logger = structlog.get_logger(__name__)

class TextNormalizerService:
    @staticmethod
    def normalize_text(text: str) -> str:
        if not text:
            return ""

        # 1. Unicode normalization (NFKC)
        normalized = unicodedata.normalize("NFKC", text)

        # 2. Convert carriage returns
        normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")

        # 3. Fix broken line-wrap hyphens (e.g. "procure-\nment" -> "procurement")
        normalized = re.sub(r"(\w+)-\n(\w+)", r"\1\2", normalized)

        # 4. Collapse multi-spaces per line (excluding newlines)
        lines = []
        for line in normalized.split("\n"):
            cleaned_line = re.sub(r"[ \t]+", " ", line).strip()
            lines.append(cleaned_line)

        # 5. Remove excessive blank lines (more than 2 consecutive newlines)
        normalized_str = "\n".join(lines)
        normalized_str = re.sub(r"\n{3,}", "\n\n", normalized_str)

        return normalized_str.strip()

text_normalizer = TextNormalizerService()
