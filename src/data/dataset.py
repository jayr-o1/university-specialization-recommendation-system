import json
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Union
import importlib.util
import subprocess

# Updated imports with proper package paths
from src.models.schemas import ProficiencyLevel, Faculty, Course, SkillProficiency
from src.data.courses import COURSES

# Define paths more robustly
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(DATA_DIR, "training_data.json")
CSV_DATASET_PATH = os.path.join(DATA_DIR, "training_data.csv")
SKILL_MATRIX_PATH = os.path.join(DATA_DIR, "skill_course_matrix.csv")

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
    Generate the skill-course matrix CSV using our generator script.
    """
    try:
        # Try to run the generator script
        generator_path = os.path.join(DATA_DIR, "generate_skill_matrix.py")
        
        # Check if the file exists
        if not os.path.exists(generator_path):
            print(f"Warning: Skill matrix generator not found at {generator_path}")
            # Fall back to the old method if the generator doesn't exist
            _generate_skill_matrix_fallback()
            return
            
        # Run the generator script as a module
        print("Running skill matrix generator...")
        
        # Import and run the module
        spec = importlib.util.spec_from_file_location("generate_skill_matrix", generator_path)
        if spec and spec.loader:
            generator = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(generator)
            generator.main()
        else:
            # If import fails, try running as a subprocess
            result = subprocess.run(
                ["python", generator_path],
                cwd=os.path.dirname(generator_path),
                capture_output=True,
                text=True
            )
            print(result.stdout)
            
            if result.returncode != 0:
                print(f"Error running generator: {result.stderr}")
                _generate_skill_matrix_fallback()
    except Exception as e:
        print(f"Error generating skill matrix: {str(e)}")
        # Fall back to the old method if there's an error
        _generate_skill_matrix_fallback()

def _generate_skill_matrix_fallback() -> None:
    """
    Fallback method to generate the skill-course matrix in case the generator script fails.
    This uses the original implementation.
    """
    print("Using fallback method to generate skill-course matrix...")
    
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
    skill_course_df.to_csv(SKILL_MATRIX_PATH, index=False)
    
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
    """Ensure all necessary dataset files exist"""
    # Create the main dataset if it doesn't exist
    if not os.path.exists(DATASET_PATH):
        dataset = create_initial_dataset()
        save_dataset_as_json(dataset)
    
    # Create the skill matrix if it doesn't exist
    if not os.path.exists(SKILL_MATRIX_PATH):
        save_dataset_as_csv()
    
    return load_dataset() 