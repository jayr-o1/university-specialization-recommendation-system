import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Union, Optional
from sklearn.decomposition import NMF
from sklearn.metrics.pairwise import cosine_similarity
import os

# Updated imports with proper package paths
from src.models.schemas import Faculty, Course, ProficiencyLevel, SkillProficiency, MatchResult
from src.data.courses import COURSES  # Import course data to access required skills

class SkillBasedRecommender:
    """
    A skill-based recommender system using matrix factorization techniques.
    This model creates latent representations of skills and courses for better matching.
    """
    
    def __init__(self, n_components: int = 10, random_state: int = 42):
        self.n_components = n_components
        self.random_state = random_state
        self.model = NMF(n_components=n_components, init='random', random_state=random_state, max_iter=500)
        self.skill_course_matrix = None
        self.course_codes = None
        self.skill_names = None
        self.is_trained = False
        
    def load_data(self, skill_course_matrix_path: str):
        """Load skill-course matrix from CSV file"""
        # Load the skill-course matrix
        df = pd.read_csv(skill_course_matrix_path)
        
        # Save course codes
        self.course_codes = df['course_code'].values
        
        # Remove the course_code column and convert to matrix
        skill_df = df.drop(columns=['course_code'])
        self.skill_names = skill_df.columns.tolist()
        self.skill_course_matrix = skill_df.values
        
        return self
    
    def train(self):
        """Train the matrix factorization model"""
        if self.skill_course_matrix is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        # Train the NMF model to get latent factors
        self.W = self.model.fit_transform(self.skill_course_matrix)  # Course-factor matrix
        self.H = self.model.components_  # Factor-skill matrix
        
        # Course latent factors (how courses relate to latent factors)
        self.course_factors = self.W
        
        # Calculate similarities between courses
        self.course_similarities = cosine_similarity(self.course_factors)
        
        self.is_trained = True
        return self
    
    def get_skill_importance(self) -> pd.DataFrame:
        """Get the importance of each skill across latent factors"""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        # Create a DataFrame with skill importance for each factor
        skill_importance = pd.DataFrame(self.H.T, columns=[f"Factor_{i}" for i in range(self.n_components)])
        skill_importance.index = self.skill_names
        
        return skill_importance
    
    def get_course_factors(self) -> pd.DataFrame:
        """Get the factor representation of each course"""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        # Create a DataFrame with course factors
        course_factors_df = pd.DataFrame(self.course_factors,
                                         columns=[f"Factor_{i}" for i in range(self.n_components)])
        course_factors_df['course_code'] = self.course_codes
        
        return course_factors_df
    
    def get_similar_courses(self, course_code: str, top_n: int = 10) -> List[Tuple[str, float]]:
        """Get the most similar courses to a given course"""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        # Find the index of the course
        try:
            course_idx = np.where(self.course_codes == course_code)[0][0]
        except IndexError:
            raise ValueError(f"Course code {course_code} not found in the dataset.")
        
        # Get similarities
        similarities = self.course_similarities[course_idx]
        
        # Get the indices of the top N similar courses (excluding the course itself)
        similar_indices = np.argsort(similarities)[::-1][1:top_n+1]
        
        # Return course codes and similarity scores
        similar_courses = [(self.course_codes[idx], similarities[idx]) for idx in similar_indices]
        
        return similar_courses
    
    def calculate_faculty_skill_vector(self, faculty: Faculty) -> np.ndarray:
        """
        Convert faculty skills to a vector in the same space as the course skills.
        This creates a representation of faculty skills that can be compared with courses.
        """
        # Initialize an empty skill vector
        skill_vector = np.zeros(len(self.skill_names))
        
        # Fill in the skill proficiencies
        for faculty_skill in faculty.skills:
            # Find the index of the skill in our known skills
            try:
                skill_idx = self.skill_names.index(faculty_skill.skill)
                
                # Convert proficiency level to numeric value (same scale as in dataset.py)
                proficiency_value = {
                    ProficiencyLevel.BEGINNER: 1,
                    ProficiencyLevel.INTERMEDIATE: 2, 
                    ProficiencyLevel.ADVANCED: 3,
                    ProficiencyLevel.EXPERT: 4
                }[faculty_skill.proficiency]
                
                # Set the skill value
                skill_vector[skill_idx] = proficiency_value
            except ValueError:
                # Skill not in our dataset, ignore for now
                pass
        
        return skill_vector
    
    def recommend_courses(self, faculty: Faculty, top_n: int = 10) -> List[MatchResult]:
        """
        Recommend courses for a faculty member based on their skills.
        Returns a list of MatchResult objects with match percentages and skill details.
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        # Calculate the faculty skill vector
        faculty_skill_vector = self.calculate_faculty_skill_vector(faculty)
        
        # Project the faculty skill vector into the latent factor space
        faculty_factor_vector = self.model.transform([faculty_skill_vector])[0]
        
        # Calculate similarity to all courses
        similarities = cosine_similarity([faculty_factor_vector], self.course_factors)[0]
        
        # Scale similarities to percentages (0-100)
        match_percentages = similarities * 100
        
        # Get top N course indices
        top_indices = np.argsort(match_percentages)[::-1][:top_n]
        
        # Create match results with detailed skill information
        results = []
        for idx in top_indices:
            course_code = self.course_codes[idx]
            match_percentage = round(match_percentages[idx], 2)
            
            # Find the course data to get required skills
            course_data = None
            for course in COURSES:
                if course["code"] == course_code:
                    course_data = course
                    break
            
            # If we found the course data, determine matched and missing skills
            missing_skills = []
            matched_skills = []
            if course_data:
                # Check each required skill
                for skill_name, required_level in course_data["required_skills"].items():
                    # Find if faculty has this skill
                    faculty_has_skill = False
                    faculty_skill_level = None
                    
                    for faculty_skill in faculty.skills:
                        if faculty_skill.skill.lower() == skill_name.lower():
                            faculty_has_skill = True
                            faculty_skill_level = faculty_skill.proficiency
                            break
                    
                    # If faculty doesn't have the skill or level is too low, add to missing skills
                    if not faculty_has_skill:
                        missing_skills.append(
                            SkillProficiency(
                                skill=skill_name,
                                proficiency=required_level
                            )
                        )
                    else:
                        # Convert enum levels to numeric for comparison
                        faculty_level_value = {
                            ProficiencyLevel.BEGINNER: 1,
                            ProficiencyLevel.INTERMEDIATE: 2,
                            ProficiencyLevel.ADVANCED: 3,
                            ProficiencyLevel.EXPERT: 4
                        }[faculty_skill_level]
                        
                        required_level_value = {
                            ProficiencyLevel.BEGINNER: 1,
                            ProficiencyLevel.INTERMEDIATE: 2,
                            ProficiencyLevel.ADVANCED: 3,
                            ProficiencyLevel.EXPERT: 4
                        }[required_level]
                        
                        # If faculty level is lower than required, add to missing skills
                        if faculty_level_value < required_level_value:
                            missing_skills.append(
                                SkillProficiency(
                                    skill=skill_name,
                                    proficiency=required_level
                                )
                            )
                        else:
                            # Add to matched skills if proficiency is sufficient
                            matched_skills.append(
                                SkillProficiency(
                                    skill=skill_name,
                                    proficiency=faculty_skill_level
                                )
                            )
            
            # Create the match result
            result = MatchResult(
                faculty_id=getattr(faculty, 'id', None),
                course_code=course_code,
                course_name=course_data.get("name") if course_data else None,
                match_percentage=match_percentage,
                matched_skills=matched_skills,
                missing_skills=missing_skills
            )
            results.append(result)
        
        return results
    
    def save_model(self, model_path: str = None):
        """Save the model components for later use"""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        if model_path is None:
            # Default location in the models directory
            models_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(models_dir, "recommender_model.npz")
        
        # Ensure course_codes is saved as object array to preserve strings
        np.savez(
            model_path,
            W=self.W,
            H=self.H,
            course_codes=np.array(self.course_codes, dtype=object),
            skill_names=np.array(self.skill_names, dtype=object),
            n_components=self.n_components,
            random_state=self.random_state
        )
        
        return model_path
    
    def load_model(self, model_path: str):
        """Load a previously trained model"""
        # Load the model components
        with np.load(model_path, allow_pickle=True) as data:
            self.W = data['W']
            self.H = data['H']
            self.course_codes = data['course_codes']
            self.skill_names = data['skill_names'].tolist()
            
            # Update n_components if available
            if 'n_components' in data:
                self.n_components = int(data['n_components'])
            else:
                # Infer from the shape of H
                self.n_components = self.H.shape[0]
        
        # Recreate the NMF model with the correct n_components
        self.model = NMF(n_components=self.n_components, init='random', random_state=self.random_state, max_iter=500)
        
        # Reconstruct the model state
        self.course_factors = self.W
        self.course_similarities = cosine_similarity(self.course_factors)
        
        # Create a fitted NMF model (needed for transform method)
        self.model.components_ = self.H
        self.model.n_components_ = self.H.shape[0]
        self.model.n_features_in_ = self.H.shape[1]
        
        self.is_trained = True
        
        return self 