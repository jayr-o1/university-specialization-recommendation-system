"""
Course data for the University Specialization Recommendation System.
This module provides access to course information including skill requirements.
"""
import os
import json
from typing import List, Dict, Optional
from src.models.schemas import ProficiencyLevel, Course

# Mapping from string proficiency levels to enum values
PROFICIENCY_MAP = {
    "Beginner": ProficiencyLevel.BEGINNER,
    "Intermediate": ProficiencyLevel.INTERMEDIATE,
    "Advanced": ProficiencyLevel.ADVANCED,
    "Expert": ProficiencyLevel.EXPERT
}

def load_course_skills() -> Dict:
    """Load course skills from JSON file"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, 'course_skills.json')
    
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Course skills file not found at {json_path}")
        return {}

# Load course data
_course_data = load_course_skills()

# Convert to list format for compatibility with existing code
COURSES = []
for code, data in _course_data.items():
    required_skills = {}
    for skill, level in data.get('required_skills', {}).items():
        required_skills[skill] = PROFICIENCY_MAP.get(level, ProficiencyLevel.BEGINNER)
    
    COURSES.append({
        "code": code,
        "name": data.get('name', ''),
        "description": data.get('description', f"Course on {data.get('name', code)}"),
        "required_skills": required_skills
    })

def get_all_courses() -> List[Dict]:
    """Get all courses in dictionary format"""
    return COURSES

def get_course_by_code(code: str) -> Optional[Dict]:
    """Get a course by its code"""
    for course in COURSES:
        if course["code"] == code:
            return course
    return None

def get_course_as_schema(code: str) -> Optional[Course]:
    """Get a course by its code as a Course schema object"""
    course_dict = get_course_by_code(code)
    if not course_dict:
        return None
    
    return Course(
        code=course_dict["code"],
        name=course_dict["name"],
        description=course_dict["description"],
        required_skills=course_dict["required_skills"]
    )

def get_all_courses_as_schemas() -> List[Course]:
    """Get all courses as Course schema objects"""
    return [
        Course(
            code=course["code"],
            name=course["name"],
            description=course["description"],
            required_skills=course["required_skills"]
        )
        for course in COURSES
    ] 