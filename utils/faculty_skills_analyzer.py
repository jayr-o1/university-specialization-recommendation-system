import json
import os
import sys
import numpy as np
from collections import defaultdict

# Add parent directory to path to import from sibling modules if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.skills_mapper import SkillsMapper
from utils.skill_categories import SkillCategories

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
    
    def identify_skill_gaps(self, faculty_skills, department_area):
        """
        Identify gaps between faculty skills and in-demand industry skills.
        
        Args:
            faculty_skills (list): List of faculty member skills
            department_area (str): Faculty member's department/area
            
        Returns:
            dict: Dictionary containing skill gaps and recommendations
        """
        # Get relevant industry skills for the department area
        industry_skills_for_area = self.industry_skills.get(department_area, {})
        if not industry_skills_for_area:
            # If department not found, use all industry skills
            all_skills = []
            for area_skills in self.industry_skills.values():
                all_skills.extend(area_skills.get("high_demand", []))
                all_skills.extend(area_skills.get("emerging", []))
            industry_skills_for_area = {
                "high_demand": all_skills
            }
        
        high_demand_skills = industry_skills_for_area.get("high_demand", [])
        emerging_skills = industry_skills_for_area.get("emerging", [])
        
        # Map faculty skills to industry skills
        faculty_to_industry_mapping = self.skills_mapper.map_skills(
            faculty_skills, 
            high_demand_skills + emerging_skills
        )
        
        # Find missing high-demand skills
        matched_high_demand = set()
        for matches in faculty_to_industry_mapping.values():
            for skill, _ in matches:
                if skill in high_demand_skills:
                    matched_high_demand.add(skill)
        
        missing_high_demand = [skill for skill in high_demand_skills if skill not in matched_high_demand]
        
        # Find missing emerging skills
        matched_emerging = set()
        for matches in faculty_to_industry_mapping.values():
            for skill, _ in matches:
                if skill in emerging_skills:
                    matched_emerging.add(skill)
        
        missing_emerging = [skill for skill in emerging_skills if skill not in matched_emerging]
        
        # Group similar missing skills
        all_missing = missing_high_demand + missing_emerging
        missing_skill_groups = self.skills_mapper.group_related_skills(all_missing)
        
        # Create skill gap analysis
        return {
            "faculty_skills": faculty_skills,
            "department_area": department_area,
            "matched_skills": {
                "high_demand": list(matched_high_demand),
                "emerging": list(matched_emerging)
            },
            "skill_gaps": {
                "high_demand": missing_high_demand,
                "emerging": missing_emerging,
                "grouped": missing_skill_groups
            }
        }
    
    def get_development_recommendations(self, skill_gaps, max_recommendations=5):
        """
        Generate personalized skill development recommendations based on identified gaps.
        
        Args:
            skill_gaps (dict): Skill gap analysis from identify_skill_gaps
            max_recommendations (int): Maximum number of recommendations to return
            
        Returns:
            list: List of skill development recommendations
        """
        recommendations = []
        
        # Prioritize high-demand skills first
        high_demand_gaps = skill_gaps["skill_gaps"]["high_demand"]
        emerging_gaps = skill_gaps["skill_gaps"]["emerging"]
        faculty_skills = skill_gaps["faculty_skills"]
        
        # Process high-demand skill gaps first
        for skill in high_demand_gaps[:max_recommendations]:
            # Find related skills that faculty already has
            related_faculty_skills = []
            skill_category = self.skill_categories.get_category_for_skill(skill)
            
            if skill_category:
                category_skills = self.skill_categories.get_category_skills(skill_category)
                related_faculty_skills = [s for s in faculty_skills if s in category_skills]
            
            # Get required prerequisite skills
            prerequisite_skills = self.get_prerequisite_skills(skill)
            missing_prerequisites = [s for s in prerequisite_skills if s not in faculty_skills]
            
            # Generate recommendation
            recommendation = {
                "skill": skill,
                "priority": "high",
                "reason": "High-demand industry skill",
                "related_faculty_skills": related_faculty_skills,
                "prerequisites": prerequisite_skills,
                "missing_prerequisites": missing_prerequisites,
                "estimated_learning_time": self.estimate_learning_time(skill, faculty_skills)
            }
            recommendations.append(recommendation)
        
        # Add emerging skills if we haven't reached max recommendations
        remaining_slots = max_recommendations - len(recommendations)
        if remaining_slots > 0:
            for skill in emerging_gaps[:remaining_slots]:
                related_faculty_skills = []
                skill_category = self.skill_categories.get_category_for_skill(skill)
                
                if skill_category:
                    category_skills = self.skill_categories.get_category_skills(skill_category)
                    related_faculty_skills = [s for s in faculty_skills if s in category_skills]
                
                prerequisite_skills = self.get_prerequisite_skills(skill)
                missing_prerequisites = [s for s in prerequisite_skills if s not in faculty_skills]
                
                recommendation = {
                    "skill": skill,
                    "priority": "medium",
                    "reason": "Emerging industry skill",
                    "related_faculty_skills": related_faculty_skills,
                    "prerequisites": prerequisite_skills,
                    "missing_prerequisites": missing_prerequisites,
                    "estimated_learning_time": self.estimate_learning_time(skill, faculty_skills)
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