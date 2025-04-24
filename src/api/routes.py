from fastapi import APIRouter, HTTPException, Path, Body, Query
from typing import List, Optional
import os
import numpy as np

from src.models.schemas import Faculty, Course, SkillProficiency, MatchResult, RecommendationRequest, SkillOnlyRequest
from src.utils.data_access import (
    load_all_courses, 
    get_course_by_code, 
    load_all_faculties, 
    get_faculty_by_id,
    update_faculty_skills
)
from src.matching.semantic_matcher import match_faculty_to_course, get_top_course_matches
from src.models import get_recommender
from src.data.dataset import ensure_dataset_exists

router = APIRouter()

@router.get("/courses", response_model=List[Course])
async def get_courses():
    """Get all available courses."""
    return load_all_courses()


@router.get("/courses/{code}", response_model=Course)
async def get_course(code: str = Path(..., title="The course code")):
    """Get a specific course by code."""
    course = get_course_by_code(code)
    if not course:
        raise HTTPException(status_code=404, detail=f"Course with code {code} not found")
    return course


@router.get("/faculties", response_model=List[Faculty])
async def get_faculties():
    """Get all faculty members."""
    return load_all_faculties()


@router.get("/faculties/{faculty_id}", response_model=Faculty)
async def get_faculty(faculty_id: str = Path(..., title="The faculty ID")):
    """Get a specific faculty member by ID."""
    faculty = get_faculty_by_id(faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail=f"Faculty with ID {faculty_id} not found")
    return faculty


@router.post("/faculties/{faculty_id}/skills", response_model=Faculty)
async def update_skills(
    faculty_id: str = Path(..., title="The faculty ID"),
    skills: List[SkillProficiency] = Body(..., title="The faculty skills")
):
    """Update a faculty member's skills."""
    updated_faculty = update_faculty_skills(faculty_id, skills)
    if not updated_faculty:
        raise HTTPException(status_code=404, detail=f"Faculty with ID {faculty_id} not found")
    return updated_faculty


@router.get("/match/faculty/{faculty_id}/course/{course_code}", response_model=MatchResult)
async def match_to_course(
    faculty_id: str = Path(..., title="The faculty ID"),
    course_code: str = Path(..., title="The course code")
):
    """Match a faculty member to a specific course."""
    faculty = get_faculty_by_id(faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail=f"Faculty with ID {faculty_id} not found")
    
    course = get_course_by_code(course_code)
    if not course:
        raise HTTPException(status_code=404, detail=f"Course with code {course_code} not found")
    
    match_result = match_faculty_to_course(faculty, course)
    return match_result


@router.get("/recommendations/faculty/{faculty_id}", response_model=List[MatchResult])
async def get_recommendations(
    faculty_id: str = Path(..., title="The faculty ID"),
    top_n: int = 10,
    use_model: bool = Query(False, title="Use model-based recommendation")
):
    """Get top N course recommendations for a faculty member."""
    faculty = get_faculty_by_id(faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail=f"Faculty with ID {faculty_id} not found")
    
    if use_model:
        # Use model-based recommendations
        recommender = get_recommender()
        match_results = recommender.recommend_courses(faculty, top_n)
    else:
        # Use semantic-based recommendations
        courses = load_all_courses()
        match_results = get_top_course_matches(faculty, courses, top_n)
    
    return match_results


@router.post("/recommendations/custom", response_model=List[MatchResult])
async def get_custom_recommendations(
    request: RecommendationRequest,
    top_n: int = 10,
    use_model: bool = Query(False, title="Use model-based recommendation")
):
    """Get course recommendations based on custom skills input."""
    # Create a temporary faculty object with the custom skills
    faculty = Faculty(
        id=request.faculty_id or "custom",
        name="Custom Request",
        department="Temporary",
        skills=request.skills
    )
    
    # If faculty ID is provided, use the faculty's name and department
    if request.faculty_id:
        existing_faculty = get_faculty_by_id(request.faculty_id)
        if existing_faculty:
            faculty.name = existing_faculty.name
            faculty.department = existing_faculty.department
    
    if use_model:
        # Use model-based recommendations
        recommender = get_recommender()
        match_results = recommender.recommend_courses(faculty, top_n)
    else:
        # Use semantic-based recommendations
        courses = load_all_courses()
        match_results = get_top_course_matches(faculty, courses, top_n)
    
    return match_results


@router.post("/skills-to-courses", response_model=List[MatchResult])
async def skills_to_courses(
    request: SkillOnlyRequest,
    top_n: int = 10,
    use_model: bool = Query(True, title="Use model-based recommendation")
):
    """
    Get course recommendations based only on skills (no faculty information needed).
    This simplified endpoint is useful for quick recommendations without needing a faculty ID.
    """
    # Create a temporary faculty object with the provided skills
    faculty = Faculty(
        id="temp",
        name="Temporary User",
        department="N/A",
        skills=request.skills
    )
    
    if use_model:
        # Use model-based recommendations
        recommender = get_recommender()
        match_results = recommender.recommend_courses(faculty, top_n)
    else:
        # Use semantic-based recommendations
        courses = load_all_courses()
        match_results = get_top_course_matches(faculty, courses, top_n)
    
    return match_results


@router.get("/similar-courses/{course_code}", response_model=List[dict])
async def get_similar_courses(
    course_code: str = Path(..., title="The course code"),
    top_n: int = 10
):
    """Find courses that are similar to a given course based on skill requirements."""
    course = get_course_by_code(course_code)
    if not course:
        raise HTTPException(status_code=404, detail=f"Course with code {course_code} not found")
    
    # Use the recommender model to find similar courses
    recommender = get_recommender()
    similar_courses = recommender.get_similar_courses(course_code, top_n)
    
    # Format the results to include course names along with similarity scores
    results = []
    for similar_code, similarity in similar_courses:
        similar_course = get_course_by_code(similar_code)
        if similar_course:
            results.append({
                "course_code": similar_code,
                "course_name": similar_course.name,
                "similarity_score": round(similarity * 100, 2)  # Convert to percentage
            })
    
    return results


@router.get("/skill-importance", response_model=dict)
async def get_skill_importance():
    """Get the importance of each skill across the latent factors in the model."""
    recommender = get_recommender()
    skill_importance = recommender.get_skill_importance()
    
    # Convert DataFrame to dict for API response
    # First convert to dict with columns as keys
    result_dict = skill_importance.to_dict(orient='dict')
    
    # Add skill names (index) as a key in each factor dict
    formatted_result = {}
    for factor, values in result_dict.items():
        formatted_result[factor] = {
            "skills": [{"skill": skill, "importance": round(float(imp), 4)} 
                      for skill, imp in values.items()]
        }
        # Sort skills by importance for each factor
        formatted_result[factor]["skills"].sort(key=lambda x: x["importance"], reverse=True)
    
    return {"skill_importance_by_factor": formatted_result} 