"""
Script to analyze how your skills match specific courses.
This shows detailed information about skill matches and gaps.
"""
import os
import json
import numpy as np
from typing import Dict, List, Set, Tuple
import argparse

# Get the absolute path to the data directory
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(SRC_DIR, "data")

def load_course_skills() -> Dict:
    """Load course skills from JSON file"""
    json_path = os.path.join(DATA_DIR, 'course_skills.json')
    
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Course skills file not found at {json_path}")
        return {}

def parse_skill_input(skill_input: str) -> List[Dict]:
    """Parse skill input in format 'Skill1: Level1, Skill2: Level2, ...'"""
    skills = []
    
    # Split by comma and process each skill pair
    skill_pairs = skill_input.split(',')
    for pair in skill_pairs:
        # Support both colon and space separators
        if ':' in pair:
            parts = pair.split(':')
        elif ' ' in pair:
            # Try to split by the last space before level
            skill_part = ' '.join(pair.split()[:-1])
            level_part = pair.split()[-1]
            parts = [skill_part, level_part]
        else:
            parts = [pair, "Intermediate"]  # Default to Intermediate if no level specified
        
        if len(parts) >= 2:
            skill = parts[0].strip()
            level = parts[1].strip()
            
            # Validate level
            valid_levels = ["Beginner", "Intermediate", "Advanced", "Expert"]
            level_cap = level.capitalize()
            if level_cap not in valid_levels and level.upper() not in [l.upper() for l in valid_levels]:
                print(f"Warning: Invalid level '{level}' for skill '{skill}'. Using 'Intermediate'.")
                level = "Intermediate"
            else:
                # Match with case insensitive comparison
                for valid_level in valid_levels:
                    if valid_level.upper() == level.upper():
                        level = valid_level
                        break
            
            if skill:  # Only add if skill name is not empty
                skills.append({
                    "skill": skill,
                    "proficiency": level
                })
    
    return skills

def proficiency_to_number(level: str) -> int:
    """Convert proficiency level to a numeric value"""
    proficiency_map = {
        "Beginner": 1,
        "Intermediate": 2,
        "Advanced": 3,
        "Expert": 4
    }
    return proficiency_map.get(level, 0)

def find_fuzzy_skill_match(skill: str, all_skills: List[str]) -> Tuple[bool, str, float]:
    """Find the best match for a skill in a list of skills"""
    # Special case handling for common programming skills
    # This helps with mapping specific technologies to general concepts
    skill_lower = skill.lower()
    
    # Define mappings for common skills to more general or specific skills
    special_mappings = {
        "mysql": ["sql", "database", "sql databases", "database management"],
        "javascript": ["js", "client-side scripting", "web programming", "front-end development"],
        "python": ["programming", "programming languages", "scripting", "back-end development"],
        "java": ["object-oriented programming", "programming", "enterprise development"],
        "kotlin": ["mobile development", "android development", "programming"],
        "ui/ux": ["user interface", "user experience", "ui design", "ux design", "web design"],
    }
    
    # Check if the skill is in our special mappings
    for key, mappings in special_mappings.items():
        if key in skill_lower or skill_lower in key:
            # Add the key itself to the mappings
            mappings = [key] + mappings
            # Check each mapped skill against all skills
            for mapped_skill in mappings:
                for target_skill in all_skills:
                    if mapped_skill in target_skill.lower() or target_skill.lower() in mapped_skill:
                        # Calculate how relevant this match is
                        match_length = min(len(mapped_skill), len(target_skill))
                        total_length = max(len(mapped_skill), len(target_skill))
                        score = match_length / total_length
                        if score >= 0.4:  # Lower threshold for special mappings
                            return True, target_skill, score
    
    # Check for exact match first
    for target_skill in all_skills:
        if skill.lower() == target_skill.lower():
            return True, target_skill, 1.0
    
    # Try fuzzy matching
    best_match = None
    best_score = 0
    
    for target_skill in all_skills:
        # Check if one contains the other
        if skill.lower() in target_skill.lower():
            score = len(skill) / len(target_skill)
            if score > best_score:
                best_match = target_skill
                best_score = score
        elif target_skill.lower() in skill.lower():
            score = len(target_skill) / len(skill)
            if score > best_score:
                best_match = target_skill
                best_score = score
    
    # If found a decent match
    if best_match and best_score >= 0.5:
        return True, best_match, best_score
    
    return False, "", 0.0

def analyze_course_match(user_skills: List[Dict], course_data: Dict, course_code: str) -> Dict:
    """Analyze how user skills match a specific course"""
    if course_code not in course_data:
        return {
            "error": f"Course {course_code} not found"
        }
    
    course = course_data[course_code]
    course_name = course.get("name", "")
    course_skills = course.get("required_skills", {})
    
    # Skip courses with no required skills
    if not course_skills:
        return {
            "error": f"Course {course_code} has no required skills"
        }
    
    # Convert user skills to dict for easier lookup
    user_skill_dict = {skill_info["skill"]: skill_info["proficiency"] for skill_info in user_skills}
    
    # Track matches and gaps
    direct_matches = []
    fuzzy_matches = []
    missing_skills = []
    
    # Compute level match scores
    total_score = 0
    max_possible = len(course_skills) * 4  # Highest possible score
    
    # To track which user skills have been used for fuzzy matches
    user_skills_used = set()
    
    # Check each course skill
    for course_skill, required_level in course_skills.items():
        required_value = proficiency_to_number(required_level)
        
        # Check for direct match
        if course_skill in user_skill_dict:
            user_level = user_skill_dict[course_skill]
            user_value = proficiency_to_number(user_level)
            
            # Calculate match score
            match_score = min(user_value / required_value, 1.0) * required_value
            total_score += match_score
            
            direct_matches.append({
                "skill": course_skill,
                "user_level": user_level,
                "required_level": required_level,
                "match_percentage": round(match_score / required_value * 100, 1)
            })
            
            # Mark this user skill as used
            user_skills_used.add(course_skill)
            continue
        
        # Try fuzzy matching - find best matching user skill for this course skill
        best_match = None
        best_score = 0
        best_user_skill = None
        
        for user_skill in user_skill_dict:
            # Skip skills that have already been used for direct matches
            if user_skill in user_skills_used:
                continue
                
            found, matched_skill, score = find_fuzzy_skill_match(user_skill, [course_skill])
            if found and score > best_score:
                best_score = score
                best_match = matched_skill
                best_user_skill = user_skill
        
        # Use the best fuzzy match if one was found
        if best_match and best_score >= 0.4:
            user_level = user_skill_dict[best_user_skill]
            user_value = proficiency_to_number(user_level)
            
            # Calculate match score with fuzzy penalty
            match_score = min(user_value / required_value, 1.0) * required_value * best_score
            total_score += match_score
            
            fuzzy_matches.append({
                "user_skill": best_user_skill,
                "course_skill": course_skill,
                "user_level": user_level,
                "required_level": required_level,
                "match_percentage": round(match_score / required_value * 100, 1)
            })
            
            # Mark this user skill as used
            user_skills_used.add(best_user_skill)
        else:
            # No match found for this course skill
            missing_skills.append({
                "skill": course_skill,
                "required_level": required_level
            })
    
    # Calculate overall match percentage
    overall_match = (total_score / max_possible * 100) if max_possible > 0 else 0
    
    # Calculate skill importance factor based on how many skills were matched
    matched_count = len(direct_matches) + len(fuzzy_matches)
    
    # Give extra weight if we matched more skills
    if matched_count > 0:
        # Basic scaling - higher weight for courses with more matched skills
        importance_factor = 1.0 + (matched_count / len(course_skills)) * 0.5
        adjusted_match = overall_match * importance_factor
        
        # Cap at 100%
        adjusted_match = min(adjusted_match, 100.0)
    else:
        adjusted_match = overall_match
    
    return {
        "course_code": course_code,
        "course_name": course_name,
        "overall_match": round(adjusted_match, 1),
        "raw_match": round(overall_match, 1),
        "direct_matches": direct_matches,
        "fuzzy_matches": fuzzy_matches,
        "missing_skills": missing_skills,
        "total_required_skills": len(course_skills),
        "matched_skills": matched_count,
        "match_ratio": f"{matched_count}/{len(course_skills)}"
    }

def find_best_matching_courses(user_skills: List[Dict], course_data: Dict, top_n: int = 5) -> List[Dict]:
    """Find the best matching courses for the user's skills"""
    results = []
    
    for course_code in course_data:
        result = analyze_course_match(user_skills, course_data, course_code)
        if "error" not in result:
            results.append(result)
    
    # Sort by overall match
    results.sort(key=lambda x: x["overall_match"], reverse=True)
    
    return results[:top_n]

def print_skill_analysis(analysis: Dict):
    """Print detailed skill analysis for a course"""
    print(f"\n{analysis['course_code']} - {analysis['course_name']}")
    print(f"Overall Match: {analysis['overall_match']}%")
    print(f"Skills Match: {analysis['match_ratio']}")
    print("=" * 80)
    
    if 'raw_match' in analysis and analysis['raw_match'] != analysis['overall_match']:
        print(f"Raw Score: {analysis['raw_match']}% (Adjusted for skill coverage)")
    
    # Print all course required skills with matches
    print("\nCourse Required Skills Analysis:")
    print("-" * 80)
    
    # Group by match status
    all_skills = []
    
    # Add direct matches
    for match in analysis['direct_matches']:
        all_skills.append({
            "skill": match['skill'],
            "status": "✓ Direct Match",
            "details": f"{match['user_level']} (Required: {match['required_level']}) - {match['match_percentage']}% match"
        })
    
    # Add fuzzy matches
    for match in analysis['fuzzy_matches']:
        all_skills.append({
            "skill": match['course_skill'],
            "status": f"~ Matched with your '{match['user_skill']}'",
            "details": f"{match['user_level']} (Required: {match['required_level']}) - {match['match_percentage']}% match"
        })
    
    # Add missing skills
    for skill in analysis['missing_skills']:
        all_skills.append({
            "skill": skill['skill'],
            "status": "✗ Missing",
            "details": f"Required: {skill['required_level']}"
        })
    
    # Sort by skill name to keep output stable
    all_skills.sort(key=lambda x: x["skill"])
    
    # Print all skills
    for skill_info in all_skills:
        print(f"{skill_info['skill']:<40} {skill_info['status']:<30} {skill_info['details']}")
    
    # Print skill matching summary
    print("\nSkill Matching Summary:")
    print(f"  Direct matches: {len(analysis['direct_matches'])}")
    print(f"  Fuzzy matches: {len(analysis['fuzzy_matches'])}")
    print(f"  Missing skills: {len(analysis['missing_skills'])}")
    
    if analysis['fuzzy_matches']:
        print("\nFuzzy Matches Detail:")
        for match in analysis['fuzzy_matches']:
            print(f"  Your '{match['user_skill']}' matched with '{match['course_skill']}'")

def main():
    parser = argparse.ArgumentParser(description='Analyze skill matches with courses')
    parser.add_argument('--skills', '-s', help='Comma-separated list of skills with proficiency levels (e.g., "Python: Intermediate, JavaScript: Advanced")')
    parser.add_argument('--course', '-c', help='Specific course code to analyze')
    parser.add_argument('--top', '-n', type=int, default=5, help='Number of best matches to show')
    
    args = parser.parse_args()
    
    # If no skills provided via arguments, prompt the user
    skills_input = args.skills
    if not skills_input:
        skills_input = input("Enter your skills (format: Skill1: Level1, Skill2: Level2, ...): ")
    
    # Parse skills
    user_skills = parse_skill_input(skills_input)
    if not user_skills:
        print("No valid skills provided. Please use the format 'Skill1: Level1, Skill2: Level2, ...'")
        return
    
    # Load course data
    course_data = load_course_skills()
    if not course_data:
        print("Error: No course data found")
        return
    
    print(f"\nProcessed {len(user_skills)} skills:")
    for skill in user_skills:
        print(f"  - {skill['skill']}: {skill['proficiency']}")
    
    # Analyze specific course if provided
    if args.course:
        if args.course not in course_data:
            print(f"Error: Course {args.course} not found")
            return
        
        analysis = analyze_course_match(user_skills, course_data, args.course)
        print_skill_analysis(analysis)
    else:
        # Find best matching courses
        print(f"\nFinding the top {args.top} matching courses...")
        best_matches = find_best_matching_courses(user_skills, course_data, args.top)
        
        # Print summary
        print("\nTop Course Matches:")
        print("=" * 80)
        print(f"{'Code':<15} {'Name':<45} {'Match':<10} {'Skills Match':<15}")
        print("-" * 80)
        for match in best_matches:
            print(f"{match['course_code']:<15} {match['course_name'][:45]:<45} {match['overall_match']}%{' ':>4} {match['match_ratio']:<15}")
        
        # Print detailed analysis for top match
        if best_matches:
            print("\nDetailed Analysis for Top Match:")
            print_skill_analysis(best_matches[0])

if __name__ == "__main__":
    main() 