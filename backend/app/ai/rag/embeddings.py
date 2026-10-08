import os
import logging
import warnings
from typing import List
from langchain_core.embeddings import Embeddings
from app.core.config import settings

logger = logging.getLogger(__name__)

# Ignore non-fatal LangChain deprecation warnings for HuggingFaceEmbeddings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain_community")

# Pass HuggingFace token to environment if available to suppress unauthenticated warnings
hf_token = getattr(settings, "HF_TOKEN", "") or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_KEY")
if hf_token:
    os.environ["HF_TOKEN"] = hf_token.strip()
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = hf_token.strip()

class MockE5Embeddings(Embeddings):
    """
    Mock Fallback Embeddings representing intfloat/multilingual-e5-base
    when model weights are not loaded or download restrictions apply.
    """
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        logger.info(f"Mocking embeddings for {len(texts)} documents.")
        return [[0.1 * i] * 768 for i in range(len(texts))]

    def embed_query(self, text: str) -> List[float]:
        logger.info(f"Mocking embedding for query: '{text}'")
        return [0.25] * 768

class EmbeddingModelLoader:
    """
    Singleton Loader for the Multilingual E5 Embedding Model.
    Exposes LangChain Embeddings wrapper.
    """
    def __init__(self):
        self._embeddings = None

    def get_embeddings(self) -> Embeddings:
        if self._embeddings is not None:
            return self._embeddings

        model_name = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-base")
        device = os.getenv("EMBEDDING_DEVICE", "cpu")
        
        logger.info(f"Initializing Multilingual E5 Embeddings (Model: {model_name}, Device: {device})...")
        
        try:
            if os.getenv("DOWNLOAD_REAL_EMBEDDINGS", "True").lower() != "true":
                raise ValueError("Loading real Embeddings is disabled by configuration.")

            # Try modern langchain_huggingface package first, fallback to langchain_community
            try:
                from langchain_huggingface import HuggingFaceEmbeddings
            except ImportError:
                from langchain_community.embeddings import HuggingFaceEmbeddings

            self._embeddings = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs={"device": device}
            )
            logger.info("Successfully loaded real E5 Embeddings model.")
        except Exception as e:
            logger.error(f"Failed to load real E5 Embeddings: {e}")
            logger.warning("Using E5 Multilingual Fallback Mock Embeddings.")
            self._embeddings = MockE5Embeddings()

        return self._embeddings

embedding_loader = EmbeddingModelLoader()

def get_embedding_model() -> Embeddings:
    return embedding_loader.get_embeddings()
