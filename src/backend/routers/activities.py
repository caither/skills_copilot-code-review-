"""
Endpoints for the High School Management System API
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import RedirectResponse
from typing import Dict, Any, Optional, List
from backend.config import get_activities_collection, get_teachers_collection
import re

router = APIRouter(
    prefix="/activities",
    tags=["activities"]
)


def validate_email(email: str) -> str:
    """
    Validate email format to prevent injection issues.

    Uses a comprehensive regex pattern for RFC 5322 standard email validation.
    While pydantic's EmailStr provides more rigorous validation via email-validator
    library, this approach is performant and handles common cases effectively.

    Pattern breakdown:
    - ^[a-zA-Z0-9._%+-]+ : Valid local part characters
    - @ : Required separator
    - [a-zA-Z0-9.-]+ : Valid domain characters
    - \\. : Required dot before TLD
    - [a-zA-Z]{2,}$ : TLD with minimum 2 letters

    Args:
        email: Email string to validate

    Returns:
        Validated email string

    Raises:
        HTTPException: If email format is invalid
    """
    # Regex pattern for email validation (RFC 5322 simplified)
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise HTTPException(
            status_code=400,
            detail="Invalid email format"
        )
    return email


@router.get("", response_model=Dict[str, Any])
@router.get("/", response_model=Dict[str, Any])
def get_activities(
    day: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    activities_collection=Depends(get_activities_collection)
) -> Dict[str, Any]:
    """
    Get all activities with their details, with optional filtering by day and time

    - day: Filter activities occurring on this day (e.g., 'Monday', 'Tuesday')
    - start_time: Filter activities starting at or after this time (24-hour format, e.g., '14:30')
    - end_time: Filter activities ending at or before this time (24-hour format, e.g., '17:00')
    """
    # Build the query based on provided filters
    query = {}

    if day:
        query["schedule_details.days"] = {"$in": [day]}

    if start_time:
        query["schedule_details.start_time"] = {"$gte": start_time}

    if end_time:
        query["schedule_details.end_time"] = {"$lte": end_time}

    # Query the database
    activities = {}
    for activity in activities_collection.find(query):
        name = activity.pop('_id')
        activities[name] = activity

    return activities


@router.get("/days", response_model=List[str])
def get_available_days(activities_collection=Depends(get_activities_collection)) -> List[str]:
    """Get a list of all days that have activities scheduled"""
    # Aggregate to get unique days across all activities
    pipeline = [
        {"$unwind": "$schedule_details.days"},
        {"$group": {"_id": "$schedule_details.days"}},
        {"$sort": {"_id": 1}}  # Sort days alphabetically
    ]

    days = []
    for day_doc in activities_collection.aggregate(pipeline):
        days.append(day_doc["_id"])

    return days


@router.post("/{activity_name}/signup")
def signup_for_activity(
    activity_name: str,
    email: str,
    teacher_username: Optional[str] = Query(None),
    activities_collection=Depends(get_activities_collection),
    teachers_collection=Depends(get_teachers_collection)
) -> Dict[str, str]:
    """Sign up a student for an activity - requires teacher authentication"""
    # Validate email format
    validated_email = validate_email(email)

    # Check teacher authentication
    if not teacher_username:
        raise HTTPException(
            status_code=401, detail="Authentication required for this action")

    teacher = teachers_collection.find_one({"_id": teacher_username})
    if not teacher:
        raise HTTPException(
            status_code=401, detail="Invalid teacher credentials")

    # Get the activity
    activity = activities_collection.find_one({"_id": activity_name})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Use the validated activity name from database
    validated_activity_name = activity["_id"]

    # Validate student is not already signed up
    if validated_email in activity["participants"]:
        raise HTTPException(
            status_code=400, detail="Already signed up for this activity")

    # Add student to participants
    result = activities_collection.update_one(
        {"_id": validated_activity_name},
        {"$push": {"participants": validated_email}}
    )

    if result.modified_count == 0:
        raise HTTPException(
            status_code=500, detail="Failed to update activity")

    return {"message": f"Successfully signed up {validated_email} for {validated_activity_name}"}


@router.delete("/{activity_name}/signup")
def cancel_signup(
    activity_name: str,
    email: str,
    teacher_username: Optional[str] = Query(None),
    activities_collection=Depends(get_activities_collection),
    teachers_collection=Depends(get_teachers_collection)
) -> Dict[str, str]:
    """Cancel a student's signup for an activity - requires teacher authentication"""
    # Validate email format
    validated_email = validate_email(email)

    # Check teacher authentication
    if not teacher_username:
        raise HTTPException(
            status_code=401, detail="Authentication required for this action")

    teacher = teachers_collection.find_one({"_id": teacher_username})
    if not teacher:
        raise HTTPException(
            status_code=401, detail="Invalid teacher credentials")

    # Get the activity
    activity = activities_collection.find_one({"_id": activity_name})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Use the validated activity name from database
    validated_activity_name = activity["_id"]

    # Validate student is signed up
    if validated_email not in activity["participants"]:
        raise HTTPException(
            status_code=400, detail="Not registered for this activity")

    # Remove student from participants
    result = activities_collection.update_one(
        {"_id": validated_activity_name},
        {"$pull": {"participants": validated_email}}
    )

    if result.modified_count == 0:
        raise HTTPException(
            status_code=500, detail="Failed to update activity")

    return {"message": f"Canceled signup for {validated_email} from {validated_activity_name}"}


@router.post("/{activity_name}/unregister")
def unregister_from_activity(
    activity_name: str,
    email: str,
    teacher_username: Optional[str] = Query(None),
    activities_collection=Depends(get_activities_collection),
    teachers_collection=Depends(get_teachers_collection)
) -> Dict[str, str]:
    """Remove a student from an activity - requires teacher authentication"""
    # Validate email format
    validated_email = validate_email(email)

    # Check teacher authentication
    if not teacher_username:
        raise HTTPException(
            status_code=401, detail="Authentication required for this action")

    teacher = teachers_collection.find_one({"_id": teacher_username})
    if not teacher:
        raise HTTPException(
            status_code=401, detail="Invalid teacher credentials")

    # Get the activity
    activity = activities_collection.find_one({"_id": activity_name})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Use the validated activity name from database
    validated_activity_name = activity["_id"]

    # Validate student is signed up
    if validated_email not in activity["participants"]:
        raise HTTPException(
            status_code=400, detail="Not registered for this activity")

    # Remove student from participants
    result = activities_collection.update_one(
        {"_id": validated_activity_name},
        {"$pull": {"participants": validated_email}}
    )

    if result.modified_count == 0:
        raise HTTPException(
            status_code=500, detail="Failed to update activity")

    return {"message": f"Unregistered {validated_email} from {validated_activity_name}"}
