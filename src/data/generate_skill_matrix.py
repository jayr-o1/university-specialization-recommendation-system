#!/usr/bin/env python3
"""
Generate a skill-course matrix from the course_skills.json file.

This script reads the course skills data and creates a CSV file with a matrix
representation where rows are courses and columns are skills. Each cell contains
the required proficiency level (1-4) for that skill in that course.
"""
import json
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Set

# Proficiency level mapping
PROFICIENCY_VALUES = {
    "Beginner": 1,
    "Intermediate": 2,
    "Advanced": 3,
    "Expert": 4
}

def load_course_skills() -> Dict:
    """Load course skills from JSON file"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, 'course_skills.json')
    
    with open(json_path, 'r') as f:
        return json.load(f)

def get_all_unique_skills(course_data: Dict) -> Set[str]:
    """Extract all unique skills from the course data"""
    all_skills = set()
    for course_code, course_info in course_data.items():
        for skill in course_info['required_skills'].keys():
            all_skills.add(skill)
    return all_skills

def generate_skill_matrix(course_data: Dict, all_skills: Set[str]) -> pd.DataFrame:
    """Generate a matrix where rows are courses and columns are skills"""
    # Initialize an empty DataFrame
    df = pd.DataFrame(0, index=list(course_data.keys()), 
                      columns=sorted(list(all_skills)))
    
    # Add a column for course names
    course_names = {code: info['name'] for code, info in course_data.items()}
    
    # Fill in the matrix with skill proficiency values
    for course_code, course_info in course_data.items():
        for skill, level in course_info['required_skills'].items():
            df.at[course_code, skill] = PROFICIENCY_VALUES.get(level, 0)
    
    # Rename the index to be clear it's course codes
    df.index.name = 'course_code'
    
    return df

def save_skill_matrix(df: pd.DataFrame) -> str:
    """Save the skill matrix as a CSV file"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, 'skill_course_matrix.csv')
    
    # Reset index to include course_code as a column
    df.reset_index().to_csv(csv_path, index=False)
    
    return csv_path

def main():
    """Main function to generate and save the skill-course matrix"""
    print("Loading course skills data...")
    course_data = load_course_skills()
    
    print("Extracting unique skills...")
    all_skills = get_all_unique_skills(course_data)
    print(f"Found {len(all_skills)} unique skills")
    
    print("Generating skill-course matrix...")
    skill_matrix = generate_skill_matrix(course_data, all_skills)
    
    print(f"Matrix shape: {skill_matrix.shape[0]} courses x {skill_matrix.shape[1]} skills")
    
    csv_path = save_skill_matrix(skill_matrix)
    print(f"Skill matrix saved to {csv_path}")
    
    # Print some statistics
    print("\nSkill frequency (top 10 most common skills):")
    skill_counts = (skill_matrix > 0).sum()
    for skill, count in skill_counts.sort_values(ascending=False).head(10).items():
        print(f"- {skill}: required in {count} courses")
    
    print("\nAverage skill requirements per course:")
    course_skill_counts = (skill_matrix > 0).sum(axis=1)
    print(f"- Mean: {course_skill_counts.mean():.1f} skills")
    print(f"- Min: {course_skill_counts.min()} skills")
    print(f"- Max: {course_skill_counts.max()} skills")

if __name__ == "__main__":
    main() 