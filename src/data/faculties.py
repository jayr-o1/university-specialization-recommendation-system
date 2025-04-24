"""
Faculty data for the University Specialization Recommendation System.
This module provides access to faculty information including their skills.
"""

# Empty list of faculties - you mentioned you won't be needing this
FACULTIES = []

def get_all_faculties():
    """Get all faculties in dictionary format"""
    return FACULTIES

def get_faculty_by_id(faculty_id):
    """Get a faculty by ID"""
    for faculty in FACULTIES:
        if faculty["id"] == faculty_id:
            return faculty
    return None 