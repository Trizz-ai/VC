"""
Google Maps API integration service
"""

import logging
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

logger = logging.getLogger(__name__)


class GoogleMapsService:
    """Service for Google Maps API integration"""
    
    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        self.base_url = "https://maps.googleapis.com/maps/api"
        self.timeout = 30.0
    
    async def _make_request(
        self,
        endpoint: str,
        params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Make request to Google Maps API"""
        try:
            params["key"] = self.api_key
            url = f"{self.base_url}/{endpoint}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Google Maps API error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error making Google Maps request: {e}")
            return None
    
    async def geocode_address(
        self,
        address: str
    ) -> Optional[Tuple[float, float]]:
        """Geocode address to coordinates"""
        try:
            params = {
                "address": address,
                "region": "us"  # Default to US region
            }
            
            result = await self._make_request("geocode/json", params)
            
            if result and result.get("status") == "OK" and result.get("results"):
                location = result["results"][0]["geometry"]["location"]
                return (location["lat"], location["lng"])
            
            return None
            
        except Exception as e:
            logger.error(f"Error geocoding address: {e}")
            return None
    
    async def reverse_geocode(
        self,
        latitude: float,
        longitude: float
    ) -> Optional[str]:
        """Reverse geocode coordinates to address"""
        try:
            params = {
                "latlng": f"{latitude},{longitude}"
            }
            
            result = await self._make_request("geocode/json", params)
            
            if result and result.get("status") == "OK" and result.get("results"):
                return result["results"][0]["formatted_address"]
            
            return None
            
        except Exception as e:
            logger.error(f"Error reverse geocoding: {e}")
            return None
    
    async def get_place_details(
        self,
        place_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get detailed information about a place"""
        try:
            params = {
                "place_id": place_id,
                "fields": "name,formatted_address,geometry,types,rating,user_ratings_total,price_level"
            }
            
            result = await self._make_request("place/details/json", params)
            
            if result and result.get("status") == "OK":
                return result.get("result")
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting place details: {e}")
            return None
    
    async def search_nearby_places(
        self,
        latitude: float,
        longitude: float,
        radius: int = 1000,
        place_type: str = "establishment"
    ) -> Optional[list]:
        """Search for nearby places"""
        try:
            params = {
                "location": f"{latitude},{longitude}",
                "radius": radius,
                "type": place_type
            }
            
            result = await self._make_request("place/nearbysearch/json", params)
            
            if result and result.get("status") == "OK":
                return result.get("results", [])
            
            return None
            
        except Exception as e:
            logger.error(f"Error searching nearby places: {e}")
            return None
    
    async def get_directions(
        self,
        origin: str,
        destination: str,
        mode: str = "driving"
    ) -> Optional[Dict[str, Any]]:
        """Get directions between two points"""
        try:
            params = {
                "origin": origin,
                "destination": destination,
                "mode": mode,
                "units": "metric"
            }
            
            result = await self._make_request("directions/json", params)
            
            if result and result.get("status") == "OK":
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting directions: {e}")
            return None
    
    async def get_static_map_url(
        self,
        latitude: float,
        longitude: float,
        zoom: int = 15,
        size: str = "400x400",
        map_type: str = "roadmap"
    ) -> str:
        """Generate static map URL"""
        try:
            params = {
                "center": f"{latitude},{longitude}",
                "zoom": zoom,
                "size": size,
                "maptype": map_type,
                "markers": f"color:red|{latitude},{longitude}",
                "key": self.api_key
            }
            
            # Build URL manually for static maps
            param_string = "&".join([f"{k}={v}" for k, v in params.items()])
            return f"https://maps.googleapis.com/maps/api/staticmap?{param_string}"
            
        except Exception as e:
            logger.error(f"Error generating static map URL: {e}")
            return ""
    
    async def get_street_view_url(
        self,
        latitude: float,
        longitude: float,
        heading: int = 0,
        pitch: int = 0,
        fov: int = 90,
        size: str = "400x400"
    ) -> str:
        """Generate Street View URL"""
        try:
            params = {
                "location": f"{latitude},{longitude}",
                "heading": heading,
                "pitch": pitch,
                "fov": fov,
                "size": size,
                "key": self.api_key
            }
            
            # Build URL manually for Street View
            param_string = "&".join([f"{k}={v}" for k, v in params.items()])
            return f"https://maps.googleapis.com/maps/api/streetview?{param_string}"
            
        except Exception as e:
            logger.error(f"Error generating Street View URL: {e}")
            return ""
    
    async def calculate_distance_matrix(
        self,
        origins: list,
        destinations: list,
        mode: str = "driving"
    ) -> Optional[Dict[str, Any]]:
        """Calculate distance matrix between origins and destinations"""
        try:
            params = {
                "origins": "|".join([f"{lat},{lng}" for lat, lng in origins]),
                "destinations": "|".join([f"{lat},{lng}" for lat, lng in destinations]),
                "mode": mode,
                "units": "metric"
            }
            
            result = await self._make_request("distancematrix/json", params)
            
            if result and result.get("status") == "OK":
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating distance matrix: {e}")
            return None
    
    async def get_elevation(
        self,
        latitude: float,
        longitude: float
    ) -> Optional[float]:
        """Get elevation for coordinates"""
        try:
            params = {
                "locations": f"{latitude},{longitude}"
            }
            
            result = await self._make_request("elevation/json", params)
            
            if result and result.get("status") == "OK" and result.get("results"):
                return result["results"][0]["elevation"]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting elevation: {e}")
            return None
    
    async def validate_coordinates(
        self,
        latitude: float,
        longitude: float
    ) -> bool:
        """Validate if coordinates are within valid ranges"""
        try:
            return (
                -90 <= latitude <= 90 and
                -180 <= longitude <= 180
            )
        except Exception as e:
            logger.error(f"Error validating coordinates: {e}")
            return False
    
    async def get_timezone(
        self,
        latitude: float,
        longitude: float,
        timestamp: Optional[datetime] = None
    ) -> Optional[str]:
        """Get timezone for coordinates"""
        try:
            params = {
                "location": f"{latitude},{longitude}"
            }
            
            if timestamp:
                params["timestamp"] = int(timestamp.timestamp())
            
            result = await self._make_request("timezone/json", params)
            
            if result and result.get("status") == "OK":
                return result.get("timeZoneId")
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting timezone: {e}")
            return None
