import os
import sys
from pathlib import Path
from modal import Image, App, asgi_app

# Set up the Modal app
app = App("university-specialization-recommendation-system")

# Create an image with all dependencies installed
image = (
    Image.debian_slim()
    .pip_install(
        "numpy==1.24.3",
        "scikit-learn==1.3.0",
        "flask==2.3.3",
        "scipy==1.10.1",
        "requests==2.31.0",
        "beautifulsoup4==4.12.2",
        "pandas==2.0.3",
        "tqdm==4.66.1",
        "networkx==3.1",
        "matplotlib==3.7.2",
        "Pillow==10.1.0",
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "python-multipart==0.0.6"
    )
    # Add data and model files
    .add_local_dir("data", "/root/data")
    .add_local_dir("models", "/root/models")
    .add_local_dir("utils", "/root/utils")
    .add_local_dir("src", "/root/src")
)

# Create a FastAPI app for serving the recommendations
@app.function(image=image)
@asgi_app()
def fastapi_app():
    from fastapi import FastAPI, HTTPException, Request, Form, File, UploadFile
    from fastapi.responses import JSONResponse, HTMLResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    import uvicorn
    import json
    import base64
    import uuid
    import sys
    
    # Add project root to path
    sys.path.append("/root")
    
    # Import project modules
    from models.train_model import load_trained_model
    from utils.input_processor import parse_user_skills, format_explanation
    from utils.visualization import generate_skill_gap_chart, generate_recommendation_explanation
    
    app = FastAPI(title="University Specialization Recommendation System")
    
    # Create a session ID for this deployment
    session_id = f"modal_user_{uuid.uuid4().hex[:8]}"
    
    # Load the model
    model = load_trained_model()
    
    class SkillsInput:
        def __init__(self, skills: str = None, include_explanation: bool = False):
            self.skills = skills
            self.include_explanation = include_explanation
    
    @app.get("/", response_class=HTMLResponse)
    async def read_root():
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>University Specialization Recommendation System</title>
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
                .results-container {
                    margin-top: 30px;
                }
                #results {
                    display: none;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
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
                .badge {
                    display: inline-block;
                    padding: 3px 8px;
                    border-radius: 12px;
                    font-size: 0.8em;
                    color: white;
                    margin-right: 5px;
                    margin-bottom: 5px;
                }
                .badge-matched {
                    background-color: #28a745;
                }
                .badge-missing {
                    background-color: #dc3545;
                }
                .loading {
                    text-align: center;
                    display: none;
                }
                .spinner {
                    border: 4px solid rgba(0, 0, 0, 0.1);
                    width: 36px;
                    height: 36px;
                    border-radius: 50%;
                    border-left-color: #2a5885;
                    animation: spin 1s linear infinite;
                    display: inline-block;
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                .explanation-container, .skill-gap-container {
                    margin-top: 20px;
                    padding: 15px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }
                .chart-container {
                    margin-top: 15px;
                    text-align: center;
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
                <p>Example: JavaScript : Intermediate, HTML : Advanced, CSS : Advanced</p>
                
                <input type="text" id="skills-input" placeholder="Enter your skills and proficiency levels">
                <button onclick="getRecommendations()">Get Recommendations</button>
            </div>
            
            <div class="loading">
                <div class="spinner"></div>
                <p>Generating recommendations...</p>
            </div>
            
            <div class="results-container">
                <div id="results"></div>
            </div>
            
            <script>
                async function getRecommendations() {
                    const skillsInput = document.getElementById('skills-input').value;
                    const resultsDiv = document.getElementById('results');
                    const loadingDiv = document.querySelector('.loading');
                    
                    if (!skillsInput) {
                        alert('Please enter your skills');
                        return;
                    }
                    
                    // Show loading spinner
                    loadingDiv.style.display = 'block';
                    resultsDiv.style.display = 'none';
                    
                    try {
                        const response = await fetch('/api/recommend', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                skills: skillsInput,
                                include_explanation: true
                            }),
                        });
                        
                        const data = await response.json();
                        
                        if (data.recommendations && data.recommendations.length > 0) {
                            // Build HTML for recommendations
                            let html = '<h2>Based on your skills, these courses are recommended:</h2>';
                            
                            data.recommendations.forEach((rec, index) => {
                                html += `
                                    <div class="course">
                                        <div class="course-header">
                                            <span>${rec.course_name}</span>
                                            <span class="match-percentage">${rec.match_percentage}% Match</span>
                                        </div>
                                `;
                                
                                // Add matched skills
                                if (rec.matched_skills && rec.matched_skills.length > 0) {
                                    html += `
                                        <div class="skills-list">
                                            <h3>Matched Skills:</h3>
                                            <div>
                                    `;
                                    
                                    rec.matched_skills.forEach(skill => {
                                        html += `<span class="badge badge-matched">${skill}</span>`;
                                    });
                                    
                                    html += `
                                            </div>
                                        </div>
                                    `;
                                }
                                
                                // Add missing skills
                                if (rec.missing_skills && rec.missing_skills.length > 0) {
                                    html += `
                                        <div class="skills-list">
                                            <h3>Skills for Further Training:</h3>
                                            <div>
                                    `;
                                    
                                    rec.missing_skills.forEach(skill => {
                                        html += `<span class="badge badge-missing">${skill}</span>`;
                                    });
                                    
                                    html += `
                                            </div>
                                        </div>
                                    `;
                                }
                                
                                // Add explanation text if available
                                if (rec.explanation_text) {
                                    html += `
                                        <div class="explanation-container">
                                            <h3>Why This Course Was Recommended</h3>
                                            <p>${rec.explanation_text.replace(/\\n/g, '<br>')}</p>
                                        </div>
                                    `;
                                }
                                
                                // Add visualization request buttons
                                if (index === 0) {
                                    html += `
                                        <div class="skill-gap-container">
                                            <h3>Skill Gap Analysis</h3>
                                            <button onclick="getSkillGapChart('${rec.course_name}')">View Skill Gap Visualization</button>
                                            <div id="skill-gap-chart-${index}" class="chart-container"></div>
                                        </div>
                                        
                                        <div class="explanation-container">
                                            <h3>Recommendation Factors</h3>
                                            <button onclick="getExplanationChart('${rec.course_name}')">View Recommendation Factors</button>
                                            <div id="explanation-chart-${index}" class="chart-container"></div>
                                        </div>
                                    `;
                                }
                                
                                html += '</div>';
                            });
                            
                            resultsDiv.innerHTML = html;
                        } else {
                            resultsDiv.innerHTML = '<p>No recommendations found for your skills. Try adding more skills or different proficiency levels.</p>';
                        }
                    } catch (error) {
                        console.error('Error:', error);
                        resultsDiv.innerHTML = '<p>Error retrieving recommendations. Please try again.</p>';
                    } finally {
                        // Hide loading spinner and show results
                        loadingDiv.style.display = 'none';
                        resultsDiv.style.display = 'block';
                    }
                }
                
                async function getSkillGapChart(courseName) {
                    const skillsInput = document.getElementById('skills-input').value;
                    const chartContainer = document.getElementById('skill-gap-chart-0');
                    
                    try {
                        const response = await fetch(`/api/skill_gap/${encodeURIComponent(courseName)}`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                skills: skillsInput
                            }),
                        });
                        
                        const data = await response.json();
                        
                        if (data.skill_gap_chart) {
                            chartContainer.innerHTML = `<img src="data:image/png;base64,${data.skill_gap_chart}" alt="Skill Gap Analysis">`;
                        } else {
                            chartContainer.innerHTML = '<p>Failed to generate skill gap visualization.</p>';
                        }
                    } catch (error) {
                        console.error('Error:', error);
                        chartContainer.innerHTML = '<p>Error retrieving skill gap chart. Please try again.</p>';
                    }
                }
                
                async function getExplanationChart(courseName) {
                    const skillsInput = document.getElementById('skills-input').value;
                    const chartContainer = document.getElementById('explanation-chart-0');
                    
                    try {
                        const response = await fetch(`/api/explanation_chart/${encodeURIComponent(courseName)}`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                skills: skillsInput
                            }),
                        });
                        
                        const data = await response.json();
                        
                        if (data.explanation_chart) {
                            chartContainer.innerHTML = `<img src="data:image/png;base64,${data.explanation_chart}" alt="Recommendation Explanation">`;
                        } else {
                            chartContainer.innerHTML = '<p>Failed to generate explanation visualization.</p>';
                        }
                    } catch (error) {
                        console.error('Error:', error);
                        chartContainer.innerHTML = '<p>Error retrieving explanation chart. Please try again.</p>';
                    }
                }
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    
    @app.post("/api/recommend")
    async def recommend(request: Request):
        try:
            data = await request.json()
            
            if not data or 'skills' not in data:
                raise HTTPException(status_code=400, detail="No skills provided")
            
            # Parse skills
            user_skills = parse_user_skills(data['skills'])
            
            # Get user_id
            user_id = data.get('user_id', session_id)
            
            # Set career goals if provided - commented out as base model doesn't support user profiles
            # if 'career_goals' in data:
            #     model.create_user_profile(user_id, career_goals=[data['career_goals']])
            
            # Get recommendations
            top_n = data.get('top_n', 5)
            recommendations = model.recommend_courses(user_skills, top_n=top_n)
            
            # Include explanations if requested
            if data.get('include_explanation', False) and recommendations:
                for rec in recommendations:
                    rec['explanation_text'] = format_explanation(rec, user_skills)
            
            return {"recommendations": recommendations}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/skill_gap/{course_name}")
    async def skill_gap(course_name: str, request: Request):
        try:
            data = await request.json()
            
            if not data or 'skills' not in data:
                raise HTTPException(status_code=400, detail="No skills provided")
            
            # Parse skills
            user_skills = parse_user_skills(data['skills'])
            
            # Find course
            course_data = None
            for course, info in model.course_data.items():
                if course.lower() == course_name.lower():
                    course_data = {'course_name': course, 'required_skills': info['required_skills']}
                    break
            
            if not course_data:
                raise HTTPException(status_code=404, detail="Course not found")
            
            # Generate chart
            chart_data = generate_skill_gap_chart(course_data, user_skills)
            
            return {
                'course_name': course_data['course_name'],
                'skill_gap_chart': chart_data,
                'total_required_skills': len(course_data['required_skills']),
                'matched_skills': len([s for s in course_data['required_skills'] if s in user_skills]),
                'gap_percentage': round((1 - len([s for s in course_data['required_skills'] if s in user_skills]) / 
                                     len(course_data['required_skills'])) * 100, 1)
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/explanation_chart/{course_name}")
    async def explanation_chart(course_name: str, request: Request):
        try:
            data = await request.json()
            
            if not data or 'skills' not in data:
                raise HTTPException(status_code=400, detail="No skills provided")
            
            # Parse skills
            user_skills = parse_user_skills(data['skills'])
            
            # Get user_id
            user_id = data.get('user_id', session_id)
            
            # Update user profile - commented out as base model doesn't support this
            # model.create_user_profile(user_id, skills=user_skills)
            
            # Get recommendations
            recommendations = model.recommend_courses(user_skills, top_n=20)
            recommendation = next((r for r in recommendations if r['course_name'].lower() == course_name.lower()), None)
            
            if not recommendation:
                raise HTTPException(status_code=404, detail="Course not found in recommendations")
            
            # Generate chart
            chart_data = generate_recommendation_explanation(recommendation, user_skills)
            
            return {
                'course_name': recommendation['course_name'],
                'explanation_chart': chart_data,
                'explanation_factors': recommendation.get('explanation_data', {}).get('recommendation_factors', [])
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/skills")
    async def get_all_skills():
        try:
            all_skills = set()
            
            # Extract skills from course data
            for course, data in model.course_data.items():
                all_skills.update(data.get('required_skills', []))
            
            return {"skills": sorted(list(all_skills))}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/learning_path")
    async def learning_path(request: Request):
        try:
            data = await request.json()
            
            if not data or 'skills' not in data:
                raise HTTPException(status_code=400, detail="No skills provided")
            
            # Parse skills
            user_skills = parse_user_skills(data['skills'])
            
            # Get user_id and career goal
            user_id = data.get('user_id', session_id)
            career_goal = data.get('career_goal')
            
            # This endpoint requires the EnhancedRecommendationModel
            return {"error": "Learning path generation is not available in this deployment. It requires the EnhancedRecommendationModel."}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return app

# Command to deploy to Modal
if __name__ == "__main__":
    # Modal handles both local development and cloud deployment
    app.deploy() 