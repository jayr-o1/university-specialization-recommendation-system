"""
Test script for the complete enhanced recommendation system with user preferences.
This script showcases all implemented improvements together.
"""
from src.models.schemas import Faculty, SkillProficiency, ProficiencyLevel
from src.utils.data_access import load_all_courses
from src.matching.enhanced_matcher import (
    get_top_course_matches_enhanced, 
    match_faculty_to_course_enhanced,
    enhance_faculty_skills
)
from src.utils.user_preferences import UserPreferences
from src.utils.skill_taxonomy import get_category

def test_complete_system():
    """Test the complete enhanced recommendation system."""
    print("\n" + "="*80)
    print("COMPLETE ENHANCED RECOMMENDATION SYSTEM")
    print("="*80)
    
    # Step 1: Create the user's skills
    user_skills = [
        SkillProficiency(skill="MySQL", proficiency=ProficiencyLevel.INTERMEDIATE),
        SkillProficiency(skill="Database Design", proficiency=ProficiencyLevel.ADVANCED),
        SkillProficiency(skill="MSSQL", proficiency=ProficiencyLevel.INTERMEDIATE)
    ]
    
    # Step 2: Create a faculty profile with these skills
    faculty = Faculty(
        id="USER",
        name="Custom User",
        department="Testing",
        skills=user_skills
    )
    
    # Step 3: Set up user preferences
    preferences = UserPreferences()
    preferences.set_category_preference("Database", 1.5)  # Boost database courses
    preferences.add_preferred_course("IT-IMDBSYS31")      # Specifically boost IMDBSYS31
    preferences.set_min_match_percentage(60.0)            # Only show courses with >60% match
    
    # Step 4: Print user profile and preferences
    print("\nUser Skills:")
    for skill in user_skills:
        print(f"  - {skill.skill}: {skill.proficiency}")
    
    print("\nUser Preferences:")
    print("  - Category Weights:")
    for category, weight in preferences.category_weights.items():
        if weight != 1.0:  # Only show non-default weights
            print(f"    - {category}: {weight:.1f}x")
    
    print("  - Preferred Courses:", ", ".join(preferences.preferred_courses) or "None")
    print("  - Minimum Match Percentage: {:.1f}%".format(preferences.min_match_percentage))
    
    # Step 5: Get enhanced faculty with inferred skills
    enhanced_faculty = enhance_faculty_skills(faculty)
    
    print("\nInferred Skills:")
    inferred_skills = [s for s in enhanced_faculty.skills if s not in faculty.skills]
    for skill in inferred_skills:
        print(f"  - {skill.skill}: {skill.proficiency}")
    
    # Step 6: Load courses and get matches
    courses = load_all_courses()
    
    # Step 7: Get specific match for IMDBSYS31 (the course of interest)
    imdbsys31_course = next((c for c in courses if c.code == "IT-IMDBSYS31"), None)
    
    if imdbsys31_course:
        match_result = match_faculty_to_course_enhanced(faculty, imdbsys31_course)
        print(f"\nEnhanced Match with IT-IMDBSYS31 - Information Management (DB Sys.1):")
        print(f"  Match Percentage: {match_result.match_percentage:.1f}%")
        
        # Get category of the course based on its required skills
        course_skills = list(imdbsys31_course.required_skills.keys())
        categories = set(get_category(skill) for skill in course_skills)
        main_categories = [cat for cat in categories if cat != "Other"]
        print(f"  Primary Skill Categories: {', '.join(main_categories) or 'None'}")
        
        # Show missing skills
        if match_result.missing_skills:
            print("  Skills to Develop:")
            for skill in match_result.missing_skills:
                print(f"    - {skill.skill}: {skill.proficiency}")
    
    # Step 8: Get all enhanced matches
    matches = get_top_course_matches_enhanced(faculty, courses)
    
    # Step 9: Apply user preferences to matches
    adjusted_matches = preferences.apply_preferences(matches, courses)
    
    # Step 10: Show final top 10 matches
    print("\nFinal Top 10 Course Recommendations:")
    for i, match in enumerate(adjusted_matches[:10], 1):
        course = next(c for c in courses if c.code == match.course_code)
        
        # Determine if this is boosted by preferences
        boosted = match.course_code in preferences.preferred_courses
        boosted_text = " (Boosted by Preferences)" if boosted else ""
        
        print(f"\n{i}. {course.code} - {course.name}{boosted_text}")
        print(f"   Match Percentage: {match.match_percentage:.1f}%")
        print(f"   Description: {course.description}")
        
        if match.missing_skills:
            print("   Top Skills to Develop:")
            for skill in match.missing_skills[:3]:  # Show only top 3 missing skills
                print(f"    - {skill.skill}: {skill.proficiency}")
    
    print("\n" + "="*80)
    print("SYSTEM TESTING COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_complete_system() 