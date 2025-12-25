"""
Announcements endpoints for the High School Management System API
"""

from fastapi import APIRouter, HTTPException, Query, Body, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel
from backend.config import get_announcements_collection, get_teachers_collection


class AnnouncementUpdateRequest(BaseModel):
    """Request body for updating an announcement"""
    message: Optional[str] = None
    expiration_date: Optional[str] = None
    start_date: Optional[str] = None


router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)


@router.get("", response_model=List[Dict[str, Any]])
@router.get("/", response_model=List[Dict[str, Any]])
def get_announcements(
    active_only: bool = Query(True),
    announcements_collection=Depends(get_announcements_collection)
) -> List[Dict[str, Any]]:
    """
    Get all announcements, optionally filtered to show only active ones

    - active_only: If True, only return announcements that are currently active based on dates
    """
    announcements = []
    current_date = datetime.now().date().isoformat()

    for announcement in announcements_collection.find():
        # Convert ObjectId to string for JSON serialization
        announcement["id"] = str(announcement.pop("_id"))

        if active_only:
            # Check if announcement is active
            start_date = announcement.get("start_date")
            expiration_date = announcement.get("expiration_date")

            # If start_date exists and is in the future, skip
            if start_date and start_date > current_date:
                continue

            # If expiration_date is in the past, skip
            if expiration_date and expiration_date < current_date:
                continue

        announcements.append(announcement)

    return announcements


@router.post("", response_model=Dict[str, Any])
@router.post("/", response_model=Dict[str, Any])
def create_announcement(
    message: str,
    expiration_date: str,
    start_date: Optional[str] = None,
    teacher_username: Optional[str] = Query(None),
    announcements_collection=Depends(get_announcements_collection),
    teachers_collection=Depends(get_teachers_collection)
) -> Dict[str, Any]:
    """Create a new announcement - requires teacher authentication"""
    # Check teacher authentication
    if not teacher_username:
        raise HTTPException(
            status_code=401, detail="Authentication required for this action")

    teacher = teachers_collection.find_one({"_id": teacher_username})
    if not teacher:
        raise HTTPException(
            status_code=401, detail="Invalid teacher credentials")

    # Validate dates
    try:
        exp_date = datetime.fromisoformat(expiration_date).date()
        if start_date:
            st_date = datetime.fromisoformat(start_date).date()
            if st_date > exp_date:
                raise HTTPException(
                    status_code=400,
                    detail="Start date cannot be after expiration date"
                )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD"
        )

    # Create announcement document
    announcement = {
        "message": message,
        "expiration_date": expiration_date
    }

    if start_date:
        announcement["start_date"] = start_date

    # Insert into database
    result = announcements_collection.insert_one(announcement)

    # Fetch the created announcement and convert _id to id
    created = announcements_collection.find_one({"_id": result.inserted_id})
    if created:
        created["id"] = str(created.pop("_id"))
        return created

    raise HTTPException(status_code=500, detail="Failed to create announcement")


@router.put("/{announcement_id}", response_model=Dict[str, Any])
def update_announcement(
    announcement_id: str,
    body: Optional[AnnouncementUpdateRequest] = Body(None),
    message: Optional[str] = Query(None),
    expiration_date: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    teacher_username: Optional[str] = Query(None),
    announcements_collection=Depends(get_announcements_collection),
    teachers_collection=Depends(get_teachers_collection)
) -> Dict[str, Any]:
    """
    Update an existing announcement - requires teacher authentication

    **Partial Update Behavior:**
    This endpoint supports partial updates, allowing you to modify one or more fields
    without affecting the others. Only the fields you provide will be updated.

    **Requirements:**
    - At least one field (message, expiration_date, or start_date) must be provided
    - Omitted or None values mean "don't update that field" (existing value preserved)
    - Empty request body or all None values will return 400 error

    **Input Options:**
    Supports both JSON body and query parameters for flexibility (body takes precedence).

    **Examples:**
    - Update only message: `PUT /announcements/{id}?message=New+text`
    - Update dates: `{"expiration_date": "2025-12-31", "start_date": "2025-12-25"}`
    - Update all fields: Provide all three parameters

    **Date Validation:**
    - Dates must be in YYYY-MM-DD format
    - start_date cannot be after expiration_date
    - Validation considers both new and existing date values
    """
    # Check teacher authentication
    if not teacher_username:
        raise HTTPException(
            status_code=401, detail="Authentication required for this action")

    teacher = teachers_collection.find_one({"_id": teacher_username})
    if not teacher:
        raise HTTPException(
            status_code=401, detail="Invalid teacher credentials")

    # Extract update values from body or query parameters (body takes precedence)
    if body:
        message = body.message if body.message is not None else message
        expiration_date = body.expiration_date if body.expiration_date is not None else expiration_date
        start_date = body.start_date if body.start_date is not None else start_date

    # Validate at least one field is provided
    if all(field is None for field in (message, expiration_date, start_date)):
        raise HTTPException(
            status_code=400,
            detail="At least one field (message, expiration_date, or start_date) must be provided"
        )

    # Get current announcement
    announcement = announcements_collection.find_one({"_id": ObjectId(announcement_id)})
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")

    # Extract non-None values
    final_expiration_date = expiration_date or announcement.get("expiration_date")
    final_start_date = start_date or announcement.get("start_date")

    try:
        exp_date = datetime.fromisoformat(final_expiration_date).date()
        if final_start_date:
            st_date = datetime.fromisoformat(final_start_date).date()
            if st_date > exp_date:
                raise HTTPException(
                    status_code=400,
                    detail="Start date cannot be after expiration date"
                )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD"
        )

    # Build update data dictionary - only include provided (non-None) fields
    update_dict = {}
    if message is not None:
        update_dict["message"] = message
    if expiration_date is not None:
        update_dict["expiration_date"] = expiration_date
    if start_date is not None:
        update_dict["start_date"] = start_date

    update_operations = {"$set": update_dict}

    result = announcements_collection.update_one(
        {"_id": ObjectId(announcement_id)},
        update_operations
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    # Fetch and return updated announcement
    announcement = announcements_collection.find_one({"_id": ObjectId(announcement_id)})
    if announcement:
        announcement["id"] = str(announcement.pop("_id"))
        return announcement

    raise HTTPException(status_code=404, detail="Announcement not found")


@router.delete("/{announcement_id}")
def delete_announcement(
    announcement_id: str,
    teacher_username: Optional[str] = Query(None),
    announcements_collection=Depends(get_announcements_collection),
    teachers_collection=Depends(get_teachers_collection)
) -> Dict[str, str]:
    """Delete an announcement - requires teacher authentication"""
    # Check teacher authentication
    if not teacher_username:
        raise HTTPException(
            status_code=401, detail="Authentication required for this action")

    teacher = teachers_collection.find_one({"_id": teacher_username})
    if not teacher:
        raise HTTPException(
            status_code=401, detail="Invalid teacher credentials")

    # Delete announcement
    result = announcements_collection.delete_one({"_id": ObjectId(announcement_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    return {"message": "Announcement deleted successfully"}
