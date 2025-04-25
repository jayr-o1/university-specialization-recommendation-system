"""
Skill taxonomy module that defines relationships between skills.
This helps the recommendation system better understand skill similarities and infer skills.
"""
from typing import Dict, List, Set

# Skill categories mapping specific skills to general skill areas
SKILL_CATEGORIES = {
    "Database": [
        "SQL", "MySQL", "MSSQL", "PostgreSQL", "SQLite", "Oracle Database",
        "NoSQL", "MongoDB", "Cassandra", "Redis", "Database Design", 
        "Data Modeling", "Relational Database", "Database Management",
        "Database Administration", "Database Security", "Database Performance",
        "Database Optimization", "Query Optimization", "Indexing", 
        "Entity-Relationship Diagrams", "ERD", "Normalization", "Denormalization",
        "ACID Properties", "Transactions", "Database Management Systems", "DBMS",
        "Data Warehousing", "ETL", "Big Data", "Data Lake", "Database Migration"
    ],
    
    "Programming": [
        "Python", "Java", "JavaScript", "C++", "C#", "Ruby", "PHP", "Go", "Rust",
        "Swift", "Kotlin", "TypeScript", "Object-Oriented Programming", "OOP",
        "Functional Programming", "Procedural Programming", "Data Structures",
        "Algorithms", "Debugging", "Version Control", "Git", "Testing",
        "Unit Testing", "Integration Testing", "Code Review", "Refactoring",
        "Clean Code", "Software Development", "API Development", "Web Development"
    ],
    
    "Web Development": [
        "HTML", "CSS", "JavaScript", "React", "Angular", "Vue.js", "Node.js",
        "Express.js", "Django", "Flask", "Ruby on Rails", "ASP.NET", "PHP",
        "WordPress", "Frontend Development", "Backend Development", "Full Stack",
        "REST API", "GraphQL", "Web Services", "Web Design", "Responsive Design",
        "Bootstrap", "Tailwind CSS", "SASS", "LESS", "jQuery", "DOM Manipulation"
    ],
    
    "Cloud Computing": [
        "AWS", "Amazon Web Services", "Azure", "Google Cloud", "GCP",
        "Cloud Architecture", "Cloud Security", "Cloud Migration", "IaaS",
        "PaaS", "SaaS", "Serverless", "Containers", "Docker", "Kubernetes",
        "Microservices", "DevOps", "CI/CD", "Infrastructure as Code", "IaC",
        "Terraform", "CloudFormation", "Ansible", "Puppet", "Chef"
    ],
    
    "Data Science": [
        "Machine Learning", "Deep Learning", "Artificial Intelligence", "AI",
        "Neural Networks", "Data Analysis", "Data Visualization", "Statistics",
        "R", "Python", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch",
        "Big Data", "Hadoop", "Spark", "Data Mining", "Natural Language Processing",
        "NLP", "Computer Vision", "Predictive Modeling", "Regression", "Classification",
        "Clustering", "Time Series Analysis", "Feature Engineering"
    ],
    
    "Security": [
        "Cybersecurity", "Network Security", "Application Security", "Cloud Security",
        "Security Operations", "Vulnerability Assessment", "Penetration Testing",
        "Ethical Hacking", "Security Auditing", "Risk Assessment", "Threat Modeling",
        "Incident Response", "Forensics", "Malware Analysis", "Cryptography",
        "Authentication", "Authorization", "Identity Management", "IAM", 
        "Security Compliance", "GDPR", "HIPAA", "PCI DSS", "ISO 27001"
    ],
    
    "Networking": [
        "Network Protocols", "TCP/IP", "HTTP", "DNS", "FTP", "SMTP", 
        "Network Design", "Routing", "Switching", "Firewalls", "VPN",
        "Subnetting", "IP Addressing", "IPv4", "IPv6", "OSI Model",
        "Network Security", "LAN", "WAN", "VLAN", "Wireless Networking",
        "Network Troubleshooting", "Network Performance", "SDN"
    ],
    
    "Project Management": [
        "Agile", "Scrum", "Kanban", "Waterfall", "Project Planning",
        "Risk Management", "Stakeholder Management", "Resource Allocation",
        "Budgeting", "Project Scheduling", "JIRA", "Trello", "Asana",
        "MS Project", "Project Documentation", "PMBOK", "PMP", "Prince2",
        "Sprint Planning", "Retrospectives", "Stand-ups"
    ],
    
    "Design": [
        "UX Design", "UI Design", "User Experience", "User Interface",
        "Interaction Design", "Visual Design", "Graphic Design", "Web Design",
        "Mobile Design", "Responsive Design", "Wireframing", "Prototyping",
        "Figma", "Sketch", "Adobe XD", "Photoshop", "Illustrator",
        "Design Thinking", "User Research", "Usability Testing", "Information Architecture",
        "Accessibility", "A11y", "Color Theory", "Typography"
    ]
}

# Skill inference rules - if someone has skill X, they likely have skill Y as well
SKILL_INFERENCE_RULES = {
    "MySQL": ["SQL", "Database Management", "Relational Database"],
    "MSSQL": ["SQL", "Database Management", "Relational Database"],
    "PostgreSQL": ["SQL", "Database Management", "Relational Database"],
    "Oracle Database": ["SQL", "Database Management", "Relational Database"],
    "NoSQL": ["Database Management", "Database Design"],
    "MongoDB": ["NoSQL", "Database Management"],
    "Database Design": ["Data Modeling", "Relational Database"],
    "Advanced Database Systems": ["Database Management", "Database Performance", "Database Optimization"],
    "React": ["JavaScript", "Frontend Development", "Web Development"],
    "Angular": ["TypeScript", "JavaScript", "Frontend Development", "Web Development"],
    "Django": ["Python", "Backend Development", "Web Development"],
    "Node.js": ["JavaScript", "Backend Development", "Web Development"]
}

# Skill similarity mapping - custom mapping of skill similarity coefficients
SKILL_SIMILARITY = {
    ("MySQL", "SQL"): 0.95,
    ("MSSQL", "SQL"): 0.95,
    ("PostgreSQL", "SQL"): 0.95,
    ("SQLite", "SQL"): 0.9,
    ("MySQL", "MSSQL"): 0.85,
    ("MySQL", "PostgreSQL"): 0.8,
    ("MSSQL", "PostgreSQL"): 0.8,
    ("Database Design", "Data Modeling"): 0.9,
    ("Database Design", "Relational Database"): 0.85,
    ("Database Design", "Entity-Relationship Diagrams"): 0.85,
    ("Database Design", "ERD"): 0.85,
    ("Database Design", "Database Management"): 0.8,
    ("Database Design", "Normalization"): 0.85,
    ("Database Administration", "Database Management"): 0.9,
    ("Advanced Database Systems", "Database Performance"): 0.85,
    ("Advanced Database Systems", "Database Optimization"): 0.85,
    ("Database Performance", "Query Optimization"): 0.9,
    ("Database Performance", "Indexing"): 0.85
}

def get_category(skill: str) -> str:
    """Get the category a skill belongs to"""
    for category, skills in SKILL_CATEGORIES.items():
        if skill in skills:
            return category
    return "Other"

def get_related_skills(skill: str) -> List[str]:
    """Get skills that are related to the given skill"""
    category = get_category(skill)
    if category == "Other":
        return []
    
    # Return all skills in the same category except the skill itself
    return [s for s in SKILL_CATEGORIES[category] if s != skill]

def get_inferred_skills(skills: List[str]) -> List[str]:
    """Get skills that can be inferred from the given skills"""
    inferred = set()
    for skill in skills:
        if skill in SKILL_INFERENCE_RULES:
            for inferred_skill in SKILL_INFERENCE_RULES[skill]:
                inferred.add(inferred_skill)
    
    # Don't include skills that are already in the original list
    return list(inferred - set(skills))

def get_skill_similarity(skill1: str, skill2: str) -> float:
    """Get custom similarity score between two skills if defined"""
    # Check direct mapping
    if (skill1, skill2) in SKILL_SIMILARITY:
        return SKILL_SIMILARITY[(skill1, skill2)]
    
    # Check reverse mapping
    if (skill2, skill1) in SKILL_SIMILARITY:
        return SKILL_SIMILARITY[(skill2, skill1)]
    
    # Check if they're in the same category
    category1 = get_category(skill1)
    category2 = get_category(skill2)
    
    if category1 == category2 and category1 != "Other":
        return 0.7  # Default similarity for skills in the same category
    
    return None  # Let the semantic matcher decide 