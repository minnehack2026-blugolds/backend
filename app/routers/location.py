from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Dict
from app.core.db import get_db
from app.services.location_service import get_schools_in_radius

router = APIRouter(prefix="/api/location", tags=["location"])

class SetLocationRequest(BaseModel):
    latitude: float
    longitude: float
    radius_miles: float = 5.0

class UpdateRadiusRequest(BaseModel):
    radius_miles: float

@router.post("/set")
async def set_location(
    request: SetLocationRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """Set user's location and find nearby schools"""
    nearby_schools = await get_schools_in_radius(
        request.latitude,
        request.longitude,
        request.radius_miles,
        db
    )
    
    if not nearby_schools:
        raise HTTPException(
            status_code=404, 
            detail=f"No universities found within {request.radius_miles} miles"
        )
    
    # Store in cookie
    school_ids = [str(school['id']) for school in nearby_schools]
    response.set_cookie(
        key="user_location",
        value=f"{request.latitude}|{request.longitude}|{request.radius_miles}|{','.join(school_ids)}",
        max_age=60*60*24*7,  # 7 days
        httponly=True,
        samesite="lax"
    )
    
    return {
        "message": f"Found {len(nearby_schools)} universities within {request.radius_miles} miles",
        "schools": nearby_schools
    }

@router.get("/schools")
async def get_user_schools(request: Request):
    """Get user's accessible schools from cookie"""
    location_cookie = request.cookies.get("user_location")
    
    if not location_cookie:
        raise HTTPException(
            status_code=404,
            detail="Location not set. Please set your location first."
        )
    
    parts = location_cookie.split("|")
    lat, lng, radius, school_ids_str = parts
    school_ids = [int(id) for id in school_ids_str.split(",")]
    
    return {
        "latitude": float(lat),
        "longitude": float(lng),
        "radius_miles": float(radius),
        "school_ids": school_ids
    }

@router.put("/radius")
async def update_radius(
    request: UpdateRadiusRequest,
    req: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """Update search radius"""
    location_cookie = req.cookies.get("user_location")
    
    if not location_cookie:
        raise HTTPException(
            status_code=404,
            detail="Location not set. Please set your location first."
        )
    
    parts = location_cookie.split("|")
    lat, lng = float(parts[0]), float(parts[1])
    
    nearby_schools = await get_schools_in_radius(
        lat, lng, request.radius_miles, db
    )
    
    if not nearby_schools:
        raise HTTPException(
            status_code=404,
            detail=f"No universities found within {request.radius_miles} miles"
        )
    
    school_ids = [str(school['id']) for school in nearby_schools]
    response.set_cookie(
        key="user_location",
        value=f"{lat}|{lng}|{request.radius_miles}|{','.join(school_ids)}",
        max_age=60*60*24*7,
        httponly=True,
        samesite="lax"
    )
    
    return {
        "message": f"Updated radius to {request.radius_miles} miles",
        "schools": nearby_schools
    }