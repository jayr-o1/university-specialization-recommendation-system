from src.models.schemas import ProficiencyLevel, SkillProficiency

# Faculty data with skills and proficiency levels
FACULTIES = [
    {
        "id": "F001",
        "name": "Dr. John Smith",
        "department": "Computer Science",
        "skills": [
            {"skill": "Python", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "Machine Learning", "proficiency": ProficiencyLevel.ADVANCED},
            {"skill": "Data Analysis", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "Algorithm Analysis", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "Data Structures", "proficiency": ProficiencyLevel.EXPERT}
        ]
    },
    {
        "id": "F002",
        "name": "Prof. Sarah Johnson",
        "department": "Information Systems",
        "skills": [
            {"skill": "Database Design", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "SQL", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "Data Modeling", "proficiency": ProficiencyLevel.ADVANCED},
            {"skill": "Software Development", "proficiency": ProficiencyLevel.INTERMEDIATE},
            {"skill": "Project Management", "proficiency": ProficiencyLevel.ADVANCED}
        ]
    },
    {
        "id": "F003",
        "name": "Dr. Michael Chang",
        "department": "Web Development",
        "skills": [
            {"skill": "HTML", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "CSS", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "JavaScript", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "Web Frameworks", "proficiency": ProficiencyLevel.ADVANCED},
            {"skill": "API Integration", "proficiency": ProficiencyLevel.ADVANCED}
        ]
    },
    {
        "id": "F004",
        "name": "Prof. Emily Davis",
        "department": "Software Engineering",
        "skills": [
            {"skill": "Software Development", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "UML", "proficiency": ProficiencyLevel.ADVANCED},
            {"skill": "Software Testing", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "Agile Methodologies", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "Project Management", "proficiency": ProficiencyLevel.EXPERT}
        ]
    },
    {
        "id": "F005",
        "name": "Dr. Robert Wilson",
        "department": "Cybersecurity",
        "skills": [
            {"skill": "Network Protocols", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "Cryptography", "proficiency": ProficiencyLevel.ADVANCED},
            {"skill": "Security Analysis", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "Firewall Configuration", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "Threat Modeling", "proficiency": ProficiencyLevel.ADVANCED}
        ]
    },
    {
        "id": "F006",
        "name": "Prof. Amanda Brown",
        "department": "Operating Systems",
        "skills": [
            {"skill": "Operating Systems", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "System Administration", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "File Systems", "proficiency": ProficiencyLevel.ADVANCED},
            {"skill": "Virtualization", "proficiency": ProficiencyLevel.ADVANCED},
            {"skill": "Cloud Computing", "proficiency": ProficiencyLevel.INTERMEDIATE}
        ]
    },
    {
        "id": "F007",
        "name": "Dr. Lisa Zhang",
        "department": "Computer Science",
        "skills": [
            {"skill": "Machine Learning", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "Deep Learning", "proficiency": ProficiencyLevel.ADVANCED},
            {"skill": "Python", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "TensorFlow", "proficiency": ProficiencyLevel.ADVANCED},
            {"skill": "Data Analysis", "proficiency": ProficiencyLevel.ADVANCED}
        ]
    },
    {
        "id": "F008",
        "name": "Prof. Mark Thompson",
        "department": "Information Technology",
        "skills": [
            {"skill": "AWS", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "Azure", "proficiency": ProficiencyLevel.ADVANCED},
            {"skill": "DevOps", "proficiency": ProficiencyLevel.ADVANCED},
            {"skill": "Kubernetes", "proficiency": ProficiencyLevel.INTERMEDIATE},
            {"skill": "Cloud Computing", "proficiency": ProficiencyLevel.EXPERT}
        ]
    },
    {
        "id": "F009",
        "name": "Dr. Olivia Martinez",
        "department": "Business Administration",
        "skills": [
            {"skill": "Digital Marketing", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "Consumer Behavior", "proficiency": ProficiencyLevel.ADVANCED},
            {"skill": "Market Research", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "Business Analytics", "proficiency": ProficiencyLevel.INTERMEDIATE}
        ]
    },
    {
        "id": "F010",
        "name": "Prof. David Kim",
        "department": "Programming Fundamentals",
        "skills": [
            {"skill": "Python", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "Java", "proficiency": ProficiencyLevel.ADVANCED},
            {"skill": "C++", "proficiency": ProficiencyLevel.ADVANCED},
            {"skill": "Programming Fundamentals", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "Logic Development", "proficiency": ProficiencyLevel.EXPERT}
        ]
    }
] 