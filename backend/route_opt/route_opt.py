import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """Haversine formula to calculate distance between two lat/lng coordinates in km."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def nearest_neighbor_tsp(locations, start_coord=None):
    """
    Optimizes a route using Nearest Neighbor algorithm.
    locations: list of dicts with 'id', 'lat', 'lng'
    start_coord: tuple (lat, lng) representing the depot/start point.
    Returns: Ordered list of locations.
    """
    if not locations:
        return []
        
    unvisited = locations.copy()
    route = []
    
    # If no start point provided, just pick the first one
    if start_coord:
        current_node = {'lat': start_coord[0], 'lng': start_coord[1]}
    else:
        current_node = unvisited.pop(0)
        route.append(current_node)
        
    while unvisited:
        nearest = min(unvisited, key=lambda loc: calculate_distance(
            current_node['lat'], current_node['lng'], loc['lat'], loc['lng']))
        route.append(nearest)
        current_node = nearest
        unvisited.remove(nearest)
        
    return route
