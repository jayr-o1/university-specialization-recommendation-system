# University Teaching Specialization Recommendation System

A system designed to match faculty members or employees with courses they are best qualified to teach, and identify skill gaps.

## Overview

This system uses a combination of techniques to provide course recommendations:

1. **Semantic Matching**: Matches skills based on semantic similarity
2. **Matrix Factorization**: Learns latent factors from skill distributions
3. **Customizable Recommendation**: Supports both faculty and custom skill inputs

## Features

-   Course recommendations based on skills
-   Skill gap analysis
-   Similar course discovery
-   Skill importance analysis
-   Employee/faculty course recommendations

## Data Structure

-   **Courses**: Defined in `src/data/course_skills.json`
-   **Employees/Faculty**: Generated or defined with skills that match to courses

## Getting Started

### Installation

1. Clone the repository
2. Install the required dependencies:

```bash
pip install fastapi uvicorn pandas numpy scikit-learn spacy
python -m spacy download en_core_web_md
```

### Running the API Server

```bash
uvicorn src.main:app --reload
```

The API will be available at http://localhost:8000 with documentation at http://localhost:8000/docs

## Using the Employee Recommendation System

### 1. Generate Employee Data

Generate synthetic employee data based on the skills in your courses:

```bash
python src/scripts/generate_employees.py
```

This will create a file called `employees.json` in the `src/data` directory.

### 2. Train the Employee-Course Model

Train a model to recommend courses for employees:

```bash
python src/scripts/train_employee_model.py
```

This process:

-   Creates matrices from employee skills and course requirements
-   Trains an NMF model to learn latent factors
-   Saves the model to `src/models/persistence/saved_models/employee_course_model.npz`
-   Generates skill importance analysis in `src/data/skill_importance.csv`

### 3. Get Recommendations

Use the trained model to get recommendations:

```bash
# List all employees
python src/scripts/recommend_with_employee_model.py --list-employees

# List all courses
python src/scripts/recommend_with_employee_model.py --list-courses

# Get recommendations for a specific employee
python src/scripts/recommend_with_employee_model.py --employee [EMPLOYEE_ID] --top 10

# Find similar courses to a specific course
python src/scripts/recommend_with_employee_model.py --course [COURSE_CODE] --top 5
```

## Customizing the System

### Adding New Courses

Add new courses to `src/data/course_skills.json` with the following format:

```json
{
    "COURSE_CODE": {
        "name": "Course Name",
        "required_skills": {
            "Skill 1": "Advanced",
            "Skill 2": "Intermediate",
            "Skill 3": "Beginner"
        }
    }
}
```

Then rebuild the model:

```bash
python src/rebuild_model.py
```

### Adding Real Employee Data

Replace the generated employee data with real data by creating an `employees.json` file:

```json
[
    {
        "id": "emp123",
        "name": "Employee Name",
        "department": "Department Name",
        "skills": [
            {
                "skill": "Skill Name",
                "proficiency": "Advanced"
            }
        ]
    }
]
```

## API Endpoints

-   `GET /api/courses`: Get all available courses
-   `GET /api/courses/{code}`: Get a specific course by code
-   `GET /api/faculties`: Get all faculty members
-   `POST /api/skills-to-courses`: Get course recommendations based only on skills
-   `GET /api/similar-courses/{course_code}`: Find courses similar to a given course
-   `GET /api/skill-importance`: Get the importance of each skill

## License

This project is licensed under the MIT License.
