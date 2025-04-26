# Faculty Skill Development System

A Python-based intelligent system designed to help university faculty identify their skill gaps, improve teaching competencies, and stay updated with industry trends. The system uses machine learning and TF-IDF based similarity matching to provide personalized course recommendations and skill development guidance.

## Key Features

-   **Machine Learning-based Recommendations**: Uses TF-IDF vectorization and cosine similarity for intelligent course matching
-   **Skill Proficiency and Certification Weighting**: Analysis factors in skill levels and formal certifications
-   **Faculty Teaching Advisor**: AI-powered system to match faculty skills with teachable courses
-   **Skill Gap Analysis**: Identifies missing skills and development opportunities
-   **Web Interface**: User-friendly interface for accessing all system features

## System Components

### Core Modules

-   `models/train_model.py`: Machine learning model for course recommendations
-   `faculty_skills_analyzer.py`: Analyzes faculty skills and identifies development opportunities
-   `faculty_teaching_advisor.py`: Matches faculty skills with courses and identifies teaching opportunities
-   `skill_matcher.py`: Core skill matching and recommendation engine

### Data Files

-   `data/enhanced_course_skills.json`: Enhanced course data with required skills and categories
-   `data/skill_categories.json`: Hierarchical organization of skills by category
-   `data/industry_skills.json`: Current in-demand and emerging skills
-   `models/trained_model.pkl`: Trained recommendation model

## How It Works

1. **Model Training**:

    - The system uses TF-IDF vectorization to create numerical representations of skills and courses
    - Cosine similarity is used to match faculty skills with course requirements
    - The trained model is saved as `trained_model.pkl` for consistent recommendations

2. **Recommendation Process**:

    - Faculty skills are vectorized using the same TF-IDF model
    - The system calculates similarity scores with all courses
    - Recommendations are filtered based on match percentage and skill requirements
    - Both skill-based matching and similarity scores are considered

3. **Faculty Teaching Analysis**:
    - Analyzes existing skills and matches them with course requirements
    - Uses the trained model to find the best course matches
    - Provides detailed match percentages and skill breakdowns
    - Identifies skill gaps with specific recommendations

## Installation and Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/faculty-skill-development-system.git
    cd faculty-skill-development-system
    ```

2. Set up a Python virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Train the recommendation model:
    ```bash
    python -c "from models.train_model import train_model; train_model()"
    ```

## Using the System

### Web Interface

1. Start the web server:

    ```bash
    python src/app.py
    ```

2. Access the interface at `http://localhost:5001`

3. Choose between:
    - Faculty Development Advisor
    - Teaching Advisor

### Faculty Teaching Advisor

Enter your skills in the format:

```
skill_name:proficiency:certified
```

Example:

```
Python:Advanced:yes, Machine Learning:Intermediate:no, Data Analysis:Expert:yes
```

Where:

-   Proficiency can be: Beginner, Intermediate, Advanced, or Expert
-   Certified is: yes/no to indicate certification status

### Example Output

```
===== Your Teaching Analysis =====

Courses You Can Teach (80%+ match):
1. Database Management (90.5% match)
   ✓ SQL (Advanced, certified)
   ✓ Database Design (Expert)
   ✗ Query Optimization

2. Data Science Fundamentals (85.2% match)
   ✓ Python (Advanced)
   ✓ Machine Learning (Intermediate)
   ✗ Deep Learning

Skill Development Opportunities:
1. Query Optimization
   - Related skills you have: SQL, Database Design
   - Estimated learning time: 1-2 months

2. Deep Learning
   - Related skills you have: Machine Learning, Python
   - Prerequisites: Mathematics, Statistics
   - Estimated learning time: 2-3 months
```

## API Usage

```python
from scripts.faculty_teaching_advisor import FacultyTeachingAdvisor

# Initialize advisor (automatically loads trained model)
advisor = FacultyTeachingAdvisor()

# Example faculty skills
faculty_skills = {
    "Python": {"proficiency": "Advanced", "isBackedByCertificate": True},
    "Machine Learning": {"proficiency": "Intermediate", "isBackedByCertificate": False},
    "SQL": {"proficiency": "Advanced", "isBackedByCertificate": True}
}

# Get teachable courses
teachable_courses = advisor.find_teachable_courses(faculty_skills, threshold=70)

# Get skill gaps
skill_gaps = advisor.identify_skill_gaps(faculty_skills)
```

## Model Training Details

The recommendation model uses:

-   TF-IDF (Term Frequency-Inverse Document Frequency) vectorization
-   Cosine similarity for skill matching
-   Proficiency level weighting
-   Certification status bonuses

The model is automatically trained when:

1. Starting the web interface for the first time
2. No existing trained model is found
3. Running the training script manually

To retrain the model:

```bash
python -c "from models.train_model import train_model; train_model()"
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests, report bugs, and suggest features.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
