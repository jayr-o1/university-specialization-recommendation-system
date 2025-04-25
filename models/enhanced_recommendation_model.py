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
        career_path_recs = []
        
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
        
        # 4. Career path recommendations (if user has career goals)
        if user_id in self.user_profiles and self.user_profiles[user_id]['career_goals']:
            career_goal = self.user_profiles[user_id]['career_goals'][0]
            career_path_recs = self.path_generator.get_career_aligned_courses(career_goal, top_n=top_n)
        
        # Combine recommendations with different weights
        combined_scores = defaultdict(float)
        component_scores = defaultdict(dict)
        course_history = self.user_profiles.get(user_id, {}).get('course_history', [])
        
        # Define weights for different recommendation components
        weights = {
            'content': 0.5,    # Content-based (skill matching) - 50%
            'collab': 0.3,     # Collaborative filtering - 30%
            'skill_graph': 0.1,  # Skill graph-based - 10%
            'career_path': 0.1   # Career path alignment - 10%
        }
        
        # Content-based recommendations (highest weight)
        for rec in content_recs:
            course = rec['course_name']
            if course not in course_history:  # Skip courses the user has already taken
                score = rec['match_percentage'] / 100.0  # Convert to 0-1 scale
                combined_scores[course] += score * weights['content']
                component_scores[course]['content_score'] = rec['match_percentage']
                component_scores[course]['content_details'] = rec
                
        # Collaborative filtering recommendations
        for rec in collab_recs:
            course = rec['course_name']
            if course not in course_history:
                # Normalize rating from 1-5 to 0-1 scale
                score = rec['predicted_rating'] / 5.0
                combined_scores[course] += score * weights['collab']
                component_scores[course]['collab_score'] = rec['predicted_rating'] * 20  # Scale to 0-100
                component_scores[course]['collab_details'] = rec
                
        # Skill graph-based recommendations
        for rec in skill_based_recs:
            course = rec['course_name']
            if course not in course_history:
                score = rec['relevance'] / 100.0  # Convert to 0-1 scale
                combined_scores[course] += score * weights['skill_graph']
                component_scores[course]['skill_graph_score'] = rec['relevance']
                
        # Career path recommendations
        for rec in career_path_recs:
            course = rec['course_name']
            if course not in course_history:
                score = rec['match_percentage'] / 100.0
                combined_scores[course] += score * weights['career_path']
                component_scores[course]['career_path_score'] = rec['match_percentage']
        
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
            
            # Add explainability data
            explanation_data = {
                'component_scores': {},
                'weights': weights,
                'recommendation_factors': []
            }
            
            # Add individual component scores
            if course_name in component_scores:
                if 'content_score' in component_scores[course_name]:
                    explanation_data['component_scores']['content_score'] = component_scores[course_name]['content_score']
                
                if 'collab_score' in component_scores[course_name]:
                    explanation_data['component_scores']['collab_score'] = component_scores[course_name]['collab_score']
                
                if 'skill_graph_score' in component_scores[course_name]:
                    explanation_data['component_scores']['skill_graph_score'] = component_scores[course_name]['skill_graph_score']
                
                if 'career_path_score' in component_scores[course_name]:
                    explanation_data['component_scores']['career_path_score'] = component_scores[course_name]['career_path_score']
            
            # Add factors that influenced this recommendation
            if recommendation['matched_skills']:
                explanation_data['recommendation_factors'].append({
                    'factor': 'Skill Match',
                    'description': f"You already have {len(recommendation['matched_skills'])} relevant skills for this course",
                    'importance': 'high'
                })
            
            if 'predicted_rating' in recommendation:
                explanation_data['recommendation_factors'].append({
                    'factor': 'User Ratings',
                    'description': f"Similar users rated this course {recommendation['predicted_rating']:.1f}/5.0",
                    'importance': 'medium'
                })
            
            if recommendation['missing_skills']:
                explanation_data['recommendation_factors'].append({
                    'factor': 'Skill Development',
                    'description': f"This course teaches {len(recommendation['missing_skills'])} new skills that complement your profile",
                    'importance': 'medium'
                })
            
            # Add career path alignment if applicable
            if user_id in self.user_profiles and self.user_profiles[user_id]['career_goals']:
                career_goal = self.user_profiles[user_id]['career_goals'][0]
                if 'career_path_score' in component_scores.get(course_name, {}):
                    explanation_data['recommendation_factors'].append({
                        'factor': 'Career Alignment',
                        'description': f"This course aligns with your {career_goal} career goal",
                        'importance': 'medium'
                    })
            
            recommendation['explanation_data'] = explanation_data
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
        similar_courses = self.content_recommender.find_similar_courses(course_name, top_n)
        
        # Enhance with additional information
        for course in similar_courses:
            course_skills = set(self.course_data.get(course['course_name'], {}).get('required_skills', []))
            target_skills = set(self.course_data.get(course_name, {}).get('required_skills', []))
            
            if course_skills and target_skills:
                common_skills = course_skills.intersection(target_skills)
                course['common_skills'] = list(common_skills)
        
        return similar_courses
    
    def explain_recommendation(self, course_name, user_id):
        """
        Generate a detailed explanation for why a course was recommended
        
        Args:
            course_name: Name of the recommended course
            user_id: User ID for the recommendation
            
        Returns:
            Dict with explanation data
        """
        if user_id not in self.user_profiles:
            return {"error": "User profile not found"}
            
        user_skills = self.user_profiles[user_id]['skills']
        
        # Find the recommendation data
        rec_history = self.user_profiles[user_id].get('recent_recommendations', [])
        if course_name not in rec_history:
            # Re-recommend to get fresh data
            recommendations = self.recommend_courses(user_id, top_n=10)
            rec = next((r for r in recommendations if r['course_name'] == course_name), None)
        else:
            # Use last recommendations to explain
            recommendations = self.recommend_courses(user_id, top_n=10)
            rec = next((r for r in recommendations if r['course_name'] == course_name), None)
        
        if not rec:
            return {"error": "Course not found in recommendations"}
            
        # Get course data
        course_data = self.course_data.get(course_name, {})
        if not course_data:
            return {"error": "Course data not found"}
            
        # Build a detailed explanation
        explanation = {
            "course_name": course_name,
            "match_percentage": rec.get('match_percentage', 0),
            "matched_skills": rec.get('matched_skills', []),
            "missing_skills": rec.get('missing_skills', []),
            "explanation_factors": rec.get('explanation_data', {}).get('recommendation_factors', []),
            "component_scores": rec.get('explanation_data', {}).get('component_scores', {}),
            "skill_gap_analysis": {}
        }
        
        # Add skill gap analysis
        if 'required_skills' in course_data and user_skills:
            required_skills = set(course_data['required_skills'])
            user_skill_set = set(user_skills.keys())
            
            explanation["skill_gap_analysis"] = {
                "total_required_skills": len(required_skills),
                "user_matched_skills": len(required_skills.intersection(user_skill_set)),
                "skill_gap_percentage": round((1 - len(required_skills.intersection(user_skill_set)) / len(required_skills)) * 100 if required_skills else 0)
            }
        
        # Add career relevance if applicable
        if self.user_profiles[user_id]['career_goals']:
            career_goal = self.user_profiles[user_id]['career_goals'][0]
            career_courses = self.path_generator.get_career_aligned_courses(career_goal)
            
            career_match = next((c for c in career_courses if c['course_name'] == course_name), None)
            if career_match:
                explanation["career_relevance"] = {
                    "career_goal": career_goal,
                    "relevance_score": career_match.get('match_percentage', 0),
                    "career_path_position": career_match.get('path_position', 'unknown')
                }
        
        return explanation

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