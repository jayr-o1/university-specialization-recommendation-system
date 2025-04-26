import json
import os
import sys
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import from other modules
from utils.skill_categories import SkillCategories

def create_skill_categories(output_file='data/skill_categories.json'):
    """
    Create comprehensive skill categories for the recommendation system.
    
    Args:
        output_file (str): Path to save the categories
    """
    # Initialize with default categories
    categories = SkillCategories()
    
    # Add more specialized categories
    add_specialized_categories(categories)
    
    # Add interdisciplinary categories
    add_interdisciplinary_categories(categories)
    
    # Add emerging tech categories
    add_emerging_tech_categories(categories)
    
    # Save categories to file
    categories.save_categories(output_file)
    
    return categories.categories
    
def add_specialized_categories(categories):
    """
    Add specialized tech categories.
    
    Args:
        categories (SkillCategories): Categories instance to update
    """
    # Data Science specializations
    categories.create_category(
        "data_science",
        "Data Science",
        "Skills specific to data science practice",
        [
            "Data Science", "Statistical Modeling", "Hypothesis Testing",
            "Experimental Design", "A/B Testing", "Feature Engineering",
            "Dimensionality Reduction", "Time Series Analysis",
            "Bayesian Methods", "Data Storytelling"
        ]
    )
    
    # AI specializations
    categories.create_category(
        "artificial_intelligence",
        "Artificial Intelligence",
        "Skills focused on artificial intelligence",
        [
            "Artificial Intelligence", "Knowledge Representation",
            "Expert Systems", "Genetic Algorithms", "Robotics",
            "Computer Vision", "Speech Recognition", "Recommendation Systems",
            "Generative AI", "Large Language Models", "Prompt Engineering",
            "Reinforcement Learning", "Multi-agent Systems"
        ]
    )
    
    # Cloud computing specializations
    categories.create_category(
        "cloud_computing",
        "Cloud Computing",
        "Skills focused on cloud technologies",
        [
            "Cloud Architecture", "Serverless Computing", "Cloud Migration",
            "Multi-cloud Strategy", "Cloud Security", "AWS Lambda",
            "Azure Functions", "Google Cloud Functions", "CloudFormation",
            "Cloud Cost Optimization", "Cloud Monitoring"
        ]
    )
    
    # Game development
    categories.create_category(
        "game_development",
        "Game Development",
        "Skills related to game development",
        [
            "Game Design", "Unity", "Unreal Engine", "Game Physics",
            "3D Modeling", "Animation", "Game AI", "Level Design",
            "Shader Programming", "Game Networking", "Game Testing"
        ]
    )
    
    # UI/UX Design
    categories.create_category(
        "ui_ux_design",
        "UI/UX Design",
        "Skills related to user interface and experience design",
        [
            "UI Design", "UX Design", "User Research", "Wireframing",
            "Prototyping", "Usability Testing", "Information Architecture",
            "Interaction Design", "Visual Design", "Design Systems",
            "Figma", "Adobe XD", "Sketch"
        ]
    )
    
def add_interdisciplinary_categories(categories):
    """
    Add interdisciplinary skill categories.
    
    Args:
        categories (SkillCategories): Categories instance to update
    """
    # Data Science + Business
    categories.create_category(
        "business_analytics",
        "Business Analytics",
        "Skills combining data analysis and business domain knowledge",
        [
            "Business Intelligence", "Business Analytics", "Data-driven Decision Making",
            "KPI Definition", "Dashboard Design", "Market Analysis",
            "Customer Analytics", "Revenue Forecasting", "Churn Analysis",
            "Pricing Optimization", "Tableau", "Power BI"
        ]
    )
    
    # Software Engineering + Project Management
    categories.create_category(
        "tech_project_management",
        "Tech Project Management",
        "Skills for managing technology projects",
        [
            "Technical Project Management", "Agile Project Management",
            "Scrum Master", "Product Owner", "Sprint Planning",
            "Backlog Grooming", "Kanban", "Software Development Lifecycle",
            "Resource Allocation", "Risk Management", "Stakeholder Communication"
        ]
    )
    
    # Security + Operations
    categories.create_category(
        "security_operations",
        "Security Operations",
        "Skills for operational security",
        [
            "Security Operations", "Incident Response", "Threat Hunting",
            "Security Monitoring", "SIEM", "Vulnerability Management",
            "Security Automation", "Compliance Monitoring", "Digital Forensics",
            "Security Awareness Training", "Zero Trust Implementation"
        ]
    )
    
def add_emerging_tech_categories(categories):
    """
    Add categories for emerging technologies.
    
    Args:
        categories (SkillCategories): Categories instance to update
    """
    # Blockchain
    categories.create_category(
        "blockchain",
        "Blockchain",
        "Skills related to blockchain technology",
        [
            "Blockchain", "Smart Contracts", "Cryptocurrency",
            "Ethereum", "Solidity", "Web3", "DeFi", "NFTs",
            "Consensus Algorithms", "Distributed Ledger Technology",
            "Tokenomics", "Blockchain Security"
        ]
    )
    
    # IoT
    categories.create_category(
        "iot",
        "Internet of Things",
        "Skills related to IoT technologies",
        [
            "Internet of Things", "IoT Architecture", "Embedded Systems",
            "Sensor Networks", "MQTT", "IoT Security", "Edge Computing",
            "Arduino", "Raspberry Pi", "IoT Analytics", "Digital Twin",
            "IoT Protocols", "Home Automation"
        ]
    )
    
    # Extended Reality
    categories.create_category(
        "extended_reality",
        "Extended Reality",
        "Skills related to AR, VR and MR",
        [
            "Augmented Reality", "Virtual Reality", "Mixed Reality",
            "AR Development", "VR Development", "3D Modeling for XR",
            "Spatial Computing", "AR/VR Design", "Motion Tracking",
            "ARKit", "ARCore", "Unity XR", "WebXR"
        ]
    )
    
    # Quantum Computing
    categories.create_category(
        "quantum_computing",
        "Quantum Computing",
        "Skills related to quantum computing",
        [
            "Quantum Computing", "Quantum Algorithms", "Quantum Programming",
            "Qiskit", "Quantum Machine Learning", "Quantum Cryptography",
            "Quantum Simulation", "Quantum Error Correction",
            "Quantum Circuit Design", "Quantum Optimization"
        ]
    )
    
def analyze_skill_distribution(categories):
    """
    Analyze the distribution of skills across categories.
    
    Args:
        categories (dict): Skill categories dictionary
        
    Returns:
        dict: Analysis results
    """
    # Count skills per category
    skills_per_category = {}
    for category_id, category_data in categories.items():
        skills_per_category[category_id] = len(category_data.get("skills", []))
    
    # Find overlapping skills
    skill_occurrences = defaultdict(list)
    for category_id, category_data in categories.items():
        for skill in category_data.get("skills", []):
            skill_occurrences[skill.lower()].append(category_id)
    
    overlapping_skills = {
        skill: categories_list
        for skill, categories_list in skill_occurrences.items()
        if len(categories_list) > 1
    }
    
    # Generate summary
    total_skills = sum(skills_per_category.values())
    unique_skills = len(skill_occurrences)
    
    return {
        "total_categories": len(categories),
        "total_skills": total_skills,
        "unique_skills": unique_skills,
        "overlapping_skills_count": len(overlapping_skills),
        "skills_per_category": skills_per_category,
        "overlapping_skills": overlapping_skills
    }

def print_analysis(analysis):
    """
    Print analysis of skill categories.
    
    Args:
        analysis (dict): Analysis results
    """
    print("\n=== Skill Categories Analysis ===")
    print(f"Total Categories: {analysis['total_categories']}")
    print(f"Total Skills (with duplicates): {analysis['total_skills']}")
    print(f"Unique Skills: {analysis['unique_skills']}")
    print(f"Overlapping Skills: {analysis['overlapping_skills_count']}")
    
    print("\nSkills per Category:")
    sorted_categories = sorted(
        analysis['skills_per_category'].items(),
        key=lambda x: x[1],
        reverse=True
    )
    for category_id, count in sorted_categories:
        print(f"  - {category_id}: {count}")
    
    if analysis['overlapping_skills']:
        print("\nSample Overlapping Skills:")
        sample_skills = list(analysis['overlapping_skills'].items())[:5]
        for skill, categories in sample_skills:
            print(f"  - {skill}: {', '.join(categories)}")

if __name__ == "__main__":
    # Create skill categories
    categories = create_skill_categories()
    
    # Analyze the created categories
    analysis = analyze_skill_distribution(categories)
    print_analysis(analysis) 