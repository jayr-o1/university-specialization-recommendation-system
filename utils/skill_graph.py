import json
import os
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

class SkillGraph:
    def __init__(self, course_skills_path=None):
        """Initialize skill graph from course data"""
        self.graph = nx.DiGraph()
        self.skill_relationships = {
            'prerequisite': {},  # skill -> prerequisites
            'complementary': {},  # skill -> complementary skills
            'advanced_version': {}  # basic skill -> advanced versions
        }
        
        # Load course skills to build initial relationships
        if course_skills_path:
            self.load_course_data(course_skills_path)
            
    def load_course_data(self, course_skills_path):
        """Load course data and build initial skill relationships"""
        with open(course_skills_path, 'r') as f:
            course_data = json.load(f)
            
        # First, collect all skills by frequency
        skill_frequency = defaultdict(int)
        skill_courses = defaultdict(list)
        
        for course_name, course_info in course_data.items():
            for skill in course_info['required_skills']:
                skill_frequency[skill] += 1
                skill_courses[skill].append(course_name)
        
        # Add all skills to the graph
        for skill in skill_frequency:
            self.graph.add_node(skill, frequency=skill_frequency[skill], courses=skill_courses[skill])
        
        # Build relationships based on co-occurrence
        for course_name, course_info in course_data.items():
            skills = course_info['required_skills']
            
            # Connect skills that appear together
            for i, skill1 in enumerate(skills):
                for skill2 in skills[i+1:]:
                    # Add edges in both directions with weight based on co-occurrence
                    if self.graph.has_edge(skill1, skill2):
                        self.graph[skill1][skill2]['weight'] += 1
                    else:
                        self.graph.add_edge(skill1, skill2, weight=1)
                        
                    if self.graph.has_edge(skill2, skill1):
                        self.graph[skill2][skill1]['weight'] += 1
                    else:
                        self.graph.add_edge(skill2, skill1, weight=1)
    
    def add_prerequisite(self, skill, prerequisite):
        """Add a prerequisite relationship"""
        if skill not in self.skill_relationships['prerequisite']:
            self.skill_relationships['prerequisite'][skill] = []
        
        if prerequisite not in self.skill_relationships['prerequisite'][skill]:
            self.skill_relationships['prerequisite'][skill].append(prerequisite)
            
        # Add edge in the graph
        self.graph.add_edge(prerequisite, skill, relationship='prerequisite')
    
    def add_complementary(self, skill1, skill2):
        """Add complementary skills relationship"""
        if skill1 not in self.skill_relationships['complementary']:
            self.skill_relationships['complementary'][skill1] = []
            
        if skill2 not in self.skill_relationships['complementary'][skill1]:
            self.skill_relationships['complementary'][skill1].append(skill2)
            
        # Add relationship for the other skill too
        if skill2 not in self.skill_relationships['complementary']:
            self.skill_relationships['complementary'][skill2] = []
            
        if skill1 not in self.skill_relationships['complementary'][skill2]:
            self.skill_relationships['complementary'][skill2].append(skill1)
            
        # Add edges in the graph
        self.graph.add_edge(skill1, skill2, relationship='complementary')
        self.graph.add_edge(skill2, skill1, relationship='complementary')
    
    def add_advanced_version(self, basic_skill, advanced_skill):
        """Add relationship showing a skill is an advanced version of another"""
        if basic_skill not in self.skill_relationships['advanced_version']:
            self.skill_relationships['advanced_version'][basic_skill] = []
            
        if advanced_skill not in self.skill_relationships['advanced_version'][basic_skill]:
            self.skill_relationships['advanced_version'][basic_skill].append(advanced_skill)
            
        # Add edge in the graph
        self.graph.add_edge(basic_skill, advanced_skill, relationship='advanced_version')
    
    def get_prerequisites(self, skill):
        """Get prerequisites for a skill"""
        if skill in self.skill_relationships['prerequisite']:
            return self.skill_relationships['prerequisite'][skill]
        return []
    
    def get_complementary_skills(self, skill):
        """Get complementary skills"""
        if skill in self.skill_relationships['complementary']:
            return self.skill_relationships['complementary'][skill]
        return []
    
    def get_advanced_versions(self, skill):
        """Get advanced versions of a skill"""
        if skill in self.skill_relationships['advanced_version']:
            return self.skill_relationships['advanced_version'][skill]
        return []
    
    def get_skill_path(self, from_skill, to_skill):
        """Find a path between two skills"""
        try:
            path = nx.shortest_path(self.graph, from_skill, to_skill)
            return path
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None
    
    def suggest_next_skills(self, user_skills, top_n=5):
        """Suggest next skills to learn based on user's current skills"""
        if not user_skills:
            return []
            
        skill_scores = defaultdict(float)
        existing_skills = set(user_skills.keys())
        
        # For each user skill, find related skills
        for skill, proficiency in user_skills.items():
            # Convert proficiency to weight
            weight = self._convert_proficiency_to_weight(proficiency)
            
            # Score is higher for skills with strong connections to multiple user skills
            for neighbor in self.graph.neighbors(skill):
                if neighbor not in existing_skills:
                    # Weight by connection strength and user's proficiency
                    edge_weight = self.graph[skill][neighbor].get('weight', 1)
                    skill_scores[neighbor] += edge_weight * weight
                    
            # Add prerequisites with higher scores
            prereqs = self.get_prerequisites(skill)
            for prereq in prereqs:
                if prereq not in existing_skills:
                    skill_scores[prereq] += 2.0 * weight
                    
            # Add advanced versions with medium scores
            advanced = self.get_advanced_versions(skill)
            for adv in advanced:
                if adv not in existing_skills:
                    skill_scores[adv] += 1.5 * weight
        
        # Sort skills by score
        sorted_skills = sorted(skill_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return top N skills with scores
        return [{'skill': skill, 'relevance': score} for skill, score in sorted_skills[:top_n]]
    
    def _convert_proficiency_to_weight(self, proficiency):
        """Convert proficiency level to numerical weight"""
        proficiency = proficiency.lower()
        if proficiency == "beginner":
            return 0.25
        elif proficiency == "intermediate":
            return 0.5
        elif proficiency == "advanced":
            return 0.75
        elif proficiency == "expert":
            return 1.0
        else:
            return 0.5  # Default to intermediate
    
    def visualize_graph(self, output_path=None, skill_subset=None):
        """Visualize the skill graph"""
        if skill_subset:
            # Create a subgraph with just the specified skills
            subgraph = self.graph.subgraph(skill_subset)
            g = subgraph
        else:
            g = self.graph
            
        plt.figure(figsize=(12, 10))
        pos = nx.spring_layout(g)
        
        # Draw nodes with size proportional to degree
        node_sizes = [10 + (g.degree(node) * 5) for node in g.nodes()]
        nx.draw_networkx_nodes(g, pos, node_size=node_sizes, alpha=0.8)
        
        # Draw edges with width proportional to weight
        edge_widths = [0.5 + (g[u][v].get('weight', 1) / 10) for u, v in g.edges()]
        nx.draw_networkx_edges(g, pos, width=edge_widths, alpha=0.5)
        
        # Draw labels
        nx.draw_networkx_labels(g, pos, font_size=8)
        
        plt.title("Skill Knowledge Graph")
        plt.axis('off')
        
        if output_path:
            plt.savefig(output_path, format="PNG", dpi=300)
        else:
            plt.show()
            
    def save_graph(self, filepath):
        """Save the skill graph to file"""
        data = {
            'nodes': list(self.graph.nodes(data=True)),
            'edges': list(self.graph.edges(data=True)),
            'relationships': self.skill_relationships
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f)
            
    def load_graph(self, filepath):
        """Load a skill graph from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        # Recreate the graph
        self.graph = nx.DiGraph()
        
        # Add nodes
        for node, attrs in data['nodes']:
            self.graph.add_node(node, **attrs)
            
        # Add edges
        for u, v, attrs in data['edges']:
            self.graph.add_edge(u, v, **attrs)
            
        # Load relationships
        self.skill_relationships = data['relationships']
        
    def initialize_common_relationships(self):
        """Initialize common skill relationships based on patterns"""
        # Add some common programming relationships
        prog_skills = {
            'basic': ['Programming Logic and Flow Control', 'Basic Programming Concepts', 
                     'Computational Thinking', 'Algorithm Design'],
            'languages': ['JavaScript', 'Python', 'Java', 'C++', 'PHP', 'Ruby'],
            'web': ['HTML', 'CSS', 'JavaScript', 'Responsive Design', 'Web Design Principles'],
            'data': ['SQL', 'Database Design', 'Data Structures', 'Data Visualization', 
                    'Data Analysis', 'Statistical Analysis'],
            'frameworks': ['React', 'Angular', 'Vue.js', 'Django', 'Flask', 'Spring']
        }
        
        # Programming logic is prerequisite to programming languages
        for basic in prog_skills['basic']:
            for lang in prog_skills['languages']:
                if basic in self.graph and lang in self.graph:
                    self.add_prerequisite(lang, basic)
        
        # HTML/CSS are prerequisites to JavaScript frameworks
        for prereq in ['HTML', 'CSS']:
            for framework in ['React', 'Angular', 'Vue.js']:
                if prereq in self.graph and framework in self.graph:
                    self.add_prerequisite(framework, prereq)
        
        # JavaScript is prerequisite to JS frameworks
        for framework in ['React', 'Angular', 'Vue.js']:
            if 'JavaScript' in self.graph and framework in self.graph:
                self.add_prerequisite(framework, 'JavaScript')
                
        # Python is prerequisite to Python frameworks
        for framework in ['Django', 'Flask']:
            if 'Python' in self.graph and framework in self.graph:
                self.add_prerequisite(framework, 'Python')
                
        # Database relationships
        if 'Database Design' in self.graph and 'SQL' in self.graph:
            self.add_complementary('Database Design', 'SQL')
            
        # Add relationships for math skills
        math_skills = ['Algebra', 'Calculus', 'Trigonometry', 'Statistics', 
                      'Linear Algebra', 'Discrete Mathematics']
        
        # Algebra is prerequisite to more advanced math
        for adv_math in ['Calculus', 'Trigonometry', 'Linear Algebra']:
            if 'Algebra' in self.graph and adv_math in self.graph:
                self.add_prerequisite(adv_math, 'Algebra')
                
        # Add relationships for communication skills
        comm_skills = ['Public Speaking', 'Academic Writing', 'Technical Writing', 
                      'Interpersonal Communication']
        
        for i, skill1 in enumerate(comm_skills):
            for skill2 in comm_skills[i+1:]:
                if skill1 in self.graph and skill2 in self.graph:
                    self.add_complementary(skill1, skill2)

# Example usage
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'data', 'course_skills.json')
    
    # Initialize the skill graph from course data
    skill_graph = SkillGraph(data_path)
    
    # Initialize common relationships
    skill_graph.initialize_common_relationships()
    
    # Save the graph
    graph_path = os.path.join(base_dir, 'data', 'skill_graph.json')
    skill_graph.save_graph(graph_path)
    
    # Visualize a subset of the graph
    output_path = os.path.join(base_dir, 'data', 'skill_graph_visualization.png')
    web_skills = ['HTML', 'CSS', 'JavaScript', 'React', 'Angular', 'Web Design Principles']
    skill_graph.visualize_graph(output_path, web_skills) 