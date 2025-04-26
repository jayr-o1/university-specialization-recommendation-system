import json
import os
from collections import defaultdict

class SkillMatcher:
    """
    A utility for matching user skills to courses based on required skills.
    This simplified version focuses solely on skill matching without additional analysis.
    """
    
    def __init__(self, course_data_path):
        """Initialize with path to course skills data file."""
        self.course_data_path = course_data_path
        self.course_data = self._load_course_data()
        
    def _load_course_data(self):
        """Load course data from JSON file."""
        try:
            with open(self.course_data_path, 'r') as f:
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
    
    def get_recommendations(self, user_skills, limit=5):
        """
        Get course recommendations based on user skills.
        
        Args:
            user_skills: Dictionary of user skills with proficiency and isBackedByCertificate flag
                         Either old format {"Python": "Advanced"} 
                         or new format {"Python": {"proficiency": "Advanced", "isBackedByCertificate": true}}
            limit: Maximum number of recommendations to return
            
        Returns:
            List of recommended courses with match details
        """
        if not user_skills:
            return []
        
        # Calculate match score for each course
        course_matches = []
        
        user_skill_set = set(user_skills.keys())
        
        # Track certified skills for weighting
        certified_skills = {skill for skill, data in user_skills.items() 
                        if isinstance(data, dict) and data.get("isBackedByCertificate", False)}
        
        for course_code, course_info in self.course_data.items():
            required_skills = set(course_info["required_skills"])
            
            # Calculate overlapping and missing skills
            matched_skills = required_skills.intersection(user_skill_set)
            missing_skills = required_skills - user_skill_set
            
            # Calculate match percentage with higher weight for certified skills
            if required_skills:
                # Base match is the proportion of matched skills
                base_match = len(matched_skills) / len(required_skills)
                
                # Apply a boost for each certified skill that's matched
                certified_match_count = len(matched_skills.intersection(certified_skills))
                certified_boost = certified_match_count * 0.1  # 10% boost per certified skill
                
                # Calculate final match percentage (capped at 100%)
                match_percentage = min(100, (base_match + certified_boost) * 100)
            else:
                match_percentage = 0
            
            # Format matched skills with proficiency and certificate status
            formatted_matched_skills = []
            for skill in matched_skills:
                proficiency, is_backed_by_certificate = self._get_skill_data(user_skills[skill])
                certificate_str = " (certified)" if is_backed_by_certificate else ""
                formatted_matched_skills.append(f"{skill} ({proficiency}{certificate_str})")
            
            course_matches.append({
                "course_code": course_code,
                "course_name": course_info.get("name", course_code),
                "match_percentage": match_percentage,
                "matched_skills": formatted_matched_skills,
                "missing_skills": list(missing_skills)
            })
        
        # Sort by match percentage (highest first)
        course_matches.sort(key=lambda x: x["match_percentage"], reverse=True)
        
        # Return top matches
        return course_matches[:limit]
    
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
            output += f"{i}. {rec['course_code']} - {rec['course_name']} ({rec['match_percentage']:.0f}% match)\n"
            
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