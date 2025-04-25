import spacy
import numpy as np
from typing import Dict, List, Tuple

# Updated import with proper package path
from src.models.schemas import ProficiencyLevel, Faculty, Course, SkillProficiency, MatchResult

# Load the spaCy model - English language model
try:
    nlp = spacy.load("en_core_web_md")
except:
    # On first run, download the model
    import os
    os.system("python -m spacy download en_core_web_md")
    nlp = spacy.load("en_core_web_md")


# Proficiency level weights
PROFICIENCY_WEIGHTS = {
    ProficiencyLevel.BEGINNER: 0.25,
    ProficiencyLevel.INTERMEDIATE: 0.5,
    ProficiencyLevel.ADVANCED: 0.75,
    ProficiencyLevel.EXPERT: 1.0
}


def get_semantic_similarity(skill1: str, skill2: str) -> float:
    """Calculate semantic similarity between two skills using spaCy."""
    doc1 = nlp(skill1.lower())
    doc2 = nlp(skill2.lower())
    
    # Check if both documents have vectors before calculating similarity
    if not doc1.has_vector or not doc2.has_vector or doc1.vector_norm == 0 or doc2.vector_norm == 0:
        # If either document doesn't have a vector, use string matching as fallback
        normalized_skill1 = skill1.lower().strip()
        normalized_skill2 = skill2.lower().strip()
        
        # Exact match
        if normalized_skill1 == normalized_skill2:
            return 1.0
        
        # Partial string containment
        if normalized_skill1 in normalized_skill2 or normalized_skill2 in normalized_skill1:
            return 0.8
        
        # Default low similarity
        return 0.2
    
    # Both documents have vectors, return similarity score between 0 and 1
    return doc1.similarity(doc2)


def calculate_skill_match(faculty_skill: SkillProficiency, 
                          required_skill: str, 
                          required_proficiency: ProficiencyLevel) -> Tuple[float, bool]:
    """
    Calculate match between faculty skill and required course skill.
    Returns a tuple of (match_score, is_exact_match)
    """
    # Check for exact skill match
    if faculty_skill.skill.lower() == required_skill.lower():
        faculty_weight = PROFICIENCY_WEIGHTS[faculty_skill.proficiency]
        required_weight = PROFICIENCY_WEIGHTS[required_proficiency]
        
        # Calculate how well the faculty meets the required proficiency
        match_score = min(1.0, faculty_weight / required_weight)
        return match_score, True
    
    # Calculate semantic similarity for non-exact matches
    similarity = get_semantic_similarity(faculty_skill.skill, required_skill)
    
    # Apply proficiency weight to similarity
    faculty_weight = PROFICIENCY_WEIGHTS[faculty_skill.proficiency]
    required_weight = PROFICIENCY_WEIGHTS[required_proficiency]
    
    # If faculty proficiency is lower than required, reduce the similarity score
    proficiency_factor = min(1.0, faculty_weight / required_weight)
    
    # Final score is a combination of semantic similarity and proficiency match
    match_score = similarity * proficiency_factor
    
    return match_score, False


def match_faculty_to_course(faculty: Faculty, course: Course) -> MatchResult:
    """Match a faculty member to a course and calculate match percentage."""
    total_score = 0.0
    max_possible_score = len(course.required_skills)
    missing_skills = []
    matched_skills = []
    
    # For each required skill in the course
    for skill_name, required_proficiency in course.required_skills.items():
        best_match_score = 0.0
        exact_match_found = False
        best_matching_faculty_skill = None
        
        # Find the best matching faculty skill
        for faculty_skill in faculty.skills:
            match_score, is_exact_match = calculate_skill_match(
                faculty_skill, skill_name, required_proficiency
            )
            
            if match_score > best_match_score:
                best_match_score = match_score
                exact_match_found = is_exact_match
                best_matching_faculty_skill = faculty_skill
        
        # Add to total score - apply a weighting to make the match percentage more stringent
        # Give more weight to exact matches and high scores
        # This creates a more realistic assessment of skill match
        if exact_match_found:
            # Exact matches get full weight plus a small bonus
            weighted_score = best_match_score * 1.1
        else:
            # Non-exact matches are weighted lower based on score
            if best_match_score > 0.8:
                weighted_score = best_match_score
            elif best_match_score > 0.6:
                weighted_score = best_match_score * 0.9
            elif best_match_score > 0.4:
                weighted_score = best_match_score * 0.8
            else:
                weighted_score = best_match_score * 0.7
                
        total_score += weighted_score
        
        # Check if the skill is missing or below required proficiency
        if best_match_score < 0.5:  # Threshold for considering a skill as "missing"
            missing_skills.append(
                SkillProficiency(
                    skill=skill_name,
                    proficiency=required_proficiency
                )
            )
        else:
            # Add to matched skills if there's a good match
            if best_matching_faculty_skill:
                matched_skills.append(
                    SkillProficiency(
                        skill=skill_name,
                        proficiency=best_matching_faculty_skill.proficiency
                    )
                )
    
    # Calculate overall match percentage
    # Apply a scaling factor to make matches more realistic
    raw_match = (total_score / max_possible_score) if max_possible_score > 0 else 0
    match_percentage = raw_match * 100
    
    # Apply a curve to make high percentages harder to achieve
    if match_percentage > 95:
        match_percentage = 95 + (match_percentage - 95) * 0.5  # Cap at ~97.5%
    elif match_percentage > 90:
        match_percentage = 90 + (match_percentage - 90) * 0.6
    elif match_percentage > 80:
        match_percentage = 80 + (match_percentage - 80) * 0.7
    elif match_percentage > 70:
        match_percentage = 70 + (match_percentage - 70) * 0.8
    
    return MatchResult(
        faculty_id=getattr(faculty, 'id', None),
        course_code=course.code,
        course_name=course.name,
        match_percentage=round(match_percentage, 2),
        matched_skills=matched_skills,
        missing_skills=missing_skills
    )


def get_top_course_matches(faculty: Faculty, courses: List[Course], top_n: int = 10) -> List[MatchResult]:
    """Get top N course matches for a faculty member."""
    matches = []
    
    for course in courses:
        match_result = match_faculty_to_course(faculty, course)
        matches.append(match_result)
    
    # Sort by match percentage in descending order
    matches.sort(key=lambda x: x.match_percentage, reverse=True)
    
    # Return top N matches
    return matches[:top_n] 