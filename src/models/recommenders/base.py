from abc import ABC, abstractmethod
from typing import List

from src.models.schemas import Faculty, MatchResult

class BaseRecommender(ABC):
    """Abstract base class for all recommendation models"""
    
    @abstractmethod
    def train(self):
        """Train the recommender model"""
        pass
        
    @abstractmethod
    def recommend_courses(self, faculty: Faculty, top_n: int) -> List[MatchResult]:
        """
        Generate course recommendations for a faculty member
        
        Args:
            faculty: Faculty object with skills
            top_n: Number of top recommendations to return
            
        Returns:
            List of MatchResult objects with recommendations
        """
        pass
        
    @abstractmethod
    def save_model(self, path: str):
        """Save model to disk"""
        pass
        
    @abstractmethod
    def load_model(self, path: str):
        """Load model from disk"""
        pass 