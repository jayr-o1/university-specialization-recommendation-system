import json
import os
import numpy as np
from collections import defaultdict
import sys

# Add parent directory to path to import from sibling modules if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class SkillsMapper:
    """
    Maps user skills to course skills using semantic similarity.
    """
    
    def __init__(self, skill_embeddings_file='data/skill_embeddings.json', threshold=0.75):
        """
        Initialize the SkillsMapper.
        
        Args:
            skill_embeddings_file (str): Path to the skill embeddings file
            threshold (float): Similarity threshold for skill matching
        """
        self.threshold = threshold
        self.skill_embeddings = {}
        self.load_skill_embeddings(skill_embeddings_file)
        
    def load_skill_embeddings(self, filename):
        """
        Load skill embeddings from file.
        
        Args:
            filename (str): Path to the embeddings file
        """
        try:
            with open(filename, 'r') as f:
                self.skill_embeddings = json.load(f)
            print(f"Loaded {len(self.skill_embeddings)} skill embeddings")
        except FileNotFoundError:
            print(f"Warning: Skill embeddings file {filename} not found")
            self.skill_embeddings = {}
            
    def cosine_similarity(self, vec1, vec2):
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1 (list): First vector
            vec2 (list): Second vector
            
        Returns:
            float: Cosine similarity score
        """
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)
        
        # Avoid division by zero
        if norm_vec1 == 0 or norm_vec2 == 0:
            return 0
            
        return dot_product / (norm_vec1 * norm_vec2)
        
    def map_skills(self, user_skills, course_skills):
        """
        Map user skills to course skills using semantic similarity.
        
        Args:
            user_skills (list): List of user skills
            course_skills (list): List of course skills
            
        Returns:
            dict: Mapping of user skills to matched course skills with similarity scores
        """
        skill_mapping = defaultdict(list)
        
        # Check if embeddings are available
        if not self.skill_embeddings:
            print("No skill embeddings available. Using exact matching only.")
            
            # Fall back to exact matching
            for user_skill in user_skills:
                for course_skill in course_skills:
                    if user_skill.lower() == course_skill.lower():
                        skill_mapping[user_skill].append((course_skill, 1.0))
            
            return dict(skill_mapping)
        
        # For each user skill, find similar course skills
        for user_skill in user_skills:
            user_embedding = self.skill_embeddings.get(user_skill.lower(), None)
            
            if not user_embedding:
                # If no embedding for this skill, try exact matching
                for course_skill in course_skills:
                    if user_skill.lower() == course_skill.lower():
                        skill_mapping[user_skill].append((course_skill, 1.0))
                continue
                
            # Calculate similarity with each course skill
            for course_skill in course_skills:
                course_embedding = self.skill_embeddings.get(course_skill.lower(), None)
                
                if not course_embedding:
                    # If no embedding for course skill, check exact match
                    if user_skill.lower() == course_skill.lower():
                        skill_mapping[user_skill].append((course_skill, 1.0))
                    continue
                    
                # Calculate similarity
                similarity = self.cosine_similarity(user_embedding, course_embedding)
                
                # If similarity exceeds threshold, add to mapping
                if similarity >= self.threshold:
                    skill_mapping[user_skill].append((course_skill, similarity))
            
            # Sort matches by similarity score (descending)
            skill_mapping[user_skill] = sorted(skill_mapping[user_skill], key=lambda x: x[1], reverse=True)
            
        return dict(skill_mapping)
        
    def get_top_skills(self, user_skills, all_course_skills, max_matches=3):
        """
        Get top matching skills for each user skill from all available course skills.
        
        Args:
            user_skills (list): List of user skills
            all_course_skills (list): List of all available course skills
            max_matches (int): Maximum number of matches to return per skill
            
        Returns:
            dict: Dictionary mapping each user skill to its top matches
        """
        return self.map_skills(user_skills, all_course_skills)
        
    def group_related_skills(self, skills, similarity_threshold=0.8):
        """
        Group related skills based on semantic similarity.
        
        Args:
            skills (list): List of skills to group
            similarity_threshold (float): Threshold for grouping
            
        Returns:
            list: List of skill groups
        """
        if not self.skill_embeddings or len(skills) == 0:
            return [[skill] for skill in skills]
            
        # Initialize groups with the first skill
        groups = []
        processed_skills = set()
        
        for skill in skills:
            if skill in processed_skills:
                continue
                
            # Start a new group with this skill
            current_group = [skill]
            processed_skills.add(skill)
            
            # Get embedding for this skill
            skill_embedding = self.skill_embeddings.get(skill.lower(), None)
            if not skill_embedding:
                groups.append(current_group)
                continue
                
            # Find related skills
            for other_skill in skills:
                if other_skill in processed_skills:
                    continue
                    
                other_embedding = self.skill_embeddings.get(other_skill.lower(), None)
                if not other_embedding:
                    continue
                    
                # Calculate similarity
                similarity = self.cosine_similarity(skill_embedding, other_embedding)
                
                # If similar enough, add to current group
                if similarity >= similarity_threshold:
                    current_group.append(other_skill)
                    processed_skills.add(other_skill)
            
            groups.append(current_group)
            
        return groups
        
    def extract_key_skills(self, skill_groups, max_skills=10):
        """
        Extract representative skills from skill groups.
        
        Args:
            skill_groups (list): List of skill groups
            max_skills (int): Maximum number of key skills to extract
            
        Returns:
            list: List of key skills
        """
        if not skill_groups:
            return []
            
        key_skills = []
        
        # Sort groups by size (descending)
        sorted_groups = sorted(skill_groups, key=len, reverse=True)
        
        # Take the first skill from each group as the representative skill
        for group in sorted_groups:
            if len(key_skills) >= max_skills:
                break
                
            if group:
                key_skills.append(group[0])
        
        return key_skills
        
    def save_skill_mapping(self, mapping, filename='data/skill_mapping.json'):
        """
        Save skill mapping to a file.
        
        Args:
            mapping (dict): Skill mapping dictionary
            filename (str): Output filename
        """
        # Convert tuple values to dictionaries for JSON serialization
        serializable_mapping = {}
        for user_skill, matches in mapping.items():
            serializable_mapping[user_skill] = [
                {"skill": match[0], "similarity": match[1]} 
                for match in matches
            ]
            
        with open(filename, 'w') as f:
            json.dump(serializable_mapping, f, indent=2)
        
        print(f"Saved skill mapping to {filename}")

if __name__ == "__main__":
    # Example usage
    mapper = SkillsMapper()
    
    user_skills = [
        "Python programming",
        "Data analysis",
        "Machine learning",
        "Statistical modeling"
    ]
    
    course_skills = [
        "Python",
        "Data science",
        "Deep learning",
        "Statistics",
        "Regression analysis"
    ]
    
    mapping = mapper.map_skills(user_skills, course_skills)
    
    print("Skill Mapping Results:")
    for skill, matches in mapping.items():
        print(f"{skill}:")
        for match, score in matches:
            print(f"  - {match} (similarity: {score:.2f})")
            
    # Group related skills
    all_skills = user_skills + course_skills
    skill_groups = mapper.group_related_skills(all_skills)
    
    print("\nSkill Groups:")
    for i, group in enumerate(skill_groups, 1):
        print(f"Group {i}: {', '.join(group)}")
        
    # Extract key skills
    key_skills = mapper.extract_key_skills(skill_groups)
    print(f"\nKey Skills: {', '.join(key_skills)}") 