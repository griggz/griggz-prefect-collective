from typing import List
import httpx
from datetime import timedelta
from prefect import task, flow
from prefect.runtime import flow_run
from prefect.cache_policies import TASK_SOURCE

import math
from sandbox.flows.suggest_cafe.flow import navigate_cafes
from sandbox.flows.suggest_park.flow import find_a_park


def name_flow():
    name = None
    base_name = "take a walk"
    params = flow_run.parameters

    city = params["city"]

    if city is not None:
        name = f"{base_name} in {city}"
    else:
        name = base_name

    return name


def deliver_lat_long(location: dict) -> dict[str, float]:
    lat = location["lat"]
    lng = location["lng"]
    return lat, lng


def haversine(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))

    # Radius of Earth in miles
    r = 3956
    return c * r


@task(retries=1, cache_policy=TASK_SOURCE, cache_expiration=timedelta(minutes=2))
def check_temperature(lat: float, lon: float):
    good_weather = False
    base_url = "https://api.open-meteo.com/v1/forecast/"
    temps = httpx.get(
        base_url,
        params=dict(
            latitude=lat,
            longitude=lon,
            hourly="temperature_2m",
            temperature_unit="fahrenheit",
        ),
    )

    forecasted_temp = float(temps.json()["hourly"]["temperature_2m"][0])
    print(f"Forecasted temp F: {forecasted_temp} degrees")

    if forecasted_temp > 50 and forecasted_temp < 85:
        print("Good weather for a walk!")
        good_weather = True

    return good_weather, temps


@task(retries=1, cache_policy=TASK_SOURCE, cache_expiration=timedelta(minutes=2))
def check_for_rain(lat: float, lon: float) -> bool:
    no_rain = False
    base_url = "https://api.open-meteo.com/v1/forecast/"
    showers = httpx.get(
        base_url,
        params=dict(latitude=lat, longitude=lon, hourly="showers"),
    )
    forcasted_rain = float(showers.json()["hourly"]["showers"][0])

    if forcasted_rain <= 0.1:
        print("No rain in the forecast!")
        no_rain = True

    return no_rain, showers


def how_far(cafe, park):
    # Example usage:
    lat1, lng1 = deliver_lat_long(cafe["geometry"]["location"])
    lat2, lng2 = deliver_lat_long(park["geometry"]["location"])
    distance_miles = haversine(lat1, lng1, lat2, lng2)

    print(f"{park["name"]} is about {distance_miles:.2f} miles from {cafe["name"]}.")

    return distance_miles


@flow(flow_run_name=name_flow, log_prints=True)
def take_a_walk(city: str, near: str):
    # Get the suggested cafe
    cafe = navigate_cafes([city])

    if cafe:
        lat, lon = deliver_lat_long(cafe["geometry"]["location"])
        good_weather, temp_forcast = check_temperature(lat, lon)
        no_rain, rain_forcast = check_for_rain(lat, lon)
        if good_weather and no_rain:
            while True:
                nearby_park = find_a_park(city, near)
                distance = how_far(cafe, nearby_park)
                if distance < 1.5:
                    print(f"Great! {cafe["name"]} is close to {nearby_park["name"]}.")
                    break
                else:
                    print("Eh, that park is too far. Let's try again.")

            return {
                "city": city,
                "near": near,
                "cafe": cafe,
                "park": nearby_park,
                "temp_forcast": temp_forcast,
                "rain_forcast": rain_forcast,
            }


if __name__ == "__main__":
    results = take_a_walk(
        "Alexandria, VA", "Shirlington"
    )
