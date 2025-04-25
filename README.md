# University Specialization Recommendation System

An intelligent recommendation system that suggests university courses based on user skills and interests. The system analyzes the skills required for different courses and matches them with the user's proficiency levels to provide personalized recommendations.

## Features

### Basic Features
- Course recommendations based on user skills and proficiency levels
- Similar course recommendations
- Integration with course data sources
- Command-line interface for interaction

### Enhanced Features
- **Skill Knowledge Graph**: Understands relationships between skills (prerequisites, complementary skills, etc.)
- **Collaborative Filtering**: Considers ratings and preferences from other users
- **Personalized Learning Paths**: Creates custom course sequences to reach career goals
- **Next Skill Recommendations**: Suggests which skills to learn next based on your profile
- **User Profiles**: Maintains user preferences, skills, and course history
- **Popular and Top-Rated Courses**: Identifies trending and highly-rated courses

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

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/university-specialization-recommendation-system.git
   cd university-specialization-recommendation-system
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Basic Mode

Run the basic recommendation system:

```
python run.py cli
```

Enter your skills and proficiency levels when prompted (e.g., "MySQL : Intermediate, Database Design : Advanced").

### Enhanced Mode

Run the enhanced recommendation system with additional features:

```
python run.py enhanced
```

The enhanced mode provides a command-line interface with the following commands:

- `skills` - Enter your skills and get course recommendations
- `path` - Generate a personalized learning path based on career goals
- `rate` - Rate a course you've taken
- `popular` - See the most popular courses
- `top` - See the top-rated courses
- `similar <course name>` - Find courses similar to a specific course
- `nextskills` - Get recommendations for skills to learn next
- `exit` - Exit the application

### Other Commands

- Train the recommendation model:
  ```
  python run.py train
  ```

- Build the skill knowledge graph:
  ```
  python run.py build-graph
  ```

- Run tests:
  ```
  python run.py test
  ```

## Data Sources

The system uses the following data files:

- `data/course_skills.json` - Contains courses and their required skills
- `data/user_ratings.json` - Contains user ratings for courses (used in collaborative filtering)
- `data/skill_graph.json` - Contains the skill knowledge graph with skill relationships

## System Architecture

The system consists of several key components:

1. **Content-Based Recommender**: Matches user skills with course requirements
2. **Skill Knowledge Graph**: Models relationships between different skills
3. **Learning Path Generator**: Creates personalized course sequences
4. **Collaborative Filter**: Incorporates user ratings and preferences
5. **Enhanced Recommendation Model**: Combines all approaches for better recommendations

## Extensions and Future Work

- Web interface for easier interaction
- API for integration with other systems
- Integration with real-time job market data
- Natural language processing for skill extraction from course descriptions
- User study to validate recommendation quality

## License

This project is licensed under the MIT License - see the LICENSE file for details.

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