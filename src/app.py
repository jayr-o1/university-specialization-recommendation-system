import os
import sys

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify, render_template, redirect, url_for, send_file
from utils.faculty_skills_analyzer import FacultySkillsAnalyzer
from scripts.faculty_teaching_advisor import FacultyTeachingAdvisor
import json
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for chart generation
import matplotlib.pyplot as plt
import base64
from io import BytesIO

app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route('/', methods=['GET'])
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/faculty-development', methods=['GET', 'POST'])
def faculty_development():
    """Faculty Development Advisor page"""
    results = None
    department = None
    skills_input = ''
    
    if request.method == 'POST':
        name = request.form.get('name', 'Faculty Member')
        department = request.form.get('department', 'computer_science')
        skills_input = request.form.get('skills', '')
        skills = [skill.strip() for skill in skills_input.split(',') if skill.strip()]
        
        if skills:
            # Initialize analyzer
            analyzer = FacultySkillsAnalyzer()
            
            # Identify skill gaps
            skill_gaps = analyzer.identify_skill_gaps(skills, department)
            
            # Get development recommendations
            recommendations = analyzer.get_development_recommendations(skill_gaps)
            
            # Save analysis to file
            output_dir = 'data/faculty_analysis'
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"{name.replace(' ', '_').lower()}_analysis.json")
            
            analyzer.save_analysis({
                "faculty_name": name,
                "skill_gaps": skill_gaps,
                "recommendations": recommendations
            }, output_file)
            
            results = {
                'name': name,
                'department': department,
                'matched_skills': skill_gaps['matched_skills'],
                'recommendations': recommendations
            }
    
    return render_template(
        'faculty_development.html',
        results=results,
        department=department,
        skills_input=skills_input
    )

@app.route('/faculty-teaching', methods=['GET', 'POST'])
def faculty_teaching():
    """Faculty Teaching Advisor page"""
    results = None
    skills_input = ''
    
    if request.method == 'POST':
        name = request.form.get('name', 'Faculty Member')
        skills_input = request.form.get('skills', '')
        threshold = int(request.form.get('threshold', '60'))
        
        # Parse skills
        faculty_skills = {}
        for skill_entry in skills_input.split(','):
            skill_entry = skill_entry.strip()
            if not skill_entry:
                continue
                
            parts = skill_entry.split(':')
            
            # Basic validation
            skill_name = parts[0].strip()
            if not skill_name:
                continue
                
            if len(parts) >= 3:
                # Full format with proficiency and certification
                proficiency = parts[1].strip() if parts[1].strip() else "Intermediate"
                cert_value = parts[2].strip().lower()
                is_certified = cert_value == 'true' or cert_value in ('yes', 'y')
                faculty_skills[skill_name] = {
                    "proficiency": proficiency,
                    "isBackedByCertificate": is_certified
                }
            elif len(parts) == 2:
                # Proficiency only
                proficiency = parts[1].strip() if parts[1].strip() else "Intermediate"
                faculty_skills[skill_name] = {
                    "proficiency": proficiency,
                    "isBackedByCertificate": False
                }
            else:
                # Skill name only
                faculty_skills[skill_name] = {
                    "proficiency": "Intermediate",
                    "isBackedByCertificate": False
                }
        
        if faculty_skills:
            # Print debug info
            print("DEBUG: Faculty skills submitted:")
            for skill, details in faculty_skills.items():
                print(f"  - {skill}: {details}")
            print(f"DEBUG: Threshold set to: {threshold}%")
            
            # Initialize advisor
            advisor = FacultyTeachingAdvisor()
            
            # Debug available courses
            try:
                print("DEBUG: Number of courses available in advisor:", len(advisor.skill_matcher.course_data))
                print("DEBUG: Sample courses:", list(advisor.skill_matcher.course_data.keys())[:5])
            except Exception as e:
                print(f"DEBUG: Error accessing course data: {e}")
            
            # Find teachable courses
            teachable_courses = advisor.find_teachable_courses(faculty_skills, threshold=threshold)
            
            # Debug teachable courses
            print(f"DEBUG: Found {len(teachable_courses)} courses matching at {threshold}% threshold")
            if teachable_courses:
                print("DEBUG: Top matching course:", teachable_courses[0])
            
            # Try with lower threshold for debugging
            if not teachable_courses:
                lower_threshold = 30
                print(f"DEBUG: No matches at {threshold}%, trying lower threshold {lower_threshold}%")
                test_courses = advisor.find_teachable_courses(faculty_skills, threshold=lower_threshold)
                if test_courses:
                    print(f"DEBUG: Found {len(test_courses)} courses at {lower_threshold}% threshold")
                    print(f"DEBUG: Best match: {test_courses[0]['course_name']} - {test_courses[0]['match_percentage']}%")
            
            # Identify skill gaps
            skill_gaps = advisor.identify_skill_gaps(faculty_skills)
            
            # Save analysis to file
            output_dir = 'data/faculty_analysis'
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"{name.replace(' ', '_').lower()}_teaching_analysis.json")
            
            with open(output_file, 'w') as f:
                json.dump({
                    "faculty_name": name,
                    "teachable_courses": teachable_courses,
                    "skill_gaps": skill_gaps
                }, f, indent=4)
            
            results = {
                'name': name,
                'teachable_courses': teachable_courses,
                'skill_gaps': skill_gaps
            }
    
    return render_template(
        'faculty_teaching.html',
        results=results,
        skills_input=skills_input
    )

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
        <title>Faculty Skills Development System</title>
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
            .nav-menu {
                display: flex;
                justify-content: center;
                margin-bottom: 30px;
            }
            .nav-item {
                margin: 0 15px;
                padding: 10px 20px;
                background-color: #f0f0f0;
                border-radius: 5px;
                text-decoration: none;
                color: #333;
                font-weight: bold;
            }
            .nav-item:hover {
                background-color: #e0e0e0;
            }
            .active {
                background-color: #2a5885;
                color: white;
            }
            .main-content {
                text-align: center;
                padding: 40px;
                background-color: #f9f9f9;
                border-radius: 5px;
            }
            .btn {
                display: inline-block;
                margin: 20px 10px;
                padding: 15px 30px;
                background-color: #2a5885;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
            }
            .btn:hover {
                background-color: #1e4060;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Faculty Skills Development System</h1>
        </div>
        
        <div class="nav-menu">
            <a href="/" class="nav-item active">Home</a>
            <a href="/faculty-development" class="nav-item">Faculty Development</a>
            <a href="/faculty-teaching" class="nav-item">Teaching Advisor</a>
        </div>
        
        <div class="main-content">
            <h2>Welcome to the Faculty Skills Development System</h2>
            <p>This system is designed to help faculty members identify skill gaps and improve teaching competencies.</p>
            
            <div>
                <a href="/faculty-development" class="btn">Faculty Development Advisor</a>
                <a href="/faculty-teaching" class="btn">Teaching Advisor</a>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Create faculty development template
    faculty_development_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Faculty Development Advisor</title>
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
            .nav-menu {
                display: flex;
                justify-content: center;
                margin-bottom: 30px;
            }
            .nav-item {
                margin: 0 15px;
                padding: 10px 20px;
                background-color: #f0f0f0;
                border-radius: 5px;
                text-decoration: none;
                color: #333;
                font-weight: bold;
            }
            .nav-item:hover {
                background-color: #e0e0e0;
            }
            .active {
                background-color: #2a5885;
                color: white;
            }
            .form-container {
                margin-bottom: 30px;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
            input, select {
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
            .section {
                margin-bottom: 20px;
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            .skill-item {
                background-color: #f0f0f0;
                padding: 8px 12px;
                margin: 5px;
                border-radius: 15px;
                display: inline-block;
            }
            .high-priority {
                border-left: 4px solid #e74c3c;
                padding-left: 10px;
            }
            .medium-priority {
                border-left: 4px solid #f39c12;
                padding-left: 10px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Faculty Skills Development Advisor</h1>
        </div>
        
        <div class="nav-menu">
            <a href="/" class="nav-item">Home</a>
            <a href="/faculty-development" class="nav-item active">Faculty Development</a>
            <a href="/faculty-teaching" class="nav-item">Teaching Advisor</a>
        </div>

        <div class="form-container">
            <h2>Enter Your Information</h2>
            
            <form method="POST">
                <div>
                    <label for="name">Your Name:</label>
                    <input type="text" id="name" name="name" required>
                </div>
                
                <div>
                    <label for="department">Select Your Department/Area:</label>
                    <select id="department" name="department">
                        <option value="data_science">Data Science</option>
                        <option value="computer_science">Computer Science</option>
                        <option value="information_systems">Information Systems</option>
                        <option value="software_engineering">Software Engineering</option>
                    </select>
                </div>
                
                <div>
                    <label for="skills">Enter Your Current Skills (comma-separated):</label>
                    <input type="text" id="skills" name="skills" placeholder="Python, Machine Learning, Data Analysis" value="{{ skills_input }}" required>
                </div>
                
                <button type="submit">Analyze Skills</button>
            </form>
        </div>

        {% if results %}
        <div class="results">
            <h2>Your Skill Analysis</h2>
            
            <div class="section">
                <h3>Skills You Already Have Matching Industry Demands</h3>
                
                {% if results.matched_skills.high_demand %}
                <h4>High-demand Skills:</h4>
                <div>
                    {% for skill in results.matched_skills.high_demand %}
                    <span class="skill-item">{{ skill }}</span>
                    {% endfor %}
                </div>
                {% endif %}
                
                {% if results.matched_skills.emerging %}
                <h4>Emerging Skills:</h4>
                <div>
                    {% for skill in results.matched_skills.emerging %}
                    <span class="skill-item">{{ skill }}</span>
                    {% endfor %}
                </div>
                {% endif %}
                
                {% if not results.matched_skills.high_demand and not results.matched_skills.emerging %}
                <p>No direct matches found with in-demand industry skills.</p>
                {% endif %}
            </div>
            
            <div class="section">
                <h3>Recommended Skill Development Areas</h3>
                
                {% if not results.recommendations %}
                <p>No specific recommendations found.</p>
                {% else %}
                    {% for rec in results.recommendations %}
                    <div class="section {% if rec.priority == 'high' %}high-priority{% else %}medium-priority{% endif %}">
                        <h4>{{ rec.skill }} (Priority: {{ rec.priority }})</h4>
                        <p><strong>Reason:</strong> {{ rec.reason }}</p>
                        
                        {% if rec.related_faculty_skills %}
                        <p><strong>Related skills you already have:</strong> {{ rec.related_faculty_skills|join(', ') }}</p>
                        {% endif %}
                        
                        {% if rec.prerequisites %}
                        <p><strong>Prerequisites:</strong> {{ rec.prerequisites|join(', ') }}</p>
                        
                        {% if rec.missing_prerequisites %}
                        <p><strong>Missing prerequisites:</strong> {{ rec.missing_prerequisites|join(', ') }}</p>
                        {% endif %}
                        {% endif %}
                        
                        <p><strong>Estimated learning time:</strong> {{ rec.estimated_learning_time }}</p>
                    </div>
                    {% endfor %}
                {% endif %}
            </div>
        </div>
        {% endif %}
    </body>
    </html>
    """
    
    # Create faculty teaching template
    faculty_teaching_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Faculty Teaching Advisor</title>
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
            .nav-menu {
                display: flex;
                justify-content: center;
                margin-bottom: 30px;
            }
            .nav-item {
                margin: 0 15px;
                padding: 10px 20px;
                background-color: #f0f0f0;
                border-radius: 5px;
                text-decoration: none;
                color: #333;
                font-weight: bold;
            }
            .nav-item:hover {
                background-color: #e0e0e0;
            }
            .active {
                background-color: #2a5885;
                color: white;
            }
            .form-container {
                margin-bottom: 30px;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
            input, select {
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
            .section {
                margin-bottom: 20px;
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            .course {
                margin-bottom: 15px;
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
            .skill-matched {
                color: #27ae60;
                margin-left: 20px;
            }
            .skill-missing {
                color: #e74c3c;
                margin-left: 20px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Faculty Teaching Advisor</h1>
        </div>
        
        <div class="nav-menu">
            <a href="/" class="nav-item">Home</a>
            <a href="/faculty-development" class="nav-item">Faculty Development</a>
            <a href="/faculty-teaching" class="nav-item active">Teaching Advisor</a>
        </div>

        <div class="form-container">
            <h2>Enter Your Skills</h2>
            <p>Format: skill name:proficiency:certified (e.g., Python:Advanced:yes, Data Analysis:Intermediate:no)</p>
            <p>Where proficiency can be Beginner, Intermediate, Advanced, or Expert and certified is yes/no to indicate if you have certification for the skill</p>
            
            <form method="POST">
                <div>
                    <label for="name">Your Name:</label>
                    <input type="text" id="name" name="name" required>
                </div>
                
                <div>
                    <label for="skills">Enter Your Skills:</label>
                    <input type="text" id="skills" name="skills" placeholder="Python:Advanced:yes, Data Analysis:Intermediate:no" value="{{ skills_input }}" required>
                </div>
                
                <div>
                    <label for="threshold">Threshold for Teachable Courses (%):</label>
                    <input type="number" id="threshold" name="threshold" min="0" max="100" value="60">
                </div>
                
                <button type="submit">Analyze Teaching Opportunities</button>
            </form>
        </div>

        {% if results %}
        <div class="results">
            <h2>Your Teaching Analysis</h2>
            
            <div class="section">
                <h3>Courses You Can Teach</h3>
                
                {% if not results.teachable_courses %}
                <p>No courses match your skills at the specified threshold.</p>
                {% else %}
                    {% for course in results.teachable_courses %}
                    <div class="course">
                        <div class="course-header">
                            <span>{{ course.course_name }}</span>
                            <span class="match-percentage">{{ course.match_percentage|int }}% Match</span>
                        </div>
                        
                        {% if course.matched_skills %}
                        <div class="skills-list">
                            <strong>Your relevant skills:</strong>
                            {% for skill in course.matched_skills %}
                            <div class="skill-matched">✓ {{ skill }}</div>
                            {% endfor %}
                        </div>
                        {% endif %}
                        
                        {% if course.missing_skills %}
                        <div class="skills-list">
                            <strong>Skills you don't have (but may not be critical):</strong>
                            {% for skill in course.missing_skills %}
                            <div class="skill-missing">✗ {{ skill }}</div>
                            {% endfor %}
                        </div>
                        {% endif %}
                    </div>
                    {% endfor %}
                {% endif %}
            </div>
            
            <div class="section">
                <h3>Skill Development Opportunities</h3>
                
                <h4>Courses Where You Have Skill Gaps</h4>
                
                {% if not results.skill_gaps %}
                <p>No relevant skill gaps found.</p>
                {% else %}
                    {% for course in results.skill_gaps %}
                    <div class="course">
                        <div class="course-header">
                            <span>{{ course.course_name }}</span>
                            <span class="match-percentage">{{ course.match_percentage|int }}% Match</span>
                        </div>
                        
                        {% if course.matched_skills %}
                        <div class="skills-list">
                            <strong>Skills you already have:</strong>
                            {% for skill in course.matched_skills %}
                            <div class="skill-matched">✓ {{ skill }}</div>
                            {% endfor %}
                        </div>
                        {% endif %}
                        
                        {% if course.missing_skills %}
                        <div class="skills-list">
                            <strong>Skills you need to develop:</strong>
                            {% for skill in course.missing_skills %}
                            <div class="skill-missing">✗ {{ skill }}</div>
                            {% endfor %}
                        </div>
                        {% endif %}
                    </div>
                    {% endfor %}
                {% endif %}
            </div>
        </div>
        {% endif %}
    </body>
    </html>
    """
    
    # Create template files if they don't exist
    index_template_path = os.path.join(templates_dir, 'index.html')
    faculty_development_template_path = os.path.join(templates_dir, 'faculty_development.html')
    faculty_teaching_template_path = os.path.join(templates_dir, 'faculty_teaching.html')
    
    if not os.path.exists(index_template_path):
        with open(index_template_path, 'w') as f:
            f.write(index_template)
            
    if not os.path.exists(faculty_development_template_path):
        with open(faculty_development_template_path, 'w') as f:
            f.write(faculty_development_template)
            
    if not os.path.exists(faculty_teaching_template_path):
        with open(faculty_teaching_template_path, 'w') as f:
            f.write(faculty_teaching_template)
    
    app.run(debug=True, port=5001)