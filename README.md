# Faculty Skill Development System

A Python-based intelligent system designed to help university faculty identify their skill gaps, improve teaching competencies, and stay updated with industry trends. The system categorizes skills into hierarchical groups, analyzes faculty skill profiles, and provides targeted recommendations for professional development.

## Key Features

-   **Hierarchical skill categorization**: Skills are organized in a structured way for meaningful analysis
-   **Skill proficiency and certification weighting**: Analysis factors in skill levels and formal certifications
-   **Faculty Skill Development**: Helps faculty members identify skill gaps and development opportunities based on industry trends
-   **Teaching Advisor**: Assists teachers in identifying courses they're qualified to teach and highlights skill gaps for courses they might want to teach
-   **Skill gap visualization**: Visual representation of skill gaps for easier understanding and planning

## System Components

### Core Modules

-   `skill_categories.py`: Core skill categorizer class that builds and maintains the skill taxonomy
-   `faculty_skills_analyzer.py`: Analyzes faculty skills and identifies development opportunities based on industry trends
-   `faculty_development_advisor.py`: Interactive CLI tool for faculty skill development recommendations
-   `faculty_teaching_advisor.py`: Helps teachers identify their skill gaps for courses and find courses where they can apply their existing skills effectively

### Data Files

-   `data/course_skills.json`: Course data with required skills
-   `data/skill_categories.json`: Hierarchical organization of skills by category
-   `data/industry_skills.json`: Current in-demand and emerging skills across academic disciplines
-   `data/faculty_skills_sample.csv`: Sample faculty skills data for demonstration
-   `data/skill_graph.json`: Knowledge graph representing relationships between different skills

## Usage Modes

The system offers multiple ways to interact with its functionality:

1. **Faculty Advisor**: `python run.py faculty` - Tool for faculty members to identify skill development opportunities
2. **Teaching Advisor**: `python run.py faculty-teaching` - Tool for teachers to identify courses they can teach and skill gaps
3. **API Mode**: `python run.py api` - Starts an API server for programmatic access
4. **Web Interface**: `python run.py web` - Starts a web application for user-friendly access

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

2. **Skill Mapping**: The system maps course skills to these categories, handling both exact and partial matches, allowing for more accurate skill gap analysis.

3. **Faculty Teaching Analysis**: For teachers, the system:

    - Analyzes existing skills and matches them with course requirements
    - Identifies skill gaps that prevent teaching specific courses
    - Recommends courses that are best matches for current skill sets
    - Suggests skill development priorities based on teaching goals

4. **Industry Trend Analysis**: The system compares faculty skills with current industry demands:

    - Identifies high-demand skills faculty already possess
    - Highlights missing skills that are in high demand
    - Prioritizes skill development recommendations based on industry relevance
    - Provides learning path information including prerequisites and estimated learning time

5. **Skill Gap Visualization**: The system can generate visual representations of skill gaps between faculty members and course requirements, making it easier to plan professional development.

## Installation and Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/faculty-skill-development-system.git
    cd faculty-skill-development-system
    ```

2. Set up a Python virtual environment (recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Generate the skill categories file:

    ```bash
    python create_skill_categories.py
    ```

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

### Faculty Teaching Advisor

To analyze which courses you're qualified to teach and identify skill gaps:

```bash
python run.py faculty-teaching
```

This tool will help you:

1. Identify courses you're fully qualified to teach
2. Show courses where you have most but not all required skills
3. Provide targeted recommendations for skills to develop to expand teaching capabilities

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

You can use the faculty development system in your own applications:

```python
from faculty_skills_analyzer import FacultySkillsAnalyzer

# Initialize the analyzer
analyzer = FacultySkillsAnalyzer()

# Example faculty profile
faculty_skills = {
    "Python": {"proficiency": "Advanced", "isBackedByCertificate": True},
    "Statistical Analysis": {"proficiency": "Advanced", "isBackedByCertificate": False},
    "Data Visualization": {"proficiency": "Intermediate", "isBackedByCertificate": False}
}

department = "data_science"

# Get skill gap analysis
skill_gaps = analyzer.identify_skill_gaps(faculty_skills, department)

# Get development recommendations
recommendations = analyzer.get_development_recommendations(skill_gaps)

# Print results
print(f"Skills to develop for {department}:")
for rec in recommendations:
    print(f"- {rec['skill']} (Priority: {rec['priority']})")
    print(f"  Reason: {rec['reason']}")
    if rec['missing_prerequisites']:
        print(f"  Missing prerequisites: {', '.join(rec['missing_prerequisites'])}")
    print(f"  Estimated learning time: {rec['estimated_learning_time']}")
```

## Customizing

-   **Add New Skill Categories**: Modify `create_skill_categories.py` to add or refine skill categories
-   **Expand Course Data**: Add more courses and their required skills to `data/course_skills.json`
-   **Update Industry Skills**: Modify `data/industry_skills.json` to reflect current industry trends

## Future Development

-   Incorporate feedback mechanisms to improve recommendations over time
-   Enhance faculty development tools with learning resources and course recommendations
-   Add collaborative skill-sharing features for faculty within the same department
-   Integrate with learning management systems for more comprehensive analysis
-   Develop department-level dashboards for skill gap analysis across faculty teams

## License

MIT License

## Proficiency Levels

-   **Beginner**: Basic knowledge (range 1-25)
-   **Intermediate**: Working knowledge (range 26-49)
-   **Advanced**: Comprehensive knowledge (range 50-74)
-   **Expert**: Deep expertise (range 75-100)
