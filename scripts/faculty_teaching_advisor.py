import json
import os
import sys
import argparse
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import from other modules
from utils.skill_matcher import SkillMatcher

class FacultyTeachingAdvisor:
    """
    A system to help teachers identify their skill gaps for courses and 
    find courses where they can apply their existing skills effectively.
    """
    
    def __init__(self, course_data_path='data/course_skills.json'):
        """Initialize with path to course skills data file."""
        self.skill_matcher = SkillMatcher(course_data_path)
        self.course_data_path = course_data_path
        
        with open(course_data_path, 'r') as f:
            self.course_data = json.load(f)
    
    def identify_skill_gaps(self, faculty_skills, limit=10):
        """
        Identify courses with skill gaps for the faculty member.
        
        Args:
            faculty_skills: Dictionary of faculty skills with proficiency and certification info
            limit: Maximum number of courses to return
            
        Returns:
            List of courses with skill gap details
        """
        skill_gap_courses = []
        
        faculty_skill_set = set(faculty_skills.keys())
        
        for course_name, course_info in self.course_data.items():
            required_skills = set(course_info.get('required_skills', []))
            
            # Skip courses with no required skills
            if not required_skills:
                continue
            
            # Calculate matching and missing skills
            matched_skills = required_skills.intersection(faculty_skill_set)
            missing_skills = required_skills - faculty_skill_set
            
            # Calculate match percentage
            if required_skills:
                match_percentage = (len(matched_skills) / len(required_skills)) * 100
            else:
                match_percentage = 0
                
            # Format matched skills with proficiency and certification status
            formatted_matched_skills = []
            for skill in matched_skills:
                if isinstance(faculty_skills[skill], dict):
                    proficiency = faculty_skills[skill].get("proficiency", "Intermediate")
                    is_certified = faculty_skills[skill].get("isBackedByCertificate", False)
                    certified_str = " (certified)" if is_certified else ""
                    formatted_matched_skills.append(f"{skill} ({proficiency}{certified_str})")
                else:
                    # Legacy support for old format
                    formatted_matched_skills.append(f"{skill} ({faculty_skills[skill]})")
            
            # Only include courses with some matched skills but also with gaps
            if matched_skills and missing_skills:
                skill_gap_courses.append({
                    "course_name": course_name,
                    "match_percentage": match_percentage,
                    "matched_skills": formatted_matched_skills,
                    "missing_skills": list(missing_skills),
                    "gap_count": len(missing_skills)
                })
        
        # Sort by match percentage (highest first) to show courses that are closest to being fully covered
        skill_gap_courses.sort(key=lambda x: x["match_percentage"], reverse=True)
        
        return skill_gap_courses[:limit]
    
    def find_teachable_courses(self, faculty_skills, threshold=70, limit=10):
        """
        Find courses that the faculty member can teach effectively based on their skills.
        
        Args:
            faculty_skills: Dictionary of faculty skills with proficiency and certification info
            threshold: Minimum percentage match required to consider a course teachable
            limit: Maximum number of courses to return
            
        Returns:
            List of teachable courses with match details
        """
        # Use skill matcher to get course recommendations
        recommendations = self.skill_matcher.get_recommendations(faculty_skills, limit=None)
        
        # Filter by threshold
        teachable_courses = [course for course in recommendations if course["match_percentage"] >= threshold]
        
        # Sort by match percentage (highest first)
        teachable_courses.sort(key=lambda x: x["match_percentage"], reverse=True)
        
        return teachable_courses[:limit]
    
    def format_skill_gaps_report(self, skill_gaps):
        """Format skill gaps into a readable report."""
        if not skill_gaps:
            return "No relevant skill gaps found."
        
        output = "Courses Where You Have Skill Gaps\n"
        output += "=" * 80 + "\n\n"
        output += "These are courses where you have some relevant skills but need to develop others:\n\n"
        
        for i, course in enumerate(skill_gaps, 1):
            output += f"{i}. {course['course_name']} ({course['match_percentage']:.0f}% match)\n"
            
            # Skills you already have
            if course['matched_skills']:
                output += "   Skills you already have:\n"
                for skill in course['matched_skills']:
                    output += f"   ✓ {skill}\n"
            
            # Skills you need to develop
            if course['missing_skills']:
                output += "   Skills you need to develop:\n"
                for skill in course['missing_skills']:
                    output += f"   ✗ {skill}\n"
            
            output += "\n"
        
        return output
    
    def format_teachable_courses_report(self, teachable_courses):
        """Format teachable courses into a readable report."""
        if not teachable_courses:
            return "No courses match your skills at the specified threshold."
        
        output = "Courses You Can Teach Based on Your Skills\n"
        output += "=" * 80 + "\n\n"
        
        for i, course in enumerate(teachable_courses, 1):
            output += f"{i}. {course['course_name']} ({course['match_percentage']:.0f}% match)\n"
            
            # Matched skills
            if course['matched_skills']:
                output += "   Your relevant skills:\n"
                for skill in course['matched_skills']:
                    output += f"   ✓ {skill}\n"
            
            # Missing skills
            if course['missing_skills']:
                output += "   Skills you don't have (but may not be critical):\n"
                for skill in course['missing_skills']:
                    output += f"   ✗ {skill}\n"
            
            output += "\n"
        
        return output

def interactive_teaching_advisor():
    """
    Interactive mode for faculty members to get teaching recommendations and identify skill gaps.
    """
    print("===== Faculty Teaching Advisor =====")
    print("This tool will help you identify which courses you can teach and where you have skill gaps.")
    
    # Get faculty information
    name = input("\nYour name: ")
    
    # Get skills
    print("\nEnter your skills (comma-separated):")
    print("Format: skill name:proficiency:certified (e.g., Python:Advanced:yes, Data Analysis:Intermediate:no)")
    print("Where proficiency can be Beginner, Intermediate, Advanced, or Expert")
    print("And certified is yes/no to indicate if you have certification for the skill")
    skills_input = input()
    
    # Parse skills
    faculty_skills = {}
    for skill_entry in skills_input.split(','):
        skill_entry = skill_entry.strip()
        if not skill_entry:
            continue
            
        parts = skill_entry.split(':')
        
        # Basic validation
        skill_name = parts[0].strip()
        if not skill_name:
            continue
            
        if len(parts) >= 3:
            # Full format with proficiency and certification
            proficiency = parts[1].strip() if parts[1].strip() else "Intermediate"
            is_certified = parts[2].strip().lower() in ('yes', 'true', 'y')
            faculty_skills[skill_name] = {
                "proficiency": proficiency,
                "isBackedByCertificate": is_certified
            }
        elif len(parts) == 2:
            # Proficiency only
            proficiency = parts[1].strip() if parts[1].strip() else "Intermediate"
            faculty_skills[skill_name] = {
                "proficiency": proficiency,
                "isBackedByCertificate": False
            }
        else:
            # Skill name only
            faculty_skills[skill_name] = {
                "proficiency": "Intermediate",
                "isBackedByCertificate": False
            }
    
    if not faculty_skills:
        print("No skills entered. Please run the program again with at least one skill.")
        return
    
    # Initialize advisor
    advisor = FacultyTeachingAdvisor()
    
    print(f"\nAnalyzing teaching opportunities and skill gaps for {name}...")
    
    # Find teachable courses
    teachable_courses = advisor.find_teachable_courses(faculty_skills, threshold=60)
    teachable_report = advisor.format_teachable_courses_report(teachable_courses)
    
    # Identify skill gaps
    skill_gaps = advisor.identify_skill_gaps(faculty_skills)
    gaps_report = advisor.format_skill_gaps_report(skill_gaps)
    
    # Save analysis to file
    output_dir = 'data/faculty_analysis'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{name.replace(' ', '_').lower()}_teaching_analysis.json")
    
    with open(output_file, 'w') as f:
        json.dump({
            "faculty_name": name,
            "faculty_skills": faculty_skills,
            "teachable_courses": teachable_courses,
            "skill_gaps": skill_gaps
        }, f, indent=2)
    
    # Print results
    print("\n===== Your Teaching Analysis =====")
    
    print("\n=== Courses You Can Teach ===")
    print(teachable_report)
    
    print("\n=== Skill Development Opportunities ===")
    print(gaps_report)
    
    print(f"\nDetailed analysis saved to {output_file}")
    print("\nThank you for using the Faculty Teaching Advisor!")

def main():
    """
    Main function to parse arguments and run the advisor.
    """
    parser = argparse.ArgumentParser(description='Faculty Teaching Advisor')
    parser.add_argument('--interactive', '-i', action='store_true', 
                        help='Run in interactive mode for a single faculty member')
    parser.add_argument('--file', '-f', type=str,
                        help='JSON file containing faculty skills')
    parser.add_argument('--output', '-o', type=str, default='data/faculty_analysis',
                        help='Output directory for analysis results')
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_teaching_advisor()
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                faculty_data = json.load(f)
            
            advisor = FacultyTeachingAdvisor()
            
            for faculty_name, skills in faculty_data.items():
                print(f"\nAnalyzing teaching opportunities for {faculty_name}...")
                
                teachable_courses = advisor.find_teachable_courses(skills)
                skill_gaps = advisor.identify_skill_gaps(skills)
                
                output_file = os.path.join(args.output, f"{faculty_name.replace(' ', '_').lower()}_teaching_analysis.json")
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                
                with open(output_file, 'w') as f:
                    json.dump({
                        "faculty_name": faculty_name,
                        "faculty_skills": skills,
                        "teachable_courses": teachable_courses,
                        "skill_gaps": skill_gaps
                    }, f, indent=2)
                
                print(f"Analysis saved to {output_file}")
        except Exception as e:
            print(f"Error processing file: {e}")
    else:
        print("Please specify either --interactive mode or provide a file with --file")
        parser.print_help()

if __name__ == "__main__":
    main() 