import json
import os
from collections import defaultdict
from typing import Dict, List, Optional
from .skill_hierarchy import SkillHierarchy

class SkillMatcher:
    """
    A utility for matching user skills to courses based on required skills.
    This simplified version focuses solely on skill matching without additional analysis.
    """
    
    def __init__(self, course_data_path: str, hierarchy_path: Optional[str] = None):
        """Initialize the skill matcher with course data and skill hierarchy.
        
        Args:
            course_data_path: Path to the course skills data file
            hierarchy_path: Optional path to custom skill hierarchy data
        """
        self.course_data = self._load_course_data(course_data_path)
        self.hierarchy = SkillHierarchy(hierarchy_path)
        
    def _load_course_data(self, course_data_path: str) -> Dict:
        """Load course data from JSON file."""
        try:
            with open(course_data_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading course data: {str(e)}")
            return {}
    
    def _get_skill_data(self, skill_info):
        """
        Extract proficiency and is_backed_by_certificate status from a skill
        
        Args:
            skill_info: Either a string (old format) or dict (new format)
            
        Returns:
            Tuple of (proficiency, is_backed_by_certificate)
        """
        if isinstance(skill_info, dict):
            return skill_info.get("proficiency", "Intermediate"), skill_info.get("isBackedByCertificate", False)
        return skill_info, False  # Old format: string proficiency, not backed
    
    def get_recommendations(self, user_skills: Dict, limit: int = 5) -> List[Dict]:
        """Get course recommendations based on user skills with enhanced matching.
        
        Args:
            user_skills: Dictionary of user skills with proficiency and certification info
            limit: Maximum number of recommendations to return
            
        Returns:
            List of recommended courses with match details
        """
        if not user_skills:
            return []
        
        course_matches = []
        user_skill_set = set(user_skills.keys())
        
        for course_name, course_info in self.course_data.items():
            required_skills = set(course_info.get('required_skills', []))
            
            if not required_skills:
                continue
            
            # Calculate enhanced match scores
            match_scores = []
            matched_skills = []
            missing_skills = []
            
            for req_skill in required_skills:
                best_match_score = 0
                best_matching_skill = None
                
                # Check each user skill against the required skill
                for user_skill in user_skill_set:
                    match_score = self.hierarchy.calculate_skill_match_score(user_skill, req_skill)
                    
                    if match_score > best_match_score:
                        best_match_score = match_score
                        best_matching_skill = user_skill
                
                if best_match_score > 0:
                    # Apply certification weight if available
                    if isinstance(user_skills[best_matching_skill], dict):
                        is_certified = user_skills[best_matching_skill].get('isBackedByCertificate', False)
                        cert_weight = self.hierarchy.calculate_certification_weight(best_matching_skill, is_certified)
                        best_match_score *= cert_weight
                    
                    match_scores.append(best_match_score)
                    matched_skills.append(best_matching_skill)
                else:
                    missing_skills.append(req_skill)
            
            # Calculate overall match percentage
            if match_scores:
                match_percentage = (sum(match_scores) / len(required_skills)) * 100
                
                # Format matched skills with proficiency and certification info
                formatted_matched_skills = []
                for skill in matched_skills:
                    skill_data = user_skills[skill]
                    if isinstance(skill_data, dict):
                        prof = skill_data.get('proficiency', 'Intermediate')
                        is_cert = skill_data.get('isBackedByCertificate', False)
                        cert_text = " (certified)" if is_cert else ""
                        formatted_matched_skills.append(f"{skill} ({prof}{cert_text})")
                    else:
                        formatted_matched_skills.append(f"{skill} ({skill_data})")
                
                course_matches.append({
                    'course_name': course_name,
                    'match_percentage': match_percentage,
                    'matched_skills': formatted_matched_skills,
                    'missing_skills': missing_skills,
                    'skill_match_details': {
                        'match_scores': match_scores,
                        'difficulty_level': max(self.hierarchy.get_skill_difficulty(skill) 
                                             for skill in required_skills)
                    }
                })
        
        # Sort by match percentage and return top matches
        course_matches.sort(key=lambda x: x['match_percentage'], reverse=True)
        return course_matches[:limit]
    
    def find_similar_courses(self, course_name: str, top_n: int = 5) -> List[Dict]:
        """Find courses similar to a given course using enhanced skill relationships."""
        if course_name not in self.course_data:
            return []
        
        target_course_skills = set(self.course_data[course_name].get('required_skills', []))
        
        if not target_course_skills:
            return []
        
        similar_courses = []
        for other_course, course_info in self.course_data.items():
            if other_course == course_name:
                continue
            
            other_course_skills = set(course_info.get('required_skills', []))
            
            if not other_course_skills:
                continue
            
            # Calculate enhanced similarity score using skill relationships
            total_score = 0
            comparisons = 0
            
            for target_skill in target_course_skills:
                for other_skill in other_course_skills:
                    match_score = self.hierarchy.calculate_skill_match_score(target_skill, other_skill)
                    total_score += match_score
                    comparisons += 1
            
            if comparisons > 0:
                similarity_score = (total_score / comparisons) * 100
                similar_courses.append({
                    'course_name': other_course,
                    'similarity_score': similarity_score,
                    'common_skills': list(target_course_skills & other_course_skills),
                    'related_skills': list(target_course_skills ^ other_course_skills)
                })
        
        similar_courses.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similar_courses[:top_n]
    
    def format_recommendations(self, recommendations):
        """
        Format recommendations into a readable string.
        
        Args:
            recommendations: List of recommendation dictionaries from get_recommendations()
            
        Returns:
            Formatted string with recommendation details
        """
        if not recommendations:
            return "No matching courses found for your skills."
        
        output = "Course Recommendations Based on Your Skills\n"
        output += "=" * 80 + "\n\n"
        
        for i, rec in enumerate(recommendations, 1):
            output += f"{i}. {rec['course_name']} ({rec['match_percentage']:.0f}% match)\n"
            
            # Matched skills
            if rec['matched_skills']:
                output += "   Matched skills:\n"
                for skill in rec['matched_skills']:
                    output += f"   - {skill}\n"
            
            # Missing skills
            if rec['missing_skills']:
                output += "   Missing skills:\n"
                for skill in rec['missing_skills']:
                    output += f"   - {skill}\n"
            
            output += "\n"
        
        return output

# Example usage
if __name__ == "__main__":
    matcher = SkillMatcher("data/course_skills_updated.json")
    
    # Example user skills (new format with isBackedByCertificate flag)
    user_skills = {
        "Python": {"proficiency": "Advanced", "isBackedByCertificate": True},
        "TensorFlow": {"proficiency": "Intermediate", "isBackedByCertificate": False},
        "PyTorch": {"proficiency": "Intermediate", "isBackedByCertificate": True},
        "Scikit-learn": {"proficiency": "Intermediate", "isBackedByCertificate": False},
        "NumPy": {"proficiency": "Intermediate", "isBackedByCertificate": False}
    }
    
    # Get and display recommendations
    recommendations = matcher.get_recommendations(user_skills)
    formatted_output = matcher.format_recommendations(recommendations)
    print(formatted_output) 