import sys
import os
import uuid
import time

# Add project root to Python path to import from other directories
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.enhanced_recommendation_model import EnhancedRecommendationModel
from utils.input_processor import parse_user_skills

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    
    course_skills_path = os.path.join(data_dir, 'course_skills.json')
    user_ratings_path = os.path.join(data_dir, 'user_ratings.json')
    
    # Initialize the enhanced recommendation model
    print("Loading enhanced recommendation model...")
    model = EnhancedRecommendationModel(course_skills_path, user_ratings_path)
    
    # Generate a unique session ID for this user
    session_id = f"user_{uuid.uuid4().hex[:8]}"
    
    print("\n" + "=" * 70)
    print("Welcome to the Enhanced University Specialization Recommendation System!")
    print("=" * 70)
    print("\nThis upgraded system includes:")
    print("- Skill knowledge graph for better skill relationships")
    print("- Collaborative filtering based on other users' preferences")
    print("- Personalized learning paths based on your career goals")
    print("- Next skill recommendations to guide your learning journey")
    print("=" * 70)
    print("\nAvailable commands:")
    print("  skills - Enter your skills and get course recommendations")
    print("  path - Generate a personalized learning path")
    print("  rate - Rate a course you've taken")
    print("  popular - See popular courses")
    print("  top - See top-rated courses")
    print("  similar <course name> - Find courses similar to a specific course")
    print("  nextskills - Get recommendations for skills to learn next")
    print("  exit - Exit the application")
    print("=" * 70)
    
    # Initialize user profile
    user_skills = {}
    career_goal = None
    
    while True:
        # Get user command
        command = input("\nEnter command: ").strip().lower()
        
        if command == 'exit':
            print("Thank you for using the enhanced recommendation system. Goodbye!")
            break
            
        elif command == 'skills':
            # Get user skills
            skills_input = input("\nEnter your skills and proficiency levels (e.g., 'MySQL : Intermediate, Database Design : Advanced'): ")
            user_skills = parse_user_skills(skills_input)
            
            if not user_skills:
                print("No valid skills provided. Please try again.")
                continue
                
            print(f"\nAnalyzing {len(user_skills)} skills...")
            
            # Create or update user profile
            model.create_user_profile(session_id, skills=user_skills)
            
            # Get recommendations
            recommendations = model.recommend_courses(session_id, top_n=10)
            
            # Display recommendations
            print("\n" + "=" * 70)
            print("Enhanced Course Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec['course_name']} - {rec['combined_score']}% Match")
                
                if 'predicted_rating' in rec:
                    print(f"   Predicted Rating: {rec['predicted_rating']:.1f}/5.0")
                    
                if rec['matched_skills']:
                    print("   Matched Skills:")
                    for skill in rec['matched_skills'][:3]:  # Show only first 3
                        print(f"   - {skill}")
                    if len(rec['matched_skills']) > 3:
                        print(f"   - ... and {len(rec['matched_skills']) - 3} more")
                
                if rec['missing_skills']:
                    print("   Skills for Further Training:")
                    for skill in rec['missing_skills'][:3]:  # Show only first 3
                        print(f"   - {skill}")
                    if len(rec['missing_skills']) > 3:
                        print(f"   - ... and {len(rec['missing_skills']) - 3} more")
                        
                print()  # Empty line between recommendations
            
        elif command == 'path':
            # Check if user has skills
            if not user_skills:
                print("Please enter your skills first using the 'skills' command.")
                continue
                
            # Get career goal
            goal_input = input("\nEnter your career goal or target specialization: ")
            career_goal = goal_input.strip()
            
            # Update user profile
            model.create_user_profile(session_id, career_goals=[career_goal])
            
            print(f"\nGenerating personalized learning path for {career_goal}...")
            
            # Generate learning path
            learning_path = model.generate_learning_path(session_id, career_goal)
            
            if not learning_path:
                print("Could not generate a learning path. Try a different career goal.")
                continue
                
            # Display learning path
            print("\n" + "=" * 70)
            print(f"Personalized Learning Path for {career_goal}:")
            print("=" * 70)
            
            for step in learning_path:
                print(f"\nStep {step['step']}: {step['course_name']} - {step['match_percentage']}% Match")
                
                if step['next_steps_rationale']:
                    print(f"Rationale: {step['next_steps_rationale']}")
                    
                if step['matched_skills']:
                    print("You already have these relevant skills:")
                    for skill in step['matched_skills'][:3]:
                        print(f"- {skill}")
                    if len(step['matched_skills']) > 3:
                        print(f"- ... and {len(step['matched_skills']) - 3} more")
                        
                if step['missing_skills']:
                    print("Skills you'll learn in this course:")
                    for skill in step['missing_skills'][:3]:
                        print(f"- {skill}")
                    if len(step['missing_skills']) > 3:
                        print(f"- ... and {len(step['missing_skills']) - 3} more")
            
        elif command == 'rate':
            # Get course to rate
            course_input = input("\nEnter the course name you want to rate: ")
            course_name = course_input.strip()
            
            try:
                rating = float(input(f"Enter your rating for '{course_name}' (1-5): "))
                if rating < 1 or rating > 5:
                    print("Rating must be between 1 and 5.")
                    continue
            except ValueError:
                print("Please enter a valid number between 1 and 5.")
                continue
                
            # Add the rating
            model.add_user_course_rating(session_id, course_name, rating)
            print(f"Thank you for rating {course_name}!")
            
        elif command == 'popular':
            # Get popular courses
            popular_courses = model.get_popular_courses(top_n=10)
            
            print("\n" + "=" * 70)
            print("Most Popular Courses:")
            
            for i, course in enumerate(popular_courses, 1):
                print(f"{i}. {course['course_name']} - {course['num_ratings']} ratings")
            
        elif command == 'top':
            # Get top-rated courses
            top_courses = model.get_top_rated_courses(min_ratings=3, top_n=10)
            
            print("\n" + "=" * 70)
            print("Top-Rated Courses:")
            
            for i, course in enumerate(top_courses, 1):
                print(f"{i}. {course['course_name']} - {course['avg_rating']:.2f}/5.0 average rating")
            
        elif command.startswith('similar '):
            # Extract course name
            course_name = command[8:].strip()
            
            if not course_name:
                print("Please specify a course name. Usage: similar <course name>")
                continue
                
            # Find similar courses
            similar_courses = model.find_similar_courses(course_name, top_n=5)
            
            if not similar_courses:
                print(f"No similar courses found for '{course_name}'. Please check the course name.")
                continue
                
            print("\n" + "=" * 70)
            print(f"Courses similar to '{course_name}':")
            
            for i, course in enumerate(similar_courses, 1):
                print(f"{i}. {course['course_name']} - {course['similarity_score']}% Similar")
            
        elif command == 'nextskills':
            # Check if user has skills
            if not user_skills:
                print("Please enter your skills first using the 'skills' command.")
                continue
                
            # Get next skill recommendations
            next_skills = model.get_next_skill_recommendations(session_id, top_n=10)
            
            if not next_skills:
                print("Could not generate skill recommendations. Try adding more initial skills.")
                continue
                
            print("\n" + "=" * 70)
            print("Recommended Skills to Learn Next:")
            
            for i, skill in enumerate(next_skills, 1):
                print(f"{i}. {skill['skill']} - {skill['relevance']:.2f} relevance score")
                
        else:
            print("Unknown command. Type 'exit' to quit or see the list of available commands.")

if __name__ == "__main__":
    main() 