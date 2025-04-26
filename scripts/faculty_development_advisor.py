import json
import os
import sys
import argparse
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import from other modules
from utils.faculty_skills_analyzer import FacultySkillsAnalyzer

def parse_skills_file(filename):
    """
    Parse faculty skills from a file.
    
    Args:
        filename (str): Path to skills file (CSV or JSON)
        
    Returns:
        dict: Dictionary with faculty information
    """
    if filename.endswith('.json'):
        with open(filename, 'r') as f:
            return json.load(f)
    elif filename.endswith('.csv'):
        import csv
        faculty_data = {}
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            
            # Assuming first column is name, second is department, rest are skills
            for row in reader:
                if len(row) >= 3:
                    faculty_data[row[0]] = {
                        'name': row[0],
                        'department': row[1],
                        'skills': [skill.strip() for skill in row[2:] if skill.strip()]
                    }
        return faculty_data
    else:
        raise ValueError(f"Unsupported file format: {filename}")

def analyze_faculty_skills(faculty_data, output_dir='data/faculty_analysis'):
    """
    Analyze skills for each faculty member.
    
    Args:
        faculty_data (dict): Faculty information with skills
        output_dir (str): Directory to save analysis results
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize analyzer
    analyzer = FacultySkillsAnalyzer()
    
    # Process each faculty member
    for faculty_name, data in faculty_data.items():
        print(f"\n\nAnalyzing skills for {faculty_name}...")
        
        department = data.get('department', 'computer_science')  # Default to computer_science
        skills = data.get('skills', [])
        
        if not skills:
            print(f"No skills found for {faculty_name}, skipping.")
            continue
        
        print(f"Department: {department}")
        print(f"Current skills ({len(skills)}): {', '.join(skills[:5])}" + 
              ("..." if len(skills) > 5 else ""))
        
        # Identify skill gaps
        skill_gaps = analyzer.identify_skill_gaps(skills, department)
        
        # Get development recommendations
        recommendations = analyzer.get_development_recommendations(skill_gaps)
        
        # Save analysis to file
        output_file = os.path.join(output_dir, f"{faculty_name.replace(' ', '_').lower()}_analysis.json")
        analyzer.save_analysis({
            "faculty_name": faculty_name,
            "skill_gaps": skill_gaps,
            "recommendations": recommendations
        }, output_file)
        
        # Print summary
        print("\nSkill Gap Summary:")
        print(f"  Matched high-demand skills: {len(skill_gaps['matched_skills']['high_demand'])}")
        print(f"  Matched emerging skills: {len(skill_gaps['matched_skills']['emerging'])}")
        print(f"  Missing high-demand skills: {len(skill_gaps['skill_gaps']['high_demand'])}")
        print(f"  Missing emerging skills: {len(skill_gaps['skill_gaps']['emerging'])}")
        
        print("\nTop Development Recommendations:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"{i}. {rec['skill']} (Priority: {rec['priority']})")
            print(f"   Estimated learning time: {rec['estimated_learning_time']}")
            if rec['missing_prerequisites']:
                print(f"   Missing prerequisites: {', '.join(rec['missing_prerequisites'])}")
        
        print(f"\nDetailed analysis saved to {output_file}")

def interactive_skill_advisor():
    """
    Interactive mode for faculty members to get skill development advice.
    """
    print("===== Faculty Skills Development Advisor =====")
    print("This tool will help you identify skill gaps and suggest development paths.")
    
    # Get faculty information
    name = input("\nYour name: ")
    
    # Get department/area
    print("\nSelect your department/area:")
    print("1. Data Science")
    print("2. Computer Science")
    print("3. Information Systems")
    print("4. Software Engineering")
    print("5. Other (specify)")
    
    dept_choice = input("Enter number (1-5): ")
    
    if dept_choice == '1':
        department = "data_science"
    elif dept_choice == '2':
        department = "computer_science"
    elif dept_choice == '3':
        department = "information_systems"
    elif dept_choice == '4':
        department = "software_engineering"
    elif dept_choice == '5':
        department = input("Specify your department/area: ").lower().replace(' ', '_')
    else:
        department = "computer_science"  # Default
    
    # Get skills
    print("\nEnter your current skills (comma-separated):")
    skills_input = input()
    skills = [skill.strip() for skill in skills_input.split(',') if skill.strip()]
    
    if not skills:
        print("No skills entered. Please run the program again with at least one skill.")
        return
    
    # Initialize analyzer and process
    analyzer = FacultySkillsAnalyzer()
    
    print(f"\nAnalyzing skills for {name}...")
    
    # Identify skill gaps
    skill_gaps = analyzer.identify_skill_gaps(skills, department)
    
    # Get development recommendations
    recommendations = analyzer.get_development_recommendations(skill_gaps)
    
    # Save analysis to file
    output_dir = 'data/faculty_analysis'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{name.replace(' ', '_').lower()}_analysis.json")
    
    analyzer.save_analysis({
        "faculty_name": name,
        "skill_gaps": skill_gaps,
        "recommendations": recommendations
    }, output_file)
    
    # Print results
    print("\n===== Your Skill Analysis =====")
    print(f"Department/Area: {department}")
    
    print("\nSkills You Already Have Matching Industry Demands:")
    if skill_gaps['matched_skills']['high_demand']:
        print("High-demand skills:")
        for skill in skill_gaps['matched_skills']['high_demand']:
            print(f"  • {skill}")
    
    if skill_gaps['matched_skills']['emerging']:
        print("\nEmerging skills:")
        for skill in skill_gaps['matched_skills']['emerging']:
            print(f"  • {skill}")
    
    if not skill_gaps['matched_skills']['high_demand'] and not skill_gaps['matched_skills']['emerging']:
        print("  No direct matches found with in-demand industry skills.")
    
    print("\nRecommended Skill Development Areas:")
    if not recommendations:
        print("  No specific recommendations found.")
    else:
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec['skill']} (Priority: {rec['priority']})")
            print(f"   Reason: {rec['reason']}")
            
            if rec['related_faculty_skills']:
                print(f"   Related skills you already have: {', '.join(rec['related_faculty_skills'])}")
            
            if rec['prerequisites']:
                print(f"   Prerequisites: {', '.join(rec['prerequisites'])}")
                
                if rec['missing_prerequisites']:
                    print(f"   Missing prerequisites: {', '.join(rec['missing_prerequisites'])}")
                else:
                    print("   You have all the prerequisites for this skill!")
            
            print(f"   Estimated learning time: {rec['estimated_learning_time']}")
    
    print(f"\nDetailed analysis saved to {output_file}")
    print("\nThank you for using the Faculty Skills Development Advisor!")

def main():
    """
    Main function to parse arguments and run the advisor.
    """
    parser = argparse.ArgumentParser(description='Faculty Skills Development Advisor')
    parser.add_argument('--interactive', '-i', action='store_true', 
                        help='Run in interactive mode for a single faculty member')
    parser.add_argument('--file', '-f', type=str,
                        help='CSV or JSON file containing faculty skills')
    parser.add_argument('--output', '-o', type=str, default='data/faculty_analysis',
                        help='Output directory for analysis results')
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_skill_advisor()
    elif args.file:
        try:
            faculty_data = parse_skills_file(args.file)
            analyze_faculty_skills(faculty_data, args.output)
        except Exception as e:
            print(f"Error processing file: {e}")
    else:
        print("Please specify either --interactive mode or provide a file with --file")
        parser.print_help()

if __name__ == "__main__":
    main() 