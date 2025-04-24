"""Factory for creating recommender instances"""
import os
from typing import Optional, Dict, Type

from src.models.recommenders.base import BaseRecommender
from src.models.recommenders.matrix_factorization import SkillBasedRecommender
from src.models.recommenders.hybrid import HybridRecommender
from src.models.persistence.model_storage import get_default_model_path, ModelRegistry
from src.data.dataset import ensure_dataset_exists

# Map model types to their implementations
MODEL_IMPLEMENTATIONS: Dict[str, Type[BaseRecommender]] = {
    "nmf": SkillBasedRecommender,
    "hybrid": HybridRecommender,
    # Add more model implementations as they are created
    # "collaborative": CollaborativeRecommender,
    # "deep": DeepRecommender,
}

def get_recommender(model_type: str = "nmf", **kwargs) -> BaseRecommender:
    """
    Get a recommender instance, creating it if it doesn't exist.
    
    Args:
        model_type: Type of recommender to get
        **kwargs: Additional parameters to pass to the recommender
        
    Returns:
        A recommender instance
    """
    # Check if the model is already registered
    existing_model = ModelRegistry.get_model(model_type)
    if existing_model:
        return existing_model
        
    # Ensure dataset exists
    ensure_dataset_exists()
    
    # Get the correct implementation class
    if model_type not in MODEL_IMPLEMENTATIONS:
        raise ValueError(f"Unknown model type: {model_type}. Available types: {list(MODEL_IMPLEMENTATIONS.keys())}")
    
    model_class = MODEL_IMPLEMENTATIONS[model_type]
    
    # Create a new model instance
    model_path = get_default_model_path(model_type)
    model = model_class(**kwargs)
    
    try:
        if os.path.exists(model_path):
            # Load existing trained model
            model.load_model(model_path)
        else:
            # Create and train a new model
            from src.data.dataset import save_dataset_as_csv
            save_dataset_as_csv()
            
            data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))
            skill_matrix_path = os.path.join(data_dir, "skill_course_matrix.csv")
            
            model.load_data(skill_matrix_path)
            model.train()
            model.save_model(model_path)
    except Exception as e:
        # On error, recreate the model from scratch
        print(f"Error loading/creating model: {str(e)}")
        print("Training new model due to error...")
        
        from src.data.dataset import save_dataset_as_csv
        save_dataset_as_csv()
        
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))
        skill_matrix_path = os.path.join(data_dir, "skill_course_matrix.csv")
        
        model = model_class(**kwargs)
        model.load_data(skill_matrix_path)
        model.train()
        model.save_model(model_path)
    
    # Register the model
    ModelRegistry.register_model(model_type, model)
    
    return model 