"""
Script to train the recommendation model using generated employee data.
This uses the employee skills and course requirements to build a customized model.
"""
import os
import json
import pandas as pd
import numpy as np
from sklearn.decomposition import NMF
from typing import Dict, List, Tuple

# Get the absolute path to the data directory
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(SRC_DIR, "data")
MODEL_DIR = os.path.join(SRC_DIR, "models", "persistence", "saved_models")

# Ensure model directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

def load_course_skills() -> Dict:
    """Load course skills from JSON file"""
    json_path = os.path.join(DATA_DIR, 'course_skills.json')
    
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Course skills file not found at {json_path}")
        return {}

def load_employees() -> List[Dict]:
    """Load employee data from JSON file"""
    json_path = os.path.join(DATA_DIR, 'employees.json')
    
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Employee data file not found at {json_path}")
        return []

def create_skill_matrices(course_data: Dict, employees: List[Dict]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Create skill matrices for courses and employees"""
    # Extract all skills
    all_skills = set()
    for course_code, info in course_data.items():
        if 'required_skills' in info:
            all_skills.update(info['required_skills'].keys())
    
    # Convert proficiency levels to numeric values
    proficiency_map = {
        "Beginner": 1,
        "Intermediate": 2,
        "Advanced": 3,
        "Expert": 4
    }
    
    # Create course-skill matrix
    course_rows = []
    for course_code, info in course_data.items():
        row = {"course_code": course_code}
        
        if 'required_skills' in info:
            required_skills = info['required_skills']
            for skill in all_skills:
                if skill in required_skills:
                    value = proficiency_map.get(required_skills[skill], 0)
                    row[skill] = value
                else:
                    row[skill] = 0
        else:
            # Handle courses without required_skills
            for skill in all_skills:
                row[skill] = 0
                
        course_rows.append(row)
    
    # Create employee-skill matrix
    employee_rows = []
    for employee in employees:
        row = {"employee_id": employee["id"]}
        
        # Initialize all skills to 0
        for skill in all_skills:
            row[skill] = 0
            
        # Add employee's skills
        for skill_info in employee["skills"]:
            skill_name = skill_info["skill"]
            if skill_name in all_skills:  # Only include skills that exist in courses
                value = proficiency_map.get(skill_info["proficiency"], 0)
                row[skill_name] = value
                
        employee_rows.append(row)
    
    # Convert to DataFrames
    course_df = pd.DataFrame(course_rows)
    employee_df = pd.DataFrame(employee_rows)
    
    return course_df, employee_df

def train_nmf_model(course_df: pd.DataFrame, employee_df: pd.DataFrame, n_components: int = 20):
    """Train NMF model on course and employee data"""
    # Set index and extract feature matrices
    course_df.set_index("course_code", inplace=True)
    course_codes = course_df.index.tolist()
    course_matrix = course_df.values
    
    employee_df.set_index("employee_id", inplace=True)
    employee_ids = employee_df.index.tolist()
    employee_matrix = employee_df.values
    
    # Get skill names (features)
    skill_names = course_df.columns.tolist()
    
    print(f"Training NMF model with {n_components} components...")
    print(f"Course matrix shape: {course_matrix.shape}")
    print(f"Employee matrix shape: {employee_matrix.shape}")
    
    # Initialize and train NMF model on course data
    model = NMF(n_components=n_components, init='random', random_state=42, max_iter=500)
    course_factors = model.fit_transform(course_matrix)
    skill_factors = model.components_
    
    # Project employee skills into the same latent space
    employee_factors = model.transform(employee_matrix)
    
    # Save the model components
    model_path = os.path.join(MODEL_DIR, "employee_course_model.npz")
    np.savez(
        model_path,
        course_factors=course_factors,
        employee_factors=employee_factors,
        skill_factors=skill_factors,
        course_codes=np.array(course_codes, dtype=object),
        employee_ids=np.array(employee_ids, dtype=object),
        skill_names=np.array(skill_names, dtype=object),
        n_components=n_components
    )
    
    print(f"Model saved to {model_path}")
    
    return model_path

def analyze_and_save_skill_importance(skill_factors, skill_names):
    """Analyze and save skill importance by factor"""
    # Create DataFrame with skill importance for each factor
    skill_importance = pd.DataFrame(
        skill_factors.T, 
        index=skill_names,
        columns=[f"Factor_{i}" for i in range(skill_factors.shape[0])]
    )
    
    # Save to CSV
    output_path = os.path.join(DATA_DIR, "skill_importance.csv")
    skill_importance.to_csv(output_path)
    print(f"Skill importance saved to {output_path}")
    
    # Find top skills for each factor
    top_skills_by_factor = {}
    for factor_idx in range(skill_factors.shape[0]):
        factor_name = f"Factor_{factor_idx}"
        # Get top skills for this factor
        top_indices = np.argsort(skill_factors[factor_idx])[::-1][:10]  # Top 10 skills
        top_skills = [(skill_names[idx], float(skill_factors[factor_idx, idx])) for idx in top_indices]
        top_skills_by_factor[factor_name] = top_skills
    
    # Save to JSON
    output_path = os.path.join(DATA_DIR, "top_skills_by_factor.json")
    with open(output_path, 'w') as f:
        json.dump(top_skills_by_factor, f, indent=2)
    print(f"Top skills by factor saved to {output_path}")

def main():
    print("Loading course and employee data...")
    
    # Load data
    course_data = load_course_skills()
    if not course_data:
        print("Error: No course skills data found")
        return
    
    employees = load_employees()
    if not employees:
        print("Error: No employee data found")
        return
    
    print(f"Loaded {len(course_data)} courses and {len(employees)} employees")
    
    # Create skill matrices
    print("Creating skill matrices...")
    course_df, employee_df = create_skill_matrices(course_data, employees)
    
    # Train NMF model
    model_path = train_nmf_model(course_df, employee_df)
    
    # Load the trained model for analysis
    model_data = np.load(model_path, allow_pickle=True)
    skill_factors = model_data['skill_factors']
    skill_names = model_data['skill_names']
    
    # Analyze skill importance
    analyze_and_save_skill_importance(skill_factors, skill_names)
    
    print("Training complete!")

if __name__ == "__main__":
    main() 