#!/usr/bin/env python
"""
Script to generate training data and train the recommendation models.
This will generate the skill matrix and train both NMF and hybrid models.
"""

import os
import sys
import argparse

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.data.dataset import ensure_dataset_exists, save_dataset_as_csv
from src.models import get_recommender
from src.data.courses import COURSES
import pandas as pd

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Train recommendation models for the university specialization system"
    )
    parser.add_argument(
        '--models', 
        type=str, 
        nargs='+', 
        default=['nmf', 'hybrid'],
        help='Models to train (options: nmf, hybrid)'
    )
    parser.add_argument(
        '--components', 
        type=int, 
        default=10,
        help='Number of latent components for matrix factorization'
    )
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Print detailed information during training'
    )
    
    return parser.parse_args()

def main():
    """Generate dataset and train the recommendation models"""
    args = parse_arguments()
    
    print("Generating dataset...")
    dataset = ensure_dataset_exists()
    
    # Make sure the CSV files are created
    save_dataset_as_csv()
    
    # Train the specified models
    for model_type in args.models:
        if model_type not in ['nmf', 'hybrid']:
            print(f"Warning: Unknown model type '{model_type}'. Skipping.")
            continue
            
        print(f"\nTraining {model_type.upper()} recommendation model...")
        try:
            # Initialize and train the model using our factory
            recommender = get_recommender(
                model_type=model_type, 
                n_components=args.components
            )
            
            # The model should be automatically trained by the factory
            # Let's verify it's trained
            if not recommender.is_trained:
                print(f"Warning: {model_type} model not properly trained. Check factory implementation.")
            
            # Show skill importances for NMF model
            if model_type == 'nmf' and hasattr(recommender, 'get_skill_importance'):
                if args.verbose:
                    skill_importances = recommender.get_skill_importance()
                    print("\nSkill Importances by Latent Factor:")
                    for factor_name in skill_importances.columns:
                        print(f"\n{factor_name}:")
                        top_skills = skill_importances[factor_name].sort_values(ascending=False).head(5)
                        for skill, importance in top_skills.items():
                            print(f"  {skill}: {importance:.4f}")
            
            print(f"{model_type.upper()} model training complete!")
            
        except Exception as e:
            print(f"Error training {model_type} model: {str(e)}")
    
    print("\nAll model training complete!")

if __name__ == "__main__":
    main() 