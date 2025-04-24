from typing import Dict, List, Optional
from models.schemas import Faculty, Course, SkillProficiency
from data.courses import COURSES
from data.faculties import FACULTIES


def load_all_courses() -> List[Course]:
    """Load all courses from data source."""
    return [Course(**course) for course in COURSES]


def get_course_by_code(code: str) -> Optional[Course]:
    """Get a course by its code."""
    for course_data in COURSES:
        if course_data["code"] == code:
            return Course(**course_data)
    return None


def load_all_faculties() -> List[Faculty]:
    """Load all faculty members from data source."""
    return [Faculty(**faculty) for faculty in FACULTIES]


def get_faculty_by_id(faculty_id: str) -> Optional[Faculty]:
    """Get a faculty member by ID."""
    for faculty_data in FACULTIES:
        if faculty_data["id"] == faculty_id:
            return Faculty(**faculty_data)
    return None


def update_faculty_skills(faculty_id: str, skills: List[SkillProficiency]) -> Optional[Faculty]:
    """Update a faculty member's skills."""
    for i, faculty_data in enumerate(FACULTIES):
        if faculty_data["id"] == faculty_id:
            # Update skills
            FACULTIES[i]["skills"] = [skill.dict() for skill in skills]
            return Faculty(**FACULTIES[i])
    return None 