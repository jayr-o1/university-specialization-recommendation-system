import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter

class CourseRecommendationModel:
    def __init__(self, course_skills_path):
        # Load course skills data
        with open(course_skills_path, 'r') as f:
            self.course_data = json.load(f)
        
        # Extract all unique skills across all courses
        self.all_skills = set()
        for course_name, course_info in self.course_data.items():
            for skill in course_info['required_skills']:
                self.all_skills.add(skill)
        
        self.all_skills = sorted(list(self.all_skills))
        self.skill_to_idx = {skill: idx for idx, skill in enumerate(self.all_skills)}
        
        # Create course vectors
        self.course_vectors = {}
        for course_name, course_info in self.course_data.items():
            vector = np.zeros(len(self.all_skills))
            for skill in course_info['required_skills']:
                vector[self.skill_to_idx[skill]] = 1
            self.course_vectors[course_name] = vector
    
    def _convert_proficiency_to_weight(self, proficiency):
        """Convert proficiency level to numerical weight"""
        proficiency = proficiency.lower()
        if proficiency == "beginner":
            return 0.25
        elif proficiency == "intermediate":
            return 0.5
        elif proficiency == "advanced":
            return 0.75
        elif proficiency == "expert":
            return 1.0
        else:
            return 0.5  # Default to intermediate
    
    def create_user_vector(self, user_skills):
        """
        Create user skill vector from a dictionary of skills and proficiency levels
        Example: {"Python": "Advanced", "Database Design": "Intermediate"}
        """
        user_vector = np.zeros(len(self.all_skills))
        
        for skill, proficiency in user_skills.items():
            if skill in self.skill_to_idx:
                weight = self._convert_proficiency_to_weight(proficiency)
                user_vector[self.skill_to_idx[skill]] = weight
        
        return user_vector
    
    def recommend_courses(self, user_skills, top_n=5):
        """
        Recommend courses based on user skills and proficiency levels
        
        Args:
            user_skills: Dict of skill-proficiency pairs (e.g., {"Python": "Advanced"})
            top_n: Number of recommendations to return
            
        Returns:
            List of dictionaries containing recommended courses with match details
        """
        # Create user vector
        user_vector = self.create_user_vector(user_skills)
        
        # Calculate similarity scores for each course
        similarity_scores = {}
        for course_name, course_vector in self.course_vectors.items():
            # Skip courses with no matching skills to avoid divide by zero
            if np.sum(course_vector) == 0 or np.sum(user_vector) == 0:
                similarity_scores[course_name] = 0
                continue
                
            # Calculate cosine similarity between user skills and course requirements
            similarity = cosine_similarity([user_vector], [course_vector])[0][0]
            similarity_scores[course_name] = similarity
        
        # Sort courses by similarity score
        sorted_courses = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Prepare detailed recommendations
        recommendations = []
        for course_name, score in sorted_courses[:top_n]:
            required_skills = set(self.course_data[course_name]['required_skills'])
            
            # Find matched skills (skills the user has that match course requirements)
            matched_skills = []
            for skill in user_skills:
                if skill in required_skills:
                    matched_skills.append(f"{skill} ({user_skills[skill]})")
            
            # Find missing skills (skills required by the course that the user doesn't have)
            user_skill_set = set(user_skills.keys())
            missing_skills = required_skills - user_skill_set
            
            # Calculate match percentage (0-100%)
            match_percentage = int(score * 100)
            
            recommendations.append({
                'course_code': course_name,  # Use course_name as course_code for backward compatibility
                'course_name': course_name,
                'match_percentage': match_percentage,
                'matched_skills': matched_skills,
                'missing_skills': list(missing_skills)
            })
        
        return recommendations
    
    def find_similar_courses(self, course_name, top_n=5):
        """Find courses similar to a given course based on skill overlap"""
        if course_name not in self.course_vectors:
            return []
        
        target_vector = self.course_vectors[course_name]
        
        # Calculate similarity with all other courses
        similarity_scores = {}
        for name, vector in self.course_vectors.items():
            if name != course_name:  # Skip comparing with itself
                similarity = cosine_similarity([target_vector], [vector])[0][0]
                similarity_scores[name] = similarity
        
        # Sort by similarity
        sorted_courses = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Prepare result
        similar_courses = []
        for similar_name, score in sorted_courses[:top_n]:
            similar_courses.append({
                'course_code': similar_name,  # Use course_name as course_code for backward compatibility
                'course_name': similar_name,
                'similarity_score': int(score * 100)
            })
        
        return similar_courses 