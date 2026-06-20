import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Normalize the base URL so we do not accidentally pass a REST endpoint path.
def normalize_supabase_url(url):
    if not url:
        return ""
    cleaned = url.strip().rstrip("/")
    if cleaned.endswith("/rest/v1"):
        cleaned = cleaned[: -len("/rest/v1")]
    return cleaned

# Check and initialize Supabase variables
supabase_url = normalize_supabase_url(os.getenv("SUPABASE_URL"))
supabase_key = os.getenv("SUPABASE_KEY", "").strip()
is_configured = False
client = None

if supabase_url and supabase_key and supabase_url.startswith("http"):
    if "your_supabase" not in supabase_url and "your_supabase" not in supabase_key:
        try:
            client = create_client(supabase_url, supabase_key)
            is_configured = True
        except Exception:
            is_configured = False

def save_volunteer_record(name, email, skills, interests, recommended_role, match_score, reason):
    """
    Saves volunteer application parameters and matched role results to Supabase.
    
    Args:
        name (str): Volunteer name
        email (str): Volunteer email address
        skills (list): Selected skills
        interests (list): Selected interests
        recommended_role (str): Matched NGO role
        match_score (int): Role matching percentage
        reason (str): Match rationale text
        
    Returns:
        postgrest.APIResponse: Response object from the Supabase client execution
    """
    if not is_configured or client is None:
        raise ValueError("Supabase is not configured. Please supply valid SUPABASE_URL and SUPABASE_KEY in .env.")

    try:
        # Create row object to insert
        row = {
            "name": name,
            "email": email.strip().lower(),
            "skills": skills,
            "interests": interests,
            "recommended_role": recommended_role,
            "match_score": match_score,
            "reason": reason
        }
        
        # Execute postgrest insert on the 'volunteers' table
        response = client.table("volunteers").insert(row).execute()
        return response
    except Exception as e:
        raise RuntimeError(f"Failed to insert record into Supabase: {str(e)}")


def get_volunteer_by_email(email):
    """
    Fetches the most recent volunteer recommendation for a given email.

    Args:
        email (str): Volunteer email address

    Returns:
        dict or None: The most recent matching record, if found.
    """
    if not is_configured or client is None:
        raise ValueError("Supabase is not configured. Please supply valid SUPABASE_URL and SUPABASE_KEY in .env.")

    try:
        normalized_email = email.strip().lower()
        response = client.table("volunteers").select("*").eq("email", normalized_email).limit(1).execute()
        records = response.data if hasattr(response, "data") else []

        if not records:
            return None

        # Sort in Python so the latest record is chosen even if the table schema differs.
        records.sort(
            key=lambda item: item.get("created_at") or "",
            reverse=True
        )
        return records[0]
    except Exception as e:
        raise RuntimeError(f"Failed to fetch volunteer record from Supabase: {str(e)}")
