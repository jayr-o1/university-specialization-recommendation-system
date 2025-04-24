from fastapi import APIRouter, HTTPException, Path, Body, Query
from typing import List, Optional
import os
import numpy as np

from models.schemas import Faculty, Course, SkillProficiency, MatchResult, RecommendationRequest, SkillOnlyRequest
from utils.data_access import (
    load_all_courses, 
    get_course_by_code, 
    load_all_faculties, 
    get_faculty_by_id,
    update_faculty_skills
)
from matching.semantic_matcher import match_faculty_to_course, get_top_course_matches
from models.recommender import SkillBasedRecommender
from data.dataset import ensure_dataset_exists

router = APIRouter()

# Initialize the recommender model - lazy loading
_recommender = None

def get_recommender():
    """Get a trained recommender model, creating it if it doesn't exist."""
    global _recommender
    
    if _recommender is None:
        # Ensure dataset exists
        ensure_dataset_exists()
        
        # Load the model if it exists, otherwise create and train it
        models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models'))
        model_path = os.path.join(models_dir, "recommender_model.npz")
        
        try:
            if os.path.exists(model_path):
                # Check the n_components value in the saved model
                with np.load(model_path, allow_pickle=True) as data:
                    if 'n_components' in data:
                        n_components = int(data['n_components'])
                    else:
                        # Default to 5 if not found
                        n_components = 5
                
                # Load existing model with the correct number of components
                print(f"Loading model from {model_path} with {n_components} components")
                _recommender = SkillBasedRecommender(n_components=n_components)
                _recommender.load_model(model_path)
                
                # Verify the model is properly loaded
                if not _recommender.is_trained:
                    raise ValueError("Model loaded but not marked as trained")
            else:
                # Create new model
                print("Model file not found. Training new model...")
                from data.dataset import save_dataset_as_csv
                save_dataset_as_csv()
                
                data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
                skill_matrix_path = os.path.join(data_dir, "skill_course_matrix.csv")
                
                # Use 5 components for consistency
                n_components = 5
                _recommender = SkillBasedRecommender(n_components=n_components)
                _recommender.load_data(skill_matrix_path)
                _recommender.train()
                _recommender.save_model(model_path)
                print(f"New model trained and saved to {model_path}")
                
        except Exception as e:
            print(f"Error loading/creating recommender model: {str(e)}")
            # If there's any error, let's just train a new model
            print("Training new model due to error...")
            from data.dataset import save_dataset_as_csv
            save_dataset_as_csv()
            
            data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
            skill_matrix_path = os.path.join(data_dir, "skill_course_matrix.csv")
            
            # Use 5 components for consistency
            n_components = 5
            _recommender = SkillBasedRecommender(n_components=n_components)
            _recommender.load_data(skill_matrix_path)
            _recommender.train()
            _recommender.save_model(model_path)
            print(f"New model trained and saved to {model_path}")
    
    return _recommender


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
    
    # Add course names
    for result in match_results:
        course = get_course_by_code(result.course_code)
        if course:
            result.course_name = course.name
    
    return match_results


@router.post("/skills-to-courses", response_model=List[MatchResult])
async def skills_to_courses(
    request: SkillOnlyRequest,
    top_n: int = 10,
    use_model: bool = Query(True, title="Use model-based recommendation")
):
    """
    Simplified endpoint to get course recommendations based only on skills and proficiencies.
    No faculty information is required.
    """
    # Create a simplified faculty object with just the skills
    faculty = Faculty(
        id="temp",
        name="Temporary",
        department="Temporary",
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
    
    # Add course names and clean up faculty information
    for result in match_results:
        # Clean up faculty information
        result.faculty_id = None
        
        # Add course name
        course = get_course_by_code(result.course_code)
        if course:
            result.course_name = course.name
    
    return match_results


@router.get("/similar-courses/{course_code}", response_model=List[dict])
async def get_similar_courses(
    course_code: str = Path(..., title="The course code"),
    top_n: int = 10
):
    """Get courses similar to the specified course."""
    # Check if course exists
    course = get_course_by_code(course_code)
    if not course:
        raise HTTPException(status_code=404, detail=f"Course with code {course_code} not found")
    
    # Get recommender
    recommender = get_recommender()
    
    # Get similar courses
    similar_courses = recommender.get_similar_courses(course_code, top_n)
    
    # Format the response
    results = []
    for similar_code, similarity in similar_courses:
        similar_course = get_course_by_code(similar_code)
        if similar_course:
            results.append({
                "course_code": similar_course.code,
                "course_name": similar_course.name,
                "similarity_score": round(similarity * 100, 2)
            })
    
    return results


@router.get("/skill-importance", response_model=dict)
async def get_skill_importance():
    """Get the importance of skills across latent factors."""
    # Get recommender
    recommender = get_recommender()
    
    # Get skill importance
    skill_importance = recommender.get_skill_importance()
    
    # Format the response
    result = {}
    for factor in skill_importance.columns:
        top_skills = skill_importance[factor].sort_values(ascending=False).head(5)
        result[factor] = {skill: round(float(importance), 2) for skill, importance in top_skills.items()}
    
    return result 