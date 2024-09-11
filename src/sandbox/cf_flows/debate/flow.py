"""
This script simulates a debate between AI agents emulating the personas of historical U.S.
Presidents (e.g. Theodore Roosevelt and Richard Nixon). The script creates three agents: two representing
the presidents and one acting as a moderator. The debate focuses on a contemporary issue—cryptocurrency
regulation—posing questions and generating responses that reflect each president's political ideology,
rhetorical style, and historical context.

- **Agent Creation**: The script defines two agents, `opponent_a` and `opponent_b`, representing
two individuals, respectively. Each agent is programmed to emulate the respective
president's views, speech style, and historical perspectives.

- **Moderator Role**: A third agent, the `moderator`, manages the debate,
ensuring that both presidents have the opportunity to express their views and engage in a
respectful and organized manner.

- **Flow Execution**: The `interview` function orchestrates the debate, starting with the moderator
posing a question, followed by responses from each individual, with the latter individual's response 
contrasting with the first response.

The script leverages the `controlflow` library to manage the sequence of tasks, ensuring a
structured and dynamic interaction between the agents.
"""

from core.clients.openai_ import OpenAIClient
import controlflow as cf
from pydantic import BaseModel, field_validator

model = OpenAIClient().chat_open_ai()

president_a = "Theodore Roosevelt"

president_b = "Richard Nixon"


class Response(BaseModel):
    response: str

    @field_validator("response")
    def validate_response(cls, v):
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Response must be a non-empty string.")
        return v


# Create three agents
opponent_a = cf.Agent(
    name=f"{president_a}",
    description=f"An AI agent that emulates the persona of President {president_a}.",
    instructions=f"""
        Your primary goal is to represent President {president_a}'s views and rhetoric accurately, without bias, 
        based on historical records, speeches, biographies, and the political context of their time.
        
        - **Political Ideology**: Prioritize President {president_a}'s known political beliefs and values.
        - **Rhetorical Style**: Emulate President {president_a}'s speaking style.
        - **Historical Context**: Consider the political and social environment during President {president_a}'s
        time in office, including major events.
        - **Famous Quotes/Speeches**: Reference or echo famous quotes or positions from President {president_a}'s 
        speeches".
        - **Core Values**: Emphasize President {president_a}'s core values.
        
        Ensure your responses align with President {president_a}'s perspective, while maintaining the authenticity 
        and integrity of their historical persona.
        """,
)

opponent_b = cf.Agent(
    name=f"{president_b}",
    description=f"An AI agent that emulates the persona of President {president_b}.",
    instructions=f"""
        Your primary goal is to represent President {president_b}'s views and rhetoric accurately, without bias, 
        based on historical records, speeches, biographies, and the political context of their time.
        
        - **Political Ideology**: Prioritize President {president_b}'s known political beliefs and values.
        - **Rhetorical Style**: Emulate President {president_b}'s speaking style.
        - **Historical Context**: Consider the political and social environment during President {president_b}'s 
        time in office, including major events.
        - **Famous Quotes/Speeches**: Reference or echo famous quotes or positions from President {president_b}'s 
        speeches".
        - **Core Values**: Emphasize President {president_b}'s core values.
        
        Ensure your responses align with President {president_b}'s perspective, while maintaining the authenticity 
        and integrity of their historical persona.
        """,
)

moderator = cf.Agent(
    name="Moderator",
    description="An AI agent that acts as moderator between political actors.",
    instructions="""
        Your primary goal is to manage a debate between two politicians running for 
        President of the United States. Your secondary objective is to ensure that both parties 
        debate appropriately and politely and have enough space to both answer the question 
        posed and respond.
        """,
)


@cf.flow
def interview():
    # Moderator poses a question
    question = cf.Task(
        "Pose a question to the two candidates about crypto-curreny regulation.",
        agents=[moderator],
    )

    debater_a = cf.Task(
        "Respond to the question posed by the moderator.",
        context=dict(question=question),
        agents=[opponent_a],
    )

    debater_b = cf.Task(
        """Respond to the question posed by the moderator while also drawing a distinct 
        contrast with the other debater's response.""",
        context=dict(question=question, first_debater_response=debater_a),
        agents=[opponent_b],
    )

    # Execute tasks in sequence
    question.run()
    debater_a.run()
    debater_b.run()


if __name__ == "__main__":
    interview()
