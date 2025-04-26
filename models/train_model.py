import os
import sys
import pickle
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class CourseRecommendationModel:
    def __init__(self, course_data_path):
        """Initialize the recommendation model with course data."""
        self.course_data_path = course_data_path
        self.course_data = self._load_course_data()
        self.all_skills = self._extract_all_skills()
        self.skill_vectors = None
        self.course_vectors = None
        self.vectorizer = None
        self._build_skill_vectors()
        
    def _load_course_data(self):
        """Load course data from JSON file."""
        try:
            with open(self.course_data_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading course data: {str(e)}")
            return {}
            
    def _extract_all_skills(self):
        """Extract all unique skills from course data."""
        all_skills = set()
        for course_info in self.course_data.values():
            all_skills.update(course_info.get('required_skills', []))
        return sorted(list(all_skills))
        
    def _build_skill_vectors(self):
        """Build TF-IDF vectors for skills and courses."""
        # Create skill descriptions for TF-IDF
        skill_descriptions = []
        course_descriptions = []
        course_names = []
        
        # Create descriptions for skills
        for skill in self.all_skills:
            skill_descriptions.append(skill)
            
        # Create descriptions for courses
        for course_name, course_info in self.course_data.items():
            skills = course_info.get('required_skills', [])
            course_descriptions.append(' '.join(skills))
            course_names.append(course_name)
            
        # Create TF-IDF vectors
        self.vectorizer = TfidfVectorizer(stop_words='english')
        
        # Fit on all documents (skills + courses)
        all_documents = skill_descriptions + course_descriptions
        self.vectorizer.fit(all_documents)
        
        # Transform skills and courses
        self.skill_vectors = self.vectorizer.transform(skill_descriptions)
        self.course_vectors = self.vectorizer.transform(course_descriptions)
        self.course_names = course_names
        
    def recommend_courses(self, user_skills, top_n=5):
        """
        Recommend courses based on user skills.
        
        Args:
            user_skills: Dictionary of user skills with proficiency and certification info
            top_n: Number of recommendations to return
            
        Returns:
            List of recommended courses with match details
        """
        if not user_skills:
            return []
            
        # Create user skill vector
        user_skill_text = ' '.join(user_skills.keys())
        user_vector = self.vectorizer.transform([user_skill_text])
        
        # Calculate similarity with all courses
        similarities = cosine_similarity(user_vector, self.course_vectors)[0]
        
        # Get top N courses
        top_indices = similarities.argsort()[-top_n:][::-1]
        
        recommendations = []
        for idx in top_indices:
            course_name = self.course_names[idx]
            course_info = self.course_data[course_name]
            required_skills = set(course_info.get('required_skills', []))
            
            # Calculate matched and missing skills
            matched_skills = required_skills.intersection(set(user_skills.keys()))
            missing_skills = required_skills - set(user_skills.keys())
            
            # Calculate match percentage
            match_percentage = (len(matched_skills) / len(required_skills)) * 100 if required_skills else 0
            
            # Format matched skills with proficiency and certification
            formatted_matched_skills = []
            for skill in matched_skills:
                if isinstance(user_skills[skill], dict):
                    proficiency = user_skills[skill].get("proficiency", "Intermediate")
                    is_certified = user_skills[skill].get("isBackedByCertificate", False)
                    certified_str = " (certified)" if is_certified else ""
                    formatted_matched_skills.append(f"{skill} ({proficiency}{certified_str})")
                else:
                    formatted_matched_skills.append(f"{skill} ({user_skills[skill]})")
            
            recommendations.append({
                "course_name": course_name,
                "match_percentage": match_percentage,
                "matched_skills": formatted_matched_skills,
                "missing_skills": list(missing_skills),
                "similarity_score": float(similarities[idx])
            })
            
        return recommendations
        
    def find_similar_courses(self, course_name, top_n=5):
        """Find courses similar to a given course."""
        if course_name not in self.course_data:
            return []
            
        # Get course index
        course_idx = self.course_names.index(course_name)
        
        # Calculate similarity with all other courses
        similarities = cosine_similarity(self.course_vectors[course_idx:course_idx+1], self.course_vectors)[0]
        
        # Get top N similar courses (excluding the input course)
        similar_indices = similarities.argsort()[-top_n-1:-1][::-1]
        
        similar_courses = []
        for idx in similar_indices:
            similar_courses.append({
                "course_name": self.course_names[idx],
                "similarity_score": float(similarities[idx]) * 100
            })
            
        return similar_courses

def load_trained_model():
    """Load the trained recommendation model."""
    model_path = os.path.join(os.path.dirname(__file__), 'trained_model.pkl')
    if os.path.exists(model_path):
        with open(model_path, 'rb') as f:
            return pickle.load(f)
    return None

def train_model():
    """Train the recommendation model and save it to disk."""
    print("Loading course skills data...")
    
    # Path to course_skills.json
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'enhanced_course_skills.json')
    
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
    """Test the model with sample skills."""
    print("\nTesting model with sample skills...")
    
    # Sample test case
    test_skills = {
        "Database Design": {"proficiency": "Advanced", "isBackedByCertificate": True},
        "SQL": {"proficiency": "Intermediate", "isBackedByCertificate": False},
        "JavaScript": {"proficiency": "Beginner", "isBackedByCertificate": False}
    }
    
    print(f"Sample input: {test_skills}")
    
    # Get recommendations
    recommendations = model.recommend_courses(test_skills, top_n=3)
    
    print("\nSample recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['course_name']} - {rec['match_percentage']:.1f}% Match")
        print(f"   Matched skills: {len(rec['matched_skills'])}")
        print(f"   Missing skills: {len(rec['missing_skills'])}")
    
    # Find similar courses for the top recommendation
    if recommendations:
        top_course = recommendations[0]['course_name']
        similar_courses = model.find_similar_courses(top_course, top_n=2)
        
        print(f"\nCourses similar to {top_course}:")
        for i, course in enumerate(similar_courses, 1):
            print(f"{i}. {course['course_name']} - {course['similarity_score']:.1f}% Similar")

if __name__ == "__main__":
    train_model() 