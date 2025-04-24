"""
Script to test recommendations with custom skill inputs.
"""
import os
import json
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Tuple
import argparse
import sys

# Get the absolute path to the data directory
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(SRC_DIR, "data")
MODEL_DIR = os.path.join(SRC_DIR, "models", "persistence", "saved_models")
MODEL_PATH = os.path.join(MODEL_DIR, "employee_course_model.npz")

def load_model():
    """Load the trained model"""
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model file not found at {MODEL_PATH}")
        print("Please run train_employee_model.py first")
        return None
    
    try:
        model_data = np.load(MODEL_PATH, allow_pickle=True)
        return model_data
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return None

def load_course_skills() -> Dict:
    """Load course skills from JSON file"""
    json_path = os.path.join(DATA_DIR, 'course_skills.json')
    
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Course skills file not found at {json_path}")
        return {}

def get_course_by_code(course_code, course_data):
    """Get course by code"""
    if course_code in course_data:
        return {
            "code": course_code,
            "name": course_data[course_code].get("name", ""),
            "description": course_data[course_code].get("description", ""),
            "required_skills": course_data[course_code].get("required_skills", {})
        }
    return None

def parse_skill_input(skill_input: str) -> List[Dict]:
    """Parse skill input in format 'Skill1: Level1, Skill2: Level2, ...'"""
    skills = []
    
    # Split by comma and process each skill pair
    skill_pairs = skill_input.split(',')
    for pair in skill_pairs:
        # Support both colon and space separators
        if ':' in pair:
            parts = pair.split(':')
        elif ' ' in pair:
            # Try to split by the last space before level
            skill_part = ' '.join(pair.split()[:-1])
            level_part = pair.split()[-1]
            parts = [skill_part, level_part]
        else:
            parts = [pair, "Intermediate"]  # Default to Intermediate if no level specified
        
        if len(parts) >= 2:
            skill = parts[0].strip()
            level = parts[1].strip()
            
            # Validate level
            valid_levels = ["Beginner", "Intermediate", "Advanced", "Expert"]
            level_cap = level.capitalize()
            if level_cap not in valid_levels and level.upper() not in [l.upper() for l in valid_levels]:
                print(f"Warning: Invalid level '{level}' for skill '{skill}'. Using 'Intermediate'.")
                level = "Intermediate"
            else:
                # Match with case insensitive comparison
                for valid_level in valid_levels:
                    if valid_level.upper() == level.upper():
                        level = valid_level
                        break
            
            if skill:  # Only add if skill name is not empty
                skills.append({
                    "skill": skill,
                    "proficiency": level
                })
    
    return skills

def create_skill_vector(skills, model_data):
    """Create a skill vector for the input skills"""
    skill_names = model_data["skill_names"]
    
    # Create a vector of zeros
    skill_vector = np.zeros(len(skill_names))
    
    # Map proficiency levels to numeric values
    proficiency_map = {
        "Beginner": 1,
        "Intermediate": 2,
        "Advanced": 3,
        "Expert": 4
    }
    
    # Fill in the values for the skills provided
    skills_found = []
    skills_not_found = []
    
    for skill_info in skills:
        skill_name = skill_info["skill"]
        proficiency = skill_info["proficiency"]
        
        # Find exact match
        exact_match = False
        for i, name in enumerate(skill_names):
            if name.lower() == skill_name.lower():
                skill_vector[i] = proficiency_map.get(proficiency, 2)
                skills_found.append((skill_name, proficiency))
                exact_match = True
                break
        
        if not exact_match:
            # If no exact match, look for partial matches
            best_match = None
            best_match_score = 0
            
            for i, name in enumerate(skill_names):
                # Calculate how much of the name matches
                if skill_name.lower() in name.lower():
                    match_score = len(skill_name) / len(name)
                    if match_score > best_match_score:
                        best_match = (i, name)
                        best_match_score = match_score
                elif name.lower() in skill_name.lower():
                    match_score = len(name) / len(skill_name)
                    if match_score > best_match_score:
                        best_match = (i, name)
                        best_match_score = match_score
            
            # Use the best match if score is above threshold
            if best_match and best_match_score > 0.5:
                i, name = best_match
                skill_vector[i] = proficiency_map.get(proficiency, 2)
                skills_found.append((f"{skill_name} → {name}", proficiency))
                exact_match = True
        
        if not exact_match:
            skills_not_found.append(skill_name)
    
    return skill_vector, skills_found, skills_not_found

def recommend_courses_for_skills(model_data, skill_vector, top_n=10):
    """Recommend courses based on skill vector"""
    course_factors = model_data["course_factors"]
    course_codes = model_data["course_codes"]
    
    # Project the skill vector into latent space
    skill_vector_reshaped = skill_vector.reshape(1, -1)
    try:
        # Use the NMF transformation matrix to project
        skill_factors = model_data["skill_factors"]
        
        # Get the pseudo-inverse of the skill factors matrix for transformation
        skill_factors_pinv = np.linalg.pinv(skill_factors)
        latent_vector = np.dot(skill_vector_reshaped, skill_factors_pinv)
        
        # Calculate similarity to courses using the latent representation
        similarities = cosine_similarity(latent_vector, course_factors)[0]
    except Exception as e:
        print(f"Warning: Error projecting skill vector to latent space: {str(e)}")
        print("Falling back to direct similarity calculation...")
        # Fallback to direct similarity calculation
        skill_matrix = np.zeros((len(course_codes), len(skill_vector)))
        for i in range(len(course_codes)):
            skill_matrix[i] = skill_vector
        
        similarities = cosine_similarity(skill_vector_reshaped, skill_matrix)[0]
    
    # Sort by similarity
    sorted_indices = np.argsort(similarities)[::-1][:top_n]
    recommended_courses = [(course_codes[idx], similarities[idx]) for idx in sorted_indices]
    
    return recommended_courses

def format_recommendations(recommendations, course_data):
    """Format course recommendations for display"""
    results = []
    
    for course_code, score in recommendations:
        course = get_course_by_code(course_code, course_data)
        if course:
            results.append({
                "code": course_code,
                "name": course["name"],
                "match_score": f"{score * 100:.2f}%",
                "required_skills": len(course["required_skills"])
            })
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Test recommendations with custom skills')
    parser.add_argument('--skills', '-s', help='Comma-separated list of skills with proficiency levels (e.g., "Python: Intermediate, JavaScript: Advanced")')
    parser.add_argument('--top', '-n', type=int, default=10, help='Number of recommendations to show')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show verbose output including skill matches')
    
    args = parser.parse_args()
    
    # If no skills provided via arguments, prompt the user
    skills_input = args.skills
    if not skills_input:
        skills_input = input("Enter your skills (format: Skill1: Level1, Skill2: Level2, ...): ")
    
    # Load the model
    model_data = load_model()
    if model_data is None:
        return
    
    # Parse skills
    skills = parse_skill_input(skills_input)
    if not skills:
        print("No valid skills provided. Please use the format 'Skill1: Level1, Skill2: Level2, ...'")
        return
    
    print(f"\nProcessed {len(skills)} skills:")
    for skill in skills:
        print(f"  - {skill['skill']}: {skill['proficiency']}")
    
    # Create skill vector
    skill_vector, skills_found, skills_not_found = create_skill_vector(skills, model_data)
    
    # Load course data
    course_data = load_course_skills()
    if not course_data:
        print("Error: No course data found")
        return
    
    # Print skill summary
    print("\nSkills matched in the system:")
    print("=" * 60)
    if skills_found:
        for skill, level in skills_found:
            print(f"  - {skill}: {level}")
    else:
        print("  None of your skills were found in the system.")
    
    if skills_not_found:
        print("\nSkills not found in the system:")
        for skill in skills_not_found:
            print(f"  - {skill}")
    
    # Get recommendations
    print("\nGenerating course recommendations based on your skills...")
    recommendations = recommend_courses_for_skills(model_data, skill_vector, args.top)
    formatted_recs = format_recommendations(recommendations, course_data)
    
    # Print recommendations
    print("\nRecommended Courses:")
    print("=" * 80)
    print(f"{'Code':<15} {'Name':<50} {'Match Score':<15}")
    print("-" * 80)
    for rec in formatted_recs:
        print(f"{rec['code']:<15} {rec['name']:<50} {rec['match_score']:<15}")
    
    # Show course details for top recommendation
    if formatted_recs:
        top_course_code = formatted_recs[0]["code"]
        top_course = get_course_by_code(top_course_code, course_data)
        if top_course and args.verbose:
            print(f"\nTop Recommendation Details - {top_course_code} {top_course['name']}:")
            print("=" * 80)
            print(f"Required Skills:")
            for skill, level in top_course['required_skills'].items():
                print(f"  - {skill}: {level}")

if __name__ == "__main__":
    main() 