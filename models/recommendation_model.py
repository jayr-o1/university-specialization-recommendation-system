import json
import os
import numpy as np
from collections import defaultdict

class CourseRecommendationModel:
    """
    Simplified version of the recommendation model that only provides basic functionality
    needed for the faculty development system.
    """
    def __init__(self, course_skills_path):
        # Load course skills data
        with open(course_skills_path, 'r') as f:
            self.course_data = json.load(f)
        
        # Extract all unique skills across all courses
        self.all_skills = set()
        for course_name, course_info in self.course_data.items():
            for skill in course_info.get('required_skills', []):
                self.all_skills.add(skill)
        
        self.all_skills = sorted(list(self.all_skills))
    
    def recommend_courses(self, user_skills, top_n=5):
        """
        Basic course recommendation based on skill matching.
        This simplified version is only for compatibility.
        
        Args:
            user_skills: Dictionary mapping skill names to proficiency levels
            top_n: Number of recommendations to return
            
        Returns:
            List of course recommendations with match details
        """
        recommendations = []
        
        # Calculate match percentage for each course
        for course_name, course_info in self.course_data.items():
            required_skills = set(course_info.get('required_skills', []))
            
            if not required_skills:
                continue
                
            user_skill_names = set(user_skills.keys())
            
            # Calculate matched and missing skills
            matched_skills = required_skills.intersection(user_skill_names)
            missing_skills = required_skills - user_skill_names
            
            # Calculate match percentage
            match_percentage = 0
            if required_skills:
                match_percentage = (len(matched_skills) / len(required_skills)) * 100
            
            # Format matched skills with proficiency
            formatted_matched_skills = []
            for skill in matched_skills:
                proficiency = user_skills[skill]
                if isinstance(proficiency, dict):
                    prof_value = proficiency.get("proficiency", "Intermediate")
                    is_certified = proficiency.get("isBackedByCertificate", False)
                    cert_text = " (certified)" if is_certified else ""
                    formatted_matched_skills.append(f"{skill} ({prof_value}{cert_text})")
                else:
                    formatted_matched_skills.append(f"{skill} ({proficiency})")
            
            # Add to recommendations
            recommendations.append({
                'course_name': course_name,
                'match_percentage': match_percentage,
                'matched_skills': formatted_matched_skills,
                'missing_skills': list(missing_skills)
            })
        
        # Sort by match percentage (highest first)
        recommendations.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        return recommendations[:top_n]
    
    def find_similar_courses(self, course_name, top_n=5):
        """
        Find courses similar to the given course based on skill overlap.
        Simplified version for compatibility.
        
        Args:
            course_name: Name of the course to find similar courses for
            top_n: Number of similar courses to return
            
        Returns:
            List of similar courses with similarity scores
        """
        if course_name not in self.course_data:
            return []
            
        # Get skills for the target course
        target_course_skills = set(self.course_data[course_name].get('required_skills', []))
        
        if not target_course_skills:
            return []
            
        # Calculate similarity scores
        similar_courses = []
        for other_course, course_info in self.course_data.items():
            if other_course == course_name:
                continue
                
            other_course_skills = set(course_info.get('required_skills', []))
            
            if not other_course_skills:
                continue
                
            # Calculate Jaccard similarity
            intersection = len(target_course_skills.intersection(other_course_skills))
            union = len(target_course_skills.union(other_course_skills))
            
            similarity_score = 0
            if union > 0:
                similarity_score = (intersection / union) * 100
                
            similar_courses.append({
                'course_name': other_course,
                'similarity_score': similarity_score
            })
        
        # Sort by similarity score (highest first)
        similar_courses.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return similar_courses[:top_n] 