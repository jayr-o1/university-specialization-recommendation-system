import json
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Union
from models.schemas import ProficiencyLevel, Faculty, Course, SkillProficiency
from data.courses import COURSES
from data.faculties import FACULTIES

# Define paths
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(DATA_DIR, "training_data.json")
CSV_DATASET_PATH = os.path.join(DATA_DIR, "training_data.csv")

def create_initial_dataset() -> Dict:
    """
    Create initial dataset from existing courses and skills data.
    Returns a dictionary that can be saved as JSON.
    """
    dataset = {
        "courses": [],
        "skills": set(),
        "faculty_course_ratings": []
    }
    
    # Extract all courses
    for course in COURSES:
        course_data = {
            "code": course["code"],
            "name": course["name"],
            "description": course["description"],
            "required_skills": course["required_skills"]
        }
        dataset["courses"].append(course_data)
        
        # Add skills to the set of all skills
        for skill in course["required_skills"].keys():
            dataset["skills"].add(skill)
    
    # Convert skills set to list for JSON serialization
    dataset["skills"] = list(dataset["skills"])
    
    return dataset

def save_dataset_as_json(dataset: Dict) -> None:
    """Save dataset to JSON file"""
    # Convert proficiency level enums to strings for JSON serialization
    serializable_dataset = dataset.copy()
    
    for course in serializable_dataset["courses"]:
        required_skills = {}
        for skill, level in course["required_skills"].items():
            if isinstance(level, ProficiencyLevel):
                required_skills[skill] = level.value
            else:
                required_skills[skill] = level
        course["required_skills"] = required_skills
    
    with open(DATASET_PATH, 'w') as f:
        json.dump(serializable_dataset, f, indent=2)
    
    print(f"Dataset saved to {DATASET_PATH}")

def save_dataset_as_csv() -> None:
    """
    Save course-skill matrix and other relevant data as CSV files.
    This format is more suitable for matrix factorization models.
    """
    # Create a courses dataframe
    courses_data = []
    for course in COURSES:
        courses_data.append({
            "course_code": course["code"],
            "course_name": course["name"],
            "description": course["description"]
        })
    
    courses_df = pd.DataFrame(courses_data)
    
    # Create a skill-course matrix for required proficiency
    all_skills = set()
    for course in COURSES:
        all_skills.update(course["required_skills"].keys())
    
    skill_course_matrix = []
    for course in COURSES:
        row = {"course_code": course["code"]}
        for skill in all_skills:
            if skill in course["required_skills"]:
                # Convert enum to numeric value for training
                prof_level = course["required_skills"][skill]
                if isinstance(prof_level, ProficiencyLevel):
                    value = {
                        ProficiencyLevel.BEGINNER: 1,
                        ProficiencyLevel.INTERMEDIATE: 2,
                        ProficiencyLevel.ADVANCED: 3,
                        ProficiencyLevel.EXPERT: 4
                    }[prof_level]
                else:
                    # Already a string like "Beginner"
                    value = {
                        "Beginner": 1,
                        "Intermediate": 2, 
                        "Advanced": 3,
                        "Expert": 4
                    }.get(prof_level, 0)
                
                row[skill] = value
            else:
                row[skill] = 0
        skill_course_matrix.append(row)
    
    skill_course_df = pd.DataFrame(skill_course_matrix)
    
    # Save to CSV
    courses_df.to_csv(os.path.join(DATA_DIR, "courses.csv"), index=False)
    skill_course_df.to_csv(os.path.join(DATA_DIR, "skill_course_matrix.csv"), index=False)
    
    print(f"CSV datasets saved to {DATA_DIR}")

def load_dataset() -> Dict:
    """Load dataset from JSON file"""
    if os.path.exists(DATASET_PATH):
        with open(DATASET_PATH, 'r') as f:
            dataset = json.load(f)
        
        # Convert string proficiency levels back to enum
        for course in dataset["courses"]:
            required_skills = {}
            for skill, level in course["required_skills"].items():
                required_skills[skill] = level
            course["required_skills"] = required_skills
        
        return dataset
    else:
        # Create and save a new dataset if it doesn't exist
        dataset = create_initial_dataset()
        save_dataset_as_json(dataset)
        return dataset

# Function to generate the dataset if it doesn't exist
def ensure_dataset_exists():
    if not os.path.exists(DATASET_PATH):
        dataset = create_initial_dataset()
        save_dataset_as_json(dataset)
        save_dataset_as_csv()
    
    return load_dataset() 