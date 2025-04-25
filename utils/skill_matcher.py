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
    
    def get_recommendations(self, user_skills, limit=5):
        """
        Get course recommendations based on user skills.
        
        Args:
            user_skills: Dictionary of user skills and proficiency levels (e.g., {"Python": "Advanced"})
            limit: Maximum number of recommendations to return
            
        Returns:
            List of recommended courses with match details
        """
        if not user_skills:
            return []
        
        # Calculate match score for each course
        course_matches = []
        
        for course_code, course_info in self.course_data.items():
            required_skills = set(course_info["required_skills"])
            user_skill_set = set(user_skills.keys())
            
            # Calculate overlapping and missing skills
            matched_skills = required_skills.intersection(user_skill_set)
            missing_skills = required_skills - user_skill_set
            
            # Calculate match percentage
            match_percentage = len(matched_skills) / len(required_skills) * 100 if required_skills else 0
            
            course_matches.append({
                "course_code": course_code,
                "course_name": course_info["name"],
                "match_percentage": match_percentage,
                "matched_skills": list(matched_skills),
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
    
    # Example user skills
    user_skills = {
        "Python": "Advanced",
        "TensorFlow": "Intermediate",
        "PyTorch": "Intermediate",
        "Scikit-learn": "Intermediate",
        "NumPy": "Intermediate"
    }
    
    # Get and display recommendations
    recommendations = matcher.get_recommendations(user_skills)
    formatted_output = matcher.format_recommendations(recommendations)
    print(formatted_output) 