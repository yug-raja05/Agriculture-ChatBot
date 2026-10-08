import logging
import re
from typing import List

logger = logging.getLogger(__name__)

class MultilingualTokenizer:
    """
    Multilingual Tokenizer wrapping spaCy.
    Provides regular expression fallback if spaCy language packs are not preloaded.
    """
    def __init__(self):
        self._nlp = None
        self._load_spacy()

    def _load_spacy(self):
        try:
            import spacy
            # Attempt loading english core model
            self._nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
            logger.info("Successfully configured spaCy English core model tokenizer.")
        except Exception as e:
            logger.warning(f"Could not load spaCy core model: {str(e)}. Using fallback regex tokenizer.")
            self._nlp = None

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenizes multilingual text (English, Hindi, Gujarati).
        """
        if not text:
            return []
            
        if self._nlp:
            try:
                doc = self._nlp(text)
                return [token.text for token in doc]
            except Exception as e:
                logger.error(f"spaCy tokenization failed: {str(e)}. Falling back to regex.")

        # Fallback Regex Tokenizer supporting multilingual scripts
        # Splits by word characters, Devanagari range, Gujarati range, and punctuation
        tokens = re.findall(r"[\u0900-\u097F]+|[\u0A80-\u0AFF]+|\w+|[^\w\s]", text)
        return tokens
