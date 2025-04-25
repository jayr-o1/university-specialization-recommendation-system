import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import numpy as np
import os
import base64
from io import BytesIO
from collections import defaultdict

def _convert_proficiency_to_value(proficiency):
    """Convert proficiency string to numerical value"""
    proficiency = proficiency.lower() if isinstance(proficiency, str) else "beginner"
    proficiency_values = {
        "beginner": 25,
        "intermediate": 50,
        "advanced": 75,
        "expert": 100
    }
    return proficiency_values.get(proficiency, 25)

def _extract_proficiency(skill_string):
    """Extract the proficiency level from a skill string like 'Python (Advanced)'"""
    if not isinstance(skill_string, str):
        return "beginner"
        
    if "(" in skill_string and ")" in skill_string:
        proficiency = skill_string.split("(")[1].split(")")[0].lower()
        proficiency_values = ["beginner", "intermediate", "advanced", "expert"]
        if proficiency in proficiency_values:
            return proficiency
    return "beginner"

def generate_skill_gap_chart(course_data, user_skills, save_path=None):
    """
    Generate a chart showing the gap between user skills and course required skills
    
    Args:
        course_data: Dict with course_name and required_skills
        user_skills: Dict of user's skills and proficiency levels
        save_path: Path to save the chart image (optional)
        
    Returns:
        Base64 encoded image string if save_path is None, otherwise path to saved image
    """
    # Extract the matched and missing skills
    if not user_skills or not course_data or 'required_skills' not in course_data:
        # Create a basic "no data" chart
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "Insufficient data for skill gap analysis", 
                ha='center', va='center', fontsize=14)
        ax.axis('off')
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            # Return as base64 string
            buf = BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            plt.close()
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            return img_str

    # Get all skills from the course
    all_skills = course_data['required_skills'][:10]  # Limit to top 10 for readability
    
    # Organize the skills data
    user_skill_values = []
    course_skill_values = []
    skill_labels = []
    
    # Sort skills: first matched, then missing
    matched_skills = []
    missing_skills = []
    
    for skill in all_skills:
        if skill in user_skills:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)
    
    # Limit to a reasonable number
    display_skills = matched_skills + missing_skills
    if len(display_skills) > 10:
        display_skills = display_skills[:10]
    
    # Create data for the chart
    for skill in display_skills:
        skill_labels.append(skill)
        # Course requires all skills at "required" level (arbitrary value of 70)
        course_skill_values.append(70)
        
        # User skill level
        if skill in user_skills:
            user_value = _convert_proficiency_to_value(user_skills[skill])
            user_skill_values.append(user_value)
        else:
            user_skill_values.append(0)  # User doesn't have this skill
    
    # Create the chart
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Set up the chart
    x = np.arange(len(skill_labels))
    width = 0.35
    
    # Plot the bars
    user_bars = ax.bar(x - width/2, user_skill_values, width, label='Your Skills', color='#4285F4')
    course_bars = ax.bar(x + width/2, course_skill_values, width, label='Required Level', color='#EA4335')
    
    # Add labels and titles
    ax.set_title(f'Skill Gap Analysis for {course_data["course_name"]}', fontsize=14, pad=20)
    ax.set_ylabel('Skill Level', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(skill_labels, rotation=45, ha='right', fontsize=10)
    ax.legend()
    
    # Add a grid for better readability
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add proficiency level markers
    ax.axhline(y=25, linestyle=':', color='gray', alpha=0.5)
    ax.axhline(y=50, linestyle=':', color='gray', alpha=0.5)
    ax.axhline(y=75, linestyle=':', color='gray', alpha=0.5)
    
    # Add text labels
    ax.text(-0.5, 25, 'Beginner', verticalalignment='center', fontsize=8, color='gray')
    ax.text(-0.5, 50, 'Intermediate', verticalalignment='center', fontsize=8, color='gray')
    ax.text(-0.5, 75, 'Advanced', verticalalignment='center', fontsize=8, color='gray')
    ax.text(-0.5, 100, 'Expert', verticalalignment='center', fontsize=8, color='gray')
    
    # Set y-axis limits
    ax.set_ylim(0, 105)
    
    # Adjust layout
    plt.tight_layout()
    
    if save_path:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()
        return save_path
    else:
        # Return as base64 string
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        return img_str

def generate_recommendation_explanation(recommendation, user_skills, as_dict=False):
    """
    Generate a chart explaining the factors that went into a recommendation
    
    Args:
        recommendation: Dict with recommendation details
        user_skills: Dict of user's skills and proficiency levels
        as_dict: Whether to return the data as a dict instead of an image
        
    Returns:
        Base64 encoded image string or dict with explanation data
    """
    # Extract recommendation factors
    factors = {
        'Skill Match': recommendation.get('match_percentage', 0),
        'Collaborative Score': recommendation.get('predicted_rating', 3.5) * 20,  # Scale to 0-100
        'Career Path Alignment': 65  # Default value if not provided
    }
    
    # Calculate contribution based on the weights in the recommendation model
    weights = {
        'Skill Match': 0.5,
        'Collaborative Score': 0.3,
        'Career Path Alignment': 0.2
    }
    
    # Calculate weighted contributions
    contributions = {}
    for factor, value in factors.items():
        contributions[factor] = (value * weights[factor]) / sum(weights.values())
    
    if as_dict:
        return {
            'factors': factors,
            'weights': weights,
            'contributions': contributions
        }
    
    # Create visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={'width_ratios': [1, 1.5]})
    
    # Create pie chart for factor weights
    explode = (0.1, 0, 0)  # Explode the skill match slice
    colors = ['#4285F4', '#EA4335', '#FBBC05']
    
    wedges, texts, autotexts = ax1.pie(
        [weights[f] for f in factors.keys()], 
        explode=explode,
        labels=None,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        wedgeprops={'edgecolor': 'w', 'linewidth': 1}
    )
    
    # Customize text properties
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(9)
    
    # Add a legend
    ax1.legend(
        wedges, 
        factors.keys(),
        title="Recommendation Factors",
        loc="center left",
        bbox_to_anchor=(0, 0.5)
    )
    ax1.set_title('How Your Recommendation Was Calculated', fontsize=12)
    
    # Create a horizontal bar chart for the factor values
    factor_bars = ax2.barh(
        list(factors.keys()),
        [factors[f] for f in factors.keys()],
        color=colors,
        height=0.5
    )
    
    # Add value labels to the right of each bar
    for i, v in enumerate(factors.values()):
        ax2.text(v + 1, i, f"{v:.1f}", va='center')
    
    # Add a vertical line to represent thresholds
    ax2.axvline(x=50, color='gray', linestyle='--', alpha=0.5)
    ax2.axvline(x=75, color='gray', linestyle='--', alpha=0.5)
    
    # Add text labels for thresholds
    ax2.text(50, -0.5, 'Good', ha='center', va='top', color='gray')
    ax2.text(75, -0.5, 'Excellent', ha='center', va='top', color='gray')
    
    ax2.set_xlim(0, 110)
    ax2.set_xlabel('Factor Score (0-100)')
    ax2.set_title('Factor Scores for Your Recommendation', fontsize=12)
    
    # Add grid for readability
    ax2.grid(axis='x', linestyle='--', alpha=0.3)
    
    plt.tight_layout()
    
    # Return as base64 string
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    return img_str

def generate_skill_interconnection_chart(skill_graph, central_skill, related_skills=None, depth=1):
    """
    Generate a network visualization showing how skills connect to each other
    
    Args:
        skill_graph: SkillGraph object
        central_skill: The skill to focus on
        related_skills: List of related skills to highlight (optional)
        depth: How many levels of connections to show
        
    Returns:
        Base64 encoded image string
    """
    # This is a placeholder for a more complex visualization
    # In a real implementation, this would use networkx to create a subgraph
    # and visualize connections between skills
    
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.text(0.5, 0.5, "Skill interconnection visualization coming soon", 
            ha='center', va='center', fontsize=14)
    ax.axis('off')
    
    # Return as base64 string
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    return img_str 