import os
import random
import requests
from prefect import flow, task
from prefect.runtime import flow_run
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# List of some major cities in Western Europe
CITIES = [
    "Paris, France",
    "Berlin, Germany",
    "Amsterdam, Netherlands",
    "Madrid, Spain",
    "Lisbon, Portugal",
    "Vienna, Austria",
    "Brussels, Belgium",
    "Zurich, Switzerland",
    "Copenhagen, Denmark",
    "Dublin, Ireland",
]


def name_flow():
    name = None
    base_name = "checking for cafes"
    params = flow_run.parameters

    city = params["where"][0]

    if city is not None:
        name = f"{base_name} in {city}"
    else:
        name = base_name

    return name


# Task to pick a random city
@task(log_prints=True, name="Pick a city")
def pick_random_city(city):
    pick = None
    if not city:
        pick = random.choice(CITIES)
    else:
        pick = city[0]

    return pick


# Task to fetch cafes in the city using Google Places API
@task(log_prints=True, name="Fetch Cafes")
def fetch_cafes(city, api_key):
    search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": f"cafes in {city}", "key": api_key}
    response = requests.get(search_url, params=params)
    data = response.json()

    return data["results"]


# Task to pick a random cafe
@task(log_prints=True, name="Pick a cafe")
def pick_random_cafe(cafes):
    cafe = random.choice(cafes)

    return cafe


# Task to print details of the chosen cafe
@task(log_prints=True, name="Print the cafe")
def print_cafe_details(cafe):
    name = cafe["name"]
    address = cafe["formatted_address"]
    rating = cafe.get("rating", "N/A")
    print(f"Randomly selected cafe in {cafe['formatted_address']}:\n")
    print(f"Name: {name}")
    print(f"Address: {address}")
    print(f"Rating: {rating}")


# Define the flow
@flow(log_prints=True, flow_run_name=name_flow)
def navigate_cafes(where=["berlin, germany"]):
    api_key = os.getenv("PLACES_API_KEY")
    city = pick_random_city(where)
    cafes = fetch_cafes(city, api_key)
    selected_cafe = pick_random_cafe(cafes)
    print_cafe_details(selected_cafe)


# Run the flow
if __name__ == "__main__":
    navigate_cafes.serve(
        name="checking for cafes",
        tags=["onboarding"],
        parameters={"where": ["paris, france"]},
    )
