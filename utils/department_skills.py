"""
Department-specific skills and requirements for different colleges.
"""

DEPARTMENT_SKILLS = {
    'business_accountancy': {
        'core_skills': [
            'Financial Accounting',
            'Managerial Accounting',
            'Auditing',
            'Taxation',
            'Business Law',
            'Financial Management',
            'Cost Accounting',
            'Management Information Systems'
        ],
        'advanced_skills': [
            'International Accounting Standards',
            'Forensic Accounting',
            'Financial Analysis',
            'Risk Management',
            'Corporate Governance',
            'Business Analytics',
            'Strategic Management'
        ]
    },
    'computer_studies': {
        'core_skills': [
            'Programming',
            'Data Structures',
            'Algorithms',
            'Database Management',
            'Computer Networks',
            'Operating Systems',
            'Software Engineering',
            'Web Development'
        ],
        'advanced_skills': [
            'Artificial Intelligence',
            'Machine Learning',
            'Cloud Computing',
            'Cybersecurity',
            'Big Data Analytics',
            'Mobile Development',
            'DevOps',
            'Blockchain Technology'
        ]
    },
    'criminology': {
        'core_skills': [
            'Criminal Law',
            'Criminal Investigation',
            'Forensic Science',
            'Crime Prevention',
            'Criminal Justice System',
            'Criminology Theory',
            'Law Enforcement',
            'Crime Analysis'
        ],
        'advanced_skills': [
            'Digital Forensics',
            'Criminal Profiling',
            'Victimology',
            'Restorative Justice',
            'Crime Scene Investigation',
            'Cybercrime Investigation',
            'Criminal Psychology'
        ]
    },
    'education': {
        'core_skills': [
            'Teaching Methods',
            'Curriculum Development',
            'Educational Psychology',
            'Classroom Management',
            'Assessment and Evaluation',
            'Educational Technology',
            'Special Education',
            'Educational Research'
        ],
        'advanced_skills': [
            'Educational Leadership',
            'Educational Policy',
            'Distance Learning',
            'Educational Assessment',
            'Teacher Training',
            'Educational Innovation',
            'Learning Analytics'
        ]
    },
    'tourism': {
        'core_skills': [
            'Tourism Management',
            'Hospitality Management',
            'Event Planning',
            'Tour Guiding',
            'Customer Service',
            'Travel Operations',
            'Tourism Marketing',
            'Cultural Heritage'
        ],
        'advanced_skills': [
            'Sustainable Tourism',
            'Tourism Policy',
            'Destination Management',
            'Tourism Economics',
            'Digital Tourism',
            'Tourism Research',
            'International Tourism'
        ]
    },
    'nursing': {
        'core_skills': [
            'Patient Care',
            'Clinical Skills',
            'Medical-Surgical Nursing',
            'Health Assessment',
            'Nursing Ethics',
            'Pharmacology',
            'Community Health',
            'Emergency Care'
        ],
        'advanced_skills': [
            'Critical Care Nursing',
            'Nursing Research',
            'Nursing Education',
            'Nursing Leadership',
            'Public Health',
            'Geriatric Nursing',
            'Pediatric Nursing'
        ]
    },
    'psychology': {
        'core_skills': [
            'Psychological Assessment',
            'Counseling',
            'Research Methods',
            'Behavioral Analysis',
            'Clinical Psychology',
            'Developmental Psychology',
            'Social Psychology',
            'Cognitive Psychology'
        ],
        'advanced_skills': [
            'Psychotherapy',
            'Psychological Testing',
            'Neuropsychology',
            'Forensic Psychology',
            'Industrial Psychology',
            'Health Psychology',
            'Psychological Research'
        ]
    },
    'engineering': {
        'core_skills': [
            'Engineering Mathematics',
            'Physics',
            'Engineering Design',
            'Technical Drawing',
            'Materials Science',
            'Engineering Mechanics',
            'Electrical Circuits',
            'Control Systems'
        ],
        'advanced_skills': [
            'Computer-Aided Design',
            'Robotics',
            'Renewable Energy',
            'Engineering Project Management',
            'Quality Control',
            'Engineering Research',
            'Sustainable Engineering'
        ]
    }
}

def get_department_skills(department):
    """
    Get the skills required for a specific department.
    
    Args:
        department (str): The department identifier
        
    Returns:
        dict: Dictionary containing core and advanced skills for the department
    """
    return DEPARTMENT_SKILLS.get(department, {
        'core_skills': [],
        'advanced_skills': []
    }) 