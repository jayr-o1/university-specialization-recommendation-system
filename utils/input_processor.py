def parse_user_skills(skills_input):
    """
    Parse user input of skills and proficiency levels
    
    Example input: "MySQL : Intermediate, Database Design : Advanced"
    Output: {"MySQL": "Intermediate", "Database Design": "Advanced"}
    """
    if not skills_input or skills_input.strip() == "":
        return {}
    
    # Split by comma to separate different skills
    skill_pairs = skills_input.split(",")
    skills_dict = {}
    
    for pair in skill_pairs:
        # Split by colon to separate skill and proficiency
        parts = pair.split(":")
        if len(parts) == 2:
            skill = parts[0].strip()
            proficiency = parts[1].strip()
            
            # Validate proficiency level
            valid_proficiencies = ["beginner", "intermediate", "advanced", "expert"]
            if proficiency.lower() not in valid_proficiencies:
                proficiency = "Intermediate"  # Default to intermediate if invalid
            
            skills_dict[skill] = proficiency
    
    return skills_dict


def normalize_proficiency(proficiency):
    """Normalize proficiency level to one of the standard levels"""
    proficiency = proficiency.lower()
    
    if proficiency in ["beginner", "basic", "novice", "elementary"]:
        return "Beginner"
    elif proficiency in ["intermediate", "mid-level", "moderate"]:
        return "Intermediate"
    elif proficiency in ["advanced", "proficient", "high"]:
        return "Advanced"
    elif proficiency in ["expert", "master", "professional"]:
        return "Expert"
    else:
        return "Intermediate"  # Default


def format_recommendations(recommendations):
    """
    Format recommendation results into a readable string
    """
    if not recommendations:
        return "No matching courses found based on your skills."
    
    output = "Based on your skills, these are the courses that are aligned:\n\n"
    
    for i, rec in enumerate(recommendations, 1):
        output += f"{i}. {rec['course_name']} - {rec['match_percentage']}% Match\n"
        
        if rec['matched_skills']:
            output += "   Matched Skills:\n"
            for skill in rec['matched_skills']:
                output += f"   - {skill}\n"
        
        if rec['missing_skills']:
            output += "   Skills for Further Training:\n"
            for skill in rec['missing_skills']:
                output += f"   - {skill}\n"
        
        output += "\n"
    
    return output


def format_similar_courses(similar_courses, original_course=None):
    """
    Format similar courses results
    """
    if not similar_courses:
        return "No similar courses found."
    
    output = f"Courses where you can apply similar skills and knowledge:\n\n"
    
    for i, course in enumerate(similar_courses, 1):
        output += f"{i}. {course['course_name']} - {course['similarity_score']}% Similar\n"
    
    return output 