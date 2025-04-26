import argparse
import os
import sys
import subprocess

def main():
    parser = argparse.ArgumentParser(description='Faculty Skill Development System')
    parser.add_argument('action', choices=['api', 'web', 'build-graph', 'faculty', 'faculty-teaching'], 
                        help='Action to perform: start API, start web app, build skill graph, run faculty advisor, or run faculty teaching advisor')
    
    args = parser.parse_args()
    
    if args.action == 'api':
        print("Starting the API server...")
        subprocess.run([sys.executable, 'src/api.py'])
    
    elif args.action == 'web':
        print("Starting the web application...")
        subprocess.run([sys.executable, 'src/app.py'])
        
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