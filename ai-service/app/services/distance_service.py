import math
from typing import Tuple

class DistanceService:
    @staticmethod
    def haversine_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees [longitude, latitude])
        Returns distance in kilometers.
        """
        lon1, lat1 = coord1
        lon2, lat2 = coord2
        
        # Convert decimal degrees to radians 
        lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

        # Haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a)) 
        r = 6371 # Radius of earth in kilometers
        
        return c * r

    @staticmethod
    def estimate_arrival_time(distance_km: float) -> int:
        """
        Rough estimate of arrival time based on distance (assuming ~30 km/h average speed in city + 5 mins buffer)
        """
        speed_kmh = 30.0
        time_hours = distance_km / speed_kmh
        time_mins = int(time_hours * 60) + 5
        return time_mins
