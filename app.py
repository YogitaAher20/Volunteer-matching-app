import streamlit as st
import json
import os
import logging

# Import the compiled LangGraph workflow
from workflow.graph import workflow_graph

# Import database persistent client functions
from database.supabase_client import save_volunteer_record, get_volunteer_by_email

logger = logging.getLogger(__name__)

# Set page configuration for a premium feel
st.set_page_config(
    page_title="NayePankh Volunteer Matching System",
    page_icon="🤝",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# The app uses native Streamlit components for all presentation.
# No custom HTML rendering is needed for the recommendation UI.

# Helper to load role descriptions from data/roles.json
def load_role_descriptions():
    path = os.path.join("data", "roles.json")
    try:
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        else:
            st.error(f"Config file not found at: {path}")
            return {}
    except Exception as e:
        st.error(f"Error loading roles description: {e}")
        return {}

def render_previous_recommendation(record):
    if not record:
        return

    st.subheader("Previous Recommendation")
    st.write(f"**Previous Role:** {record.get('recommended_role', 'N/A')}")
    st.write(f"**Previous Match Score:** {record.get('match_score', 'N/A')}%")
    st.write(f"**Previous Reason:** {record.get('reason', 'N/A')}")
    st.write(f"**Generated Date:** {record.get('created_at', 'N/A')}")


def render_workflow_section():
    st.subheader("Workflow")
    st.write("Volunteer Form → Profile Agent → AI Role Agent → Opportunity Agent → Recommendation")


def render_debug_panel(debug_info):
    with st.expander("Debug Info", expanded=False):
        st.json(debug_info)


# App Title & Description
st.title("NayePankh Volunteer Matching System")
st.caption("Empowering youths, transforming lives. Find your perfect role at NayePankh Foundation.")

# Form container
with st.container():
    st.subheader("Volunteer Registration Form")
    
    # Grid layout for personal information
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name", placeholder="Enter your full name")
    with col2:
        email = st.text_input("Email", placeholder="Enter your email address")
        
    # Skills and Interests multi-selects
    skills_options = [
        "Teaching", "Public Speaking", "Content Writing", "Graphic Design", 
        "Social Media", "Video Editing", "Fundraising", "Event Management", 
        "Leadership", "Data Analysis", "Programming", "Photography"
    ]
    skills = st.multiselect(
        "Skills (Select all that apply)",
        options=skills_options,
        placeholder="Choose your skills"
    )
    
    interests_options = [
        "Education", "Fundraising", "Awareness Campaigns", "Content Creation", 
        "Volunteer Coordination", "Event Organization", "Community Outreach", 
        "Technology Projects"
    ]
    interests = st.multiselect(
        "Interests (Select all that apply)",
        options=interests_options,
        placeholder="Choose areas of interest"
    )
    
    # Row for availability and weekly hours
    col3, col4 = st.columns(2)
    with col3:
        availability = st.radio(
            "Availability",
            options=["Weekdays", "Weekends", "Both"],
            index=0,
            horizontal=True
        )
    with col4:
        weekly_hours = st.selectbox(
            "Weekly Hours Commitment",
            options=["1-3", "4-6", "7-10", "10+"],
            index=0
        )
        
    # Previous experience radio
    experience = st.radio(
        "Previous Volunteer Experience?",
        options=["Yes", "No"],
        index=1,
        horizontal=True
    )
    
    # Submit Button
    submit_button = st.button("Find My Best Volunteer Role")

# Handle Submission
if submit_button:
    # Basic validation
    if not name.strip():
        st.error("Please enter your name.")
    elif not email.strip() or "@" not in email:
        st.error("Please enter a valid email address.")
    elif not skills:
        st.error("Please select at least one skill.")
    elif not interests:
        st.error("Please select at least one interest.")
    else:
        # Show helpful configuration warnings without stopping the app.
        gemini_key_present = bool(os.getenv("GEMINI_API_KEY") and os.getenv("GEMINI_API_KEY").strip() and os.getenv("GEMINI_API_KEY") != "your_gemini_api_key_here")
        supabase_ready = bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY") and os.getenv("SUPABASE_URL").strip() and os.getenv("SUPABASE_KEY").strip())
        debug_info = {
            "email": email,
            "gemini_key_present": gemini_key_present,
            "supabase_ready": supabase_ready,
            "execution_path": "workflow-started",
            "raw_gemini_response": None,
            "error": None,
        }

        if not gemini_key_present:
            st.warning("Gemini API key is missing. The app will use the rule-based fallback recommendation.")
            debug_info["error"] = "Gemini API key is missing or placeholder."
        if not supabase_ready:
            st.warning("Supabase configuration is missing. Recommendations will still appear, but saved history will not be available.")
            debug_info["error"] = (debug_info["error"] or "") + " Supabase is not configured."

        # Check database first for a previous recommendation using the email.
        previous_record = None
        try:
            previous_record = get_volunteer_by_email(email)
        except Exception as e:
            st.warning(f"Could not check previous recommendations: {e}")

        render_workflow_section()
        if previous_record:
            render_previous_recommendation(previous_record)

        # Construct the initial state dict matching LangGraph schema
        initial_state = {
            "skills": skills,
            "interests": interests,
            "availability": availability,
            "hours": weekly_hours,
            "profile": {},
            "recommendation": {},
            "activities": []
        }
        
        # Execute the multi-agent pipeline via LangGraph workflow
        try:
            final_state = workflow_graph.invoke(initial_state)
            debug_info["execution_path"] = "workflow-completed"
        except Exception as e:
            debug_info["error"] = str(e)
            debug_info["execution_path"] = "workflow-failed"
            st.error(f"The recommendation workflow could not complete. Please try again later. Details: {e}")
            render_debug_panel(debug_info)
            st.stop()
        
        # Extract variables from final state
        structured_profile = final_state.get("profile", {})
        recommendation = final_state.get("recommendation", {})
        activities = final_state.get("activities", [])
        debug_info["execution_path"] = "role-agent-completed"
        debug_info["recommendation"] = recommendation
        debug_info["activities_count"] = len(activities)
        debug_info["raw_gemini_response"] = recommendation.get("debug", {}).get("raw_response") if isinstance(recommendation.get("debug"), dict) else None
        
        # Load descriptions from roles.json
        descriptions = load_role_descriptions()
        role_desc = descriptions.get(recommendation.get("role"), "No description available for this role.")

        if not recommendation.get("role") or not recommendation.get("match_score"):
            debug_info["error"] = (debug_info["error"] or "") + " Recommendation data is incomplete."
            st.warning("The recommendation response looks incomplete. Showing a fallback result if available.")
        
        # Create columns to display output side-by-side
        col_left, col_right = st.columns([1, 1.2])
        
        with col_left:
            st.subheader("Submitted Profile Details")
            st.write(f"**Name:** {name}")
            st.write(f"**Email:** {email}")
            st.write(f"**Skills:** {', '.join(skills)}")
            st.write(f"**Interests:** {', '.join(interests)}")
            st.write(f"**Availability:** {availability}")
            st.write(f"**Weekly Hours:** {weekly_hours}")
            st.write(f"**Previous Experience:** {experience}")
            
        with col_right:
            st.subheader("Current Recommendation")
            st.metric("Match Score", f"{recommendation.get('match_score', 0)}%")
            st.progress(min(100, max(0, int(recommendation.get('match_score', 0)))))
            st.write(f"**Recommended Role:** {recommendation.get('role', 'N/A')}")
            st.write(f"**Role Description:** {role_desc}")
            st.write(f"**Why This Role?** {recommendation.get('reason', 'N/A')}")
            st.write("**Suggested Volunteer Activities**")
            for activity in activities:
                st.write(f"- {activity}")

        render_debug_panel(debug_info)

        # 4. Save recommendation match results to Supabase (Persistence)
        if supabase_ready:
            try:
                save_volunteer_record(
                    name=name,
                    email=email,
                    skills=skills,
                    interests=interests,
                    recommended_role=recommendation.get("role"),
                    match_score=recommendation.get("match_score"),
                    reason=recommendation.get("reason")
                )
                st.success("Recommendation saved successfully.")
            except Exception as e:
                debug_info["error"] = str(e)
                st.warning(f"Could not save profile details to the database. Recommendation generated locally. Details: {e}")
                render_debug_panel(debug_info)
        else:
            st.info("Database saving is skipped because Supabase is not configured.")
