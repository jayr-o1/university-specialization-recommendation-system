import os
import sys

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify, render_template, redirect, url_for
from models.train_model import load_trained_model
from utils.input_processor import parse_user_skills, format_recommendations, format_similar_courses

app = Flask(__name__, template_folder='templates')

# Load or train the model
model = load_trained_model()

@app.route('/', methods=['GET', 'POST'])
def index():
    """Home page with skill input form"""
    results = None
    similar_courses = None
    
    if request.method == 'POST':
        skills_input = request.form.get('skills', '')
        user_skills = parse_user_skills(skills_input)
        
        if user_skills:
            # Get recommendations
            recommendations = model.recommend_courses(user_skills, top_n=5)
            
            # Get similar courses for top recommendation
            if recommendations:
                top_course = recommendations[0]['course_code']
                similar_courses = model.find_similar_courses(top_course, top_n=3)
            
            return render_template(
                'index.html',
                recommendations=recommendations,
                similar_courses=similar_courses,
                skills_input=skills_input
            )
    
    # GET request or no recommendations
    return render_template('index.html', recommendations=None, skills_input='')

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
    
    return jsonify({'recommendations': recommendations})

@app.route('/api/skills', methods=['GET'])
def api_skills():
    """API endpoint to get all skills"""
    return jsonify({'skills': model.all_skills})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
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
            .similar-courses {
                margin-top: 30px;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f5f5f5;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>University Specialization Recommendation System</h1>
        </div>
        
        <div class="form-container">
            <h2>Enter Your Skills</h2>
            <p>Format: Skill1 : Proficiency1, Skill2 : Proficiency2</p>
            <p>Example: MySQL : Intermediate, Database Design : Advanced</p>
            
            <form method="POST">
                <input type="text" name="skills" placeholder="Enter your skills and proficiency levels" value="{{ skills_input }}">
                <button type="submit">Get Recommendations</button>
            </form>
        </div>
        
        {% if recommendations %}
            <div class="results">
                <h2>Based on your skills, these are the courses that are aligned:</h2>
                
                {% for rec in recommendations %}
                    <div class="course">
                        <div class="course-header">
                            <span>{{ rec.course_code }} - {{ rec.course_name }}</span>
                            <span class="match-percentage">{{ rec.match_percentage }}% Match</span>
                        </div>
                        
                        {% if rec.matched_skills %}
                            <div class="skills-list">
                                <h3>Matched Skills:</h3>
                                <ul>
                                    {% for skill in rec.matched_skills %}
                                        <li>{{ skill }}</li>
                                    {% endfor %}
                                </ul>
                            </div>
                        {% endif %}
                        
                        {% if rec.missing_skills %}
                            <div class="skills-list">
                                <h3>Skills for Further Training:</h3>
                                <ul>
                                    {% for skill in rec.missing_skills[:5] %}
                                        <li>{{ skill }}</li>
                                    {% endfor %}
                                    {% if rec.missing_skills|length > 5 %}
                                        <li>...</li>
                                    {% endif %}
                                </ul>
                            </div>
                        {% endif %}
                    </div>
                {% endfor %}
            </div>
            
            {% if similar_courses %}
                <div class="similar-courses">
                    <h2>Courses where you can apply similar skills:</h2>
                    
                    {% for course in similar_courses %}
                        <div class="course">
                            <div class="course-header">
                                <span>{{ course.course_code }} - {{ course.course_name }}</span>
                                <span class="match-percentage">{{ course.similarity_score }}% Similar</span>
                            </div>
                        </div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endif %}
    </body>
    </html>
    """
    
    # Write the template to file
    with open(os.path.join(templates_dir, 'index.html'), 'w') as f:
        f.write(index_template)
    
    # Run the Flask app
    app.run(debug=True, port=5001) 