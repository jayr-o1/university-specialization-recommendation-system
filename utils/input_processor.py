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
            proficiency_normalized = proficiency.lower()
            if proficiency_normalized not in valid_proficiencies:
                proficiency = "Intermediate"  # Default to intermediate if invalid
            else:
                # Capitalize first letter for consistency
                proficiency = proficiency_normalized.capitalize()
            
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
        
        # Add explanation of recommendation factors
        if 'predicted_rating' in rec:
            output += f"   Predicted Rating: {rec['predicted_rating']:.1f}/5.0\n"
        
        if 'explanation_data' in rec:
            exp_data = rec['explanation_data']
            output += f"   Recommendation Factors:\n"
            for factor, value in exp_data['factors'].items():
                output += f"   - {factor}: {value:.1f}/100 (Weight: {exp_data['weights'][factor]*100:.1f}%)\n"
        
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
        if 'common_skills' in course and course['common_skills']:
            output += "   Common skills:\n"
            for skill in course['common_skills'][:5]:  # Show top 5
                output += f"   - {skill}\n"
            if len(course['common_skills']) > 5:
                output += f"   - ... and {len(course['common_skills']) - 5} more\n"
    
    return output


def format_explanation(recommendation, user_skills):
    """
    Create a textual explanation of why a course was recommended
    
    Args:
        recommendation: Dict with recommendation details
        user_skills: Dict of user's skills and proficiency levels
        
    Returns:
        String with explanation text
    """
    if not recommendation:
        return "No recommendation data available."
    
    course_name = recommendation.get('course_name', 'this course')
    match_percentage = recommendation.get('match_percentage', 0)
    matched_skills = recommendation.get('matched_skills', [])
    missing_skills = recommendation.get('missing_skills', [])
    predicted_rating = recommendation.get('predicted_rating', None)
    
    # Start with a general explanation
    explanation = f"{course_name} was recommended because:\n\n"
    
    # Skill match explanation
    if matched_skills:
        skill_count = len(matched_skills)
        explanation += f"1. You already have {skill_count} relevant skills for this course "
        explanation += f"({match_percentage}% skill match).\n"
        explanation += "   Key skills you have: " + ", ".join(matched_skills[:3])
        if len(matched_skills) > 3:
            explanation += f", and {len(matched_skills) - 3} more"
        explanation += ".\n\n"
    else:
        explanation += f"1. This course introduces new skills that complement your existing knowledge.\n\n"
    
    # Collaborative filtering explanation
    if predicted_rating:
        explanation += f"2. Users with similar skill profiles rated this course highly "
        explanation += f"(predicted rating: {predicted_rating:.1f}/5.0).\n\n"
    
    # Career path alignment
    explanation += f"3. This course would help you develop a more comprehensive skill set "
    if missing_skills:
        explanation += f"by teaching you {len(missing_skills)} new skills.\n"
        explanation += "   Skills you'll learn: " + ", ".join(missing_skills[:3])
        if len(missing_skills) > 3:
            explanation += f", and {len(missing_skills) - 3} more"
        explanation += ".\n\n"
    
    # Add customized advice
    if match_percentage >= 75:
        explanation += "Overall: You're well-prepared for this course! Your existing skills provide a strong foundation.\n"
    elif match_percentage >= 50:
        explanation += "Overall: You have a good foundation for this course, with some areas to strengthen beforehand.\n"
    else:
        explanation += "Overall: This course would be challenging but valuable for expanding your skill set.\n"
    
    return explanation 