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
    faculty_id: str
    course_code: str
    match_percentage: float
    missing_skills: List[SkillProficiency] = []
    
    
class RecommendationRequest(BaseModel):
    faculty_id: str
    skills: List[SkillProficiency] 