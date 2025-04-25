"""
User preferences module to customize the recommendation system.
"""
from typing import Dict, List, Optional
from src.models.schemas import Faculty, Course, MatchResult

class UserPreferences:
    """Class to store and apply user preferences for recommendations."""
    
    def __init__(self):
        # Weight factors for different categories (default: all equal)
        self.category_weights = {
            "Database": 1.0,
            "Programming": 1.0,
            "Web Development": 1.0,
            "Cloud Computing": 1.0,
            "Data Science": 1.0,
            "Security": 1.0,
            "Networking": 1.0,
            "Project Management": 1.0,
            "Design": 1.0,
            "Other": 1.0
        }
        
        # Preferred courses (will be boosted in rankings)
        self.preferred_courses: List[str] = []
        
        # Excluded courses (will be filtered out)
        self.excluded_courses: List[str] = []
        
        # Minimum match percentage to include in results
        self.min_match_percentage: float = 0.0
    
    def set_category_preference(self, category: str, weight: float) -> None:
        """Set preference weight for a category."""
        if category in self.category_weights:
            self.category_weights[category] = max(0.0, min(weight, 2.0))  # Limit between 0 and 2
    
    def add_preferred_course(self, course_code: str) -> None:
        """Add a course to the preferred list."""
        if course_code not in self.preferred_courses:
            self.preferred_courses.append(course_code)
    
    def add_excluded_course(self, course_code: str) -> None:
        """Add a course to the excluded list."""
        if course_code not in self.excluded_courses:
            self.excluded_courses.append(course_code)
    
    def set_min_match_percentage(self, percentage: float) -> None:
        """Set minimum match percentage threshold."""
        self.min_match_percentage = max(0.0, min(percentage, 100.0))  # Limit between 0 and 100
    
    def apply_preferences(self, matches: List[MatchResult], courses: List[Course]) -> List[MatchResult]:
        """Apply user preferences to match results."""
        from src.utils.skill_taxonomy import get_category
        
        # Make a deep copy of matches to avoid modifying originals
        adjusted_matches = []
        
        for match in matches:
            # Skip excluded courses
            if match.course_code in self.excluded_courses:
                continue
            
            # Skip courses below minimum threshold
            if match.match_percentage < self.min_match_percentage:
                continue
            
            # Find the course
            course = next((c for c in courses if c.code == match.course_code), None)
            if not course:
                continue
                
            # Create a copy of the match
            adjusted_match = MatchResult(
                faculty_id=match.faculty_id,
                course_code=match.course_code,
                course_name=match.course_name,
                match_percentage=match.match_percentage,
                matched_skills=match.matched_skills,
                missing_skills=match.missing_skills
            )
            
            # Determine course categories based on required skills
            course_categories = set()
            for skill_name in course.required_skills.keys():
                category = get_category(skill_name)
                if category != "Other":
                    course_categories.add(category)
            
            # Apply category weight boosts
            if course_categories:
                # Get the average category weight for this course
                total_weight = sum(self.category_weights.get(cat, 1.0) for cat in course_categories)
                avg_weight = total_weight / len(course_categories)
                
                # Only apply boost if average weight > 1.0
                if avg_weight > 1.0:
                    boost_factor = avg_weight * 0.1  # 10% boost per weight point
                    adjusted_match.match_percentage = min(99.0, match.match_percentage * (1.0 + boost_factor))
            
            # Boost preferred courses
            if match.course_code in self.preferred_courses:
                # Boost by 10%
                adjusted_match.match_percentage = min(99.0, adjusted_match.match_percentage * 1.1)
            
            adjusted_matches.append(adjusted_match)
        
        # Sort by adjusted match percentage
        adjusted_matches.sort(key=lambda x: x.match_percentage, reverse=True)
        
        return adjusted_matches

# Create a default instance that can be imported and customized
default_preferences = UserPreferences()

# Example: Boost database courses
default_preferences.set_category_preference("Database", 1.5) 