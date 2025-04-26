import json
import sys
import os
from collections import defaultdict
import numpy as np

# Add the parent directory to sys.path to import from other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import local modules
from utils.skill_matcher import SkillMatcher
from models.recommendation_model import RecommendationModel

def recommend_courses(user_skills, num_recommendations=5):
    """
    Recommends courses based on user skills.
    
    Args:
        user_skills (list): List of user skills
        num_recommendations (int): Number of course recommendations to return
        
    Returns:
        list: List of recommended courses
    """
    # Load courses data
    try:
        with open('data/courses_with_skills.json', 'r') as f:
            courses = json.load(f)
    except FileNotFoundError:
        print("Error: courses_with_skills.json not found. Please run update_course_skills.py first.")
        return []

    # Initialize skill matcher and recommendation model
    skill_matcher = SkillMatcher()
    recommendation_model = RecommendationModel()
    
    # Get skill matches
    matched_skills = skill_matcher.match_skills(user_skills)
    
    # Calculate skill scores for each course
    course_scores = defaultdict(float)
    for course_id, course_data in courses.items():
        course_skills = course_data.get('skills', [])
        if not course_skills:
            continue
            
        # Calculate skill overlap score
        overlap_score = 0
        for skill in matched_skills:
            if skill in course_skills:
                overlap_score += 1
                
        # Normalize score by course skill count
        if len(course_skills) > 0:
            normalized_score = overlap_score / len(course_skills)
            course_scores[course_id] = normalized_score
    
    # Get recommendations from model
    model_recommendations = recommendation_model.get_recommendations(
        user_skills=matched_skills,
        courses=courses,
        num_recommendations=num_recommendations
    )
    
    # Combine direct matching with model recommendations
    top_courses = sorted(course_scores.items(), key=lambda x: x[1], reverse=True)[:num_recommendations]
    
    # Merge and deduplicate recommendations
    all_recommendations = []
    seen_courses = set()
    
    # Add top direct matches
    for course_id, score in top_courses:
        if course_id not in seen_courses:
            course_info = courses.get(course_id, {})
            recommendation = {
                'course_id': course_id,
                'title': course_info.get('title', 'Unknown Course'),
                'description': course_info.get('description', ''),
                'match_score': float(score),
                'skills': course_info.get('skills', []),
                'source': 'direct_match'
            }
            all_recommendations.append(recommendation)
            seen_courses.add(course_id)
    
    # Add model recommendations
    for rec in model_recommendations:
        course_id = rec.get('course_id')
        if course_id and course_id not in seen_courses:
            rec['source'] = 'model'
            all_recommendations.append(rec)
            seen_courses.add(course_id)
    
    # Sort by match score
    sorted_recommendations = sorted(all_recommendations, key=lambda x: x.get('match_score', 0), reverse=True)
    
    return sorted_recommendations[:num_recommendations]

if __name__ == "__main__":
    # Example usage
    test_skills = [
        "Python programming",
        "Data analysis",
        "Machine learning",
        "Statistical modeling"
    ]
    
    recommendations = recommend_courses(test_skills, num_recommendations=5)
    
    print(f"Recommendations for skills: {', '.join(test_skills)}")
    print("-" * 50)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['title']}")
        print(f"   Match score: {rec['match_score']:.2f}")
        print(f"   Skills: {', '.join(rec['skills'][:3])}{'...' if len(rec['skills']) > 3 else ''}")
        print(f"   Source: {rec['source']}")
        print() 