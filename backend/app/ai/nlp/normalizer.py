import unicodedata
import re

class TextNormalizer:
    """
    Sanitizes, cleans, and normalizes raw message texts.
    """
    def __init__(self):
        # Stopwords placeholder matching agricultural questions
        self.stopwords = {"the", "a", "an", "is", "are", "of", "to", "in", "on", "for", "with", "at", "by", "from"}

    def clean_emojis(self, text: str) -> str:
        """
        Removes emojis and visual icons.
        """
        # Range matching common emojis
        return re.sub(r'[\U00010000-\U0010ffff]', '', text)

    def normalize_unicode(self, text: str) -> str:
        return unicodedata.normalize("NFKC", text)

    def normalize_spaces(self, text: str) -> str:
        return " ".join(text.split())

    def expand_abbreviations(self, text: str) -> str:
        # Standard farm shorthand abbreviations
        abbrev_map = {
            "npk": "nitrogen phosphorus potassium",
            "temp": "temperature",
            "qty": "quantity",
            "loc": "location"
        }
        words = text.split()
        expanded = [abbrev_map.get(w.lower(), w) for w in words]
        return " ".join(expanded)

    def clean_special_characters(self, text: str) -> str:
        # Retain standard alphanumerics, punctuation, devanagari (hindi), and gujarati scripts
        # Devanagari range: \u0900-\u097F, Gujarati range: \u0A80-\u0AFF
        cleaned = re.sub(r"[^\w\s\?\.\!\,\u0900-\u097F\u0A80-\u0AFF]", "", text)
        return cleaned

    def clean_stopwords(self, text: str) -> str:
        words = text.split()
        filtered = [w for w in words if w.lower() not in self.stopwords]
        return " ".join(filtered)

    def process(self, text: str, remove_stopwords: bool = False) -> str:
        if not text:
            return ""
        
        normalized = self.normalize_unicode(text)
        cleaned_emoji = self.clean_emojis(normalized)
        cleaned_chars = self.clean_special_characters(cleaned_emoji)
        expanded = self.expand_abbreviations(cleaned_chars)
        clean_spaces = self.normalize_spaces(expanded)
        
        if remove_stopwords:
            clean_spaces = self.clean_stopwords(clean_spaces)
            
        return clean_spaces
