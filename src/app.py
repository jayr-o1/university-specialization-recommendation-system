import os
import sys

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify, render_template, redirect, url_for, send_file
from models.train_model import load_trained_model
from utils.input_processor import parse_user_skills, format_recommendations, format_similar_courses
from utils.visualization import generate_skill_gap_chart, generate_recommendation_explanation
import json
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for chart generation
import matplotlib.pyplot as plt
import base64
from io import BytesIO

app = Flask(__name__, template_folder='templates', static_folder='static')

# Load or train the model
model = load_trained_model()

@app.route('/', methods=['GET', 'POST'])
def index():
    """Home page with skill input form"""
    results = None
    similar_courses = None
    explanation_chart = None
    skill_gap_chart = None
    
    if request.method == 'POST':
        skills_input = request.form.get('skills', '')
        user_skills = parse_user_skills(skills_input)
        
        if user_skills:
            # Get recommendations
            recommendations = model.recommend_courses(user_skills, top_n=5)
            
            # Get similar courses for top recommendation
            if recommendations:
                top_course = recommendations[0]['course_name']
                similar_courses = model.find_similar_courses(top_course, top_n=3)
                
                # Generate explanation chart for top course
                explanation_chart = generate_recommendation_explanation(recommendations[0], user_skills)
                
                # Get course details for skill gap visualization
                course_data = None
                for course_name, info in model.course_data.items():
                    if course_name.lower() == top_course.lower():
                        course_data = {
                            'course_name': course_name,
                            'required_skills': info['required_skills']
                        }
                        break
                
                # Generate skill gap visualization
                if course_data:
                    skill_gap_chart = generate_skill_gap_chart(course_data, user_skills)
            
            return render_template(
                'index.html',
                recommendations=recommendations,
                similar_courses=similar_courses,
                skills_input=skills_input,
                explanation_chart=explanation_chart,
                skill_gap_chart=skill_gap_chart
            )
    
    # GET request or no recommendations
    return render_template('index.html', recommendations=None, skills_input='', explanation_chart=None, skill_gap_chart=None)

@app.route('/api/recommend', methods=['POST'])
def api_recommend():
    """API endpoint for recommendations"""
    data = request.json
    
    if not data or 'skills' not in data:
        return jsonify({'error': 'No skills provided'}), 400
    
    # Parse skills
    if isinstance(data['skills'], str):
        user_skills = parse_user_skills(data['skills'])
    else:
        user_skills = data['skills']
    
    # Get recommendations
    top_n = data.get('top_n', 5)
    recommendations = model.recommend_courses(user_skills, top_n=top_n)
    
    # Add explanation data if requested
    if data.get('include_explanation', False) and recommendations:
        explanation_data = generate_recommendation_explanation(recommendations[0], user_skills, as_dict=True)
        recommendations[0]['explanation_data'] = explanation_data
    
    return jsonify({'recommendations': recommendations})

@app.route('/api/skills', methods=['GET'])
def api_skills():
    """API endpoint to get all skills"""
    return jsonify({'skills': model.all_skills})

@app.route('/skill_gap/<course_name>', methods=['GET'])
def skill_gap(course_name):
    """Generate and display a skill gap visualization for a specific course"""
    skills_param = request.args.get('skills', '')
    user_skills = parse_user_skills(skills_param)
    
    # Find the course in the model
    course_data = None
    for course, info in model.course_data.items():
        if course.lower() == course_name.lower():
            course_data = {'course_name': course, 'required_skills': info['required_skills']}
            break
    
    if not course_data:
        return jsonify({'error': 'Course not found'}), 404
    
    # Generate skill gap chart
    chart_path = generate_skill_gap_chart(course_data, user_skills, save_path=f"static/skill_gap_{course_name.replace(' ', '_')}.png")
    
    return send_file(chart_path, mimetype='image/png')

@app.route('/api/certificate_info', methods=['GET'])
def certificate_info():
    """Get information about certificate-based skill matching"""
    return jsonify({
        'description': 'Adding certification information to your skills improves your match score.',
        'format': 'In skill entries, add a third parameter (true/false) to indicate certification status.',
        'example': 'Python : Advanced : true',
        'benefit': 'Certified skills receive a 10% boost in matching scores.'
    })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    
    # Create a basic HTML template for the index page
    index_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Course Recommendation System</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                background-color: #2a5885;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px;
                margin-bottom: 20px;
            }
            .form-container {
                margin-bottom: 30px;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
            input[type="text"] {
                width: 100%;
                padding: 10px;
                margin: 10px 0;
                box-sizing: border-box;
            }
            button {
                background-color: #2a5885;
                color: white;
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            .results {
                margin-top: 20px;
            }
            .course {
                margin-bottom: 20px;
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            .course-header {
                display: flex;
                justify-content: space-between;
                margin-bottom: 10px;
                font-weight: bold;
            }
            .match-percentage {
                color: #2a5885;
                font-weight: bold;
            }
            .skills-list {
                margin-top: 10px;
            }
            .certificate-info {
                background-color: #e6f7ff;
                border-left: 4px solid #1890ff;
                padding: 10px 15px;
                margin: 10px 0;
                border-radius: 0 5px 5px 0;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>University Specialization Recommendation System</h1>
        </div>
        
        <div class="form-container">
            <h2>Enter Your Skills</h2>
            <p>Format: Skill1 : Proficiency1 : CertificationStatus, Skill2 : Proficiency2 : CertificationStatus</p>
            <p>Example: MySQL : Intermediate : true, Database Design : Advanced : false</p>
            <div class="certificate-info">
                <p><strong>Note:</strong> Adding a third value of "true" indicates you have certification for that skill, which will boost your matching score.</p>
                <p>Example: Python : Advanced : true (indicates you have certification for Python)</p>
            </div>
            
            <form method="POST">
                <input type="text" name="skills" placeholder="Enter your skills, proficiency levels, and certification status">
                <button type="submit">Get Recommendations</button>
            </form>
        </div>
        
        <div class="results">
            <p>Enter your skills above to get course recommendations.</p>
        </div>
    </body>
    </html>
    """
    
    # Create default template file if it doesn't exist
    index_template_path = os.path.join(templates_dir, 'index.html')
    if not os.path.exists(index_template_path):
        with open(index_template_path, 'w') as f:
            f.write(index_template)
    
    app.run(debug=True, port=5001) 