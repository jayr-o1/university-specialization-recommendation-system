import os
import sys
import json
import numpy as np
from collections import defaultdict

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.recommendation_model import CourseRecommendationModel
from models.learning_path import LearningPathGenerator
from models.collaborative_filter import CollaborativeFilter
from utils.skill_graph import SkillGraph

class EnhancedRecommendationModel:
    def __init__(self, course_skills_path, user_ratings_path=None):
        """Initialize the enhanced recommendation model
        
        Args:
            course_skills_path: Path to the course skills JSON file
            user_ratings_path: Path to user ratings JSON file (optional)
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, 'data')
        
        # Default paths if not provided
        if not course_skills_path:
            course_skills_path = os.path.join(data_dir, 'course_skills.json')
            
        if not user_ratings_path:
            user_ratings_path = os.path.join(data_dir, 'user_ratings.json')
        
        # Load course data
        with open(course_skills_path, 'r') as f:
            self.course_data = json.load(f)
        
        # Initialize skill graph
        self.skill_graph_path = os.path.join(os.path.dirname(course_skills_path), 'skill_graph.json')
        
        if os.path.exists(self.skill_graph_path):
            self.skill_graph = SkillGraph()
            self.skill_graph.load_graph(self.skill_graph_path)
        else:
            self.skill_graph = SkillGraph(course_skills_path)
            self.skill_graph.initialize_common_relationships()
            self.skill_graph.save_graph(self.skill_graph_path)
        
        # Initialize content-based recommender
        self.content_recommender = CourseRecommendationModel(course_skills_path)
        
        # Initialize learning path generator
        self.path_generator = LearningPathGenerator(course_skills_path, self.skill_graph)
        
        # Initialize collaborative filter
        self.collab_filter = CollaborativeFilter(user_ratings_path)
        
        # Create default user ratings if the file doesn't exist
        if not os.path.exists(user_ratings_path):
            self.collab_filter.create_default_ratings(course_skills_path, user_ratings_path)
            self.collab_filter.load_ratings(user_ratings_path)
        
        # User profile storage
        self.user_profiles = {}
    
    def create_user_profile(self, user_id, skills=None, interests=None, career_goals=None):
        """Create or update a user profile
        
        Args:
            user_id: Unique identifier for the user
            skills: Dict of skill-proficiency pairs (e.g., {"Python": "Advanced"})
            interests: List of topics the user is interested in
            career_goals: List of career fields or roles the user is targeting
        """
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'skills': {},
                'interests': [],
                'career_goals': [],
                'course_history': [],
                'recent_recommendations': []
            }
            
        # Update profile with new information
        if skills:
            self.user_profiles[user_id]['skills'].update(skills)
            
        if interests:
            self.user_profiles[user_id]['interests'] = list(set(
                self.user_profiles[user_id]['interests'] + interests
            ))
            
        if career_goals:
            self.user_profiles[user_id]['career_goals'] = list(set(
                self.user_profiles[user_id]['career_goals'] + career_goals
            ))
    
    def add_user_course_rating(self, user_id, course_name, rating):
        """Add a course rating from a user
        
        Args:
            user_id: Unique identifier for the user
            course_name: Name of the course
            rating: Rating value (typically 1-5)
        """
        # Add to collaborative filter
        if user_id in self.user_profiles:
            self.collab_filter.add_user_ratings(user_id, {course_name: rating})
            
            # Add to course history if not already there
            if course_name not in self.user_profiles[user_id]['course_history']:
                self.user_profiles[user_id]['course_history'].append(course_name)
            
            # Save the updated ratings
            ratings_dir = os.path.dirname(self.skill_graph_path)
            ratings_path = os.path.join(ratings_dir, 'user_ratings.json')
            self.collab_filter.save_ratings(ratings_path)
    
    def recommend_courses(self, user_id, user_skills=None, top_n=10):
        """Generate course recommendations using multiple recommendation strategies
        
        Args:
            user_id: Unique identifier for the user
            user_skills: Dict of skill-proficiency pairs (optional, will use profile if available)
            top_n: Number of recommendations to return
            
        Returns:
            List of recommended courses with details
        """
        # Get or create user profile
        if user_id not in self.user_profiles and user_skills:
            self.create_user_profile(user_id, skills=user_skills)
        elif user_id not in self.user_profiles:
            # Create empty profile if user doesn't exist and no skills provided
            self.create_user_profile(user_id)
        
        # Use skills from profile if not provided directly
        if not user_skills and user_id in self.user_profiles:
            user_skills = self.user_profiles[user_id]['skills']
        
        if not user_skills:
            user_skills = {}
        
        # Get recommendations from different sources
        content_recs = []
        collab_recs = []
        skill_based_recs = []
        
        # 1. Content-based recommendations
        if user_skills:
            content_recs = self.content_recommender.recommend_courses(user_skills, top_n=top_n*2)
        
        # 2. Collaborative filtering recommendations
        collab_recs = self.collab_filter.hybrid_recommendations(user_id, top_n=top_n*2)
        
        # 3. Skill graph-based recommendations
        if user_skills:
            next_skills = self.skill_graph.suggest_next_skills(user_skills, top_n=10)
            skill_based_recs = self._recommend_courses_for_skills(
                [item['skill'] for item in next_skills], top_n=top_n
            )
        
        # Combine recommendations with different weights
        combined_scores = defaultdict(float)
        course_history = self.user_profiles.get(user_id, {}).get('course_history', [])
        
        # Content-based recommendations (highest weight)
        for rec in content_recs:
            course = rec['course_name']
            if course not in course_history:  # Skip courses the user has already taken
                score = rec['match_percentage'] / 100.0  # Convert to 0-1 scale
                combined_scores[course] += score * 0.5  # 50% weight
                
        # Collaborative filtering recommendations
        for rec in collab_recs:
            course = rec['course_name']
            if course not in course_history:
                # Normalize rating from 1-5 to 0-1 scale
                score = rec['predicted_rating'] / 5.0
                combined_scores[course] += score * 0.3  # 30% weight
                
        # Skill graph-based recommendations
        for rec in skill_based_recs:
            course = rec['course_name']
            if course not in course_history:
                score = rec['relevance'] / 100.0  # Convert to 0-1 scale
                combined_scores[course] += score * 0.2  # 20% weight
        
        # Sort courses by combined score
        sorted_courses = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Prepare detailed recommendations
        recommendations = []
        for course_name, score in sorted_courses[:top_n]:
            # Get match details from content recommender
            match_details = next((rec for rec in content_recs if rec['course_name'] == course_name), None)
            
            if match_details:
                # Already have details from content-based recommender
                recommendation = match_details.copy()
                recommendation['combined_score'] = int(score * 100)  # Convert to percentage
            else:
                # Create basic recommendation details
                recommendation = {
                    'course_name': course_name,
                    'combined_score': int(score * 100),
                    'matched_skills': [],
                    'missing_skills': []
                }
                
                # Try to get skill matches from course data
                if course_name in self.course_data:
                    required_skills = set(self.course_data[course_name]['required_skills'])
                    user_skill_set = set(user_skills.keys())
                    
                    matched = required_skills.intersection(user_skill_set)
                    missing = required_skills - user_skill_set
                    
                    recommendation['matched_skills'] = [
                        f"{skill} ({user_skills[skill]})" for skill in matched
                    ]
                    recommendation['missing_skills'] = list(missing)
            
            # Add collaborative filtering score if available
            collab_rec = next((rec for rec in collab_recs if rec['course_name'] == course_name), None)
            if collab_rec:
                recommendation['predicted_rating'] = collab_rec['predicted_rating']
            
            recommendations.append(recommendation)
        
        # Store recommendations in user profile
        if user_id in self.user_profiles:
            self.user_profiles[user_id]['recent_recommendations'] = [
                rec['course_name'] for rec in recommendations
            ]
            
        return recommendations
    
    def _recommend_courses_for_skills(self, target_skills, top_n=5):
        """Recommend courses that teach specific target skills"""
        course_scores = {}
        
        for course_name, course_info in self.course_data.items():
            course_skills = set(course_info['required_skills'])
            
            # Score based on how many target skills are covered
            matches = 0
            for skill in target_skills:
                if skill in course_skills:
                    matches += 1
            
            if matches > 0:
                # Calculate relevance percentage
                relevance = (matches / len(target_skills)) * 100
                course_scores[course_name] = relevance
        
        # Sort by relevance
        sorted_courses = sorted(course_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return top N courses
        return [{'course_name': course, 'relevance': score} 
                for course, score in sorted_courses[:top_n]]
    
    def generate_learning_path(self, user_id, career_goal=None, path_length=5):
        """Generate a personalized learning path for a user
        
        Args:
            user_id: Unique identifier for the user
            career_goal: Target career or specialization (optional)
            path_length: Maximum number of courses in the path
            
        Returns:
            List of courses forming a learning path
        """
        # Get user skills
        if user_id not in self.user_profiles:
            return []
        
        user_skills = self.user_profiles[user_id]['skills']
        
        # Use first career goal from profile if not provided
        if not career_goal and self.user_profiles[user_id]['career_goals']:
            career_goal = self.user_profiles[user_id]['career_goals'][0]
        
        # Generate learning path
        return self.path_generator.generate_learning_path(
            user_skills, career_goal, path_length
        )
    
    def get_next_skill_recommendations(self, user_id, top_n=5):
        """Get recommendations for next skills to learn
        
        Args:
            user_id: Unique identifier for the user
            top_n: Number of skills to recommend
            
        Returns:
            List of recommended skills with relevance scores
        """
        if user_id not in self.user_profiles:
            return []
        
        user_skills = self.user_profiles[user_id]['skills']
        
        return self.skill_graph.suggest_next_skills(user_skills, top_n)
    
    def get_popular_courses(self, top_n=10):
        """Get the most popular courses based on user ratings"""
        return self.collab_filter.get_popular_courses(top_n)
    
    def get_top_rated_courses(self, min_ratings=3, top_n=10):
        """Get the highest rated courses"""
        return self.collab_filter.get_top_rated_courses(min_ratings, top_n)
    
    def find_similar_courses(self, course_name, top_n=5):
        """Find courses similar to a given course"""
        return self.content_recommender.find_similar_courses(course_name, top_n)

# Example usage
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    
    course_skills_path = os.path.join(data_dir, 'course_skills.json')
    user_ratings_path = os.path.join(data_dir, 'user_ratings.json')
    
    # Initialize enhanced recommendation model
    model = EnhancedRecommendationModel(course_skills_path, user_ratings_path)
    
    # Create a test user profile
    test_user = "test_user_1"
    test_skills = {
        "HTML": "Advanced",
        "CSS": "Intermediate",
        "JavaScript": "Beginner",
        "Web Design Principles": "Intermediate"
    }
    
    model.create_user_profile(
        test_user, 
        skills=test_skills,
        interests=["Web Development", "Design"],
        career_goals=["Web Design & Development"]
    )
    
    # Generate recommendations
    recommendations = model.recommend_courses(test_user, top_n=5)
    
    print("Enhanced Course Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['course_name']} - {rec['combined_score']}% Match")
        
    # Generate learning path
    learning_path = model.generate_learning_path(test_user, career_goal="Web Design & Development")
    
    print("\nPersonalized Learning Path:")
    for step in learning_path:
        print(f"{step['step']}. {step['course_name']} - {step['match_percentage']}% Match")
        if step['next_steps_rationale']:
            print(f"   Rationale: {step['next_steps_rationale']}")
            
    # Get next skill recommendations
    next_skills = model.get_next_skill_recommendations(test_user)
    
    print("\nRecommended Skills to Learn Next:")
    for i, skill in enumerate(next_skills, 1):
        print(f"{i}. {skill['skill']} - {skill['relevance']:.2f} relevance score") 