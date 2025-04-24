from src.models.schemas import Faculty, Course, SkillProficiency, ProficiencyLevel
from src.utils.data_access import load_all_courses, load_all_faculties
from src.matching.semantic_matcher import match_faculty_to_course, get_top_course_matches

def print_course_details(course: Course):
    """Print details of a course."""
    print(f"\nCourse: {course.code} - {course.name}")
    print(f"Description: {course.description}")
    print("Required Skills:")
    for skill, level in course.required_skills.items():
        print(f"  - {skill}: {level}")


def print_faculty_details(faculty: Faculty):
    """Print details of a faculty member."""
    print(f"\nFaculty: {faculty.name} (ID: {faculty.id})")
    print(f"Department: {faculty.department}")
    print("Skills:")
    for skill in faculty.skills:
        print(f"  - {skill.skill}: {skill.proficiency}")


def print_match_result(match_result):
    """Print details of a match result."""
    print(f"\nMatch Percentage: {match_result.match_percentage}%")
    if match_result.missing_skills:
        print("Missing or Underdeveloped Skills:")
        for skill in match_result.missing_skills:
            print(f"  - {skill.skill}: {skill.proficiency} (Needed)")
    else:
        print("No missing skills identified!")


def test_faculty_course_match():
    """Test the faculty-course matching functionality."""
    print("Loading data...")
    courses = load_all_courses()
    faculties = load_all_faculties()
    
    # For each faculty, get top 3 course matches
    for faculty in faculties:
        print("\n" + "="*50)
        print_faculty_details(faculty)
        print("\nTop 3 Course Matches:")
        
        matches = get_top_course_matches(faculty, courses, top_n=3)
        
        for i, match in enumerate(matches, 1):
            course = next(c for c in courses if c.code == match.course_code)
            print(f"\n{i}. {course.code} - {course.name}")
            print(f"   Match Percentage: {match.match_percentage}%")
            
            if match.missing_skills:
                print("   Skills to Develop:")
                for skill in match.missing_skills:
                    print(f"    - {skill.skill}: {skill.proficiency}")
    
    print("\n" + "="*50)


def test_custom_skills_match():
    """Test matching with custom skills input."""
    print("\nTesting custom skills matching...\n")
    
    # Create a custom skill set
    custom_skills = [
        SkillProficiency(skill="Python", proficiency=ProficiencyLevel.INTERMEDIATE),
        SkillProficiency(skill="SQL", proficiency=ProficiencyLevel.INTERMEDIATE),
        SkillProficiency(skill="Database Design", proficiency=ProficiencyLevel.BEGINNER),
        SkillProficiency(skill="File Systems", proficiency=ProficiencyLevel.ADVANCED)
    ]
    
    # Create a temporary faculty with these skills
    temp_faculty = Faculty(
        id="TEMP",
        name="Custom Faculty",
        department="Testing",
        skills=custom_skills
    )
    
    print("Custom Faculty Skills:")
    for skill in custom_skills:
        print(f"  - {skill.skill}: {skill.proficiency}")
    
    # Get course matches
    courses = load_all_courses()
    matches = get_top_course_matches(temp_faculty, courses)
    
    print("\nTop Course Matches:")
    for i, match in enumerate(matches, 1):
        course = next(c for c in courses if c.code == match.course_code)
        print(f"\n{i}. {course.code} - {course.name}")
        print(f"   Match Percentage: {match.match_percentage}%")
        
        if match.missing_skills:
            print("   Skills to Develop:")
            for skill in match.missing_skills:
                print(f"    - {skill.skill}: {skill.proficiency}")


if __name__ == "__main__":
    print("Testing Faculty-Course Matching System\n")
    print("="*50)
    
    # Test faculty-course matching
    test_faculty_course_match()
    
    # Test custom skills matching
    test_custom_skills_match() 