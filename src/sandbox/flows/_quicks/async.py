from prefect import flow
import asyncio
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class SummaryReportRequestMessage:
    user_id: str
    start_date: str
    end_date: str

@dataclass
class CreatorBackgroundResults:
    total_posts: int
    average_likes: float
    top_post_id: str

async def _get_posts(summary_report: SummaryReportRequestMessage) -> List[Dict]:
    # Simulate fetching posts from a database
    return [
        {"id": "1", "likes": 100},
        {"id": "2", "likes": 200},
        {"id": "3", "likes": 150}
    ]

def _prepare_inputs(future_posts: List[Dict], summary_report: SummaryReportRequestMessage) -> List[Dict]:
    return [{"post": post, "report": summary_report} for post in future_posts]

async def _store_post(input_data: Dict) -> None:
    # Simulate storing a post
    print(f"Stored post {input_data['post']['id']} for report {input_data['report'].user_id}")

@flow(log_prints=True)
async def fetch_posts(summary_report: SummaryReportRequestMessage) -> None:
    future_posts = await _get_posts(summary_report)
    post_inputs = _prepare_inputs(future_posts, summary_report)
    await asyncio.gather(*[_store_post(input_data) for input_data in post_inputs])

def _generate_report(summary_report: SummaryReportRequestMessage) -> CreatorBackgroundResults:
    # Simulate report generation
    return CreatorBackgroundResults(total_posts=3, average_likes=150.0, top_post_id="2")

def _store_report(summary_report: SummaryReportRequestMessage, background_report: CreatorBackgroundResults) -> None:
    # Simulate storing the report
    print(f"Stored report for user {summary_report.user_id}")

@flow(log_prints=True)
async def generate_report(summary_report: SummaryReportRequestMessage) -> CreatorBackgroundResults:
    background_report = _generate_report(summary_report)
    _store_report(summary_report, background_report)
    return background_report

@flow
async def parent_flow(summary_report: SummaryReportRequestMessage):
    fetch_posts_task = await fetch_posts(summary_report)
    generate_report_task = await generate_report(summary_report)


if __name__ == "__main__":
    sample_report = SummaryReportRequestMessage(user_id="user123", start_date="2023-01-01", end_date="2023-12-31")
    asyncio.run(parent_flow(sample_report))
