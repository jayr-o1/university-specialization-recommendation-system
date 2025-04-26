import json
import os
import sys

# Add parent directory to path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class SkillCategories:
    """
    Defines and manages skill categories for the recommendation system.
    """
    
    def __init__(self, categories_file='data/skill_categories.json'):
        """
        Initialize the SkillCategories.
        
        Args:
            categories_file (str): Path to the categories file
        """
        self.categories_file = categories_file
        self.categories = self.load_categories()
        self.skill_to_category = self.build_skill_category_index()
        
    def load_categories(self):
        """
        Load skill categories from file or use default if file not found.
        
        Returns:
            dict: Skill categories
        """
        try:
            with open(self.categories_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Categories file not found: {self.categories_file}")
            print("Using default categories")
            return self.get_default_categories()
            
    def save_categories(self, output_file=None):
        """
        Save skill categories to file.
        
        Args:
            output_file (str, optional): Output file path
        """
        if output_file is None:
            output_file = self.categories_file
            
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(self.categories, f, indent=2)
            
        print(f"Saved {len(self.categories)} skill categories to {output_file}")
        
    def get_default_categories(self):
        """
        Define default skill categories.
        
        Returns:
            dict: Default skill categories
        """
        return {
            "programming_languages": {
                "name": "Programming Languages",
                "description": "Skills related to programming languages and syntax",
                "skills": [
                    "Python", "Java", "JavaScript", "C++", "C#", "R", 
                    "Go", "Ruby", "PHP", "Swift", "Kotlin", "TypeScript"
                ]
            },
            "data_analysis": {
                "name": "Data Analysis",
                "description": "Skills related to data processing and analysis",
                "skills": [
                    "Data Analysis", "Statistical Analysis", "Data Visualization",
                    "Data Cleaning", "Exploratory Data Analysis", "Data Mining",
                    "Data Wrangling", "Pandas", "NumPy", "Regression Analysis"
                ]
            },
            "machine_learning": {
                "name": "Machine Learning",
                "description": "Skills related to machine learning techniques and algorithms",
                "skills": [
                    "Machine Learning", "Deep Learning", "Neural Networks",
                    "Supervised Learning", "Unsupervised Learning", "Reinforcement Learning",
                    "Classification", "Clustering", "Natural Language Processing",
                    "Computer Vision", "TensorFlow", "PyTorch", "Scikit-learn"
                ]
            },
            "web_development": {
                "name": "Web Development",
                "description": "Skills related to web development",
                "skills": [
                    "HTML", "CSS", "JavaScript", "React", "Angular", "Vue.js",
                    "Node.js", "Django", "Flask", "Ruby on Rails", "REST APIs",
                    "Frontend Development", "Backend Development", "Full Stack Development"
                ]
            },
            "databases": {
                "name": "Databases",
                "description": "Skills related to database systems and management",
                "skills": [
                    "SQL", "NoSQL", "MongoDB", "PostgreSQL", "MySQL", "SQLite",
                    "Database Design", "Data Modeling", "Query Optimization",
                    "Database Administration", "Redis", "Elasticsearch"
                ]
            },
            "devops": {
                "name": "DevOps",
                "description": "Skills related to development operations and infrastructure",
                "skills": [
                    "DevOps", "CI/CD", "Docker", "Kubernetes", "AWS", "Azure",
                    "Google Cloud", "Infrastructure as Code", "Terraform",
                    "Ansible", "Jenkins", "Git", "Linux", "Shell Scripting"
                ]
            },
            "data_engineering": {
                "name": "Data Engineering",
                "description": "Skills related to building data pipelines and infrastructure",
                "skills": [
                    "Data Engineering", "ETL", "Data Pipelines", "Apache Spark",
                    "Apache Kafka", "Hadoop", "Data Warehousing", "Big Data",
                    "Airflow", "Data Modeling", "Data Architecture"
                ]
            },
            "software_engineering": {
                "name": "Software Engineering",
                "description": "Skills related to software development methodologies and practices",
                "skills": [
                    "Software Development", "Agile", "Scrum", "Object-Oriented Programming",
                    "Design Patterns", "TDD", "Unit Testing", "Microservices",
                    "Version Control", "Code Review", "Debugging", "Refactoring"
                ]
            },
            "mobile_development": {
                "name": "Mobile Development",
                "description": "Skills related to mobile app development",
                "skills": [
                    "Android Development", "iOS Development", "React Native",
                    "Flutter", "Swift", "Kotlin", "Mobile UI Design",
                    "Cross-Platform Development", "Mobile Testing"
                ]
            },
            "cybersecurity": {
                "name": "Cybersecurity",
                "description": "Skills related to information security",
                "skills": [
                    "Cybersecurity", "Network Security", "Ethical Hacking",
                    "Penetration Testing", "Security Auditing", "Cryptography",
                    "Threat Analysis", "Security Protocols", "Vulnerability Assessment"
                ]
            }
        }
        
    def build_skill_category_index(self):
        """
        Build an index mapping skills to their categories.
        
        Returns:
            dict: Mapping of skills to categories
        """
        skill_to_category = {}
        
        for category_id, category_data in self.categories.items():
            for skill in category_data.get("skills", []):
                # Lowercase for case-insensitive matching
                skill_to_category[skill.lower()] = category_id
                
        return skill_to_category
        
    def get_category_for_skill(self, skill):
        """
        Get the category for a given skill.
        
        Args:
            skill (str): Skill to find category for
            
        Returns:
            str: Category ID or None if not found
        """
        return self.skill_to_category.get(skill.lower())
        
    def get_related_skills(self, skill, max_skills=10):
        """
        Get related skills from the same category.
        
        Args:
            skill (str): The skill to find related skills for
            max_skills (int): Maximum number of related skills to return
            
        Returns:
            list: List of related skills
        """
        category_id = self.get_category_for_skill(skill.lower())
        if not category_id:
            return []
            
        # Get all skills in the category
        category_skills = self.categories[category_id].get("skills", [])
        
        # Filter out the original skill
        related_skills = [s for s in category_skills if s.lower() != skill.lower()]
        
        # Return up to max_skills
        return related_skills[:max_skills]
        
    def add_skill_to_category(self, skill, category_id):
        """
        Add a skill to a category.
        
        Args:
            skill (str): Skill to add
            category_id (str): Category ID to add the skill to
            
        Returns:
            bool: True if added successfully, False otherwise
        """
        if category_id not in self.categories:
            return False
            
        # Check if skill already exists in the category
        if skill in self.categories[category_id].get("skills", []):
            return True
            
        # Add skill to category
        if "skills" not in self.categories[category_id]:
            self.categories[category_id]["skills"] = []
            
        self.categories[category_id]["skills"].append(skill)
        
        # Update index
        self.skill_to_category[skill.lower()] = category_id
        
        return True
        
    def create_category(self, category_id, name, description="", skills=None):
        """
        Create a new skill category.
        
        Args:
            category_id (str): Category ID
            name (str): Category name
            description (str): Category description
            skills (list): List of skills for the category
            
        Returns:
            bool: True if created successfully, False if category already exists
        """
        if category_id in self.categories:
            return False
            
        # Create category
        self.categories[category_id] = {
            "name": name,
            "description": description,
            "skills": skills or []
        }
        
        # Update index for new skills
        for skill in skills or []:
            self.skill_to_category[skill.lower()] = category_id
            
        return True
        
    def get_all_skills(self):
        """
        Get all skills across all categories.
        
        Returns:
            list: List of all skills
        """
        all_skills = []
        
        for category_data in self.categories.values():
            all_skills.extend(category_data.get("skills", []))
            
        return all_skills
        
    def get_category_skills(self, category_id):
        """
        Get all skills for a specific category.
        
        Args:
            category_id (str): Category ID
            
        Returns:
            list: List of skills in the category or empty list if category not found
        """
        if category_id not in self.categories:
            return []
            
        return self.categories[category_id].get("skills", [])

if __name__ == "__main__":
    skill_categories = SkillCategories()
    
    # Print category information
    print(f"Loaded {len(skill_categories.categories)} skill categories")
    
    for category_id, category_data in skill_categories.categories.items():
        print(f"\n{category_data['name']} ({category_id}):")
        print(f"Description: {category_data['description']}")
        print(f"Skills ({len(category_data['skills'])}):")
        
        for skill in category_data['skills'][:5]:
            print(f"  - {skill}")
            
        if len(category_data['skills']) > 5:
            print(f"  - ... and {len(category_data['skills']) - 5} more")
            
    # Save categories to file
    skill_categories.save_categories() 