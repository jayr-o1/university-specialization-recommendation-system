import os
import sys

# Add project root to Python path to import from other directories
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify
from models.recommendation_model import CourseRecommendationModel
from models.train_model import load_trained_model
from utils.input_processor import parse_user_skills

app = Flask(__name__)

# Load trained recommendation model
model = load_trained_model()

if not model:
    print("Error: Failed to load or train model. API may not work correctly.")

@app.route('/recommend', methods=['POST'])
def recommend_courses():
    """API endpoint to get course recommendations based on user skills"""
    data = request.json
    
    if not data or 'skills' not in data:
        return jsonify({'error': 'No skills provided'}), 400
    
    # Two input formats supported:
    # 1. String format: "MySQL : Intermediate, Database Design : Advanced"
    # 2. Dictionary format: {"MySQL": "Intermediate", "Database Design": "Advanced"}
    
    if isinstance(data['skills'], str):
        user_skills = parse_user_skills(data['skills'])
    elif isinstance(data['skills'], dict):
        user_skills = data['skills']
    else:
        return jsonify({'error': 'Invalid skills format'}), 400
    
    # Get number of recommendations to return
    top_n = data.get('top_n', 5)
    
    # Get recommendations
    recommendations = model.recommend_courses(user_skills, top_n=top_n)
    
    # Get similar courses for the top recommendation if requested
    if recommendations and data.get('include_similar', False):
        top_course = recommendations[0]['course_code']
        similar_courses = model.find_similar_courses(top_course, top_n=3)
        return jsonify({
            'recommendations': recommendations,
            'similar_courses': similar_courses
        })
    
    return jsonify({'recommendations': recommendations})

@app.route('/similar', methods=['GET'])
def find_similar_courses():
    """API endpoint to find courses similar to a given course"""
    course_code = request.args.get('course_code')
    
    if not course_code:
        return jsonify({'error': 'No course code provided'}), 400
    
    top_n = request.args.get('top_n', 5, type=int)
    similar_courses = model.find_similar_courses(course_code, top_n=top_n)
    
    return jsonify({'similar_courses': similar_courses})

@app.route('/courses', methods=['GET'])
def get_courses():
    """API endpoint to get all available courses"""
    courses = []
    for course_code, course_info in model.course_data.items():
        courses.append({
            'course_code': course_code,
            'name': course_info['name'],
            'skills_count': len(course_info['required_skills'])
        })
    
    return jsonify({'courses': courses})

@app.route('/skills', methods=['GET'])
def get_all_skills():
    """API endpoint to get all available skills"""
    return jsonify({'skills': model.all_skills})

if __name__ == '__main__':
    app.run(debug=True, port=5000) 