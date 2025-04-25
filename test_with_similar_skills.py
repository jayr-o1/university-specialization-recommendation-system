from src.models.schemas import Faculty, SkillProficiency, ProficiencyLevel
from src.utils.data_access import load_all_courses
from src.matching.semantic_matcher import get_top_course_matches, match_faculty_to_course

def test_with_similar_skills():
    """Test the recommender with enhanced similarity matching."""
    print("\n" + "="*70)
    print("Testing University Specialization Recommender With Enhanced Similarity")
    print("="*70)
    
    # Create a custom skill set with primary skills
    primary_skills = [
        SkillProficiency(skill="MySQL", proficiency=ProficiencyLevel.INTERMEDIATE),
        SkillProficiency(skill="Database Design", proficiency=ProficiencyLevel.ADVANCED),
        SkillProficiency(skill="MSSQL", proficiency=ProficiencyLevel.INTERMEDIATE)
    ]
    
    # Add related skills to enhance matching
    # These are skills that are semantically related to your primary skills
    related_skills = [
        SkillProficiency(skill="SQL", proficiency=ProficiencyLevel.INTERMEDIATE),
        SkillProficiency(skill="Relational Database", proficiency=ProficiencyLevel.INTERMEDIATE),
        SkillProficiency(skill="Database Management", proficiency=ProficiencyLevel.INTERMEDIATE)
    ]
    
    all_skills = primary_skills + related_skills
    
    # Create a temporary faculty with these skills
    temp_faculty = Faculty(
        id="USER",
        name="Custom User",
        department="Testing",
        skills=all_skills
    )
    
    print("\nYour Primary Skills:")
    for skill in primary_skills:
        print(f"  - {skill.skill}: {skill.proficiency}")
    
    print("\nAdded Related Skills:")
    for skill in related_skills:
        print(f"  - {skill.skill}: {skill.proficiency}")
    
    # Get course matches
    courses = load_all_courses()
    
    # Get specific course match for IMDBSYS31
    imdbsys31_course = next((c for c in courses if c.code == "IT-IMDBSYS31"), None)
    imdbsys32_course = next((c for c in courses if c.code == "IT-IMDBSYS32"), None)
    
    if imdbsys31_course:
        match_result = match_faculty_to_course(temp_faculty, imdbsys31_course)
        print(f"\nMatch with IT-IMDBSYS31 - Information Management (DB Sys.1):")
        print(f"  Match Percentage: {match_result.match_percentage:.1f}%")
        if match_result.missing_skills:
            print("  Skills to Develop:")
            for skill in match_result.missing_skills:
                print(f"    - {skill.skill}: {skill.proficiency}")
    
    if imdbsys32_course:
        match_result = match_faculty_to_course(temp_faculty, imdbsys32_course)
        print(f"\nMatch with IT-IMDBSYS32 - Information Management (DB Sys.2):")
        print(f"  Match Percentage: {match_result.match_percentage:.1f}%")
        if match_result.missing_skills:
            print("  Skills to Develop:")
            for skill in match_result.missing_skills:
                print(f"    - {skill.skill}: {skill.proficiency}")
    
    # Get top 10 matches overall
    matches = get_top_course_matches(temp_faculty, courses, top_n=10)
    
    print("\nTop 10 Course Matches with Enhanced Skills:")
    for i, match in enumerate(matches, 1):
        course = next(c for c in courses if c.code == match.course_code)
        print(f"\n{i}. {course.code} - {course.name}")
        print(f"   Match Percentage: {match.match_percentage:.1f}%")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    test_with_similar_skills() 