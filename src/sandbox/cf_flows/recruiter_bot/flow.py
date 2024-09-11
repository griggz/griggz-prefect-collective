import os
from time import sleep

import controlflow as cf
import requests
from get_contributions import fetch_pull_request_files
from prefect import task
from prefect.artifacts import create_markdown_artifact
from pydantic import BaseModel, field_validator


class CommonRoomContact(BaseModel):
    name: str
    email: str
    phone: str
    github: str


class PRFileData(BaseModel):
    repo_owner: str
    repo_name: str
    file_name: str
    base_file: str
    pr_content: str


class Fitness(BaseModel):
    score: int

    @field_validator("score")
    def validate_score(cls, v):
        if v < 1 or v > 10:
            raise ValueError("Score must be between 1 and 10")
        return v


@task
def fetch_job_description() -> str:
    return """Senior Software Engineer (Backend)
Remote, USA

About Prefect:
Prefect provides workflow orchestration for the modern data enterprise. Our remote first company is singularly focused on this vision, and every team member directly contributes to its advancement. Every role solves a problem, and everyone can understand exactly how their work helps achieve our mission.

To that end, we've carefully created a supportive, high-performance culture - the operating system of our company - that empowers our team to do the best work of their careers and achieve their personal and professional aspirations.

We are looking for folks who want to join a remote-first team #LI-Remote to build an equally amazing company and product.

Role Summary:
We are looking for an experienced Senior Backend Engineer to join our team of insatiably curious and passionate engineers who never settle for "good enough".

In this role you will work with the engineering team to build, maintain, and scale our SaaS platform. To succeed in this role, you’ll need to be comfortable with Python, have experience operating data intensive applications at scale, and enjoy engaging with cross-functional teams to understand which technical solution best delivers for our product.

What You’ll Do:
Build, maintain, and scale Prefect’s SaaS platform in collaboration with engineering and cross-functional teams
Optimize Python web applications for performance, reliability, and maintainability
Design and optimize data architecture
Exercise ownership of your work end-to-end, observe it from problem definition through prototyping, development, and deployment to production
Your Qualifications:
5+ years of experience in backend engineering roles, with a focus on web applications and distributed systems
Proficiency in Python, async experience preferred
Prior experience developing and maintaining data intensive applications at scale
3+ years of experience with Postgres and Redis
3+ years of experience with monitoring technologies (Grafana, Datadog, or equivalent)
3+ years of experience with at least one major cloud platform (Azure, AWS, or GCP)
Self-directed - with initiative for identifying problems, tenacity to propose solutions, and communication to keep our team updated of progress and blockers
What You'll Get in Return:
We take care of our team- our benefits are top-notch so that employees can work comfortably from wherever in the world they call home. Check out some of our most exciting benefits offered below.

Remote-first team with flexible-first culture
Equity Stock Options
401(k) with 5% company match (vests immediately!)
Unlimited PTO
Medical, Dental and Vision insurance
Generous Parental Leave
Life Insurance and Disability benefits
$800 remote work stipend for whatever you need to work (food, wellness, equipment etc.)
Opportunity to attend 3-4 in-person offsite gatherings per year
And that is just the start, there's more! For more info check out our top-of-the-line benefits and perks on our careers page.

The U.S. base salary range for this full-time position is $144,000-$193,000. Our salary ranges are determined by role, level, and work location. The range displayed on each job posting reflects the minimum and maximum target for new hire salaries for the position across all US locations and relevant job levels. Your recruiter can share more about the salary range for your preferred location during the hiring process. Please keep in mind that equity is not included in the range provided above and will represent a significant part of your total compensation. Benefits and any bonus or incentive compensation is also not included in the range provided above."""


@task
def call_candidate(new_contact: CommonRoomContact) -> str:
    BLEND_AI_API_KEY = os.getenv("BLEND_AI_API_KEY")
    url = "https://api.bland.ai/v1/calls"

    payload = {
        "phone_number": "",
        "task": f"Inform the candidate (named {new_contact.name}) that Prefect, a company in the data orchestration space, is interested in interviewing them for a job and request some times that they'd be available in the next few days.",
        "summary_prompt": "Summarize the call in a few sentances and then outline the times the candidate is available in the next few days",
    }
    headers = {"authorization": BLEND_AI_API_KEY, "Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.text
    create_markdown_artifact(data)

    return response.json()


@task(retries=5)
def poll_for_call_result(call_data):
    BLEND_AI_API_KEY = os.getenv("BLEND_AI_API_KEY")
    url = f"https://api.bland.ai/v1/calls/{call_data['call_id']}"
    headers = {"authorization": BLEND_AI_API_KEY, "Content-Type": "application/json"}

    while True:
        print("checking for call completion")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        if response_data["completed"]:
            create_markdown_artifact(response_data["summary"])
            print(response_data["summary"])
            return response_data["summary"]
        sleep(20)


@task
def send_call_result_to_sarah(call_result: str) -> None:
    print(call_result)


@cf.flow
def recruiter_bot_5000_flow(new_contact: CommonRoomContact) -> None:
    print(f"Recruiter Bot 5000 is starting for {new_contact.name}")

    # collect recent contributions from GitHub
    contributions = fetch_pull_request_files(new_contact.github)
    print(f"Found {len(contributions)} contributions for {new_contact.name}")

    if not len(contributions):
        raise ValueError("No contributions found for the candidate.")

    # fetch job description
    job_description = fetch_job_description()
    print("Job description discovered on prefect.io")

    # evaluate fitness for role
    evaluate = cf.Task(
        "Given the code contributions and job description, evaluate the code author's fitness for the role on a scale from 1 to 10.",
        context=dict(contributions=contributions, job_description=job_description),
        result_type=Fitness,
    )
    evaluate.run()
    score = evaluate.result.score

    print(f"Evaluation complete. Fitness score: {score}")

    # if fitness is greater than 7, call the candidate and schedule an interview with Sarah Newman
    if score > 7:
        print(f"Fitness score of {score} is greater than 7. Calling candidate.")
        call_information = call_candidate(new_contact)
        call_result = poll_for_call_result(call_information)
        return call_result


if __name__ == "__main__":
    new_contact = CommonRoomContact(

    )
    recruiter_bot_5000_flow(new_contact)
