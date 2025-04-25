import json
import os
import sys
import networkx as nx
from collections import defaultdict

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.skill_graph import SkillGraph

class LearningPathGenerator:
    def __init__(self, course_skills_path, skill_graph=None):
        """Initialize learning path generator with course data and skill graph"""
        # Load course data
        with open(course_skills_path, 'r') as f:
            self.course_data = json.load(f)
            
        # Initialize or load skill graph
        if skill_graph:
            self.skill_graph = skill_graph
        else:
            # Try to load the saved skill graph, or create a new one
            graph_path = os.path.join(os.path.dirname(course_skills_path), 'skill_graph.json')
            if os.path.exists(graph_path):
                self.skill_graph = SkillGraph()
                self.skill_graph.load_graph(graph_path)
            else:
                self.skill_graph = SkillGraph(course_skills_path)
                self.skill_graph.initialize_common_relationships()
                
        # Create course dependency graph
        self.course_graph = self._build_course_dependency_graph()
        
    def _build_course_dependency_graph(self):
        """Build a graph of course dependencies based on skill relationships"""
        course_graph = nx.DiGraph()
        
        # Add all courses as nodes
        for course_name in self.course_data:
            course_graph.add_node(course_name)
        
        # Analyze skill dependencies to determine course dependencies
        for course1, info1 in self.course_data.items():
            for course2, info2 in self.course_data.items():
                if course1 != course2:
                    # Check if course1 provides prerequisites for course2
                    prerequisite_score = 0
                    dependency_skills = []
                    
                    for skill in info2['required_skills']:
                        prerequisites = self.skill_graph.get_prerequisites(skill)
                        for prereq in prerequisites:
                            if prereq in info1['required_skills']:
                                prerequisite_score += 1
                                dependency_skills.append(prereq)
                    
                    # Add an edge if there's significant skill dependency
                    if prerequisite_score >= 2:  # Threshold for significant dependency
                        course_graph.add_edge(course1, course2, 
                                              weight=prerequisite_score,
                                              dependency_skills=list(set(dependency_skills)))
        
        return course_graph
        
    def generate_learning_path(self, user_skills, career_goal=None, path_length=5):
        """
        Generate a personalized learning path based on user skills and optional career goal
        
        Args:
            user_skills: Dict of skill-proficiency pairs (e.g., {"Python": "Advanced"})
            career_goal: Target career or specialization (optional)
            path_length: Maximum number of courses in the path
            
        Returns:
            List of courses forming a learning path
        """
        # Step 1: Find courses that match user's existing skills
        course_matches = self._match_courses_to_skills(user_skills)
        
        # Step 2: Determine starting point(s) based on best matches
        starting_courses = [course for course, score in 
                           sorted(course_matches.items(), key=lambda x: x[1], reverse=True)[:3]]
        
        # Step 3: Generate paths from starting points
        paths = []
        for start_course in starting_courses:
            # Use shortest path algorithms if a career goal is specified
            if career_goal and career_goal in self.course_data:
                try:
                    path = nx.shortest_path(self.course_graph, start_course, career_goal)
                    paths.append((path, self._calculate_path_score(path, user_skills)))
                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    # If no direct path, find a path that gets closest to the goal
                    partial_path = self._find_best_partial_path(start_course, career_goal, user_skills)
                    if partial_path:
                        paths.append((partial_path, self._calculate_path_score(partial_path, user_skills)))
            else:
                # Without a specific goal, find paths that build on each other
                path = self._find_progressive_path(start_course, user_skills, path_length)
                paths.append((path, self._calculate_path_score(path, user_skills)))
        
        # Step 4: Choose the best path
        paths.sort(key=lambda x: x[1], reverse=True)
        best_path = paths[0][0] if paths else []
        
        # Step 5: Format the learning path with details
        formatted_path = self._format_learning_path(best_path, user_skills)
        
        return formatted_path
    
    def _match_courses_to_skills(self, user_skills):
        """Calculate how well each course matches user's existing skills"""
        course_scores = {}
        user_skill_set = set(user_skills.keys())
        
        for course_name, course_info in self.course_data.items():
            course_skills = set(course_info['required_skills'])
            
            # Calculate overlap between user skills and course required skills
            overlap = user_skill_set.intersection(course_skills)
            
            # Calculate match score based on overlap and proficiency
            score = 0
            for skill in overlap:
                proficiency = user_skills.get(skill, "Beginner")
                weight = self.skill_graph._convert_proficiency_to_weight(proficiency)
                score += weight
                
            # Normalize score by total required skills
            if course_skills:
                normalized_score = score / len(course_skills)
                course_scores[course_name] = normalized_score
            else:
                course_scores[course_name] = 0
        
        return course_scores
    
    def _find_progressive_path(self, start_course, user_skills, path_length=5):
        """Find a progressive learning path that builds on user's current skills"""
        path = [start_course]
        current = start_course
        
        # Keep track of visited courses to avoid cycles
        visited = {start_course}
        
        while len(path) < path_length:
            # Get all possible next courses
            next_courses = []
            for successor in self.course_graph.successors(current):
                if successor not in visited:
                    # Calculate how well the user can take this course
                    readiness_score = self._calculate_course_readiness(successor, user_skills, path)
                    next_courses.append((successor, readiness_score))
            
            # Sort by readiness score and pick the best
            next_courses.sort(key=lambda x: x[1], reverse=True)
            
            if not next_courses:
                # No more courses to add
                break
                
            # Add the best next course
            best_next = next_courses[0][0]
            path.append(best_next)
            visited.add(best_next)
            current = best_next
            
            # Update virtual user skills - assume they learn the skills from the course
            virtual_user_skills = user_skills.copy()
            for skill in self.course_data[best_next]['required_skills']:
                if skill not in virtual_user_skills:
                    virtual_user_skills[skill] = "Beginner"
                else:
                    # Upgrade skill level if not already at expert
                    current_level = virtual_user_skills[skill].lower()
                    if current_level == "beginner":
                        virtual_user_skills[skill] = "Intermediate"
                    elif current_level == "intermediate":
                        virtual_user_skills[skill] = "Advanced"
                    elif current_level == "advanced":
                        virtual_user_skills[skill] = "Expert"
        
        return path
    
    def _find_best_partial_path(self, start_course, goal_course, user_skills):
        """Find a path that gets closest to the goal when a direct path doesn't exist"""
        # Calculate the course sequence leading to the goal
        backwards_paths = nx.bfs_tree(self.course_graph.reverse(), goal_course)
        
        # Find courses reachable from the start that intersect with the goal tree
        forwards_paths = nx.bfs_tree(self.course_graph, start_course)
        
        # Find common nodes (intersection points)
        intersection_nodes = set(backwards_paths.nodes()).intersection(set(forwards_paths.nodes()))
        
        if not intersection_nodes:
            # No path connection, return a default progressive path
            return self._find_progressive_path(start_course, user_skills)
        
        # Find the best intersection point based on path quality
        best_bridge = None
        best_score = -1
        
        for bridge in intersection_nodes:
            # Get path from start to bridge
            path_to_bridge = nx.shortest_path(self.course_graph, start_course, bridge)
            # Get path from bridge to goal
            path_from_bridge = nx.shortest_path(self.course_graph, bridge, goal_course)
            
            # Combine paths (exclude duplicate bridge node)
            full_path = path_to_bridge + path_from_bridge[1:]
            
            # Score the path
            score = self._calculate_path_score(full_path, user_skills)
            
            if score > best_score:
                best_score = score
                best_bridge = bridge
        
        if best_bridge:
            # Construct the best path
            path_to_bridge = nx.shortest_path(self.course_graph, start_course, best_bridge)
            path_from_bridge = nx.shortest_path(self.course_graph, best_bridge, goal_course)
            full_path = path_to_bridge + path_from_bridge[1:]
            return full_path
        
        # Fallback
        return self._find_progressive_path(start_course, user_skills)
    
    def _calculate_course_readiness(self, course, user_skills, previous_courses):
        """Calculate how ready a user is to take a course based on skills and previous courses"""
        required_skills = set(self.course_data[course]['required_skills'])
        user_skill_set = set(user_skills.keys())
        
        # Calculate direct skill match
        direct_match = len(required_skills.intersection(user_skill_set)) / len(required_skills) if required_skills else 0
        
        # Calculate skill preparation from previous courses
        previous_skills = set()
        for prev_course in previous_courses:
            previous_skills.update(self.course_data[prev_course]['required_skills'])
        
        skill_preparation = len(required_skills.intersection(previous_skills)) / len(required_skills) if required_skills else 0
        
        # Calculate weighted readiness score
        readiness = (direct_match * 0.7) + (skill_preparation * 0.3)
        
        return readiness
    
    def _calculate_path_score(self, path, user_skills):
        """Calculate overall score for a learning path"""
        if not path:
            return 0
            
        # Initialize score
        score = 0
        
        # Calculate progression quality
        for i in range(len(path) - 1):
            current = path[i]
            next_course = path[i + 1]
            
            # Check if there's a strong dependency
            if self.course_graph.has_edge(current, next_course):
                # Higher weight means stronger dependency
                edge_weight = self.course_graph[current][next_course].get('weight', 0)
                score += edge_weight
        
        # Adjust score based on starting point match quality
        start_match = self._match_courses_to_skills(user_skills).get(path[0], 0)
        score *= (0.5 + start_match)
        
        # Normalize score by path length
        normalized_score = score / len(path) if path else 0
        
        return normalized_score
    
    def _format_learning_path(self, path, user_skills):
        """Format learning path with details about each course"""
        formatted_path = []
        
        # For tracking virtual skill acquisition through the path
        virtual_skills = user_skills.copy()
        
        for i, course_name in enumerate(path):
            course_info = self.course_data[course_name]
            required_skills = course_info['required_skills']
            
            # Determine matched and missing skills
            matched_skills = []
            missing_skills = []
            
            for skill in required_skills:
                if skill in virtual_skills:
                    matched_skills.append(f"{skill} ({virtual_skills[skill]})")
                else:
                    missing_skills.append(skill)
            
            # Calculate match percentage
            match_percentage = int((len(matched_skills) / len(required_skills)) * 100) if required_skills else 0
            
            # Get the next steps rationale
            next_steps_rationale = ""
            if i < len(path) - 1:
                next_course = path[i + 1]
                if self.course_graph.has_edge(course_name, next_course):
                    dependency_skills = self.course_graph[course_name][next_course].get('dependency_skills', [])
                    if dependency_skills:
                        skill_list = ", ".join(dependency_skills[:3])
                        if len(dependency_skills) > 3:
                            skill_list += f", and {len(dependency_skills) - 3} more"
                        next_steps_rationale = f"This course helps prepare you for {next_course} by teaching {skill_list}."
            
            # Add course to formatted path
            formatted_path.append({
                'course_name': course_name,
                'step': i + 1,
                'match_percentage': match_percentage,
                'matched_skills': matched_skills,
                'missing_skills': missing_skills,
                'next_steps_rationale': next_steps_rationale
            })
            
            # Update virtual skills with new skills learned from this course
            for skill in required_skills:
                if skill not in virtual_skills:
                    virtual_skills[skill] = "Beginner"
                else:
                    # Upgrade skill level if not already at expert
                    current_level = virtual_skills[skill].lower()
                    if current_level == "beginner":
                        virtual_skills[skill] = "Intermediate"
                    elif current_level == "intermediate":
                        virtual_skills[skill] = "Advanced"
                    elif current_level == "advanced":
                        virtual_skills[skill] = "Expert"
        
        return formatted_path
    
    def get_career_aligned_courses(self, career_goal, top_n=5):
        """Get courses most aligned with a specific career goal"""
        if career_goal not in self.course_data:
            return []
            
        # Get skills required for the career goal
        goal_skills = set(self.course_data[career_goal]['required_skills'])
        
        # Score each course based on skill overlap with career goal
        course_scores = {}
        for course_name, course_info in self.course_data.items():
            if course_name == career_goal:
                continue  # Skip the goal itself
                
            course_skills = set(course_info['required_skills'])
            overlap = goal_skills.intersection(course_skills)
            
            if overlap:
                # Score based on percentage of goal skills covered
                score = len(overlap) / len(goal_skills) if goal_skills else 0
                course_scores[course_name] = score
        
        # Return top courses
        return sorted(course_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]

# Example usage
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'data', 'course_skills.json')
    
    # Initialize learning path generator
    path_generator = LearningPathGenerator(data_path)
    
    # Example user skills
    user_skills = {
        "HTML": "Advanced",
        "CSS": "Intermediate",
        "JavaScript": "Beginner",
        "Programming Logic and Flow Control": "Intermediate"
    }
    
    # Generate a learning path
    career_goal = "Web Design & Development"
    learning_path = path_generator.generate_learning_path(user_skills, career_goal)
    
    # Print the path
    print(f"Personalized Learning Path for Web Development:")
    for step in learning_path:
        print(f"{step['step']}. {step['course_name']} - {step['match_percentage']}% Match")
        if step['next_steps_rationale']:
            print(f"   Rationale: {step['next_steps_rationale']}")
        print() 