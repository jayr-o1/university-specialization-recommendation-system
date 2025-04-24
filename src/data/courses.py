from src.models.schemas import ProficiencyLevel

# Course data with required skills and proficiency levels
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
        "code": "WEBDEV",
        "name": "Web Development",
        "description": "Creating interactive web applications using HTML, CSS, JavaScript, and web frameworks.",
        "required_skills": {
            "HTML": ProficiencyLevel.ADVANCED,
            "CSS": ProficiencyLevel.ADVANCED,
            "JavaScript": ProficiencyLevel.INTERMEDIATE,
            "Web Frameworks": ProficiencyLevel.INTERMEDIATE
        }
    },
    {
        "code": "DATANAL",
        "name": "Data Analytics",
        "description": "Techniques for analyzing and visualizing data to extract insights and support decision-making.",
        "required_skills": {
            "Python": ProficiencyLevel.INTERMEDIATE,
            "Statistics": ProficiencyLevel.INTERMEDIATE,
            "Data Analysis": ProficiencyLevel.ADVANCED,
            "Data Visualization": ProficiencyLevel.INTERMEDIATE
        }
    },
    {
        "code": "SOFTENG",
        "name": "Software Engineering",
        "description": "Principles and practices for developing high-quality software systems.",
        "required_skills": {
            "Software Development": ProficiencyLevel.ADVANCED,
            "UML": ProficiencyLevel.INTERMEDIATE,
            "Software Testing": ProficiencyLevel.INTERMEDIATE,
            "Agile Methodologies": ProficiencyLevel.INTERMEDIATE,
            "Project Management": ProficiencyLevel.INTERMEDIATE
        }
    },
    {
        "code": "NETSEC",
        "name": "Network Security",
        "description": "Protection of networking systems from unauthorized access and cyber threats.",
        "required_skills": {
            "Network Protocols": ProficiencyLevel.ADVANCED,
            "Cryptography": ProficiencyLevel.INTERMEDIATE,
            "Security Analysis": ProficiencyLevel.ADVANCED,
            "Firewall Configuration": ProficiencyLevel.INTERMEDIATE,
            "Threat Modeling": ProficiencyLevel.INTERMEDIATE
        }
    },
    {
        "code": "MLINTRO",
        "name": "Introduction to Machine Learning",
        "description": "Fundamental concepts and algorithms in machine learning and their applications.",
        "required_skills": {
            "Python": ProficiencyLevel.ADVANCED,
            "Statistics": ProficiencyLevel.ADVANCED,
            "Machine Learning": ProficiencyLevel.INTERMEDIATE,
            "Data Analysis": ProficiencyLevel.ADVANCED
        }
    },
    {
        "code": "APIDSGN",
        "name": "API Design and Development",
        "description": "Design principles and implementation of robust and scalable APIs.",
        "required_skills": {
            "Python": ProficiencyLevel.ADVANCED,
            "API Integration": ProficiencyLevel.ADVANCED,
            "Web Frameworks": ProficiencyLevel.ADVANCED,
            "Database Design": ProficiencyLevel.INTERMEDIATE
        }
    }
] 