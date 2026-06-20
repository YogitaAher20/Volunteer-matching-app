# Volunteer Matching System

## Project Overview
This project helps volunteers find the most suitable role at an Educational Foundation. The app collects profile details, analyzes them using a simple multi-agent workflow, and suggests a recommended role along with related activities.

## Tech Stack
- Python
- Streamlit
- LangGraph
- Gemini API
- Supabase
- dotenv

## Architecture Diagram
```text
Volunteer Form
    ↓
Profile Agent
    ↓
AI Role Agent
    ↓
Opportunity Agent
    ↓
Recommendation Output
    ↓
Supabase Storage (optional)
```

## Workflow Diagram
```text
User inputs skills, interests, availability, and weekly hours
    ↓
Profile Agent analyzes the inputs
    ↓
Role Agent recommends the best role
    ↓
Opportunity Agent suggests activities
    ↓
App displays the recommendation and saves the record if possible
```

## Folder Structure
```text
app.py
agents/
  profile_agent.py
  role_agent.py
  opportunity_agent.py
workflow/
  graph.py
database/
  supabase_client.py
utils/
  gemini_client.py
  prompts.py
data/
  roles.json
requirements.txt
.env
```

## Setup Instructions
1. Create a virtual environment.
2. Install dependencies:
   pip install -r requirements.txt
3. Add environment variables to `.env`.
4. Run the app:
   streamlit run app.py

## Environment Variables
```env
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## Deployment Instructions
1. Ensure all dependencies are installed.
2. Set environment variables on the hosting platform.
3. Run the app with Streamlit.
4. Keep `.env` local and never commit it.

## Future Improvements
- Add a simple dashboard for past recommendations
- Improve role matching accuracy
- Add filtering for different volunteer categories

## Sample Test Cases
### Test Case 1
Input: Teaching + Education
Expected Role: Education Volunteer

### Test Case 2
Input: Programming + Technology
Expected Role: Technical Volunteer

### Test Case 3
Input: Graphic Design + Content Creation
Expected Role: Social Media Volunteer
