import subprocess
import sys
import os

def main():
    """
    Set up the University Specialization Recommendation System
    """
    print("Setting up the University Specialization Recommendation System...")
    
    # Install requirements
    print("\nInstalling dependencies...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    
    # Create necessary directories
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created data directory at {data_dir}")
    
    models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
        print(f"Created models directory at {models_dir}")
    
    # Check if course_skills.json exists
    course_skills_path = os.path.join(data_dir, 'course_skills.json')
    if not os.path.exists(course_skills_path):
        print(f"\nWARNING: Course skills data file not found at {course_skills_path}")
        print("Please create a course_skills.json file in the data directory with course skill data.")
    
    # Build skill graph if using enhanced mode
    print("\nWould you like to set up the enhanced recommendation system? (y/n)")
    choice = input("This will install additional packages and build the skill knowledge graph: ")
    
    if choice.lower() in ('y', 'yes'):
        # Install enhanced requirements
        print("\nInstalling additional dependencies for enhanced mode...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'networkx', 'matplotlib', 'pandas', 'numpy', 'scikit-learn'])
        
        # Build skill graph
        print("\nBuilding skill knowledge graph...")
        
        # Check if the script exists
        skill_graph_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'utils', 'skill_graph.py')
        
        if os.path.exists(skill_graph_script):
            subprocess.run([sys.executable, skill_graph_script])
        else:
            print(f"Error: Skill graph script not found at {skill_graph_script}")
            print("Please run the enhanced mode to build the skill graph automatically.")
    
    print("\nSetup completed!")
    print("\nTo use the basic system, run:")
    print("python run.py cli")
    print("\nTo use the enhanced system, run:")
    print("python run.py enhanced")

if __name__ == "__main__":
    main() 