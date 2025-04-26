import json
import os
import sys
import numpy as np
from collections import defaultdict

# Add parent directory to path to import from sibling modules if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.skills_mapper import SkillsMapper
from utils.skill_categories import SkillCategories
from utils.department_skills import get_department_skills

class FacultySkillsAnalyzer:
    """
    Analyzes faculty skills to identify gaps and development opportunities.
    This class focuses on helping faculty members improve their skills by
    identifying relevant skill gaps and suggesting development paths.
    """
    
    def __init__(self, skill_embeddings_file='data/skill_embeddings.json', industry_skills_file='data/industry_skills.json'):
        """
        Initialize the FacultySkillsAnalyzer.
        
        Args:
            skill_embeddings_file (str): Path to the skill embeddings file
            industry_skills_file (str): Path to file containing in-demand industry skills
        """
        self.skills_mapper = SkillsMapper(skill_embeddings_file)
        self.skill_categories = SkillCategories()
        self.industry_skills = self.load_industry_skills(industry_skills_file)
        
    def load_industry_skills(self, filename):
        """
        Load in-demand industry skills from file.
        
        Args:
            filename (str): Path to the industry skills file
            
        Returns:
            dict: Dictionary of industry skills by category
        """
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Industry skills file {filename} not found. Using default values.")
            # Default industry skills if file not found
            return self.get_default_industry_skills()
    
    def get_default_industry_skills(self):
        """
        Provides a default set of in-demand industry skills.
        
        Returns:
            dict: Dictionary of industry skills by category
        """
        return {
            "data_science": {
                "high_demand": ["Machine Learning", "Python", "Data Visualization", "Statistical Analysis"],
                "emerging": ["MLOps", "AutoML", "Reinforcement Learning", "Responsible AI"]
            },
            "computer_science": {
                "high_demand": ["Cloud Computing", "DevOps", "Microservices", "Cybersecurity"],
                "emerging": ["Quantum Computing", "Edge Computing", "Blockchain Development"]
            },
            "information_systems": {
                "high_demand": ["Business Intelligence", "Data Warehousing", "System Integration"],
                "emerging": ["Digital Transformation", "Process Mining", "Data Lakes"]
            },
            "software_engineering": {
                "high_demand": ["Agile Methodologies", "CI/CD", "Test Automation", "Containerization"],
                "emerging": ["Infrastructure as Code", "GitOps", "Low-Code Development"]
            }
        }
    
    def identify_skill_gaps(self, faculty_skills, department):
        """
        Identify skill gaps for a faculty member in their department.
        
        Args:
            faculty_skills (list): List of skills the faculty member has
            department (str): The department/college the faculty member belongs to
            
        Returns:
            dict: Dictionary containing matched skills and skill gaps
        """
        # Get department-specific required skills
        dept_skills = get_department_skills(department)
        required_skills = dept_skills['core_skills'] + dept_skills['advanced_skills']
        
        # Normalize skills for comparison
        faculty_skills = [skill.lower().strip() for skill in faculty_skills]
        required_skills = [skill.lower().strip() for skill in required_skills]
        
        # Find matched skills
        matched_skills = []
        skill_gaps = []
        
        for skill in required_skills:
            # Check for exact matches
            if skill in faculty_skills:
                matched_skills.append(skill)
                continue
                
            # Check for similar skills using skills mapper
            similar_skills = self.skills_mapper.find_similar_skills(skill)
            if any(s.lower() in faculty_skills for s in similar_skills):
                matched_skills.append(skill)
                continue
                
            # If no match found, add to gaps
            skill_gaps.append(skill)
        
        # Categorize gaps by priority
        high_priority = []
        medium_priority = []
        
        for gap in skill_gaps:
            if gap in dept_skills['core_skills']:
                high_priority.append(gap)
            else:
                medium_priority.append(gap)
        
        return {
            'matched_skills': matched_skills,
            'skill_gaps': {
                'high_priority': high_priority,
                'medium_priority': medium_priority
            }
        }
    
    def get_development_recommendations(self, skill_gaps):
        """
        Get development recommendations based on identified skill gaps.
        
        Args:
            skill_gaps (dict): Dictionary containing skill gaps analysis
            
        Returns:
            list: List of development recommendations
        """
        recommendations = []
        
        # Process high priority gaps
        for skill in skill_gaps["skill_gaps"]["high_priority"]:
            recommendation = {
                "skill": skill,
                "priority": "high",
                "reason": "Core skill required for your department",
                "related_faculty_skills": self.skills_mapper.find_similar_skills(skill) if self.skills_mapper else [],
                "prerequisites": [],
                "missing_prerequisites": [],
                "estimated_learning_time": "3-6 months"
            }
            recommendations.append(recommendation)
            
        # Process medium priority gaps
        for skill in skill_gaps["skill_gaps"]["medium_priority"]:
            recommendation = {
                "skill": skill,
                "priority": "medium",
                "reason": "Advanced skill recommended for your department",
                "related_faculty_skills": self.skills_mapper.find_similar_skills(skill) if self.skills_mapper else [],
                "prerequisites": [],
                "missing_prerequisites": [],
                "estimated_learning_time": "2-3 months"
            }
            recommendations.append(recommendation)
            
        return recommendations
    
    def get_prerequisite_skills(self, target_skill):
        """
        Determine prerequisite skills for a given target skill.
        
        Args:
            target_skill (str): The skill to find prerequisites for
            
        Returns:
            list: List of prerequisite skills
        """
        # This is a simplified implementation
        # In a real system, you'd have a knowledge graph or structured data for prerequisites
        
        # Some example prerequisites for common skills
        prerequisites = {
            "Machine Learning": ["Python", "Statistics", "Linear Algebra", "Calculus"],
            "Deep Learning": ["Machine Learning", "Python", "Neural Networks"],
            "Data Visualization": ["Python", "Statistics", "Data Analysis"],
            "Cloud Computing": ["Networking", "Operating Systems", "Security Basics"],
            "DevOps": ["Linux", "Scripting", "Version Control", "CI/CD"],
            "Blockchain Development": ["Cryptography", "Distributed Systems", "Data Structures"],
            "MLOps": ["DevOps", "Machine Learning", "Docker", "Kubernetes"]
        }
        
        return prerequisites.get(target_skill, [])
    
    def estimate_learning_time(self, skill, faculty_skills):
        """
        Estimate learning time for a skill based on faculty's existing skills.
        
        Args:
            skill (str): Target skill to learn
            faculty_skills (list): Faculty member's existing skills
            
        Returns:
            str: Estimated learning time category
        """
        # Get prerequisites for the skill
        prerequisites = self.get_prerequisite_skills(skill)
        
        # Calculate how many prerequisites are already known
        known_prerequisites = sum(1 for p in prerequisites if p in faculty_skills)
        
        # Calculate percentage of known prerequisites
        if not prerequisites:
            prerequisite_knowledge = 1.0  # No prerequisites needed
        else:
            prerequisite_knowledge = known_prerequisites / len(prerequisites)
        
        # Estimate time based on prerequisite knowledge
        if prerequisite_knowledge == 1.0:
            return "1-2 months"
        elif prerequisite_knowledge >= 0.7:
            return "2-3 months"
        elif prerequisite_knowledge >= 0.4:
            return "3-6 months"
        else:
            return "6+ months"
    
    def save_analysis(self, analysis, filename='data/faculty_skill_analysis.json'):
        """
        Save faculty skill analysis to a file.
        
        Args:
            analysis (dict): Faculty skill analysis
            filename (str): Output filename
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"Saved faculty skill analysis to {filename}")

if __name__ == "__main__":
    # Example usage
    analyzer = FacultySkillsAnalyzer()
    
    faculty_skills = [
        "Python programming",
        "Data analysis", 
        "Statistical modeling",
        "Linear Algebra",
        "Teaching",
        "Research Methods"
    ]
    
    # Identify skill gaps for a faculty member in the data science department
    skill_gaps = analyzer.identify_skill_gaps(faculty_skills, "data_science")
    
    print("\nFaculty Skill Gap Analysis:")
    print(f"Department: {skill_gaps['department_area']}")
    print("\nMatched Skills:")
    print(f"  High-demand: {', '.join(skill_gaps['matched_skills']['high_demand'])}")
    print(f"  Emerging: {', '.join(skill_gaps['matched_skills']['emerging'])}")
    
    print("\nSkill Gaps:")
    print(f"  High-demand: {', '.join(skill_gaps['skill_gaps']['high_demand'])}")
    print(f"  Emerging: {', '.join(skill_gaps['skill_gaps']['emerging'])}")
    
    # Get development recommendations
    recommendations = analyzer.get_development_recommendations(skill_gaps)
    
    print("\nDevelopment Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['skill']} (Priority: {rec['priority']})")
        print(f"   Reason: {rec['reason']}")
        print(f"   Related skills you have: {', '.join(rec['related_faculty_skills'])}")
        print(f"   Prerequisites: {', '.join(rec['prerequisites'])}")
        print(f"   Missing prerequisites: {', '.join(rec['missing_prerequisites'])}")
        print(f"   Estimated learning time: {rec['estimated_learning_time']}")
    
    # Save analysis
    analyzer.save_analysis({
        "skill_gaps": skill_gaps,
        "recommendations": recommendations
    }) 