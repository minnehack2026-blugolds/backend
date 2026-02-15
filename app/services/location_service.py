from geopy.distance import geodesic
from typing import List, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Returns distance in miles between two coordinates"""
    point1 = (lat1, lng1)
    point2 = (lat2, lng2)
    return geodesic(point1, point2).miles

async def get_schools_in_radius(
    user_lat: float, 
    user_lng: float, 
    radius_miles: float,
    db: AsyncSession
) -> List[Dict]:
    """
    Get all universities within radius of user's location
    Returns list of dicts with school info and distance
    """
    from app.models.university import University
    
    # Query all universities using async SQLAlchemy
    result = await db.execute(select(University))
    schools = result.scalars().all()
    
    nearby_schools = []
    for school in schools:
        if school.latitude and school.longitude:
            distance = calculate_distance(
                user_lat, user_lng, 
                float(school.latitude), float(school.longitude)
            )
            if distance <= radius_miles:
                nearby_schools.append({
                    'id': school.id,
                    'name': school.name,
                    'distance': round(distance, 2),
                    'latitude': float(school.latitude),
                    'longitude': float(school.longitude)
                })
    
    # Sort by distance
    nearby_schools.sort(key=lambda x: x['distance'])
    return nearby_schools