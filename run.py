import argparse
import os
import sys
import subprocess

def main():
    parser = argparse.ArgumentParser(description='University Specialization Recommendation System')
    parser.add_argument('action', choices=['train', 'cli', 'enhanced', 'api', 'web', 'test', 'build-graph', 'faculty', 'faculty-teaching'], 
                        help='Action to perform: train model, run CLI, run enhanced CLI, start API, start web app, run tests, build skill graph, run faculty advisor, or run faculty teaching advisor')
    
    args = parser.parse_args()
    
    if args.action == 'train':
        print("Training the recommendation model...")
        subprocess.run([sys.executable, 'models/train_model.py'])
    
    elif args.action == 'cli' or args.action == 'enhanced':
        print("Starting the enhanced command-line interface...")
        
        # Check if required packages are installed
        try:
            import networkx
            import matplotlib
            import pandas
            import numpy
        except ImportError:
            print("Installing required packages for enhanced mode...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'networkx', 'matplotlib', 'pandas', 'numpy', 'scikit-learn'])
            
        # Build skill graph if it doesn't exist
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        skill_graph_path = os.path.join(data_dir, 'skill_graph.json')
        
        if not os.path.exists(skill_graph_path):
            print("Building skill knowledge graph...")
            subprocess.run([sys.executable, 'utils/skill_graph.py'])
            
        # Run the enhanced recommendation app
        subprocess.run([sys.executable, 'src/enhanced_recommendation_app.py'])
    
    elif args.action == 'api':
        print("Starting the API server...")
        subprocess.run([sys.executable, 'src/api.py'])
    
    elif args.action == 'web':
        print("Starting the web application...")
        subprocess.run([sys.executable, 'src/app.py'])
    
    elif args.action == 'test':
        print("Running the test with example input...")
        subprocess.run([sys.executable, 'scripts/test_recommendation_system.py'])
        
    elif args.action == 'build-graph':
        print("Building the skill knowledge graph...")
        
        # Ensure required packages are installed
        try:
            import networkx
            import matplotlib
        except ImportError:
            print("Installing required packages...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'networkx', 'matplotlib'])
            
        # Run the skill graph builder
        subprocess.run([sys.executable, 'utils/skill_graph.py'])
        
    elif args.action == 'faculty':
        print("Starting the Faculty Skills Development Advisor...")
        
        # Check if required packages are installed
        try:
            import numpy
        except ImportError:
            print("Installing required packages...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'numpy', 'pandas'])
            
        # Run the faculty advisor in interactive mode
        subprocess.run([sys.executable, 'scripts/faculty_development_advisor.py', '--interactive'])

    elif args.action == 'faculty-teaching':
        print("Starting the Faculty Teaching Advisor...")
        
        # Check if required packages are installed
        try:
            import numpy
        except ImportError:
            print("Installing required packages...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'numpy', 'pandas'])
            
        # Run the faculty teaching advisor in interactive mode
        subprocess.run([sys.executable, 'scripts/faculty_teaching_advisor.py', '--interactive'])

if __name__ == '__main__':
    main() 