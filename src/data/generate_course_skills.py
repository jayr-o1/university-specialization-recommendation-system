#!/usr/bin/env python3
"""
Generate course skills automatically using OpenAI API.

This script takes a list of course codes and titles, and generates
appropriate skills with proficiency levels required to teach each course.
It uses the OpenAI API to suggest relevant skills based on course names.

Usage:
    python -m src.data.generate_course_skills [--update] [--api-key YOUR_API_KEY]

Arguments:
    --update: Update existing skills in course_skills.json instead of creating a new file
    --api-key: Your OpenAI API key (or set OPENAI_API_KEY environment variable)
"""

import os
import json
import argparse
import time
from typing import Dict, List, Optional
import random
import sys

# Try to import OpenAI - install if not available
try:
    import openai
except ImportError:
    print("OpenAI package not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"])
    import openai

# Define paths
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
COURSE_SKILLS_PATH = os.path.join(DATA_DIR, 'course_skills.json')
COURSE_LIST_PATH = os.path.join(DATA_DIR, 'course_list.txt')

# Proficiency levels
PROFICIENCY_LEVELS = ["Beginner", "Intermediate", "Advanced", "Expert"]

def load_existing_skills() -> Dict:
    """Load existing course skills if available"""
    if os.path.exists(COURSE_SKILLS_PATH):
        try:
            with open(COURSE_SKILLS_PATH, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error: {COURSE_SKILLS_PATH} is not valid JSON")
            return {}
    return {}

def load_course_list() -> List[Dict[str, str]]:
    """
    Load list of courses from course_list.txt.
    Expected format is one course per line: "COURSE_CODE Course Title"
    """
    courses = []
    
    # First, check if course_list.txt exists
    if not os.path.exists(COURSE_LIST_PATH):
        # Create a sample file with course codes and titles from your previous list
        sample_courses = [
            "ENGL 100 Communication Arts",
            "SOCIO 102 Gender and Society",
            "MATH 100 College Mathematics",
            "PSYCH 101 Understanding the Self",
            "CC-INTCOM11 Introduction to Computing",
            "CC-COMPROG11 Computer Programming 1"
        ]
        
        with open(COURSE_LIST_PATH, 'w') as f:
            f.write("\n".join(sample_courses))
            f.write("\n")
        
        print(f"Created sample course list at {COURSE_LIST_PATH}")
        print("Please edit this file to include all your courses, then run this script again.")
        sys.exit(0)
    
    # Read the file
    with open(COURSE_LIST_PATH, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        # Parse the line - first part is the code, rest is the title
        parts = line.split(' ', 1)
        if len(parts) != 2:
            print(f"Warning: Could not parse line: {line}")
            continue
            
        code = parts[0]
        if len(parts) > 1:
            title = parts[1]
        else:
            title = code  # Use code as title if no title provided
            
        courses.append({"code": code, "title": title})
    
    return courses

def generate_skills_with_ai(course_code: str, course_title: str, api_key: Optional[str] = None) -> Dict[str, str]:
    """
    Generate skills for a given course using OpenAI API.
    
    Args:
        course_code: The course code
        course_title: The course title
        api_key: OpenAI API key (optional if set in environment)
        
    Returns:
        Dictionary mapping skill names to proficiency levels
    """
    if api_key:
        openai.api_key = api_key
    elif 'OPENAI_API_KEY' in os.environ:
        openai.api_key = os.environ['OPENAI_API_KEY']
    else:
        print("No OpenAI API key provided. Using fallback skill generation.")
        return generate_skills_fallback(course_code, course_title)
    
    try:
        # Create system prompt
        system_prompt = """
        You are an expert in educational curriculum design. Your task is to identify the 5 most important skills 
        that a professor would need to effectively teach a specific university course.
        
        For each skill, assign the minimum proficiency level required (Beginner, Intermediate, Advanced, or Expert).
        
        Your response should be in valid JSON format with exactly 5 skills, like this:
        {
            "Skill Name 1": "Advanced",
            "Skill Name 2": "Intermediate",
            "Skill Name 3": "Expert",
            "Skill Name 4": "Beginner", 
            "Skill Name 5": "Advanced"
        }
        """
        
        # Create user prompt
        user_prompt = f"Course Code: {course_code}\nCourse Title: {course_title}"
        
        # Make API call
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,  # Lower temperature for more consistent results
            max_tokens=300  # Limit to avoid excessive output
        )
        
        # Extract the response content
        skill_json_str = response.choices[0].message.content.strip()
        
        # Clean up the response to ensure it's valid JSON
        # Remove any markdown code block markers
        skill_json_str = skill_json_str.replace("```json", "").replace("```", "").strip()
        
        # Parse the JSON
        skills = json.loads(skill_json_str)
        
        # Ensure we have exactly 5 skills
        skill_items = list(skills.items())
        if len(skill_items) > 5:
            skills = dict(skill_items[:5])
        elif len(skill_items) < 5:
            # Add generic skills to reach 5
            generic_skills = [
                "Subject Knowledge", "Teaching Methodology", 
                "Research Skills", "Communication Skills", "Assessment Design"
            ]
            
            for skill in generic_skills:
                if len(skills) < 5 and skill not in skills:
                    skills[skill] = random.choice(["Intermediate", "Advanced"])
        
        return skills
        
    except Exception as e:
        print(f"Error using OpenAI API: {str(e)}")
        print("Falling back to manual skill generation...")
        return generate_skills_fallback(course_code, course_title)

def generate_skills_fallback(course_code: str, course_title: str) -> Dict[str, str]:
    """
    Generate skills without using AI for fallback.
    
    This function uses a rule-based approach to suggest skills based on the course title.
    """
    skills = {}
    title_lower = course_title.lower()
    
    # Common skills across all courses
    skills["Teaching Methodology"] = "Advanced"
    
    # Computer/IT related
    if any(term in title_lower for term in ["computer", "programming", "web", "network", "database", "system", "software", "it", "computing"]):
        if "programming" in title_lower or "algorithm" in title_lower:
            skills["Programming Skills"] = "Advanced"
            skills["Algorithm Design"] = "Advanced"
            skills["Problem Solving"] = "Advanced"
            skills["Software Development"] = "Intermediate"
        elif "web" in title_lower:
            skills["Web Development"] = "Advanced"
            skills["HTML/CSS"] = "Advanced"
            skills["JavaScript"] = "Intermediate"
            skills["Responsive Design"] = "Intermediate"
        elif "network" in title_lower:
            skills["Network Protocols"] = "Advanced"
            skills["Routing and Switching"] = "Advanced"
            skills["Network Security"] = "Intermediate"
            skills["Network Management"] = "Intermediate"
        elif "database" in title_lower or "data" in title_lower:
            skills["Database Design"] = "Advanced"
            skills["SQL"] = "Advanced"
            skills["Data Modeling"] = "Intermediate"
            skills["Data Analysis"] = "Intermediate"
    # Mathematics
    elif any(term in title_lower for term in ["math", "calculus", "algebra", "statistics"]):
        skills["Mathematical Analysis"] = "Advanced"
        skills["Problem Solving"] = "Advanced"
        skills["Mathematical Modeling"] = "Advanced"
        skills["Logic and Reasoning"] = "Advanced"
    # Languages and communication
    elif any(term in title_lower for term in ["english", "communication", "writing", "language"]):
        skills["English Proficiency"] = "Advanced"
        skills["Communication Skills"] = "Advanced"
        skills["Writing Skills"] = "Advanced"
        skills["Public Speaking"] = "Intermediate"
    # Business/Management
    elif any(term in title_lower for term in ["business", "management", "entrepreneurship", "marketing"]):
        skills["Business Fundamentals"] = "Advanced"
        skills["Strategic Thinking"] = "Advanced"
        skills["Project Management"] = "Intermediate"
        skills["Organizational Behavior"] = "Intermediate"
    # Science
    elif any(term in title_lower for term in ["physics", "chemistry", "biology", "science"]):
        skills["Scientific Method"] = "Advanced"
        skills["Laboratory Techniques"] = "Advanced"
        skills["Research Methodology"] = "Advanced"
        skills["Data Analysis"] = "Intermediate"
    # Social Sciences
    elif any(term in title_lower for term in ["psychology", "sociology", "history", "political"]):
        skills["Research Methodology"] = "Advanced"
        skills["Critical Analysis"] = "Advanced"
        skills["Theoretical Frameworks"] = "Advanced"
        skills["Statistical Analysis"] = "Intermediate"
    
    # Add a generic skill if we don't have enough
    if len(skills) < 5:
        generic_skills = [
            "Subject Expertise", "Research Skills", "Assessment Design", 
            "Academic Writing", "Critical Thinking", "Instructional Design"
        ]
        for skill in generic_skills:
            if len(skills) < 5 and skill not in skills:
                skills[skill] = random.choice(["Intermediate", "Advanced"])
    
    # Limit to exactly 5 skills
    return dict(list(skills.items())[:5])

def save_course_skills(course_skills: Dict, output_path: str):
    """Save the generated course skills to a JSON file"""
    with open(output_path, 'w') as f:
        json.dump(course_skills, f, indent=2)
    print(f"Course skills saved to {output_path}")

def main():
    """Main function to generate course skills"""
    parser = argparse.ArgumentParser(description="Generate course skills using OpenAI API")
    parser.add_argument("--update", action="store_true", help="Update existing skills")
    parser.add_argument("--api-key", type=str, help="OpenAI API key")
    args = parser.parse_args()
    
    # Load existing skills if updating
    course_skills = {}
    if args.update and os.path.exists(COURSE_SKILLS_PATH):
        course_skills = load_existing_skills()
        print(f"Loaded {len(course_skills)} existing course skills")
    
    # Load course list
    courses = load_course_list()
    print(f"Loaded {len(courses)} courses")
    
    # Track how many courses we've processed
    processed = 0
    
    # Generate skills for each course
    for course in courses:
        code = course["code"]
        title = course["title"]
        
        # Skip if already in skills and we're not updating
        if code in course_skills and not args.update:
            print(f"Skipping {code} - already exists")
            continue
        
        print(f"Generating skills for {code}: {title}")
        skills = generate_skills_with_ai(code, title, args.api_key)
        
        # Add to course skills dictionary
        course_skills[code] = {
            "name": title,
            "required_skills": skills
        }
        
        processed += 1
        print(f"Generated {len(skills)} skills for {code}")
        
        # Sleep to avoid rate limits if using API
        if args.api_key or 'OPENAI_API_KEY' in os.environ:
            time.sleep(1)
    
    # Save the course skills
    output_path = COURSE_SKILLS_PATH if args.update else os.path.join(DATA_DIR, 'generated_course_skills.json')
    save_course_skills(course_skills, output_path)
    
    print(f"Processed {processed} courses")
    print(f"Total courses with skills: {len(course_skills)}")
    
    # If we generated a new file, show instructions
    if not args.update:
        print("\nTo use these generated skills in your system:")
        print(f"1. Review the skills in {output_path}")
        print(f"2. If satisfied, rename the file to {COURSE_SKILLS_PATH} or use --update next time")
        print("3. Run your skill matrix generator to update the skill matrix")

if __name__ == "__main__":
    main() 