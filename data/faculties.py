from models.schemas import ProficiencyLevel

# Sample faculty members with their skills
FACULTIES = [
    {
        "id": "F001",
        "name": "Dr. Alan Smith",
        "department": "Computer Science",
        "skills": [
            {"skill": "Python", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "Data Structures", "proficiency": ProficiencyLevel.ADVANCED},
            {"skill": "Algorithm Analysis", "proficiency": ProficiencyLevel.ADVANCED},
            {"skill": "Machine Learning", "proficiency": ProficiencyLevel.INTERMEDIATE},
            {"skill": "Database Design", "proficiency": ProficiencyLevel.INTERMEDIATE}
        ]
    },
    {
        "id": "F002",
        "name": "Prof. Maria Garcia",
        "department": "Information Technology",
        "skills": [
            {"skill": "SQL", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "Database Design", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "MSSQL", "proficiency": ProficiencyLevel.ADVANCED},
            {"skill": "File Systems", "proficiency": ProficiencyLevel.ADVANCED},
            {"skill": "Data Modeling", "proficiency": ProficiencyLevel.ADVANCED}
        ]
    },
    {
        "id": "F003",
        "name": "Dr. James Wilson",
        "department": "Software Engineering",
        "skills": [
            {"skill": "Software Development", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "Project Management", "proficiency": ProficiencyLevel.ADVANCED},
            {"skill": "UML", "proficiency": ProficiencyLevel.ADVANCED},
            {"skill": "Software Testing", "proficiency": ProficiencyLevel.ADVANCED},
            {"skill": "Agile Methodologies", "proficiency": ProficiencyLevel.EXPERT}
        ]
    },
    {
        "id": "F004",
        "name": "Prof. Sarah Johnson",
        "department": "Web Technologies",
        "skills": [
            {"skill": "HTML", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "CSS", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "JavaScript", "proficiency": ProficiencyLevel.ADVANCED},
            {"skill": "Web Frameworks", "proficiency": ProficiencyLevel.ADVANCED},
            {"skill": "API Integration", "proficiency": ProficiencyLevel.INTERMEDIATE}
        ]
    },
    {
        "id": "F005",
        "name": "Dr. Robert Chen",
        "department": "Data Science",
        "skills": [
            {"skill": "Python", "proficiency": ProficiencyLevel.ADVANCED},
            {"skill": "Statistics", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "Machine Learning", "proficiency": ProficiencyLevel.ADVANCED},
            {"skill": "Data Visualization", "proficiency": ProficiencyLevel.ADVANCED},
            {"skill": "Data Analysis", "proficiency": ProficiencyLevel.EXPERT}
        ]
    },
    {
        "id": "F006",
        "name": "Prof. Emily Davis",
        "department": "Cybersecurity",
        "skills": [
            {"skill": "Network Protocols", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "Cryptography", "proficiency": ProficiencyLevel.ADVANCED},
            {"skill": "Security Analysis", "proficiency": ProficiencyLevel.ADVANCED},
            {"skill": "Firewall Configuration", "proficiency": ProficiencyLevel.EXPERT},
            {"skill": "Threat Modeling", "proficiency": ProficiencyLevel.ADVANCED}
        ]
    }
] 