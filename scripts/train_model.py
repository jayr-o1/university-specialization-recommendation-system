#!/usr/bin/env python
# Script to generate training data and train the recommendation model

import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.dataset import ensure_dataset_exists, save_dataset_as_csv
from models.recommender import SkillBasedRecommender
from data.courses import COURSES
from data.faculties import FACULTIES
from models.schemas import Faculty, SkillProficiency, ProficiencyLevel
import pandas as pd

def main():
    """Generate dataset and train the recommendation model"""
    print("Generating dataset...")
    dataset = ensure_dataset_exists()
    
    # Make sure the CSV files are created
    save_dataset_as_csv()
    
    # Train the model
    print("Training recommendation model...")
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
    skill_matrix_path = os.path.join(DATA_DIR, "skill_course_matrix.csv")
    
    # Initialize and train the model
    recommender = SkillBasedRecommender(n_components=5)
    recommender.load_data(skill_matrix_path)
    recommender.train()
    
    # Save the model
    model_path = recommender.save_model()
    print(f"Model saved to {model_path}")
    
    # Show example recommendations for a faculty member
    if FACULTIES:
        faculty_data = FACULTIES[0]
        faculty = Faculty(
            id=faculty_data["id"],
            name=faculty_data["name"],
            department=faculty_data["department"],
            skills=[
                SkillProficiency(
                    skill=skill["skill"],
                    proficiency=ProficiencyLevel(skill["proficiency"])
                )
                for skill in faculty_data["skills"]
            ]
        )
        
        print(f"\nExample recommendations for {faculty.name}:")
        recommendations = recommender.recommend_courses(faculty, top_n=10)
        
        # Get course names
        course_dict = {course["code"]: course["name"] for course in COURSES}
        
        # Display recommendations
        for i, rec in enumerate(recommendations, 1):
            course_name = course_dict.get(rec.course_code, "Unknown Course")
            print(f"\n{i}. {course_name} (Code: {rec.course_code}) - Match: {rec.match_percentage:.2f}%")
            
            # Display matched skills
            if rec.matched_skills:
                print("  Matched Skills:")
                for skill in rec.matched_skills:
                    print(f"    - {skill.skill} ({skill.proficiency.value})")
            else:
                print("  Matched Skills: None")
            
            # Display missing skills
            if rec.missing_skills:
                print("  Missing Skills (Recommended Training):")
                for skill in rec.missing_skills:
                    print(f"    - {skill.skill} ({skill.proficiency.value})")
            else:
                print("  Missing Skills: None")
    
        # Show similar courses for a course
        if COURSES:
            course_code = COURSES[0]["code"]
            print(f"\nCourses similar to {course_code}:")
            similar_courses = recommender.get_similar_courses(course_code, top_n=10)
            
            for i, (similar_code, similarity) in enumerate(similar_courses, 1):
                course_name = course_dict.get(similar_code, "Unknown Course")
                print(f"{i}. {course_name} (Code: {similar_code}) - Similarity: {similarity:.2f}")
    
        # Display skill importance for each factor
        print("\nSkill importance for each latent factor:")
        skill_importance = recommender.get_skill_importance()
        # Show top 3 skills for each factor
        for factor in skill_importance.columns:
            top_skills = skill_importance[factor].sort_values(ascending=False).head(3)
            print(f"\n{factor}:")
            for skill, importance in top_skills.items():
                print(f"  - {skill}: {importance:.2f}")

if __name__ == "__main__":
    main() 