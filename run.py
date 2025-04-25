import argparse
import os
import sys
import subprocess

def main():
    parser = argparse.ArgumentParser(description='University Specialization Recommendation System')
    parser.add_argument('action', choices=['train', 'cli', 'api', 'web', 'test'], 
                        help='Action to perform: train model, run CLI, start API, start web app, or run tests')
    
    args = parser.parse_args()
    
    if args.action == 'train':
        print("Training the recommendation model...")
        subprocess.run([sys.executable, 'models/train_model.py'])
    
    elif args.action == 'cli':
        print("Starting the command-line interface...")
        subprocess.run([sys.executable, 'src/recommendation_app.py'])
    
    elif args.action == 'api':
        print("Starting the API server...")
        subprocess.run([sys.executable, 'src/api.py'])
    
    elif args.action == 'web':
        print("Starting the web application...")
        subprocess.run([sys.executable, 'src/app.py'])
    
    elif args.action == 'test':
        print("Running the test with example input...")
        subprocess.run([sys.executable, 'test_recommendation.py'])

if __name__ == '__main__':
    main() 