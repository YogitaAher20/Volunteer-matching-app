def analyze_profile(skills, interests, availability, hours):
    """
    Transforms raw volunteer inputs into structured profiles with mapped strengths.
    
    Args:
        skills (list): List of user skills
        interests (list): List of user interests
        availability (str): General availability (e.g., Weekdays)
        hours (str): Weekly hours commitment
        
    Returns:
        dict: Structured profile with 'strengths', 'interests', and 'availability'
    """
    # Mapping of raw skills to structured strengths
    strengths_map = {
        "teaching": "Education & Instruction",
        "public speaking": "Public Communication",
        "content writing": "Written Communication",
        "graphic design": "Visual Design",
        "social media": "Digital Marketing",
        "video editing": "Video Production",
        "fundraising": "Resource Mobilization",
        "event management": "Operations & Logistics",
        "leadership": "Strategic Management",
        "data analysis": "Research & Analytics",
        "programming": "Software Development",
        "photography": "Visual Media"
    }
    
    strengths = []
    for s in skills:
        mapped = strengths_map.get(s.lower())
        if mapped:
            strengths.append(mapped)
            
    # Fallback strength if none matched
    if not strengths:
        strengths = ["General Assistance"]
        
    return {
        "strengths": strengths,
        "interests": interests,
        "availability": f"{availability} ({hours} hrs/week)"
    }
