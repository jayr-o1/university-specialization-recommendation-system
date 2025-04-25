import os
import re
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm

class SyllabusScraper:
    """
    A utility class for scraping and processing university syllabi to extract course information
    and required skills for the recommendation system.
    """
    
    def __init__(self, output_dir='data'):
        """Initialize the scraper with an output directory."""
        self.output_dir = output_dir
        self.course_data = {}
        
        # Ensure the output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def scrape_university_website(self, university_url, university_name):
        """
        Scrape course information from a university website.
        This is a generic method that needs to be customized for each university website structure.
        """
        try:
            print(f"Scraping syllabi from {university_name}...")
            # This is a placeholder for the actual scraping logic
            # The implementation will vary based on each university's website structure
            
            response = requests.get(university_url)
            if response.status_code != 200:
                print(f"Failed to access {university_url}")
                return False
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # This is where you would implement custom parsing logic
            # For example:
            # course_links = soup.find_all('a', href=re.compile('syllabus|course'))
            # for link in course_links:
            #     course_url = link['href']
            #     self.process_course_page(course_url)
            
            print(f"Completed scraping from {university_name}")
            return True
            
        except Exception as e:
            print(f"Error scraping {university_name}: {str(e)}")
            return False
    
    def process_course_page(self, url):
        """Process a single course page to extract course code, name, and skills."""
        try:
            response = requests.get(url)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract course code and name
            # This is a placeholder - actual implementation depends on page structure
            course_code = soup.find('span', class_='course-code').text.strip()
            course_name = soup.find('h1', class_='course-title').text.strip()
            
            # Extract skills from course outcomes or competencies
            skills = []
            skill_sections = soup.find_all('div', class_=['outcomes', 'competencies', 'objectives'])
            for section in skill_sections:
                items = section.find_all('li')
                for item in items:
                    # Process text to extract skills
                    skill_text = item.text.strip()
                    # Apply NLP or regex to extract skill keywords
                    extracted_skills = self._extract_skills_from_text(skill_text)
                    skills.extend(extracted_skills)
            
            # Add to course data
            if course_code and course_name:
                self.course_data[course_code] = {
                    "name": course_name,
                    "required_skills": list(set(skills))  # Remove duplicates
                }
                return True
            
            return False
            
        except Exception as e:
            print(f"Error processing course page {url}: {str(e)}")
            return False
    
    def _extract_skills_from_text(self, text):
        """
        Extract skills from text using keyword matching or NLP techniques.
        This is a simplified version - a real implementation would use more sophisticated NLP.
        """
        # Example skill keywords to look for
        skill_keywords = [
            "programming", "python", "java", "database", "sql", "web development",
            "html", "css", "javascript", "analysis", "design", "management",
            "communication", "teamwork", "problem solving", "critical thinking",
            "research", "project management", "data science", "machine learning",
            "tensorflow", "pytorch", "numpy", "scikit-learn", "statistics"
        ]
        
        found_skills = []
        for skill in skill_keywords:
            if re.search(r'\b' + re.escape(skill) + r'\b', text.lower()):
                found_skills.append(skill.title())  # Capitalize skill names
        
        return found_skills
    
    def process_pdf_syllabus(self, pdf_path, university_code):
        """
        Process a PDF syllabus to extract course information.
        Requires PyPDF2 or a similar library for PDF processing.
        """
        try:
            # This is a placeholder for PDF processing logic
            # In a real implementation, you would:
            # 1. Extract text from PDF
            # 2. Parse for course code, name, and skills
            # 3. Add to course_data dictionary
            
            print(f"Processing PDF: {pdf_path}")
            # Implement PDF processing here
            
            return True
            
        except Exception as e:
            print(f"Error processing PDF {pdf_path}: {str(e)}")
            return False
    
    def process_csv_data(self, csv_path, course_code_col, course_name_col, skills_col=None):
        """
        Process course data from a CSV file.
        If skills_col is not provided, will attempt to extract skills from course descriptions.
        """
        try:
            df = pd.read_csv(csv_path)
            
            for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing CSV data"):
                course_code = str(row[course_code_col]).strip()
                course_name = str(row[course_name_col]).strip()
                
                if course_code and course_name:
                    skills = []
                    if skills_col and skills_col in df.columns:
                        skills_text = str(row[skills_col])
                        # Process skills text - could be comma-separated or similar
                        skills = [s.strip() for s in skills_text.split(',') if s.strip()]
                    
                    # If no skills column or empty skills, try to extract from description
                    if not skills and 'description' in df.columns:
                        skills = self._extract_skills_from_text(str(row['description']))
                    
                    self.course_data[course_code] = {
                        "name": course_name,
                        "required_skills": skills
                    }
            
            return True
            
        except Exception as e:
            print(f"Error processing CSV {csv_path}: {str(e)}")
            return False
    
    def manually_add_course(self, course_code, course_name, skills):
        """Manually add a course with its skills."""
        if course_code and course_name:
            self.course_data[course_code] = {
                "name": course_name,
                "required_skills": skills
            }
            return True
        return False
    
    def add_cebu_universities_courses(self):
        """
        Add sample courses from universities in Cebu.
        This is a placeholder for demonstration - in a real implementation,
        you would scrape actual university websites or process their syllabi.
        """
        # Sample data structure for Cebu universities
        cebu_universities = [
            {
                "name": "University of San Carlos",
                "prefix": "USC",
                "courses": [
                    {
                        "code": "USC-CS101",
                        "name": "Introduction to Computer Science",
                        "skills": ["Programming Fundamentals", "Algorithm Design", "Python", "Problem Solving", "Computational Thinking"]
                    },
                    {
                        "code": "USC-CS215",
                        "name": "Data Structures and Algorithms",
                        "skills": ["Algorithm Analysis", "Data Structures", "Java", "Problem Solving", "Software Design"]
                    },
                    {
                        "code": "USC-DS201",
                        "name": "Fundamentals of Data Science",
                        "skills": ["Python", "NumPy", "Pandas", "Data Analysis", "Statistics", "Data Visualization"]
                    },
                    {
                        "code": "USC-ML301",
                        "name": "Machine Learning",
                        "skills": ["TensorFlow", "PyTorch", "Scikit-learn", "NumPy", "Statistical Modeling", "Neural Networks"]
                    }
                ]
            },
            {
                "name": "Cebu Institute of Technology - University",
                "prefix": "CIT",
                "courses": [
                    {
                        "code": "CIT-IT101",
                        "name": "Information Technology Fundamentals",
                        "skills": ["Computer Fundamentals", "Information Systems", "Digital Literacy", "Office Productivity"]
                    },
                    {
                        "code": "CIT-SE201",
                        "name": "Software Engineering",
                        "skills": ["Software Development", "UML", "Requirements Analysis", "Agile Methodologies", "Testing"]
                    },
                    {
                        "code": "CIT-DS301",
                        "name": "Advanced Data Science",
                        "skills": ["Machine Learning", "TensorFlow", "Deep Learning", "NumPy", "Data Mining", "Big Data"]
                    }
                ]
            },
            {
                "name": "University of Cebu",
                "prefix": "UC",
                "courses": [
                    {
                        "code": "UC-DB101",
                        "name": "Database Management",
                        "skills": ["SQL", "Database Design", "Data Modeling", "MySQL", "NoSQL"]
                    },
                    {
                        "code": "UC-WD201",
                        "name": "Web Development",
                        "skills": ["HTML", "CSS", "JavaScript", "Responsive Design", "Web Frameworks"]
                    },
                    {
                        "code": "UC-AI301",
                        "name": "Artificial Intelligence",
                        "skills": ["Python", "TensorFlow", "Machine Learning", "Neural Networks", "Computer Vision"]
                    }
                ]
            }
        ]
        
        for university in cebu_universities:
            print(f"Adding courses from {university['name']}...")
            for course in university["courses"]:
                self.manually_add_course(
                    course["code"],
                    course["name"],
                    course["skills"]
                )
        
        return True
    
    def merge_with_existing_data(self, existing_json_path):
        """Merge scraped data with existing course_skills.json file."""
        try:
            if os.path.exists(existing_json_path):
                with open(existing_json_path, 'r') as f:
                    existing_data = json.load(f)
                
                # Merge data
                for course_code, course_info in existing_data.items():
                    if course_code not in self.course_data:
                        self.course_data[course_code] = course_info
                    else:
                        # If course exists in both, merge skills
                        existing_skills = set(self.course_data[course_code]["required_skills"])
                        new_skills = set(course_info["required_skills"])
                        self.course_data[course_code]["required_skills"] = list(existing_skills.union(new_skills))
                
                print(f"Successfully merged with existing data from {existing_json_path}")
                return True
            else:
                print(f"No existing data file found at {existing_json_path}")
                return False
                
        except Exception as e:
            print(f"Error merging with existing data: {str(e)}")
            return False
    
    def save_to_json(self, output_file='course_skills.json'):
        """Save the collected course data to a JSON file."""
        try:
            output_path = os.path.join(self.output_dir, output_file)
            with open(output_path, 'w') as f:
                json.dump(self.course_data, f, indent=4)
            
            print(f"Successfully saved {len(self.course_data)} courses to {output_path}")
            return True
            
        except Exception as e:
            print(f"Error saving to JSON: {str(e)}")
            return False
    
    def generate_skills_report(self):
        """Generate a report of all skills across courses."""
        all_skills = {}
        
        for course_code, course_info in self.course_data.items():
            for skill in course_info["required_skills"]:
                if skill in all_skills:
                    all_skills[skill].append(course_code)
                else:
                    all_skills[skill] = [course_code]
        
        # Sort by frequency
        sorted_skills = sorted(all_skills.items(), key=lambda x: len(x[1]), reverse=True)
        
        report = "Skills Report\n"
        report += "=" * 50 + "\n"
        report += "Skill Name | Frequency | Courses\n"
        report += "-" * 50 + "\n"
        
        for skill, courses in sorted_skills:
            report += f"{skill} | {len(courses)} | {', '.join(courses[:5])}"
            if len(courses) > 5:
                report += f" and {len(courses) - 5} more"
            report += "\n"
        
        report_path = os.path.join(self.output_dir, "skills_report.txt")
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(f"Skills report generated at {report_path}")
        return sorted_skills


# Example usage
if __name__ == "__main__":
    scraper = SyllabusScraper()
    
    # Add sample data from Cebu universities
    scraper.add_cebu_universities_courses()
    
    # Merge with existing data if available
    existing_data_path = os.path.join('data', 'course_skills.json')
    scraper.merge_with_existing_data(existing_data_path)
    
    # Save the updated data
    scraper.save_to_json('course_skills_updated.json')
    
    # Generate a skills report
    scraper.generate_skills_report() 