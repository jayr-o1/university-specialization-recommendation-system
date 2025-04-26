import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def update_course_skills(courses_file='data/courses.json', output_file='data/courses_with_skills.json'):
    """
    Update courses with extracted skills.
    
    Args:
        courses_file (str): Path to the input courses file
        output_file (str): Path to the output file with updated skills
    """
    # Load courses
    try:
        with open(courses_file, 'r') as f:
            courses = json.load(f)
    except FileNotFoundError:
        print(f"Error: Courses file {courses_file} not found.")
        return
        
    # Directory for output file
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Extract skills from course descriptions and titles
    updated_courses = {}
    for course_id, course_data in courses.items():
        # Extract relevant information
        title = course_data.get('title', '')
        description = course_data.get('description', '')
        
        # Simple keyword-based skill extraction
        skills = extract_skills_from_text(title + " " + description)
        
        # Update course data with skills
        updated_course = course_data.copy()
        updated_course['skills'] = skills
        updated_courses[course_id] = updated_course
        
    # Save updated courses
    with open(output_file, 'w') as f:
        json.dump(updated_courses, f, indent=2)
        
    print(f"Updated {len(updated_courses)} courses with skills. Saved to {output_file}")
    
def extract_skills_from_text(text):
    """
    Extract skills from text using simple keyword matching.
    
    Args:
        text (str): Text to extract skills from
        
    Returns:
        list: List of extracted skills
    """
    # Lowercase for matching
    text = text.lower()
    
    # Common skills in computer science and data science
    common_skills = [
        "python", "java", "javascript", "c++", "r programming", 
        "machine learning", "deep learning", "neural networks",
        "data analysis", "data visualization", "statistics",
        "algorithms", "data structures", "database", "sql",
        "web development", "cloud computing", "distributed systems",
        "natural language processing", "computer vision",
        "artificial intelligence", "software engineering",
        "backend development", "frontend development", "fullstack development"
    ]
    
    # Extract skills that appear in the text
    extracted_skills = []
    for skill in common_skills:
        if skill in text:
            extracted_skills.append(skill)
            
    return extracted_skills

if __name__ == "__main__":
    update_course_skills() 