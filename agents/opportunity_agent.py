def suggest_activities(role):
    """
    Suggests concrete, actionable volunteer activities for a recommended NGO role.
    
    Args:
        role (str): The recommended volunteer role name
        
    Returns:
        dict: Containing a list of 'activities'
    """
    # Mapping of roles to concrete, beginner-friendly tasks
    activities_map = {
        "Education Volunteer": [
            "Tutoring children in English and Mathematics",
            "Organizing interactive weekly story-reading sessions",
            "Assisting teachers with preparing classroom materials"
        ],
        "Fundraising Volunteer": [
            "Drafting templates for donor outreach emails",
            "Managing community crowdfunding campaign updates",
            "Organizing local public donation box collection drives"
        ],
        "Social Media Volunteer": [
            "Designing graphics in Canva for weekly posts",
            "Drafting captions and selecting trending hashtags",
            "Compiling monthly visitor engagement analytics"
        ],
        "Content Creator": [
            "Writing blog posts capturing impact stories",
            "Drafting copy for the monthly supporter newsletter",
            "Writing video scripts for campaigns and reels"
        ],
        "Event Management Volunteer": [
            "Coordinating logistics for weekend donation drives",
            "Managing check-in registrations at workshop events",
            "Directing volunteer groups at community clean-up projects"
        ],
        "Community Outreach Volunteer": [
            "Distributing flyers and organizing door-to-door drives",
            "Conducting local surveys to understand neighborhood needs",
            "Liaising with school coordinators to explain NGO programs"
        ],
        "Technical Volunteer": [
            "Optimizing web layout components on platforms",
            "Writing python scripts to automate report generation",
            "Debugging database schemas and user management forms"
        ]
    }
    
    activities = activities_map.get(role, ["Assisting with general coordination and supporting ground operations"])
    
    return {
        "activities": activities
    }
