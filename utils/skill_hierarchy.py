import json
from typing import Dict, List, Set, Optional

class SkillHierarchy:
    def __init__(self, hierarchy_path: Optional[str] = None):
        """Initialize the skill hierarchy system.
        
        Args:
            hierarchy_path: Optional path to a JSON file containing skill hierarchy data.
                          If not provided, uses default hierarchy.
        """
        self.skill_relationships = {}
        self.skill_difficulties = {}
        self.skill_prerequisites = {}
        
        if hierarchy_path:
            self.load_hierarchy(hierarchy_path)
        else:
            self._initialize_default_hierarchy()
    
    def _initialize_default_hierarchy(self):
        """Initialize with default skill hierarchy data."""
        # Define skill relationships (parent-child and related skills)
        self.skill_relationships = {
            "Programming": {
                "children": ["Python", "Java", "JavaScript", "C++"],
                "related": ["Software Development", "Web Development", "Mobile Development"]
            },
            "Python": {
                "parent": "Programming",
                "related": ["Data Science", "Machine Learning", "Web Development"],
                "children": ["Django", "Flask", "PyTorch", "TensorFlow"]
            },
            "Data Science": {
                "related": ["Python", "Machine Learning", "Statistics"],
                "children": ["Data Analysis", "Data Visualization", "Big Data"]
            },
            "Machine Learning": {
                "related": ["Python", "Data Science", "Statistics"],
                "children": ["Deep Learning", "Natural Language Processing", "Computer Vision"]
            },
            "Web Development": {
                "related": ["Programming", "Frontend Development", "Backend Development"],
                "children": ["HTML", "CSS", "JavaScript", "React", "Node.js"]
            }
        }
        
        # Define skill difficulty levels (1-5, where 5 is most difficult)
        self.skill_difficulties = {
            "Programming": 3,
            "Python": 2,
            "Java": 3,
            "JavaScript": 2,
            "C++": 4,
            "Data Science": 4,
            "Machine Learning": 5,
            "Web Development": 3,
            "HTML": 1,
            "CSS": 2,
            "React": 3,
            "Node.js": 3,
            "Django": 3,
            "Flask": 2,
            "PyTorch": 4,
            "TensorFlow": 4,
            "Statistics": 4,
            "Data Analysis": 3,
            "Data Visualization": 2,
            "Big Data": 4,
            "Deep Learning": 5,
            "Natural Language Processing": 4,
            "Computer Vision": 4
        }
        
        # Define skill prerequisites
        self.skill_prerequisites = {
            "Machine Learning": ["Python", "Statistics", "Data Science"],
            "Deep Learning": ["Machine Learning", "Python", "Linear Algebra"],
            "Data Science": ["Python", "Statistics"],
            "Web Development": ["HTML", "CSS", "JavaScript"],
            "React": ["JavaScript", "HTML", "CSS"],
            "Node.js": ["JavaScript"],
            "Django": ["Python"],
            "Flask": ["Python"],
            "PyTorch": ["Python", "Machine Learning"],
            "TensorFlow": ["Python", "Machine Learning"]
        }
    
    def load_hierarchy(self, hierarchy_path: str):
        """Load skill hierarchy from a JSON file."""
        try:
            with open(hierarchy_path, 'r') as f:
                data = json.load(f)
                self.skill_relationships = data.get('relationships', {})
                self.skill_difficulties = data.get('difficulties', {})
                self.skill_prerequisites = data.get('prerequisites', {})
        except Exception as e:
            print(f"Error loading hierarchy: {str(e)}")
            self._initialize_default_hierarchy()
    
    def get_related_skills(self, skill: str) -> Set[str]:
        """Get all related skills for a given skill."""
        related = set()
        if skill in self.skill_relationships:
            rel_data = self.skill_relationships[skill]
            related.update(rel_data.get('related', []))
            related.update(rel_data.get('children', []))
            if 'parent' in rel_data:
                related.add(rel_data['parent'])
        return related
    
    def get_skill_difficulty(self, skill: str) -> int:
        """Get the difficulty level of a skill (1-5)."""
        return self.skill_difficulties.get(skill, 3)  # Default to medium difficulty
    
    def get_prerequisites(self, skill: str) -> List[str]:
        """Get prerequisites for a skill."""
        return self.skill_prerequisites.get(skill, [])
    
    def calculate_skill_match_score(self, user_skill: str, required_skill: str) -> float:
        """Calculate a match score between a user's skill and a required skill.
        
        Args:
            user_skill: The skill the user has
            required_skill: The skill required by the course
            
        Returns:
            float: Match score between 0 and 1
        """
        # Direct match
        if user_skill == required_skill:
            return 1.0
            
        # Check if skills are related
        related_skills = self.get_related_skills(user_skill)
        if required_skill in related_skills:
            return 0.7  # Related skills get 70% match score
            
        # Check if required skill is a prerequisite of user's skill
        if required_skill in self.get_prerequisites(user_skill):
            return 0.5  # Prerequisite relationship gets 50% match score
            
        return 0.0  # No relationship
    
    def calculate_certification_weight(self, skill: str, is_certified: bool) -> float:
        """Calculate the weight for a certified skill based on its difficulty.
        
        Args:
            skill: The skill name
            is_certified: Whether the skill is certified
            
        Returns:
            float: Weight between 1.0 and 1.5
        """
        if not is_certified:
            return 1.0
            
        # Higher difficulty skills get higher certification weights
        difficulty = self.get_skill_difficulty(skill)
        return 1.0 + (difficulty * 0.1)  # 1.0 to 1.5 based on difficulty 