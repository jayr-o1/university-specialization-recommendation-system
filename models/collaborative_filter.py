import os
import json
import numpy as np
import pandas as pd
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity

class CollaborativeFilter:
    def __init__(self, user_ratings_path=None):
        """Initialize the collaborative filtering model"""
        self.user_ratings = {}  # user_id -> {course: rating}
        self.course_ratings = {}  # course -> {user_id: rating}
        self.user_similarity = {}  # user_id -> {other_user_id: similarity}
        self.course_similarity = {}  # course -> {other_course: similarity}
        
        # Load user ratings if provided
        if user_ratings_path and os.path.exists(user_ratings_path):
            self.load_ratings(user_ratings_path)
            self.compute_similarities()
    
    def load_ratings(self, ratings_path):
        """Load user ratings from a JSON file"""
        with open(ratings_path, 'r') as f:
            ratings_data = json.load(f)
            
        for user_id, ratings in ratings_data.items():
            self.add_user_ratings(user_id, ratings)
    
    def add_user_ratings(self, user_id, ratings):
        """Add ratings for a user
        
        Args:
            user_id (str): Unique identifier for the user
            ratings (dict): Dict of {course_name: rating} pairs
        """
        # Add to user_ratings dictionary
        self.user_ratings[user_id] = ratings
        
        # Add to course_ratings dictionary
        for course, rating in ratings.items():
            if course not in self.course_ratings:
                self.course_ratings[course] = {}
            self.course_ratings[course][user_id] = rating
        
        # Recompute similarities with the new data
        self._compute_user_similarity(user_id)
        for course in ratings:
            self._compute_course_similarity(course)
    
    def compute_similarities(self):
        """Compute all user and course similarities"""
        # Compute user similarities
        for user_id in self.user_ratings:
            self._compute_user_similarity(user_id)
        
        # Compute course similarities
        for course in self.course_ratings:
            self._compute_course_similarity(course)
    
    def _compute_user_similarity(self, user_id):
        """Compute similarity between a user and all other users"""
        if user_id not in self.user_ratings:
            return
            
        # Get the target user's ratings
        target_ratings = self.user_ratings[user_id]
        
        # Calculate similarity with each other user
        similarities = {}
        for other_id, other_ratings in self.user_ratings.items():
            if other_id == user_id:
                continue
                
            # Find common courses
            common_courses = set(target_ratings.keys()) & set(other_ratings.keys())
            
            # Need at least 2 common courses to calculate meaningful similarity
            if len(common_courses) >= 2:
                # Extract ratings for common courses
                target_vector = [target_ratings[course] for course in common_courses]
                other_vector = [other_ratings[course] for course in common_courses]
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(target_vector, other_vector)
                similarities[other_id] = similarity
        
        # Store the calculated similarities
        self.user_similarity[user_id] = similarities
    
    def _compute_course_similarity(self, course):
        """Compute similarity between a course and all other courses"""
        if course not in self.course_ratings:
            return
            
        # Get ratings for the target course
        target_ratings = self.course_ratings[course]
        
        # Calculate similarity with each other course
        similarities = {}
        for other_course, other_ratings in self.course_ratings.items():
            if other_course == course:
                continue
                
            # Find common users
            common_users = set(target_ratings.keys()) & set(other_ratings.keys())
            
            # Need at least 2 common users for meaningful similarity
            if len(common_users) >= 2:
                # Extract ratings from common users
                target_vector = [target_ratings[user] for user in common_users]
                other_vector = [other_ratings[user] for user in common_users]
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(target_vector, other_vector)
                similarities[other_course] = similarity
        
        # Store the calculated similarities
        self.course_similarity[course] = similarities
    
    def _cosine_similarity(self, vector1, vector2):
        """Calculate cosine similarity between two vectors"""
        dot_product = sum(a * b for a, b in zip(vector1, vector2))
        magnitude1 = sum(a * a for a in vector1) ** 0.5
        magnitude2 = sum(b * b for b in vector2) ** 0.5
        
        if magnitude1 * magnitude2 == 0:
            return 0
            
        return dot_product / (magnitude1 * magnitude2)
    
    def user_based_recommendations(self, user_id, top_n=5):
        """Generate user-based collaborative filtering recommendations
        
        Find similar users and recommend courses they rated highly
        """
        if user_id not in self.user_ratings:
            return []
            
        # Get the user's existing ratings
        user_courses = set(self.user_ratings[user_id].keys())
        
        # If user doesn't have similarities calculated yet
        if user_id not in self.user_similarity:
            self._compute_user_similarity(user_id)
        
        # Get similar users
        similar_users = self.user_similarity.get(user_id, {})
        
        if not similar_users:
            return []  # No similar users found
        
        # Calculate predicted ratings for unrated courses
        predicted_ratings = {}
        
        for course in self.course_ratings:
            # Skip courses the user has already rated
            if course in user_courses:
                continue
                
            # Find users who rated this course
            course_raters = set(self.course_ratings[course].keys())
            
            # Find similar users who rated this course
            similar_raters = {u: s for u, s in similar_users.items() if u in course_raters}
            
            if not similar_raters:
                continue  # No similar users rated this course
                
            # Calculate weighted average rating
            numerator = 0
            denominator = 0
            
            for rater, similarity in similar_raters.items():
                rating = self.course_ratings[course][rater]
                numerator += similarity * rating
                denominator += abs(similarity)
            
            if denominator > 0:
                predicted_ratings[course] = numerator / denominator
        
        # Sort by predicted rating
        sorted_recommendations = sorted(predicted_ratings.items(), 
                                       key=lambda x: x[1], 
                                       reverse=True)
        
        # Return top N recommendations
        return [{'course_name': course, 'predicted_rating': rating} 
                for course, rating in sorted_recommendations[:top_n]]
    
    def item_based_recommendations(self, user_id, top_n=5):
        """Generate item-based collaborative filtering recommendations
        
        Find courses similar to those the user has rated highly
        """
        if user_id not in self.user_ratings:
            return []
            
        # Get the user's existing ratings
        user_ratings = self.user_ratings[user_id]
        
        # Calculate predicted ratings for unrated courses
        predicted_ratings = {}
        
        for candidate_course in self.course_ratings:
            # Skip courses the user has already rated
            if candidate_course in user_ratings:
                continue
                
            # Skip courses with no similarity data
            if candidate_course not in self.course_similarity:
                continue
                
            # Calculate weighted rating based on similar courses the user has rated
            similarities = []
            ratings = []
            
            for rated_course, rating in user_ratings.items():
                # Check if we have similarity data for this pair
                if rated_course in self.course_similarity.get(candidate_course, {}):
                    similarity = self.course_similarity[candidate_course][rated_course]
                    similarities.append(similarity)
                    ratings.append(rating)
            
            # Need at least one similar course
            if similarities:
                # Calculate weighted average
                weighted_sum = sum(s * r for s, r in zip(similarities, ratings))
                sum_similarities = sum(abs(s) for s in similarities)
                
                if sum_similarities > 0:
                    predicted_ratings[candidate_course] = weighted_sum / sum_similarities
        
        # Sort by predicted rating
        sorted_recommendations = sorted(predicted_ratings.items(), 
                                       key=lambda x: x[1], 
                                       reverse=True)
        
        # Return top N recommendations
        return [{'course_name': course, 'predicted_rating': rating} 
                for course, rating in sorted_recommendations[:top_n]]
    
    def hybrid_recommendations(self, user_id, top_n=5, user_weight=0.5):
        """Generate hybrid recommendations combining user and item based approaches"""
        # Get recommendations from both methods
        user_recs = self.user_based_recommendations(user_id, top_n=top_n*2)
        item_recs = self.item_based_recommendations(user_id, top_n=top_n*2)
        
        # Convert to dictionaries for easier merging
        user_dict = {rec['course_name']: rec['predicted_rating'] for rec in user_recs}
        item_dict = {rec['course_name']: rec['predicted_rating'] for rec in item_recs}
        
        # Combine predictions
        combined_ratings = {}
        all_courses = set(user_dict.keys()) | set(item_dict.keys())
        
        for course in all_courses:
            user_rating = user_dict.get(course, 0)
            item_rating = item_dict.get(course, 0)
            
            # Weighted average of the two ratings
            if course in user_dict and course in item_dict:
                # Both methods gave a prediction
                combined_ratings[course] = (user_weight * user_rating + 
                                           (1 - user_weight) * item_rating)
            elif course in user_dict:
                # Only user-based gave a prediction
                combined_ratings[course] = user_rating
            else:
                # Only item-based gave a prediction
                combined_ratings[course] = item_rating
        
        # Sort by combined rating
        sorted_recommendations = sorted(combined_ratings.items(), 
                                       key=lambda x: x[1], 
                                       reverse=True)
        
        # Return top N recommendations
        return [{'course_name': course, 'predicted_rating': rating} 
                for course, rating in sorted_recommendations[:top_n]]
                
    def create_default_ratings(self, course_skills_path, output_path):
        """Create a default ratings file from course data for testing"""
        # Load course data
        with open(course_skills_path, 'r') as f:
            course_data = json.load(f)
            
        # Generate synthetic users and ratings
        num_users = 50  # Number of synthetic users
        synthetic_ratings = {}
        
        courses = list(course_data.keys())
        rng = np.random.RandomState(42)  # For reproducibility
        
        # For each synthetic user
        for i in range(num_users):
            user_id = f"user_{i}"
            
            # Randomly select 5-15 courses to rate
            num_ratings = rng.randint(5, min(15, len(courses)))
            rated_courses = rng.choice(courses, size=num_ratings, replace=False)
            
            # Generate ratings (1-5 scale)
            user_ratings = {}
            for course in rated_courses:
                rating = rng.randint(1, 6)  # 1-5 scale
                user_ratings[course] = rating
                
            synthetic_ratings[user_id] = user_ratings
            
        # Save the synthetic ratings
        with open(output_path, 'w') as f:
            json.dump(synthetic_ratings, f, indent=2)
            
        print(f"Created default ratings file at {output_path}")
        
    def save_ratings(self, output_path):
        """Save current user ratings to file"""
        with open(output_path, 'w') as f:
            json.dump(self.user_ratings, f, indent=2)
            
    def get_popular_courses(self, top_n=10):
        """Get the most popular courses based on number of ratings"""
        course_popularity = {course: len(ratings) for course, ratings in self.course_ratings.items()}
        
        # Sort by number of ratings
        sorted_courses = sorted(course_popularity.items(), key=lambda x: x[1], reverse=True)
        
        # Return top N courses
        return [{'course_name': course, 'num_ratings': count} 
                for course, count in sorted_courses[:top_n]]
                
    def get_top_rated_courses(self, min_ratings=3, top_n=10):
        """Get the top rated courses with a minimum number of ratings"""
        # Calculate average rating for each course with enough ratings
        avg_ratings = {}
        
        for course, ratings in self.course_ratings.items():
            if len(ratings) >= min_ratings:
                avg_rating = sum(ratings.values()) / len(ratings)
                avg_ratings[course] = avg_rating
        
        # Sort by average rating
        sorted_courses = sorted(avg_ratings.items(), key=lambda x: x[1], reverse=True)
        
        # Return top N courses
        return [{'course_name': course, 'avg_rating': rating} 
                for course, rating in sorted_courses[:top_n]]

# Example usage
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    
    # Path for course skills data
    course_skills_path = os.path.join(data_dir, 'course_skills.json')
    
    # Path for user ratings
    ratings_path = os.path.join(data_dir, 'user_ratings.json')
    
    # Create a new collaborative filter
    collab_filter = CollaborativeFilter()
    
    # Create default ratings if they don't exist
    if not os.path.exists(ratings_path):
        collab_filter.create_default_ratings(course_skills_path, ratings_path)
    
    # Load the ratings
    collab_filter.load_ratings(ratings_path)
    
    # Print top-rated courses
    top_courses = collab_filter.get_top_rated_courses(min_ratings=3)
    print("Top Rated Courses:")
    for i, course in enumerate(top_courses[:5], 1):
        print(f"{i}. {course['course_name']} - {course['avg_rating']:.2f} average rating")
    
    # Generate recommendations for a test user
    test_user = "user_0"
    recommendations = collab_filter.hybrid_recommendations(test_user, top_n=5)
    
    print(f"\nRecommendations for {test_user}:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['course_name']} - {rec['predicted_rating']:.2f} predicted rating") 