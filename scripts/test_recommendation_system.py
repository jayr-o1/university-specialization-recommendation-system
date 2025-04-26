import json
import os
import sys
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import from other modules
from utils.skills_mapper import SkillsMapper
from models.recommendation_model import RecommendationModel
from models.enhanced_recommendation_model import EnhancedRecommendationModel
from models.learning_path import LearningPathGenerator

def test_skill_mapping():
    """Test skill mapping functionality"""
    print("\n=== Testing Skill Mapping ===")
    
    mapper = SkillsMapper()
    
    # Test skills
    user_skills = [
        "Python programming",
        "Data analysis",
        "Machine learning",
        "Statistical modeling"
    ]
    
    course_skills = [
        "Python",
        "Data science",
        "Deep learning",
        "Statistics",
        "Regression analysis"
    ]
    
    # Map skills
    mapping = mapper.map_skills(user_skills, course_skills)
    
    print("Skill Mapping Results:")
    for skill, matches in mapping.items():
        print(f"{skill}:")
        for match, score in matches:
            print(f"  - {match} (similarity: {score:.2f})")
    
    # Test skill grouping
    print("\nTesting Skill Grouping:")
    all_skills = user_skills + course_skills
    skill_groups = mapper.group_related_skills(all_skills)
    
    for i, group in enumerate(skill_groups, 1):
        print(f"Group {i}: {', '.join(group)}")
    
    # Return test results
    return {
        "skill_mapping": mapping,
        "skill_groups": skill_groups
    }

def test_basic_recommendations():
    """Test basic recommendation model"""
    print("\n=== Testing Basic Recommendation Model ===")
    
    # Load test data
    try:
        with open('data/courses_with_skills.json', 'r') as f:
            courses = json.load(f)
    except FileNotFoundError:
        print("Error: courses_with_skills.json not found. Running update_course_skills.py...")
        from scripts.update_course_skills import update_course_skills
        update_course_skills()
        
        # Try loading again
        try:
            with open('data/courses_with_skills.json', 'r') as f:
                courses = json.load(f)
        except FileNotFoundError:
            print("Error: Could not create or find courses_with_skills.json")
            return {"error": "Missing course data"}
    
    # Test skills
    test_skills = [
        "Python programming",
        "Data analysis",
        "Machine learning"
    ]
    
    # Initialize model
    model = RecommendationModel()
    
    # Get recommendations
    recommendations = model.get_recommendations(
        user_skills=test_skills,
        courses=courses,
        num_recommendations=5
    )
    
    # Print recommendations
    print(f"Recommendations for skills: {', '.join(test_skills)}")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['title']} (Score: {rec['match_score']:.2f})")
        if 'skills' in rec:
            print(f"   Skills: {', '.join(rec['skills'][:3])}" + 
                  ("..." if len(rec['skills']) > 3 else ""))
    
    # Return test results
    return {
        "input_skills": test_skills,
        "recommendations": recommendations
    }

def test_enhanced_recommendations():
    """Test enhanced recommendation model"""
    print("\n=== Testing Enhanced Recommendation Model ===")
    
    # Load test data
    try:
        with open('data/courses_with_skills.json', 'r') as f:
            courses = json.load(f)
    except FileNotFoundError:
        print("Error: courses_with_skills.json not found.")
        return {"error": "Missing course data"}
    
    # Test skills and preferences
    test_data = {
        "skills": [
            "Python programming",
            "Data analysis",
            "Machine learning"
        ],
        "preferences": {
            "learning_style": "practical",
            "difficulty_level": "intermediate",
            "time_commitment": "medium"
        }
    }
    
    # Initialize model
    model = EnhancedRecommendationModel()
    
    # Get recommendations
    recommendations = model.get_personalized_recommendations(
        user_data=test_data,
        courses=courses,
        num_recommendations=5
    )
    
    # Print recommendations
    print(f"Enhanced recommendations for {', '.join(test_data['skills'])}")
    print(f"Preferences: {json.dumps(test_data['preferences'], indent=2)}")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['title']} (Score: {rec['match_score']:.2f})")
        if 'skills' in rec:
            print(f"   Skills: {', '.join(rec['skills'][:3])}" + 
                  ("..." if len(rec['skills']) > 3 else ""))
        if 'reasons' in rec:
            print(f"   Reasons: {rec['reasons']}")
    
    # Return test results
    return {
        "input_data": test_data,
        "recommendations": recommendations
    }

def test_learning_path():
    """Test learning path generation"""
    print("\n=== Testing Learning Path Generation ===")
    
    # Load test data
    try:
        with open('data/courses_with_skills.json', 'r') as f:
            courses = json.load(f)
    except FileNotFoundError:
        print("Error: courses_with_skills.json not found.")
        return {"error": "Missing course data"}
    
    # Test user data
    user_data = {
        "current_skills": [
            "Python basics",
            "Data structures"
        ],
        "target_skills": [
            "Machine learning",
            "Deep learning",
            "Neural networks"
        ],
        "preferences": {
            "learning_style": "practical",
            "time_frame": "6 months",
            "difficulty": "progressive"
        }
    }
    
    # Initialize path generator
    path_generator = LearningPathGenerator()
    
    # Generate learning path
    learning_path = path_generator.generate_path(
        user_data=user_data,
        courses=courses
    )
    
    # Print learning path
    print(f"Learning path from {', '.join(user_data['current_skills'])} to {', '.join(user_data['target_skills'])}")
    print(f"Preferences: {json.dumps(user_data['preferences'], indent=2)}")
    
    for i, stage in enumerate(learning_path, 1):
        print(f"\nStage {i}: {stage['name']}")
        print(f"Focus: {stage['focus']}")
        print("Courses:")
        for j, course in enumerate(stage['courses'], 1):
            print(f"  {j}. {course['title']}")
            if 'skills' in course:
                print(f"     Skills: {', '.join(course['skills'][:3])}" + 
                      ("..." if len(course['skills']) > 3 else ""))
    
    # Return test results
    return {
        "user_data": user_data,
        "learning_path": learning_path
    }

def run_all_tests():
    """Run all test functions and save results"""
    test_results = {
        "skill_mapping": test_skill_mapping(),
        "basic_recommendations": test_basic_recommendations(),
        "enhanced_recommendations": test_enhanced_recommendations(),
        "learning_path": test_learning_path()
    }
    
    # Save test results
    os.makedirs('data', exist_ok=True)
    with open('data/test_results.json', 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print("\nTest results saved to 'data/test_results.json'")
    
    return test_results

if __name__ == "__main__":
    run_all_tests() 