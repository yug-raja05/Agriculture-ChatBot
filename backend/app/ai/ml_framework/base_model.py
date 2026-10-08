from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseMLModel(ABC):
    """
    Abstract Base Class for every Machine Learning model in AgriGenius AI.
    """
    def __init__(self, name: str, version: str, category: str):
        self.name = name
        self.version = version
        self.category = category  # crop, fertilizer, yield, soil
        self.is_active = False

    @abstractmethod
    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes prediction.
        """
        pass

    @abstractmethod
    def train(self, training_data: Any) -> Dict[str, Any]:
        """
        Trains model weights.
        """
        pass

    @abstractmethod
    def evaluate(self, test_data: Any) -> Dict[str, Any]:
        """
        Computes evaluation parameters (Accuracy, Precision, recall, latency).
        """
        pass
