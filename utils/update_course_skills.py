import os
import json
import sys
from syllabus_scraper import SyllabusScraper

def update_course_skills_by_name():
    """
    Updates the course_skills.json file with new skills from syllabi.
    Uses course names as keys instead of course codes.
    Adds new skills to existing courses without duplicating them.
    """
    # Initialize the scraper
    scraper = SyllabusScraper(output_dir='../data')
    
    # Load the existing course_skills.json
    try:
        with open('../data/course_skills.json', 'r') as f:
            existing_data = json.load(f)
        print(f"Loaded existing data with {len(existing_data)} courses")
    except Exception as e:
        print(f"Error loading existing data: {str(e)}")
        return False
    
    # Option 1: Add sample courses from universities
    # This uses the built-in sample data for demonstration
    print("Adding sample university courses...")
    scraper.add_cebu_universities_courses()
    
    # Option 2: Process a CSV file with course data
    # Uncomment and modify this section if you have a CSV file
    """
    csv_path = '../data/new_courses.csv'
    if os.path.exists(csv_path):
        print(f"Processing course data from CSV: {csv_path}")
        scraper.process_csv_data(
            csv_path,
            course_code_col='Course Code',
            course_name_col='Course Name',
            skills_col='Skills'
        )
    """
    
    # Option 3: Process syllabi from a directory
    # Uncomment and modify this section if you have syllabus PDFs
    """
    syllabi_dir = '../data/syllabi'
    if os.path.exists(syllabi_dir):
        print(f"Processing syllabi from directory: {syllabi_dir}")
        for filename in os.listdir(syllabi_dir):
            if filename.endswith('.pdf'):
                pdf_path = os.path.join(syllabi_dir, filename)
                scraper.process_pdf_syllabus(pdf_path, 'UNIV')
    """
    
    # Now merge the new data with the existing data, using course names as keys
    new_data = {}
    course_name_map = {}
    
    # First, create a mapping from course code to course name
    for course_code, course_info in scraper.course_data.items():
        course_name = course_info["name"]
        course_name_map[course_code] = course_name
        
        # Initialize the new data structure with course names as keys
        if course_name not in new_data:
            new_data[course_name] = {"required_skills": []}
    
    # Now add skills from scraped data to the new structure
    for course_code, course_info in scraper.course_data.items():
        course_name = course_name_map[course_code]
        new_data[course_name]["required_skills"] = course_info["required_skills"]
    
    # Merge with existing data - add new skills without duplicates
    courses_updated = 0
    skills_added = 0
    
    for course_name, course_info in new_data.items():
        if course_name in existing_data:
            # Course exists, merge skills
            existing_skills = set(existing_data[course_name]["required_skills"])
            new_skills = set(course_info["required_skills"])
            
            # Only add skills that don't already exist
            skills_to_add = new_skills - existing_skills
            
            if skills_to_add:
                existing_data[course_name]["required_skills"].extend(list(skills_to_add))
                courses_updated += 1
                skills_added += len(skills_to_add)
                print(f"Updated '{course_name}' with {len(skills_to_add)} new skills")
        else:
            # New course, add it
            existing_data[course_name] = course_info
            courses_updated += 1
            skills_added += len(course_info["required_skills"])
            print(f"Added new course '{course_name}' with {len(course_info['required_skills'])} skills")
    
    # Save the updated data
    try:
        with open('../data/course_skills.json', 'w') as f:
            json.dump(existing_data, f, indent=4)
        print(f"Successfully updated course_skills.json")
        print(f"Summary: {courses_updated} courses updated, {skills_added} new skills added")
        return True
    except Exception as e:
        print(f"Error saving updated data: {str(e)}")
        return False

if __name__ == "__main__":
    update_course_skills_by_name() 