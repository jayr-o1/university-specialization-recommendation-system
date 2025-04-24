# University Teaching Specialization Recommendation System

A system designed to match university faculty members with courses they are best qualified to teach, based on their skills and proficiency levels using semantic benchmarking and machine learning.

## Purpose

This system helps university departments:

-   Match faculty members with subjects they can teach most effectively
-   Identify skill gaps for professional development opportunities
-   Improve teaching quality by ensuring instructors teach subjects aligned with their expertise
-   Support faculty professional growth through targeted skill development

## Features

-   Faculty skill and proficiency level tracking (Beginner, Intermediate, Advanced, Expert)
-   Course-to-faculty matching using semantic similarity analysis
-   Advanced recommendations using matrix factorization models
-   Percentage match calculation for course recommendations
-   Identification of missing or underdeveloped skills
-   Similar course recommendations based on skill profiles
-   Skill importance analysis across latent factors
-   API for programmatic access and integration

## Technology Stack

-   **Backend Framework**: FastAPI with Uvicorn server
-   **Data Processing**: Pandas and NumPy for data manipulation
-   **Machine Learning**: scikit-learn for matrix factorization (NMF)
-   **Natural Language Processing**: spaCy for semantic similarity with en_core_web_md model
-   **Data Visualization**: Matplotlib (for visualization in scripts)
-   **Data Storage**: JSON and CSV formats
-   **API Documentation**: OpenAPI (Swagger UI via FastAPI)

## Recommendation Models

The system provides two types of recommendation approaches:

1. **Semantic-based matching** (default):

    - Uses spaCy's NLP similarity to match skills directly
    - Calculates semantic similarity between faculty skills and course requirements
    - Weights matching based on proficiency levels
    - Identifies missing skills for development

2. **Model-based recommendations**:
    - Uses Non-negative Matrix Factorization (NMF) to learn latent factors
    - Represents courses and skills in a lower-dimensional latent space
    - Provides collaborative filtering-style recommendations
    - Offers insight into skill importance and course similarities

To use model-based recommendations via the API, add the query parameter `?use_model=true` to recommendation endpoints.

## Data Structure

-   **Courses**: Each course has a code, name, description, and required skills with proficiency levels
-   **Faculty**: Each faculty member has an ID, name, department, and a list of skills with proficiency levels
-   **Skills**: Skills are represented with a name and a proficiency level (Beginner to Expert)
-   **Dataset**: The system maintains both JSON and CSV formats:
    -   JSON format for easy human readability and editing
    -   CSV matrix format for machine learning models

## Setup

1. Install dependencies:

    ```
    pip install -r requirements.txt
    ```

2. Download the spaCy language model (will be done automatically on first run):

    ```
    python -m spacy download en_core_web_md
    ```

3. Run the application:

    ```
    python run.py
    ```

4. Or test the matching system directly:

    ```
    python test_matching.py
    ```

5. To train the recommendation model explicitly:
    ```
    python scripts/train_model.py
    ```

## API Endpoints

The system provides a RESTful API with the following endpoints:

### Courses

-   `GET /courses` - Get all available courses
-   `GET /courses/{code}` - Get a specific course by code

### Faculty

-   `GET /faculties` - Get all faculty members
-   `GET /faculties/{faculty_id}` - Get a specific faculty member by ID
-   `POST /faculties/{faculty_id}/skills` - Update a faculty member's skills

### Matching & Recommendations

-   `GET /match/faculty/{faculty_id}/course/{course_code}` - Match faculty to specific course
-   `GET /recommendations/faculty/{faculty_id}` - Get course recommendations for faculty
    -   Add `?use_model=true` to use ML-based recommendations
    -   Add `?top_n=10` to customize number of results
-   `POST /recommendations/custom` - Get recommendations based on custom skills
    -   Add `?use_model=true` to use ML-based recommendations

### Model-specific Endpoints

-   `GET /similar-courses/{course_code}` - Find courses similar to a given course
-   `GET /skill-importance` - Get the importance of skills across latent factors

For detailed API documentation with request/response schemas, visit `/docs` after starting the server.

## Project Structure

-   `models/` - Data models, schemas, and ML models
    -   `schemas.py` - Pydantic data models
    -   `recommender.py` - Matrix factorization recommendation model
-   `data/` - Course, faculty data, and training datasets
    -   `courses.py` - Course data with required skills
    -   `faculties.py` - Faculty data with skills and proficiency
    -   `dataset.py` - Dataset generation and management
-   `utils/` - Utility functions
    -   `data_access.py` - Data loading and manipulation functions
-   `matching/` - Matching algorithm implementation
    -   `semantic_matcher.py` - Semantic similarity based matching
-   `api/` - API endpoints
    -   `routes.py` - FastAPI route definitions
-   `scripts/` - Utility scripts
    -   `train_model.py` - Script to train and test the ML model
-   `main.py` - Application entry point
-   `run.py` - Server startup script
-   `test_matching.py` - Script to test the matching functionality

## Machine Learning Details

### Matrix Factorization (NMF)

The system uses Non-negative Matrix Factorization to decompose the skill-course matrix into:

-   Course-factor matrix (W) - How courses relate to latent factors
-   Factor-skill matrix (H) - How skills relate to latent factors

This allows the system to:

1. Find underlying patterns between skills and courses
2. Identify skill clusters through latent factors
3. Calculate similarity between courses based on their factor representation
4. Project faculty skills into the same latent space for matching

### Model Training

The model is trained on a matrix where:

-   Rows represent courses
-   Columns represent skills
-   Values represent required proficiency levels (1-4)

The training process:

1. Creates CSV datasets from existing course data
2. Initializes the NMF model with specified components (default: 5)
3. Learns the latent representations
4. Calculates course similarities
5. Saves the model for future use

The model is automatically loaded when needed or can be explicitly trained with the provided script.

## Extending the System

To add more courses or faculty members:

1. Edit the data files in the `data/` directory
2. Run `python scripts/train_model.py` to update the recommendation model

To extend the system with new features:

1. For new data models, add to `models/schemas.py`
2. For new API endpoints, add to `api/routes.py`
3. For algorithm improvements, modify `matching/semantic_matcher.py` or `models/recommender.py`

## License

This project is available for educational and research purposes.

For more detailed usage instructions, see [USAGE.md](USAGE.md)
