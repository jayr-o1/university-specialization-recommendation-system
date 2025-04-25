# University Specialization Recommendation System

This system recommends university courses based on a user's skills and proficiency levels. It uses a cosine similarity algorithm to match user skills with course requirements and suggests the most suitable courses.

## Features

- Recommends courses based on user skills and proficiency levels
- Provides match percentages and detailed skill matching information
- Identifies missing skills for further training
- Suggests similar courses where skills can be applied
- Offers both a command-line interface and a REST API

## Project Structure

```
.
├── data/                    # Data files
│   └── course_skills.json   # Course skills dataset
├── models/                  # ML models
│   └── recommendation_model.py
├── src/                     # Source code
│   ├── recommendation_app.py   # CLI application
│   └── api.py               # REST API
├── utils/                   # Utility functions
│   └── input_processor.py   # Input parsing utilities
├── config/                  # Configuration files
├── tests/                   # Test files
└── requirements.txt         # Project dependencies
```

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

Run the command-line application:

```bash
python src/recommendation_app.py
```

Enter your skills in the format: `Skill1 : Proficiency1, Skill2 : Proficiency2`

Example: `MySQL : Intermediate, Database Design : Advanced`

### REST API

Start the API server:

```bash
python src/api.py
```

#### API Endpoints

- **POST /recommend**: Get course recommendations based on skills
  - Request body: `{"skills": {"MySQL": "Intermediate", "Database Design": "Advanced"}, "top_n": 5, "include_similar": true}`
  - Alternative format: `{"skills": "MySQL : Intermediate, Database Design : Advanced"}`

- **GET /similar?course_code=CC-COMPROG11**: Find courses similar to a given course

- **GET /courses**: Get all available courses

- **GET /skills**: Get all skills in the system

## Proficiency Levels

- **Beginner**: Basic knowledge (range 1-25)
- **Intermediate**: Working knowledge (range 26-49)
- **Advanced**: Comprehensive knowledge (range 50-74)
- **Expert**: Deep expertise (range 75-100)

## Example Output

For input: `MySQL : Intermediate, Database Design : Advanced`

```
Based on your skills, these are the courses that are aligned:

1. IT-DB101 - Database Management - 85% Match
   Matched Skills:
   - MySQL (Intermediate)
   - Database Design (Advanced)
   
   Skills for Further Training:
   - SQL Query Optimization
   - NoSQL Databases
   - Database Administration

2. ...
```

## Adding More Courses

The system can be expanded by adding more courses and skills to the `course_skills.json` file. 