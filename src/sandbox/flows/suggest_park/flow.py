import os
import random
import requests
from prefect import flow, task
from prefect.runtime import flow_run
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def name_flow():
    name = None
    base_name = "checking for parks"
    params = flow_run.parameters

    city = params["city"]

    if city is not None:
        name = f"{base_name} in {city} near {params['stop']}"
    else:
        name = base_name

    return name


# Task to fetch cafes in the city using Google Places API
@task(name="Fetch Parks")
def fetch_parks(city, stop, api_key):
    search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": f"parks in {city} near {stop}", "key": api_key}
    response = requests.get(search_url, params=params)
    data = response.json()

    return data["results"]


# Task to pick a random cafe
@task(name="Pick a cafe")
def pick_random_parks(cafes):
    cafe = random.choice(cafes)

    return cafe


# Task to print details of the chosen cafe
@task(name="Print the cafe")
def print_park_details(park):
    name = park["name"]
    address = park["formatted_address"]
    rating = park.get("rating", "N/A")
    print(f"Randomly selected park in {park['formatted_address']}:\n")
    print(f"Name: {name}")
    print(f"Address: {address}")
    print(f"Rating: {rating}")


# Define the flow
@flow(log_prints=True, flow_run_name=name_flow)
def find_a_park(city: str, stop: str):
    if city:
        api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        parks = fetch_parks(city, stop, api_key)
        selected_cafe = pick_random_parks(parks)
        print_park_details(selected_cafe)
        return selected_cafe


# Run the flow
if __name__ == "__main__":
    find_a_park.serve(
        name="checking for cafes",
        tags=["onboarding"],
        parameters={"city": "paris, france", "stop": "eiffel tower"},
    )
