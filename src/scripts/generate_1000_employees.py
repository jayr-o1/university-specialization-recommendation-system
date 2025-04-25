"""
Script to generate 1000 synthetic employee data for training the recommendation model.
This creates a dataset of employees with varied skill sets derived from the course skills.
"""
import json
import os
import random
import pandas as pd
import numpy as np
from typing import List, Dict
import uuid

# Get the absolute path to the data directory
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(SRC_DIR, "data")
OUTPUT_PATH = os.path.join(DATA_DIR, "employees.json")

# Departments for assigning employees
DEPARTMENTS = [
    "Computer Science",
    "Information Technology",
    "Mathematics",
    "Engineering",
    "Business",
    "Communications",
    "Education",
    "Psychology",
    "Social Sciences",
    "Natural Sciences",
    "Arts and Humanities"
]

# Proficiency levels and their weights (for random selection)
PROFICIENCY_LEVELS = {
    "Beginner": 0.35,
    "Intermediate": 0.4,
    "Advanced": 0.2,
    "Expert": 0.05
}

def load_course_skills() -> Dict:
    """Load course skills from JSON file"""
    json_path = os.path.join(DATA_DIR, 'course_skills.json')
    
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Course skills file not found at {json_path}")
        return {}

def extract_all_skills(course_data: Dict) -> List[str]:
    """Extract all unique skills from course data"""
    all_skills = set()
    
    for course_code, info in course_data.items():
        if 'required_skills' in info:
            all_skills.update(info['required_skills'].keys())
            
    return list(all_skills)

def generate_employee_skills(all_skills: List[str], num_skills: int) -> List[Dict]:
    """Generate a list of skills for an employee"""
    # Select random subset of skills
    selected_skills = random.sample(all_skills, min(num_skills, len(all_skills)))
    
    # Assign proficiency levels
    employee_skills = []
    for skill in selected_skills:
        # Weighted random selection of proficiency level
        proficiency = random.choices(
            list(PROFICIENCY_LEVELS.keys()),
            weights=list(PROFICIENCY_LEVELS.values())
        )[0]
        
        employee_skills.append({
            "skill": skill,
            "proficiency": proficiency
        })
    
    return employee_skills

def generate_employees(num_employees: int, all_skills: List[str]) -> List[Dict]:
    """Generate synthetic employee data"""
    employees = []
    
    for i in range(num_employees):
        # Generate a unique ID
        employee_id = str(uuid.uuid4())[:8]
        
        # Random department
        department = random.choice(DEPARTMENTS)
        
        # Random number of skills (between 5 and 20)
        num_skills = random.randint(5, 20)
        
        # Generate skills
        skills = generate_employee_skills(all_skills, num_skills)
        
        # Create employee record
        employee = {
            "id": employee_id,
            "name": f"Employee {i+1}",
            "department": department,
            "skills": skills
        }
        
        employees.append(employee)
    
    return employees

def save_employees(employees: List[Dict]):
    """Save employees to JSON file"""
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(employees, f, indent=2)
    
    print(f"Saved {len(employees)} employees to {OUTPUT_PATH}")

def main(num_employees: int = 1000):
    print(f"Generating {num_employees} synthetic employees...")
    
    # Load course skills
    course_data = load_course_skills()
    if not course_data:
        print("Error: No course skills data found")
        return
    
    print(f"Loaded {len(course_data)} courses with skills")
    
    # Extract all skills
    all_skills = extract_all_skills(course_data)
    print(f"Found {len(all_skills)} unique skills")
    
    # Generate employees
    employees = generate_employees(num_employees, all_skills)
    
    # Save to file
    save_employees(employees)
    
    print("Done!")

if __name__ == "__main__":
    # Generate 1000 employees
    main(1000) 