import os
import sys

# Add project root to Python path to import from other directories
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify
from models.recommendation_model import CourseRecommendationModel
from models.train_model import load_trained_model
from utils.input_processor import parse_user_skills, format_explanation
from utils.visualization import generate_skill_gap_chart, generate_recommendation_explanation
import uuid
import base64
from io import BytesIO

app = Flask(__name__)

# Load trained recommendation model
model = load_trained_model()

# Generate a unique session ID for this API instance
session_id = f"api_user_{uuid.uuid4().hex[:8]}"

if not model:
    print("Error: Failed to load or train model. API may not work correctly.")

@app.route('/api/recommend', methods=['POST'])
def recommend():
    """API endpoint to get course recommendations"""
    data = request.json
    
    if not data or 'skills' not in data:
        return jsonify({'error': 'No skills provided'}), 400
        
    # Parse user skills
    if isinstance(data['skills'], str):
        user_skills = parse_user_skills(data['skills'])
    else:
        user_skills = data['skills']
        
    # Check if user provided a user_id
    user_id = data.get('user_id', session_id)
    
    # Set any career goals
    if 'career_goals' in data:
        model.create_user_profile(user_id, career_goals=[data['career_goals']])
    
    # Get recommendations    
    top_n = data.get('top_n', 5)
    recommendations = model.recommend_courses(user_id, user_skills, top_n=top_n)
    
    # Include explainability data if requested
    include_explanation = data.get('include_explanation', False)
    if include_explanation and recommendations:
        # Add textual explanation
        for rec in recommendations:
            rec['explanation_text'] = format_explanation(rec, user_skills)
    
    return jsonify({'recommendations': recommendations})

@app.route('/api/explain/<course_name>', methods=['POST'])
def explain_recommendation(course_name):
    """Get detailed explanation for a specific course recommendation"""
    data = request.json
    
    if not data:
        return jsonify({'error': 'Missing request data'}), 400
        
    # Parse user skills
    if 'skills' in data:
        if isinstance(data['skills'], str):
            user_skills = parse_user_skills(data['skills'])
        else:
            user_skills = data['skills']
            
        # Check if user provided a user_id
        user_id = data.get('user_id', session_id)
        
        # Update user profile
        model.create_user_profile(user_id, skills=user_skills)
        
        if 'career_goals' in data:
            model.create_user_profile(user_id, career_goals=[data['career_goals']])
        
        # Get explanation
        explanation = model.explain_recommendation(course_name, user_id)
        
        return jsonify(explanation)
    else:
        return jsonify({'error': 'User skills required'}), 400

@app.route('/api/skill_gap/<course_name>', methods=['POST'])
def skill_gap(course_name):
    """Generate a visualization of the skill gap for a specific course"""
    data = request.json
    
    if not data or 'skills' not in data:
        return jsonify({'error': 'No skills provided'}), 400
        
    # Parse user skills
    if isinstance(data['skills'], str):
        user_skills = parse_user_skills(data['skills'])
    else:
        user_skills = data['skills']
    
    # Find the course in the model
    course_data = None
    for course, info in model.course_data.items():
        if course.lower() == course_name.lower():
            course_data = {'course_name': course, 'required_skills': info['required_skills']}
            break
    
    if not course_data:
        return jsonify({'error': 'Course not found'}), 404
    
    # Generate skill gap chart as base64
    chart_data = generate_skill_gap_chart(course_data, user_skills)
    
    return jsonify({
        'course_name': course_data['course_name'],
        'skill_gap_chart': chart_data,
        'total_required_skills': len(course_data['required_skills']),
        'matched_skills': len([s for s in course_data['required_skills'] if s in user_skills]),
        'gap_percentage': round((1 - len([s for s in course_data['required_skills'] if s in user_skills]) / 
                              len(course_data['required_skills'])) * 100, 1)
    })

@app.route('/api/explanation_chart/<course_name>', methods=['POST'])
def explanation_chart(course_name):
    """Generate a visualization explaining a recommendation"""
    data = request.json
    
    if not data or 'skills' not in data:
        return jsonify({'error': 'No skills provided'}), 400
        
    # Parse user skills
    if isinstance(data['skills'], str):
        user_skills = parse_user_skills(data['skills'])
    else:
        user_skills = data['skills']
    
    # Get user_id
    user_id = data.get('user_id', session_id)
    
    # Update user profile
    model.create_user_profile(user_id, skills=user_skills)
    
    # Get recommendations to find this course
    recommendations = model.recommend_courses(user_id, user_skills, top_n=20)
    recommendation = next((r for r in recommendations if r['course_name'].lower() == course_name.lower()), None)
    
    if not recommendation:
        return jsonify({'error': 'Course not found in recommendations'}), 404
    
    # Generate explanation chart
    chart_data = generate_recommendation_explanation(recommendation, user_skills)
    
    return jsonify({
        'course_name': recommendation['course_name'],
        'explanation_chart': chart_data,
        'explanation_factors': recommendation.get('explanation_data', {}).get('recommendation_factors', [])
    })

@app.route('/api/skills', methods=['GET'])
def get_all_skills():
    """Get a list of all skills in the system"""
    all_skills = set()
    
    # Extract all skills from course data
    for course, data in model.course_data.items():
        all_skills.update(data.get('required_skills', []))
    
    return jsonify({'skills': sorted(list(all_skills))})

@app.route('/api/learning_path', methods=['POST'])
def learning_path():
    """Generate a personalized learning path"""
    data = request.json
    
    if not data or 'skills' not in data:
        return jsonify({'error': 'No skills provided'}), 400
        
    # Parse user skills
    if isinstance(data['skills'], str):
        user_skills = parse_user_skills(data['skills'])
    else:
        user_skills = data['skills']
    
    # Get user_id and career goal
    user_id = data.get('user_id', session_id)
    career_goal = data.get('career_goal')
    
    # Update user profile
    model.create_user_profile(user_id, skills=user_skills)
    if career_goal:
        model.create_user_profile(user_id, career_goals=[career_goal])
    
    # Get path length
    path_length = data.get('path_length', 5)
    
    # Generate learning path
    learning_path = model.generate_learning_path(user_id, career_goal, path_length)
    
    return jsonify({'learning_path': learning_path})

if __name__ == '__main__':
    app.run(debug=True, port=5002) 