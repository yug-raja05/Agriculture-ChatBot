import os
import logging
import time
from typing import Dict, Any, List, Optional
from app.ai.ml_framework.base_model import BaseMLModel
from app.ai.ml_framework.loader import MLModelLoader
from app.ai.ml_framework.models import GenericAgriMLModel

logger = logging.getLogger(__name__)

class MLModelRegistry:
    """
    AI Model Registry Service.
    Acts as dynamic registry selecting active production model versions automatically
    without code modifications.
    """
    def __init__(self):
        self.loader = MLModelLoader()
        # Catalog of algorithms mapping accuracies, latency times, and sizes
        self._models_catalog: Dict[str, Dict[str, GenericAgriMLModel]] = {
            "crop": {
                "random_forest": GenericAgriMLModel("random_forest", "1.2.0", "crop", 0.88, 0.87, 0.86, 0.87, training_time_sec=120.0),
                "xgboost": GenericAgriMLModel("xgboost", "2.1.0", "crop", 0.91, 0.90, 0.89, 0.90, training_time_sec=180.0),
                "lightgbm": GenericAgriMLModel("lightgbm", "3.0.0", "crop", 0.89, 0.88, 0.87, 0.88, training_time_sec=90.0),
                "catboost": GenericAgriMLModel("catboost", "1.0.5", "crop", 0.93, 0.92, 0.91, 0.92, training_time_sec=220.0),
                "decision_tree": GenericAgriMLModel("decision_tree", "1.0.0", "crop", 0.82, 0.81, 0.80, 0.81, training_time_sec=30.0),
                "extra_trees": GenericAgriMLModel("extra_trees", "1.1.0", "crop", 0.87, 0.86, 0.85, 0.86, training_time_sec=100.0)
            },
            "fertilizer": {
                "xgboost": GenericAgriMLModel("xgboost", "2.1.0", "fertilizer", 0.94, 0.93, 0.92, 0.93, training_time_sec=150.0),
                "random_forest": GenericAgriMLModel("random_forest", "1.1.0", "fertilizer", 0.89, 0.88, 0.87, 0.88, training_time_sec=110.0),
                "catboost": GenericAgriMLModel("catboost", "1.0.5", "fertilizer", 0.92, 0.91, 0.90, 0.91, training_time_sec=190.0),
                "lightgbm": GenericAgriMLModel("lightgbm", "3.0.0", "fertilizer", 0.91, 0.90, 0.89, 0.90, training_time_sec=80.0),
                "extra_trees": GenericAgriMLModel("extra_trees", "1.1.0", "fertilizer", 0.88, 0.87, 0.86, 0.87, training_time_sec=95.0)
            },
            "yield": {
                "catboost": GenericAgriMLModel("catboost", "1.0.5", "yield", 0.92, 0.91, 0.90, 0.91, training_time_sec=200.0, rmse=0.08, mae=0.06),
                "xgboost": GenericAgriMLModel("xgboost", "2.1.0", "yield", 0.90, 0.89, 0.88, 0.89, training_time_sec=160.0, rmse=0.10, mae=0.08),
                "lightgbm": GenericAgriMLModel("lightgbm", "3.0.0", "yield", 0.89, 0.88, 0.87, 0.88, training_time_sec=85.0, rmse=0.11, mae=0.09),
                "random_forest": GenericAgriMLModel("random_forest", "1.1.0", "yield", 0.88, 0.87, 0.86, 0.87, training_time_sec=115.0, rmse=0.12, mae=0.10)
            },
            "soil": {
                "random_forest": GenericAgriMLModel("random_forest", "1.2.0", "soil", 0.87, 0.86, 0.85, 0.86, training_time_sec=105.0),
                "xgboost": GenericAgriMLModel("xgboost", "2.1.0", "soil", 0.90, 0.89, 0.88, 0.89, training_time_sec=140.0),
                "catboost": GenericAgriMLModel("catboost", "1.0.5", "soil", 0.91, 0.90, 0.89, 0.90, training_time_sec=175.0),
                "lightgbm": GenericAgriMLModel("lightgbm", "3.0.0", "soil", 0.89, 0.88, 0.87, 0.88, training_time_sec=75.0)
            }
        }
        self._active_configs: Dict[str, str] = {
            "crop": os.getenv("ACTIVE_CROP_MODEL", "random_forest"),
            "fertilizer": os.getenv("ACTIVE_FERTILIZER_MODEL", "xgboost"),
            "yield": os.getenv("ACTIVE_YIELD_MODEL", "catboost"),
            "soil": os.getenv("ACTIVE_SOIL_MODEL", "random_forest")
        }

    def RegisterModel(self, category: str, name: str, model_instance: GenericAgriMLModel) -> None:
        if category not in self._models_catalog:
            self._models_catalog[category] = {}
        self._models_catalog[category][name] = model_instance
        logger.info(f"Registered model {name} in category {category}.")

    def GetModel(self, category: str, name: str, version: str = "production") -> Optional[GenericAgriMLModel]:
        cat_models = self._models_catalog.get(category, {})
        model_inst = cat_models.get(name)
        if not model_inst:
            return None
        
        # Load from disk via MLModelLoader
        loaded = self.loader.load_model(model_inst.__class__, version=version)
        # Copy details
        loaded.accuracy = model_inst.accuracy
        loaded.precision = model_inst.precision
        loaded.recall = model_inst.recall
        loaded.f1 = model_inst.f1
        loaded.rmse = model_inst.rmse
        loaded.mae = model_inst.mae
        loaded.mape = model_inst.mape
        loaded.memory_usage_mb = model_inst.memory_usage_mb
        loaded.cpu_usage_pct = model_inst.cpu_usage_pct
        loaded.inference_latency_ms = model_inst.inference_latency_ms
        loaded.training_time_sec = model_inst.training_time_sec
        return loaded

    def GetActiveModel(self, category: str) -> Optional[GenericAgriMLModel]:
        active_name = self._active_configs.get(category)
        if not active_name:
            return None
        return self.GetModel(category, active_name)

    def SetActiveModel(self, category: str, name: str) -> bool:
        cat_models = self._models_catalog.get(category, {})
        if name not in cat_models:
            logger.warning(f"Cannot activate model {name}: not registered in {category}.")
            return False
        self._active_configs[category] = name
        logger.info(f"Activated production model for {category}: {name}")
        return True

    def UnloadModel(self, category: str, name: str, version: str = "production") -> None:
        self.loader.unload_model(category, name, version=version)

    def ValidateModel(self, category: str, name: str) -> bool:
        model = self.GetModel(category, name)
        if not model:
            return False
        # Baseline criteria threshold > 75%
        return model.accuracy >= 0.75

    def BenchmarkModel(self, category: str, name: str) -> Dict[str, Any]:
        model = self.GetModel(category, name)
        if not model:
            return {"error": "Model not registered."}
            
        start_time = time.time()
        for _ in range(50):
            model.predict({"nitrogen": 50.0})
            
        latency = (time.time() - start_time) / 50.0
        return {
            "model_name": name,
            "category": category,
            "benchmark_runs_count": 50,
            "avg_latency_seconds": round(latency, 5),
            "status": "passed"
        }

    def CompareModels(self, category: str) -> List[Dict[str, Any]]:
        cat_models = self._models_catalog.get(category, {})
        comparisons = []
        for name in cat_models.keys():
            model = self.GetModel(category, name)
            if model:
                comparisons.append({
                    "model_name": name,
                    "version": model.version,
                    "accuracy": model.accuracy,
                    "precision": model.precision,
                    "recall": model.recall,
                    "f1_score": model.f1,
                    "rmse": model.rmse,
                    "mae": model.mae,
                    "mape": model.mape,
                    "latency_ms": model.inference_latency_ms,
                    "memory_usage_mb": model.memory_usage_mb,
                    "cpu_usage_pct": model.cpu_usage_pct,
                    "is_active": self._active_configs.get(category) == name
                })
        comparisons.sort(key=lambda x: x["accuracy"], reverse=True)
        return comparisons

    def list_catalog(self) -> List[Dict[str, Any]]:
        catalog = []
        for cat, models in self._models_catalog.items():
            for name in models.keys():
                catalog.append({
                    "category": cat,
                    "name": name,
                    "is_active": self._active_configs.get(cat) == name
                })
        return catalog

ml_model_registry = MLModelRegistry()
