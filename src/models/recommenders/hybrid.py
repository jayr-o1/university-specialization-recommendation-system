"""Hybrid recommender that combines multiple recommendation techniques"""
from typing import List, Dict, Optional, Tuple
import numpy as np

from src.models.schemas import Faculty, MatchResult, SkillProficiency
from src.models.recommenders.base import BaseRecommender
from src.models.recommenders.matrix_factorization import SkillBasedRecommender
from src.matching.semantic_matcher import get_top_course_matches
from src.utils.data_access import load_all_courses

class HybridRecommender(BaseRecommender):
    """
    A hybrid recommender that combines matrix factorization with semantic matching.
    This approach can provide better recommendations by leveraging the strengths of both methods.
    """
    
    def __init__(self, nmf_weight: float = 0.7, semantic_weight: float = 0.3, n_components: int = 10):
        """
        Initialize the hybrid recommender.
        
        Args:
            nmf_weight: Weight given to NMF recommendations (0-1)
            semantic_weight: Weight given to semantic recommendations (0-1)
            n_components: Number of latent factors for NMF model
        """
        self.nmf_weight = nmf_weight
        self.semantic_weight = semantic_weight
        self.nmf_model = SkillBasedRecommender(n_components=n_components)
        self.is_trained = False
        
        # Normalize weights to sum to 1
        total_weight = nmf_weight + semantic_weight
        self.nmf_weight = nmf_weight / total_weight
        self.semantic_weight = semantic_weight / total_weight
    
    def train(self):
        """Train the component models"""
        # Train the NMF model
        self.nmf_model.train()
        self.is_trained = True
        return self
    
    def recommend_courses(self, faculty: Faculty, top_n: int = 10) -> List[MatchResult]:
        """
        Generate hybrid recommendations using both NMF and semantic matching.
        
        Args:
            faculty: Faculty object with skills
            top_n: Number of recommendations to return
            
        Returns:
            List of MatchResult objects
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        # Get recommendations from NMF model
        nmf_recommendations = self.nmf_model.recommend_courses(faculty, top_n=top_n*2)  # Get more to ensure enough options
        
        # Get recommendations from semantic matcher
        courses = load_all_courses()
        semantic_recommendations = get_top_course_matches(faculty, courses, top_n=top_n*2)
        
        # Create dictionaries to store scores by course code
        nmf_scores = {rec.course_code: rec.match_percentage for rec in nmf_recommendations}
        semantic_scores = {rec.course_code: rec.match_percentage for rec in semantic_recommendations}
        
        # Combine scores with weights
        combined_scores = {}
        all_course_codes = set(nmf_scores.keys()) | set(semantic_scores.keys())
        
        for course_code in all_course_codes:
            nmf_score = nmf_scores.get(course_code, 0) * self.nmf_weight
            semantic_score = semantic_scores.get(course_code, 0) * self.semantic_weight
            combined_scores[course_code] = nmf_score + semantic_score
        
        # Sort and get top N course codes by combined score
        top_course_codes = sorted(combined_scores.keys(), key=lambda x: combined_scores[x], reverse=True)[:top_n]
        
        # Create final result list
        results = []
        for course_code in top_course_codes:
            # Use the NMF result if available, otherwise use semantic result
            if course_code in nmf_scores:
                for rec in nmf_recommendations:
                    if rec.course_code == course_code:
                        # Update match percentage to combined score
                        result = MatchResult(
                            faculty_id=rec.faculty_id,
                            course_code=rec.course_code,
                            course_name=rec.course_name,
                            match_percentage=round(combined_scores[course_code], 2),
                            matched_skills=rec.matched_skills,
                            missing_skills=rec.missing_skills
                        )
                        results.append(result)
                        break
            else:
                for rec in semantic_recommendations:
                    if rec.course_code == course_code:
                        # Update match percentage to combined score
                        result = MatchResult(
                            faculty_id=rec.faculty_id,
                            course_code=rec.course_code,
                            course_name=rec.course_name,
                            match_percentage=round(combined_scores[course_code], 2),
                            matched_skills=rec.matched_skills,
                            missing_skills=rec.missing_skills
                        )
                        results.append(result)
                        break
        
        return results
    
    def save_model(self, path: str):
        """Save model to disk"""
        # For now, just save the NMF component
        self.nmf_model.save_model(path)
        return path
    
    def load_model(self, path: str):
        """Load model from disk"""
        # Load the NMF component
        self.nmf_model.load_model(path)
        self.is_trained = self.nmf_model.is_trained
        return self 