import sys
import os

# Add project root to Python path to import from other directories
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.recommendation_model import CourseRecommendationModel
from models.train_model import load_trained_model
from utils.input_processor import parse_user_skills, format_recommendations, format_similar_courses

def main():
    # Load or train the model
    print("Loading recommendation model...")
    model = load_trained_model()
    
    if not model:
        print("Error: Failed to load or train model.")
        return
    
    print("Welcome to the University Specialization Recommendation System!")
    print("=" * 70)
    print("Enter your skills and proficiency levels (e.g., 'MySQL : Intermediate, Database Design : Advanced')")
    print("Type 'exit' to quit")
    print("=" * 70)
    
    while True:
        # Get user input
        skills_input = input("\nEnter your skills: ")
        
        if skills_input.lower() == 'exit':
            print("Thank you for using the recommendation system. Goodbye!")
            break
        
        # Parse user skills
        user_skills = parse_user_skills(skills_input)
        
        if not user_skills:
            print("No valid skills provided. Please try again.")
            continue
        
        print(f"\nAnalyzing {len(user_skills)} skills...")
        
        # Get course recommendations
        recommendations = model.recommend_courses(user_skills, top_n=10)
        
        # Display recommendations
        print("\n" + "=" * 70)
        print(format_recommendations(recommendations))
        
        # If we have recommendations, also show similar courses for the top recommendation
        if recommendations:
            top_course = recommendations[0]['course_name']
            similar_courses = model.find_similar_courses(top_course, top_n=3)
            
            print("\n" + "=" * 70)
            print(format_similar_courses(similar_courses, top_course))
            print("=" * 70)

if __name__ == "__main__":
    main() 