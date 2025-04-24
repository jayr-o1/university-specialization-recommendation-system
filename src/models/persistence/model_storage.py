"""Model storage utilities for model persistence"""
import os
from typing import Dict, Union, Optional

# Dictionary mapping model types to their file names
MODEL_FILE_MAPPING = {
    "nmf": "recommender_model.npz",
    "collaborative": "collaborative_model.pkl",
    "deep": "deep_model.h5",
    "hybrid": "hybrid_model.pkl"
}

def get_models_dir() -> str:
    """Get the path to the models directory"""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def get_default_model_path(model_type: str) -> str:
    """
    Get the default model file path for a given model type
    
    Args:
        model_type: Type of model (nmf, collaborative, deep, hybrid)
        
    Returns:
        Path to the model file
    """
    if model_type not in MODEL_FILE_MAPPING:
        raise ValueError(f"Unknown model type: {model_type}. Available types: {list(MODEL_FILE_MAPPING.keys())}")
    
    model_filename = MODEL_FILE_MAPPING[model_type]
    return os.path.join(get_models_dir(), model_filename)

class ModelRegistry:
    """Registry for tracking and managing model instances"""
    
    _models: Dict[str, object] = {}
    
    @classmethod
    def register_model(cls, model_type: str, model_instance: object) -> None:
        """Register a model instance"""
        cls._models[model_type] = model_instance
    
    @classmethod
    def get_model(cls, model_type: str) -> Optional[object]:
        """Get a registered model instance"""
        return cls._models.get(model_type)
    
    @classmethod
    def is_model_registered(cls, model_type: str) -> bool:
        """Check if a model type is registered"""
        return model_type in cls._models 