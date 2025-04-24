from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ProficiencyLevel(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"


class Skill(BaseModel):
    name: str
    description: Optional[str] = None


class SkillProficiency(BaseModel):
    skill: str
    proficiency: ProficiencyLevel
    
    
class Course(BaseModel):
    code: str
    name: str
    description: str
    required_skills: Dict[str, ProficiencyLevel]
    

class Faculty(BaseModel):
    id: str
    name: str
    department: str
    skills: List[SkillProficiency] = []
    
    
class MatchResult(BaseModel):
    faculty_id: Optional[str] = None
    course_code: str
    course_name: Optional[str] = None
    match_percentage: float
    matched_skills: List[SkillProficiency] = []
    missing_skills: List[SkillProficiency] = []
    
    
class RecommendationRequest(BaseModel):
    faculty_id: Optional[str] = None
    skills: List[SkillProficiency]


class SkillOnlyRequest(BaseModel):
    """Request model for providing only skills and proficiencies"""
    skills: List[SkillProficiency] 