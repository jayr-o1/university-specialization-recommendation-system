# University Teaching Specialization Recommendation System

## Setup and Installation

1. Make sure you have Python 3.8+ installed
2. Install dependencies:
    ```
    pip install -r requirements.txt
    ```
3. Download the spaCy language model (will be done automatically on first run, or run this):
    ```
    python -m spacy download en_core_web_md
    ```

## Running the Application

### API Server

To start the API server:

```
python run.py
```

The API will be available at:

-   API: http://localhost:8000
-   Swagger UI documentation: http://localhost:8000/docs
-   ReDoc documentation: http://localhost:8000/redoc

### Testing the Matching System

To run the test script to see how the matching system works:

```
python test_matching.py
```

This will display sample faculty profiles, their top course matches, and recommended skills to develop.

## API Endpoints

### Courses

-   `GET /api/courses` - Get all courses
-   `GET /api/courses/{code}` - Get a specific course by code

### Faculty

-   `GET /api/faculties` - Get all faculty members
-   `GET /api/faculties/{faculty_id}` - Get a specific faculty member by ID
-   `POST /api/faculties/{faculty_id}/skills` - Update a faculty member's skills

### Matching

-   `GET /api/match/faculty/{faculty_id}/course/{course_code}` - Match a faculty member to a specific course
-   `GET /api/recommendations/faculty/{faculty_id}` - Get course recommendations for a faculty member
-   `POST /api/recommendations/custom` - Get course recommendations based on custom skills input

## Example Usage

### Get Course Recommendations for a Faculty Member

```
GET /api/recommendations/faculty/F001
```

### Get Course Recommendations for Custom Skills

```
POST /api/recommendations/custom
Content-Type: application/json

{
  "faculty_id": "",
  "skills": [
    {
      "skill": "Python",
      "proficiency": "Intermediate"
    },
    {
      "skill": "SQL",
      "proficiency": "Intermediate"
    },
    {
      "skill": "Database Design",
      "proficiency": "Beginner"
    }
  ]
}
```

## How the Matching Works

1. Faculty skills are compared with course required skills
2. Both exact matches and semantic similarities are considered
3. Proficiency levels are weighted (Beginner: 0.25, Intermediate: 0.5, Advanced: 0.75, Expert: 1.0)
4. A match percentage is calculated based on how well the faculty skills meet the course requirements
5. Missing or underdeveloped skills are identified for professional development
