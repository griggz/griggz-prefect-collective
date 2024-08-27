import httpx
from prefect import task, flow


@task
def fetch_weather(lat: float = 38.9, lon: float = -77.0):
    base_url = "https://api.open-meteo.com/v1/forecast/"
    temps = httpx.get(
        base_url,
        params=dict(latitude=lat, longitude=lon, hourly="temperature_2m"),
    )
    forecasted_temp = float(temps.json()["hourly"]["temperature_2m"][0])
    print(f"Forecasted temp C: {forecasted_temp} degrees")
    return forecasted_temp


@flow
def weather_getter():
    temp = fetch_weather()

    return temp


if __name__ == "__main__":
    weather_getter.serve(name="checking for weather", tags=["101"])
