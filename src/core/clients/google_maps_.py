import logging
import os

import googlemaps


class GoogleMapsClient:
    """_summary_"""

    def __init__(self):
        self.client = googlemaps.Client(key=os.getenv("GOOGLE_API_TOKEN"))

    def get_location_from_postal_code(self, postal_code):
        """summary"""
        try:
            geocode_result = self.client.geocode(postal_code)
            if not geocode_result:
                return None
            if len(geocode_result) > 1:
                logging.warning("Multiple Matches Found, Assuming First Match")
            loc = geocode_result[0]["geometry"]["location"]
            return loc["lat"], loc["lng"]
        except Exception as exe:
            logging.error("Error in geocoding: %s", {exe})
            return None

    def get_location_from_string(self, addr):
        """summary"""
        try:
            geocode_result = self.client.geocode(addr)
            if not geocode_result:
                return 0, 0
            if len(geocode_result) > 1:
                logging.warning("Multiple Matches Found, Assuming First Match")
            loc = geocode_result[0]["geometry"]["location"]
            return loc["lat"], loc["lng"]
        except Exception as exe:
            logging.error("Error in geocoding: %s", {exe})
            return 0, 0

    def get_distances(self, endpoints):
        """summary"""
        try:
            origins = [x[0] for x in endpoints]
            destinations = [x[1] for x in endpoints]
            matrix = self.client.distance_matrix(
                origins, destinations, units="imperial"
            )
            output = []
            for i, origin in enumerate(matrix["origin_addresses"]):
                for j, destination in enumerate(matrix["destination_addresses"]):
                    if destination == destinations[i]:
                        distance_meters = matrix["rows"][i]["elements"][j]["distance"][
                            "value"
                        ]
                        output.append(
                            int(distance_meters * 3.28084)
                        )  # Convert meters to feet
            return output
        except Exception as exe:
            logging.error("Error in distance matrix: %s", {exe})
            return []
