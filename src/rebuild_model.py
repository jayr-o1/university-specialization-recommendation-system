"""
Script to rebuild the model after course_skills.json has been updated.
Run this script from the root directory.
"""
import os
import json
import pandas as pd
import numpy as np
import shutil

# Get the absolute path to the src directory
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SRC_DIR, "data")
SKILL_MATRIX_PATH = os.path.join(DATA_DIR, "skill_course_matrix.csv")

def clear_models():
    """Remove existing model files"""
    model_dir = os.path.join(SRC_DIR, "models", "persistence", "saved_models")
    if os.path.exists(model_dir):
        print(f"Clearing model files from {model_dir}")
        for file_name in os.listdir(model_dir):
            file_path = os.path.join(model_dir, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"  Deleted {file_name}")
    else:
        print("No model directory found. It will be created when you run the system.")

def generate_skill_matrix():
    """Generate the skill-course matrix from course_skills.json"""
    # Read the course skills
    course_skills_path = os.path.join(DATA_DIR, "course_skills.json")
    with open(course_skills_path, 'r') as f:
        course_data = json.load(f)
    
    print(f"Loaded {len(course_data)} courses from course_skills.json")
    
    # Extract all skills
    all_skills = set()
    for course_code, info in course_data.items():
        if 'required_skills' in info:
            all_skills.update(info['required_skills'].keys())
        else:
            # Handle case where required_skills might be missing
            print(f"Warning: No required_skills found for {course_code}")
    
    print(f"Found {len(all_skills)} unique skills across all courses")
    
    # Create matrix
    skill_matrix = []
    for course_code, info in course_data.items():
        row = {"course_code": course_code}
        
        required_skills = info.get('required_skills', {})
        for skill in all_skills:
            # Convert proficiency level to numeric
            if skill in required_skills:
                level = required_skills[skill]
                value = {
                    "Beginner": 1,
                    "Intermediate": 2,
                    "Advanced": 3,
                    "Expert": 4
                }.get(level, 0)
                row[skill] = value
            else:
                row[skill] = 0
        
        skill_matrix.append(row)
    
    # Create and save DataFrame
    skill_df = pd.DataFrame(skill_matrix)
    skill_df.to_csv(SKILL_MATRIX_PATH, index=False)
    print(f"Generated skill matrix: {SKILL_MATRIX_PATH}")
    
    # Also create courses.csv file
    courses_data = []
    for course_code, info in course_data.items():
        courses_data.append({
            "course_code": course_code,
            "course_name": info.get('name', ''),
            "description": info.get('description', f"Course on {info.get('name', course_code)}")
        })
    
    courses_df = pd.DataFrame(courses_data)
    courses_df.to_csv(os.path.join(DATA_DIR, "courses.csv"), index=False)
    print(f"Generated courses.csv")

if __name__ == "__main__":
    print("Rebuilding recommendation system with updated course_skills.json")
    clear_models()
    generate_skill_matrix()
    print("\nSystem configuration complete! Your updated course_skills.json is now in use.")
    print("\nYou can run the API using: uvicorn src.main:app --reload")
    print("The system will automatically retrain the model on first use.") 