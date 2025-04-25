"""
Enhanced matching module that uses skill taxonomy and inference for better recommendations.
"""
import spacy
import numpy as np
from typing import Dict, List, Tuple, Set, Optional
from src.models.schemas import ProficiencyLevel, Faculty, Course, SkillProficiency, MatchResult
from src.utils.skill_taxonomy import (
    get_category, get_related_skills, get_inferred_skills, get_skill_similarity,
    SKILL_INFERENCE_RULES
)
from src.matching.semantic_matcher import nlp, PROFICIENCY_WEIGHTS, get_semantic_similarity

def enhance_faculty_skills(faculty: Faculty) -> Faculty:
    """
    Enhance faculty skills by adding inferred skills based on their existing skills.
    """
    original_skills = [skill.skill for skill in faculty.skills]
    inferred_skills = get_inferred_skills(original_skills)
    
    # Create enhanced faculty with original and inferred skills
    enhanced_faculty = Faculty(
        id=faculty.id,
        name=faculty.name,
        department=faculty.department,
        skills=list(faculty.skills)  # Create a copy of the original skills
    )
    
    # Add inferred skills with reduced proficiency level
    for inferred_skill in inferred_skills:
        # Find the skill that led to this inference
        source_skills = [s for s in faculty.skills 
                         if s.skill in SKILL_INFERENCE_RULES and
                         inferred_skill in SKILL_INFERENCE_RULES[s.skill]]
        
        if source_skills:
            # Use the highest proficiency of source skills, but reduce by one level
            source_proficiency = max(s.proficiency for s in source_skills)
            
            # Convert enum to lower proficiency
            if source_proficiency == ProficiencyLevel.EXPERT:
                inferred_proficiency = ProficiencyLevel.ADVANCED
            elif source_proficiency == ProficiencyLevel.ADVANCED:
                inferred_proficiency = ProficiencyLevel.INTERMEDIATE
            else:
                inferred_proficiency = ProficiencyLevel.BEGINNER
            
            enhanced_faculty.skills.append(
                SkillProficiency(skill=inferred_skill, proficiency=inferred_proficiency)
            )
    
    return enhanced_faculty

def calculate_enhanced_skill_match(faculty_skill: SkillProficiency, 
                                  required_skill: str, 
                                  required_proficiency: ProficiencyLevel) -> Tuple[float, bool]:
    """
    Calculate match between faculty skill and required course skill using taxonomy.
    Returns a tuple of (match_score, is_exact_match)
    """
    # Check for exact skill match
    if faculty_skill.skill.lower() == required_skill.lower():
        faculty_weight = PROFICIENCY_WEIGHTS[faculty_skill.proficiency]
        required_weight = PROFICIENCY_WEIGHTS[required_proficiency]
        
        # Calculate how well the faculty meets the required proficiency
        match_score = min(1.0, faculty_weight / required_weight)
        return match_score, True
    
    # Check for custom similarity if available
    custom_similarity = get_skill_similarity(faculty_skill.skill, required_skill)
    
    if custom_similarity is not None:
        similarity = custom_similarity
    else:
        # Fall back to semantic similarity
        similarity = get_semantic_similarity(faculty_skill.skill, required_skill)
    
    # Apply proficiency weight to similarity
    faculty_weight = PROFICIENCY_WEIGHTS[faculty_skill.proficiency]
    required_weight = PROFICIENCY_WEIGHTS[required_proficiency]
    
    # If faculty proficiency is lower than required, reduce the similarity score
    proficiency_factor = min(1.0, faculty_weight / required_weight)
    
    # Final score is a combination of similarity and proficiency match
    match_score = similarity * proficiency_factor
    
    return match_score, False

def match_faculty_to_course_enhanced(faculty: Faculty, course: Course) -> MatchResult:
    """Match a faculty member to a course using enhanced matching algorithm."""
    # First, enhance faculty skills by adding inferred skills
    enhanced_faculty = enhance_faculty_skills(faculty)
    
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
        for faculty_skill in enhanced_faculty.skills:
            match_score, is_exact_match = calculate_enhanced_skill_match(
                faculty_skill, skill_name, required_proficiency
            )
            
            if match_score > best_match_score:
                best_match_score = match_score
                exact_match_found = is_exact_match
                best_matching_faculty_skill = faculty_skill
        
        # Add to total score with enhanced weighting
        if exact_match_found:
            # Exact matches get full weight plus a small bonus
            weighted_score = best_match_score * 1.1
        else:
            # Non-exact matches are weighted based on score and category matching
            faculty_category = get_category(best_matching_faculty_skill.skill if best_matching_faculty_skill else "")
            required_category = get_category(skill_name)
            
            category_bonus = 0.1 if faculty_category == required_category and faculty_category != "Other" else 0.0
            
            if best_match_score > 0.8:
                weighted_score = best_match_score * (1.0 + category_bonus)
            elif best_match_score > 0.6:
                weighted_score = best_match_score * (0.9 + category_bonus)
            elif best_match_score > 0.4:
                weighted_score = best_match_score * (0.8 + category_bonus)
            else:
                weighted_score = best_match_score * (0.7 + category_bonus)
                
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
    
    # Calculate overall match percentage with curve adjustments
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

def get_top_course_matches_enhanced(faculty: Faculty, courses: List[Course], top_n: int = 10) -> List[MatchResult]:
    """Get top N course matches for a faculty member using enhanced matching."""
    matches = []
    
    for course in courses:
        match_result = match_faculty_to_course_enhanced(faculty, course)
        matches.append(match_result)
    
    # Sort by match percentage in descending order
    matches.sort(key=lambda x: x.match_percentage, reverse=True)
    
    # Return top N matches
    return matches[:top_n] 