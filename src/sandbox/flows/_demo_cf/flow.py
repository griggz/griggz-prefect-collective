import controlflow as cf
from sandbox.flows._demo.flow import take_a_walk

assistant = cf.Agent(
    name="Assistant",
    description="An AI agent that is an expert in creating itineraries for a day out.",
    instructions="""
        Your primary goal is to summarize the weather forecast for the day, suggest a 
        cafe to visit, and find a nearby park to sit and enjoy said coffee.
        """,
)

@cf.flow
def illustrate_my_day():
    itinerary = take_a_walk(
        city="Alexandria, Virginia", near="1655 Mount Eagle Pl, Alexandria, VA 22302"
    )
    where_am_i_going = cf.Task(
        """
            Lets take the itenerary for a day out and write a nice story about it. I want my day
            to feel like a script for a film. Can you also add the details of my and any suggestions 
            for things to do that would add to the experience? The context I'm giving you is the 
            itinerary for the day out. It includes 4 keys, cafe, park, temp_forcast, and rain_forcast. The cafe is 
            the suggested cafe to visit, the park is the nearby park to visit, the temp_forcast is an object that includes 
            details about the temperature for the day, and the rain_forcast is an object that includes details about the potential for 
            rain for the day.
        """,
        context=dict(
            data=itinerary,
        ),
        agents=[assistant],
    )
    where_am_i_going.run()

if __name__ == "__main__":
    illustrate_my_day()
