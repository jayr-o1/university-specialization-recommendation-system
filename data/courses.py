from models.schemas import ProficiencyLevel

# Sample courses based on common university subjects
COURSES = [
    {
        "code": "IMDBSYS32",
        "name": "Information Management and Database Systems",
        "description": "This course covers database design principles, SQL, and database management systems.",
        "required_skills": {
            "SQL": ProficiencyLevel.INTERMEDIATE,
            "Database Design": ProficiencyLevel.INTERMEDIATE,
            "MSSQL": ProficiencyLevel.INTERMEDIATE,
            "File Systems": ProficiencyLevel.ADVANCED,
            "Data Modeling": ProficiencyLevel.INTERMEDIATE
        }
    },
    {
        "code": "DASTRUCT",
        "name": "Data Structures and Algorithms",
        "description": "Introduction to data structures, algorithm analysis, and problem-solving techniques.",
        "required_skills": {
            "Python": ProficiencyLevel.INTERMEDIATE,
            "Data Structures": ProficiencyLevel.ADVANCED,
            "Algorithm Analysis": ProficiencyLevel.INTERMEDIATE,
            "Problem Solving": ProficiencyLevel.ADVANCED,
            "Computational Complexity": ProficiencyLevel.INTERMEDIATE
        }
    },
    {
        "code": "INTPROG",
        "name": "Introduction to Programming",
        "description": "Fundamentals of programming concepts, syntax, and problem-solving using Python.",
        "required_skills": {
            "Python": ProficiencyLevel.INTERMEDIATE,
            "Programming Fundamentals": ProficiencyLevel.INTERMEDIATE,
            "Logic Development": ProficiencyLevel.INTERMEDIATE,
            "Problem Solving": ProficiencyLevel.INTERMEDIATE
        }
    },
    {
        "code": "PLATECH",
        "name": "Platform Technologies",
        "description": "Overview of various computing platforms, operating systems, and infrastructure technologies.",
        "required_skills": {
            "Operating Systems": ProficiencyLevel.INTERMEDIATE,
            "Cloud Computing": ProficiencyLevel.INTERMEDIATE,
            "Virtualization": ProficiencyLevel.INTERMEDIATE,
            "System Administration": ProficiencyLevel.INTERMEDIATE
        }
    },
    {
        "code": "WEBDEVT",
        "name": "Web Development",
        "description": "Development of web applications using HTML, CSS, JavaScript, and web frameworks.",
        "required_skills": {
            "HTML": ProficiencyLevel.ADVANCED,
            "CSS": ProficiencyLevel.ADVANCED,
            "JavaScript": ProficiencyLevel.INTERMEDIATE,
            "Web Frameworks": ProficiencyLevel.INTERMEDIATE,
            "API Integration": ProficiencyLevel.INTERMEDIATE
        }
    },
    {
        "code": "NETSEC",
        "name": "Network Security",
        "description": "Principles of network security, cryptography, and secure network design.",
        "required_skills": {
            "Network Protocols": ProficiencyLevel.ADVANCED,
            "Cryptography": ProficiencyLevel.INTERMEDIATE,
            "Security Analysis": ProficiencyLevel.INTERMEDIATE,
            "Firewall Configuration": ProficiencyLevel.INTERMEDIATE,
            "Threat Modeling": ProficiencyLevel.INTERMEDIATE
        }
    },
    {
        "code": "SOFTENG",
        "name": "Software Engineering",
        "description": "Software development lifecycle, project management, and quality assurance.",
        "required_skills": {
            "Software Development": ProficiencyLevel.ADVANCED,
            "Project Management": ProficiencyLevel.INTERMEDIATE,
            "UML": ProficiencyLevel.INTERMEDIATE,
            "Software Testing": ProficiencyLevel.INTERMEDIATE,
            "Agile Methodologies": ProficiencyLevel.INTERMEDIATE
        }
    },
    {
        "code": "DATASCI",
        "name": "Data Science",
        "description": "Introduction to data analysis, machine learning, and statistical techniques.",
        "required_skills": {
            "Python": ProficiencyLevel.ADVANCED,
            "Statistics": ProficiencyLevel.ADVANCED,
            "Machine Learning": ProficiencyLevel.INTERMEDIATE,
            "Data Visualization": ProficiencyLevel.INTERMEDIATE,
            "Data Analysis": ProficiencyLevel.ADVANCED
        }
    }
] 