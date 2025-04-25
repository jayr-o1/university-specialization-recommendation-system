"""
Test script for the enhanced recommendation system with skill taxonomy.
"""
from src.models.schemas import Faculty, SkillProficiency, ProficiencyLevel
from src.utils.data_access import load_all_courses
from src.matching.enhanced_matcher import (
    get_top_course_matches_enhanced, 
    match_faculty_to_course_enhanced,
    enhance_faculty_skills
)

def test_enhanced_recommendations():
    """Test the enhanced recommendation system."""
    print("\n" + "="*80)
    print("TESTING ENHANCED RECOMMENDATION SYSTEM WITH SKILL TAXONOMY")
    print("="*80)
    
    # Create a custom skill set with your skills
    primary_skills = [
        SkillProficiency(skill="MySQL", proficiency=ProficiencyLevel.INTERMEDIATE),
        SkillProficiency(skill="Database Design", proficiency=ProficiencyLevel.ADVANCED),
        SkillProficiency(skill="MSSQL", proficiency=ProficiencyLevel.INTERMEDIATE)
    ]
    
    # Create a faculty with these skills
    faculty = Faculty(
        id="USER",
        name="Custom User",
        department="Testing",
        skills=primary_skills
    )
    
    # Get enhanced faculty with inferred skills
    enhanced_faculty = enhance_faculty_skills(faculty)
    
    print("\nYour Primary Skills:")
    for skill in primary_skills:
        print(f"  - {skill.skill}: {skill.proficiency}")
    
    print("\nAutomatically Inferred Skills:")
    inferred_skills = [s for s in enhanced_faculty.skills if s not in faculty.skills]
    for skill in inferred_skills:
        print(f"  - {skill.skill}: {skill.proficiency}")
    
    # Get all courses
    courses = load_all_courses()
    
    # Get specific course matches for IMDBSYS31 and IMDBSYS32
    imdbsys31_course = next((c for c in courses if c.code == "IT-IMDBSYS31"), None)
    imdbsys32_course = next((c for c in courses if c.code == "IT-IMDBSYS32"), None)
    
    if imdbsys31_course:
        match_result = match_faculty_to_course_enhanced(faculty, imdbsys31_course)
        print(f"\nEnhanced Match with IT-IMDBSYS31 - Information Management (DB Sys.1):")
        print(f"  Match Percentage: {match_result.match_percentage:.1f}%")
        if match_result.missing_skills:
            print("  Skills to Develop:")
            for skill in match_result.missing_skills:
                print(f"    - {skill.skill}: {skill.proficiency}")
    
    if imdbsys32_course:
        match_result = match_faculty_to_course_enhanced(faculty, imdbsys32_course)
        print(f"\nEnhanced Match with IT-IMDBSYS32 - Information Management (DB Sys.2):")
        print(f"  Match Percentage: {match_result.match_percentage:.1f}%")
        if match_result.missing_skills:
            print("  Skills to Develop:")
            for skill in match_result.missing_skills:
                print(f"    - {skill.skill}: {skill.proficiency}")
    
    # Get top matches overall
    matches = get_top_course_matches_enhanced(faculty, courses, top_n=15)
    
    print("\nTop 15 Course Matches with Enhanced Recommendation System:")
    for i, match in enumerate(matches, 1):
        course = next(c for c in courses if c.code == match.course_code)
        print(f"\n{i}. {course.code} - {course.name}")
        print(f"   Match Percentage: {match.match_percentage:.1f}%")
        print(f"   Description: {course.description}")
        
        if match.missing_skills:
            print("   Skills to Develop:")
            for skill in match.missing_skills[:3]:  # Show only top 3 missing skills
                print(f"    - {skill.skill}: {skill.proficiency}")
    
    print("\n" + "="*80)
    print("ENHANCED RECOMMENDATION TESTING COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_enhanced_recommendations() 