#!/usr/bin/env python
# Script to generate training data and train the recommendation model

import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.data.dataset import ensure_dataset_exists, save_dataset_as_csv
from src.models.recommender import SkillBasedRecommender
from src.data.courses import COURSES
from src.data.faculties import FACULTIES
from src.models.schemas import Faculty, SkillProficiency, ProficiencyLevel
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
    
    # Show skill importances for each latent factor
    skill_importances = recommender.get_skill_importance()
    print("\nSkill Importances by Latent Factor:")
    for factor_name in skill_importances.columns:
        print(f"\n{factor_name}:")
        top_skills = skill_importances[factor_name].sort_values(ascending=False).head(5)
        for skill, importance in top_skills.items():
            print(f"  {skill}: {importance:.4f}")
    
    print("\nModel training complete!")

if __name__ == "__main__":
    main() 