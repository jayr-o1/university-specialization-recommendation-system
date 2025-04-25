from src.models.schemas import Faculty, SkillProficiency, ProficiencyLevel
from src.utils.data_access import load_all_courses
from src.matching.semantic_matcher import get_top_course_matches

def test_with_custom_skills():
    """Test the recommender with specific skills."""
    print("\n" + "="*70)
    print("Testing University Specialization Recommender with Custom Skills")
    print("="*70)
    
    # Create a custom skill set based on user input
    custom_skills = [
        SkillProficiency(skill="MySQL", proficiency=ProficiencyLevel.INTERMEDIATE),
        SkillProficiency(skill="Database Design", proficiency=ProficiencyLevel.ADVANCED),
        SkillProficiency(skill="MSSQL", proficiency=ProficiencyLevel.INTERMEDIATE)
    ]
    
    # Create a temporary faculty with these skills
    temp_faculty = Faculty(
        id="USER",
        name="Custom User",
        department="Testing",
        skills=custom_skills
    )
    
    print("\nYour Skills:")
    for skill in custom_skills:
        print(f"  - {skill.skill}: {skill.proficiency}")
    
    # Get course matches
    courses = load_all_courses()
    matches = get_top_course_matches(temp_faculty, courses, top_n=5)
    
    print("\nTop 5 Course Matches:")
    for i, match in enumerate(matches, 1):
        course = next(c for c in courses if c.code == match.course_code)
        print(f"\n{i}. {course.code} - {course.name}")
        print(f"   Match Percentage: {match.match_percentage:.1f}%")
        print(f"   Description: {course.description}")
        
        if match.missing_skills:
            print("   Skills to Develop:")
            for skill in match.missing_skills:
                print(f"    - {skill.skill}: {skill.proficiency}")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    test_with_custom_skills() 