"""
Script to recommend courses for employees using the trained model.
"""
import os
import json
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Tuple
import argparse

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

def load_employees() -> List[Dict]:
    """Load employee data from JSON file"""
    json_path = os.path.join(DATA_DIR, 'employees.json')
    
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Employee data file not found at {json_path}")
        return []

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

def get_employee_by_id(employee_id, employees):
    """Get employee by ID"""
    for employee in employees:
        if employee["id"] == employee_id:
            return employee
    return None

def find_similar_courses(model_data, course_code, top_n=5):
    """Find similar courses to a given course"""
    course_factors = model_data["course_factors"]
    course_codes = model_data["course_codes"]
    
    # Find index of the course
    try:
        course_idx = np.where(course_codes == course_code)[0][0]
    except:
        print(f"Course {course_code} not found in the model")
        return []
    
    # Get course factors
    course_vector = course_factors[course_idx].reshape(1, -1)
    
    # Calculate similarity to all courses
    similarities = cosine_similarity(course_vector, course_factors)[0]
    
    # Sort by similarity (excluding the course itself)
    sorted_indices = np.argsort(similarities)[::-1]
    similar_courses = []
    
    for idx in sorted_indices:
        if course_codes[idx] != course_code:  # Skip the course itself
            similar_courses.append((course_codes[idx], similarities[idx]))
            if len(similar_courses) >= top_n:
                break
    
    return similar_courses

def recommend_courses_for_employee(model_data, employee_id, top_n=10):
    """Recommend courses for an employee"""
    employee_factors = model_data["employee_factors"]
    employee_ids = model_data["employee_ids"]
    course_factors = model_data["course_factors"]
    course_codes = model_data["course_codes"]
    
    # Find index of the employee
    try:
        employee_idx = np.where(employee_ids == employee_id)[0][0]
    except:
        print(f"Employee {employee_id} not found in the model")
        return []
    
    # Get employee factors
    employee_vector = employee_factors[employee_idx].reshape(1, -1)
    
    # Calculate similarity to all courses
    similarities = cosine_similarity(employee_vector, course_factors)[0]
    
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

def show_all_employees(employees):
    """Show a list of all employees"""
    print("\nAvailable Employees:")
    print("=" * 60)
    print(f"{'ID':<10} {'Name':<20} {'Department':<20} {'Skills':<10}")
    print("-" * 60)
    
    for employee in employees:
        print(f"{employee['id']:<10} {employee['name']:<20} {employee['department']:<20} {len(employee['skills']):<10}")

def show_all_courses(course_data):
    """Show a list of all courses"""
    print("\nAvailable Courses:")
    print("=" * 90)
    print(f"{'Code':<15} {'Name':<50} {'Required Skills':<15}")
    print("-" * 90)
    
    for code, info in course_data.items():
        name = info.get("name", "")
        skills_count = len(info.get("required_skills", {}))
        print(f"{code:<15} {name:<50} {skills_count:<15}")

def main():
    parser = argparse.ArgumentParser(description='Recommend courses for employees')
    parser.add_argument('--employee', '-e', help='Employee ID to get recommendations for')
    parser.add_argument('--course', '-c', help='Course code to find similar courses')
    parser.add_argument('--top', '-n', type=int, default=5, help='Number of recommendations to show')
    parser.add_argument('--list-employees', '-le', action='store_true', help='List all employees')
    parser.add_argument('--list-courses', '-lc', action='store_true', help='List all courses')
    
    args = parser.parse_args()
    
    # Load the model
    model_data = load_model()
    if model_data is None:
        return
    
    # Load course data
    course_data = load_course_skills()
    if not course_data:
        print("Error: No course data found")
        return
    
    # Load employee data
    employees = load_employees()
    if not employees:
        print("Error: No employee data found")
        return
    
    # List employees if requested
    if args.list_employees:
        show_all_employees(employees)
        return
    
    # List courses if requested
    if args.list_courses:
        show_all_courses(course_data)
        return
    
    # Get recommendations for an employee
    if args.employee:
        employee = get_employee_by_id(args.employee, employees)
        if not employee:
            print(f"Employee with ID {args.employee} not found")
            return
        
        print(f"\nRecommendations for {employee['name']} ({employee['department']}):")
        print("=" * 80)
        
        recommendations = recommend_courses_for_employee(model_data, args.employee, args.top)
        formatted_recs = format_recommendations(recommendations, course_data)
        
        print(f"{'Code':<15} {'Name':<50} {'Match Score':<15}")
        print("-" * 80)
        for rec in formatted_recs:
            print(f"{rec['code']:<15} {rec['name']:<50} {rec['match_score']:<15}")
    
    # Find similar courses
    elif args.course:
        if args.course not in course_data:
            print(f"Course with code {args.course} not found")
            return
        
        course_name = course_data[args.course].get("name", "")
        print(f"\nCourses similar to {args.course} - {course_name}:")
        print("=" * 80)
        
        similar_courses = find_similar_courses(model_data, args.course, args.top)
        formatted_courses = format_recommendations(similar_courses, course_data)
        
        print(f"{'Code':<15} {'Name':<50} {'Similarity':<15}")
        print("-" * 80)
        for course in formatted_courses:
            print(f"{course['code']:<15} {course['name']:<50} {course['match_score']:<15}")
    
    # If no specific action, show usage
    else:
        print("Please specify an action. Use --help for options.")

if __name__ == "__main__":
    main() 