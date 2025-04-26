import os
import sys
import pickle
import json

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def load_trained_model():
    """
    This is a simplified version that returns None, 
    as we don't need the recommendation model for the faculty system.
    """
    return None

def train_model():
    """
    Train the recommendation model and save it to disk
    """
    print("Loading course skills data...")
    
    # Path to course_skills.json
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'course_skills.json')
    
    # Check if data file exists
    if not os.path.exists(data_path):
        print(f"Error: Data file not found at {data_path}")
        return False
    
    try:
        # Initialize and train the model
        print("Initializing recommendation model...")
        model = CourseRecommendationModel(data_path)
        
        # Count total number of unique skills
        print(f"Total unique skills found: {len(model.all_skills)}")
        
        # Count total number of courses
        print(f"Total courses loaded: {len(model.course_data)}")
        
        # Save the trained model
        model_path = os.path.join(os.path.dirname(__file__), 'trained_model.pkl')
        print(f"Saving trained model to {model_path}...")
        
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        print("Model training completed and saved successfully!")
        
        # Test the model with a sample input
        test_model(model)
        
        return True
    
    except Exception as e:
        print(f"Error training model: {str(e)}")
        return False

def test_model(model):
    """Test the model with sample skills"""
    print("\nTesting model with sample skills...")
    
    # Sample test case
    test_skills = {
        "Database Design": "Advanced",
        "SQL": "Intermediate",
        "JavaScript": "Beginner"
    }
    
    print(f"Sample input: {test_skills}")
    
    # Get recommendations
    recommendations = model.recommend_courses(test_skills, top_n=3)
    
    print("\nSample recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['course_name']} - {rec['match_percentage']}% Match")
        print(f"   Matched skills: {len(rec['matched_skills'])}")
        print(f"   Missing skills: {len(rec['missing_skills'])}")
    
    # Find similar courses for the top recommendation
    if recommendations:
        top_course = recommendations[0]['course_name']
        similar_courses = model.find_similar_courses(top_course, top_n=2)
        
        print(f"\nCourses similar to {top_course}:")
        for i, course in enumerate(similar_courses, 1):
            print(f"{i}. {course['course_name']} - {course['similarity_score']}% Similar")

if __name__ == "__main__":
    train_model() 