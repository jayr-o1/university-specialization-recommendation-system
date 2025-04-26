# University Specialization Recommendation System

A Python-based intelligent recommendation system that suggests university courses based on student skill profiles and interests. The system categorizes skills into related hierarchical groups, making it easier to match students with appropriate courses and suggest related skills they might want to learn. It also provides tools for faculty members to identify their skill gaps and development opportunities.

## Key Features

-   **Hierarchical skill categorization**: Skills are organized in a structured way (e.g., Tailwind CSS is categorized with other CSS frameworks)
-   **Skill proficiency and project experience weighting**: Recommendations factor in skill levels and practical application
-   **Multi-dimensional course matching**: Finds courses based on skill category matches
-   **Related skill suggestions**: Helps students discover new skills to complement their existing knowledge
-   **Faculty Skill Development**: Helps faculty members identify skill gaps and development opportunities based on industry trends
-   **Teaching Advisor**: Assists teachers in identifying courses they're qualified to teach and highlights skill gaps for courses they might want to teach

## System Components

### Core Modules

-   `skill_categories.py`: Core skill categorizer class that builds and maintains the skill taxonomy
-   `enhanced_recommendation_model.py`: Advanced recommendation model using content-based filtering, collaborative filtering, skill graph analysis, and career path alignment
-   `faculty_skills_analyzer.py`: Analyzes faculty skills and identifies development opportunities based on industry trends
-   `faculty_development_advisor.py`: Interactive CLI tool for faculty skill development recommendations
-   `faculty_teaching_advisor.py`: Helps teachers identify their skill gaps for courses and find courses where they can apply their existing skills effectively

### Data Files

-   `data/course_skills.json`: Original course data with required skills
-   `data/skill_categories.json`: Hierarchical organization of skills by category
-   `data/enhanced_course_skills.json`: Generated file that maps courses to skill categories
-   `data/industry_skills.json`: Current in-demand and emerging skills across academic disciplines
-   `data/faculty_skills_sample.csv`: Sample faculty skills data for demonstration
-   `data/skill_graph.json`: Knowledge graph representing relationships between different skills

## Usage Modes

The system offers multiple ways to interact with its functionality:

1. **Enhanced CLI Mode**: `python run.py enhanced` - Interactive command-line interface for course recommendations based on skills
2. **Faculty Advisor**: `python run.py faculty` - Tool for faculty members to identify skill development opportunities
3. **Teaching Advisor**: `python run.py faculty-teaching` - Tool for teachers to identify courses they can teach and skill gaps
4. **API Mode**: `python run.py api` - Starts an API server for programmatic access to recommendations
5. **Web Interface**: `python run.py web` - Starts a web application for user-friendly access
6. **Test Mode**: `python run.py test` - Runs the system with example input

## How It Works

1. **Skill Categorization**: Skills are organized in a hierarchical structure in `data/skill_categories.json`. For example:

    ```
    web_development
    ├── frontend
    │   ├── markup_and_styling
    │   ├── css_frameworks (Bootstrap, Tailwind CSS, etc.)
    │   ├── javascript
    │   └── ui_ux
    ├── backend
    ├── devops_deployment
    └── ...
    ```

2. **Skill Mapping**: The system maps course skills to these categories, handling both exact and partial matches. For example, "CSS Frameworks (e.g., Bootstrap, Tailwind CSS)" will properly categorize even if a student specifically lists "Tailwind CSS".

3. **Enhanced Recommendation Algorithm**: Recommendations factor in:

    - Skill proficiency (Beginner, Intermediate, Advanced, Expert)
    - Project-backed skills (practical application)
    - Skill category matching between student profile and course requirements
    - Collaborative filtering based on other users' preferences
    - Skill graph analysis for suggesting related skills
    - Career path alignment for personalized learning paths

4. **Faculty Teaching Analysis**: For teachers, the system:

    - Analyzes existing skills and matches them with course requirements
    - Identifies skill gaps that prevent teaching specific courses
    - Recommends courses that are best matches for current skill sets
    - Suggests skill development priorities based on teaching goals

5. **Skill Gap Visualization**: The system can generate visual representations of skill gaps between faculty members and course requirements, making it easier to plan professional development.

## Installation and Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/university-specialization-recommendation-system.git
    cd university-specialization-recommendation-system
    ```

2. Set up a Python virtual environment (recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Generate the skill categories file:

    ```bash
    python create_skill_categories.py
    ```

4. Train the model and generate enhanced course skills:
    ```bash
    python skill_categories.py
    ```

## Running Tests

Run the test suite with 10 diverse student profiles:

```bash
python test_recommendation_system.py
```

This will:

1. Process each test case student profile
2. Generate course recommendations for each profile
3. Suggest related skills to learn
4. Save detailed results to `test_results.json`
5. Print a summary of the test results

## Faculty Development Advisor

The system includes a Faculty Development Advisor tool designed to help faculty members identify skill gaps and development opportunities based on current industry trends.

### Running the Faculty Advisor

```bash
python run.py faculty
```

This will start an interactive session where faculty members can:

1. Enter their current skills
2. Identify their academic department/area
3. Receive a personalized skill gap analysis
4. Get recommendations for skill development prioritized by industry demand

### Batch Analysis of Faculty Skills

You can also analyze skills for multiple faculty members using a CSV file:

```bash
python scripts/faculty_development_advisor.py --file data/faculty_skills_sample.csv
```

The system will:

1. Process each faculty member's profile
2. Generate skill gap analysis based on their department and current skills
3. Provide personalized development recommendations
4. Save detailed results to JSON files in the specified output directory

### Example Output

```
===== Your Skill Analysis =====
Department/Area: data_science

Skills You Already Have Matching Industry Demands:
High-demand skills:
  • Python
  • Statistical Analysis
  • Data Visualization

Recommended Skill Development Areas:

1. Machine Learning (Priority: high)
   Reason: High-demand industry skill
   Related skills you already have: Statistical Analysis, Data Analysis
   Prerequisites: Python, Statistics, Linear Algebra, Calculus
   Estimated learning time: 2-3 months

2. SQL (Priority: high)
   Reason: High-demand industry skill
   Prerequisites: Database Basics
   Missing prerequisites: Database Basics
   Estimated learning time: 1-2 months

3. Predictive Modeling (Priority: high)
   Reason: High-demand industry skill
   Related skills you already have: Statistical Analysis, Data Analysis
   Prerequisites: Statistics, Python, Data Analysis
   Estimated learning time: 2-3 months
```

## Using the API

You can use the recommendation system in your own applications:

```python
from skill_categories import SkillCategorizer
from test_recommendation_system import SkillRecommender

# Initialize the recommender
recommender = SkillRecommender()

# Example student profile
student_profile = {
    "name": "Jane Doe",
    "skills": [
        {"name": "HTML", "proficiency": "Advanced", "isBackedByProjects": True},
        {"name": "CSS", "proficiency": "Advanced", "isBackedByProjects": True},
        {"name": "JavaScript", "proficiency": "Intermediate", "isBackedByProjects": False},
        {"name": "Tailwind CSS", "proficiency": "Beginner", "isBackedByProjects": False}
    ],
    "interests": ["Web Development", "UI/UX Design"]
}

# Get course recommendations
recommendations = recommender.recommend_courses(student_profile)

# Get skill suggestions
suggested_skills = recommender.suggest_related_skills(student_profile)

# Print results
print("Recommended Courses:")
for match in recommendations["strongMatches"]:
    print(f"- {match['course']}: {match['reasoning']}")

print("\nSkills to Learn Next:")
for skill in suggested_skills:
    print(f"- {skill}")
```

## Customizing

-   **Add New Skill Categories**: Modify `create_skill_categories.py` to add or refine skill categories
-   **Adjust Matching Thresholds**: Change the matching thresholds in `SkillRecommender.recommend_courses()` method
-   **Expand Course Data**: Add more courses and their required skills to `data/course_skills.json`

## Future Development

-   Implement a web interface for student skill profile creation and recommendations
-   Add career path recommendations based on skill profiles
-   Incorporate feedback mechanisms to improve recommendations over time
-   Implement curriculum planning tools based on skill progression
-   Enhance faculty development tools with learning resources and course recommendations
-   Add collaborative skill-sharing features for faculty within the same department

## License

MIT License

## Proficiency Levels

-   **Beginner**: Basic knowledge (range 1-25)
-   **Intermediate**: Working knowledge (range 26-49)
-   **Advanced**: Comprehensive knowledge (range 50-74)
-   **Expert**: Deep expertise (range 75-100)

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
