import random
from pydantic import BaseModel, field_validator
from typing import List, Optional
from sandbox.flows.account_analysis.models import Opportunity, Account
import controlflow as cf
from datetime import timedelta
from prefect import task, flow
from prefect.cache_policies import INPUTS
from core.clients.notion_ import NotionClient

# from prefect.artifacts import create_markdown_artifact
from core.clients.salesforce_ import SalesforceClient

analyst = cf.Agent(
    name="Analyst",
    description="An AI agent that is an expert in conducting thorough account analyses.",
    instructions="""
        Your primary goal is to provide a comprehensive and detailed analysis of accounts. This includes
        identifying key players, understanding their use cases, exploring expansion opportunities, 
        and summarizing recent interactions. Additionally, you should highlight any gaps in knowledge 
        that should be addressed.

        Key areas to focus on:
        1. **Key Players**: Identify the main contacts and decision-makers within the account. 
        Determine their roles, influence, and any relationships they may have with our organization.
        2. **Use Cases**: Understand how the account currently uses our products or services. 
        Highlight any specific pain points or goals they aim to achieve through our offerings.
        3. **Expansion Opportunities**: Analyze potential upsell and cross-sell opportunities. 
        Consider long-term partnership potential and any areas where our solutions could further 
        support the account.
        4. **Recent Interactions**: Summarize the latest communications and engagements with the 
        account. Note any requests, issues raised, or feedback provided by the client.
        5. **Knowledge Gaps**: Identify what information we still need to gather about the account. 
        Recommend steps for filling these gaps to better serve the client and enhance our relationship.

        Provide your analysis in a clear and structured narrative in markdown format, focusing on 
        thoroughness and actionable insights. The report will be further refined by a Writer for style 
        and clarity, and reviewed by an Editor for final approval.
        """,
)


writer = cf.Agent(
    name="Writer",
    description="""An AI agent that focuses on refining and enhancing account analyses, 
    ensuring clarity, cohesion, and adherence to writing best practices.""",
    instructions="""
        Your primary goal is to take the account analysis provided by the Analyst and craft it into a 
        well-written, coherent, and polished report. Ensure that the narrative flows smoothly and that 
        all sections are clearly articulated.

        Specifically, you should:

        1. **Enhance Clarity**: Ensure that each section of the analysis is clearly written, with a 
        focus on making the content easily understandable. Rewrite any parts that are unclear or 
        overly complex.
        2. **Improve Cohesion**: Make sure that the report reads as a cohesive whole. Connect ideas 
        between sections, ensuring a logical flow from one point to the next.
        3. **Refine Language**: Focus on refining the language to ensure it's professional, concise, 
        and free of grammatical errors. Enhance word choice where necessary to make the report more 
        impactful.
        4. **Structure and Format**: Verify that the report is well-structured, with appropriate 
        headings, bullet points, and other formatting elements that improve readability. Ensure 
        consistency in style and tone throughout the document.
        5. **Summary Analysis**: Craft the "Summary Analysis" section, summarizing the key takeaways 
        and providing a concise overview of the most critical points in a compelling manner.

        Your task is to transform the initial analysis into a polished document that is ready for 
        presentation to stakeholders. Provide suggestions for any further improvements that can 
        elevate the quality of the report.
        """,
)

staff_editor = cf.Agent(
    name="Staff Editor",
    description="""An AI agent that reviews the account analysis to confirm its accuracy, 
    completeness, while also ensuring the writing is polished and well-structured. 
    As the editor you have full access to make changes where necessary.""",
    instructions="""
        Your primary goal is to review the account analysis produced by the Analyst and refined by 
        the Writer. Ensure that the report adheres to all the provided guidelines and instructions, 
        and that the writing is clear, cohesive, and professional. Make enhancement edits where necessary and 
        ensure that the markdown report adheres to Notion's markdown requirements, as the final result will 
        be uploaded to notion. Here is a cheat sheet for reference: https://cheatsheets.namaraii.com/notion.html. 

        Specifically, confirm the following:

        - Writing Quality: Assess the overall quality of the writing. Ensure that the report is 
        clear, cohesive, free of grammatical errors, and that the language is professional and polished.
        - Structure and Formatting: Confirm that the report is well-structured with appropriate 
        headings, bullet points, and consistent formatting throughout. The document should be easy to 
        read and navigate.

        Make changes to the report in areas that need improvement, whether they relate to content, 
        writing, or formatting. Your review and edits should ensure that the final report is comprehensive,
        accurate, and ready for presentation to it's audience (sales engineers).
        """,
)

chief_editor = cf.Agent(
    name="Cheif Editor",
    description="""An AI agent that reviews the edited report to confirm its accuracy, 
    completeness, and adherence to specified guidelines.""",
    instructions="""
        Your primary goal is to approve whether or not the edited report contains specific sections.

        Specifically, confirm the following:

        1. Key Players: Verify that the analysis correctly identifies the main contacts and 
        decision-makers within the account, including their roles, influence, and relationships 
        with our organization.
        2. Use Cases: Ensure that the report accurately describes how the account uses our 
        products or services, highlights specific pain points, and outlines the goals the account 
        aims to achieve.
        3. Expansion Opportunities: Check that the analysis thoroughly explores potential upsell 
        and cross-sell opportunities, considers long-term partnership potential, and identifies areas 
        where our solutions could further support the account.
        4. Recent Interactions: Confirm that the report includes a summary of the latest 
        communications and engagements with the account, noting any requests, issues raised, or 
        feedback provided by the client.
        5. Knowledge Gaps: Ensure that the analysis identifies any missing information about the 
        account and recommends steps for gathering this information to better serve the client.
        6. Summary Analysis: Review the final "Summary Analysis" section to ensure it provides key 
        takeaways and context in a concise and compelling manner.

        """,
)


class Context(BaseModel):
    account: Account
    opportunity: Optional[Opportunity] = None


class ResultType(BaseModel):
    success: bool

    @field_validator("success")
    def validate_success(cls, v):
        if not isinstance(v, bool):
            raise ValueError("Result must be a boolean value (True or False).")
        return v


@task
def fetch_opportunity(AccountId: str) -> List[Opportunity]:
    opportunity = None
    sf_ = SalesforceClient()
    opportunity_metadata = sf_.Opportunity.describe()
    field_names = [field["name"] for field in opportunity_metadata["fields"]]
    query = f"SELECT {', '.join(field_names)} FROM Opportunity WHERE AccountId = '{AccountId}'"
    opportunities = sf_.query_all(query).get("records", "")
    if len(opportunities):
        opportunity = opportunities[0]
        print(f"{opportunity["Name"]} opportunity fetched.")

    return opportunity


@task(cache_policy=INPUTS, cache_expiration=timedelta)
def fetch_accounts():
    sf_ = SalesforceClient()
    account_metadata = sf_.Account.describe()
    field_names = [field["name"] for field in account_metadata["fields"]]
    query = f"SELECT {', '.join(field_names)} FROM Account"
    accounts = sf_.query_all(query).get("records", "")
    print(f"Found {len(accounts)} accounts.")

    return accounts


@task
def fetch_account(Name: str):
    account = None
    sf_ = SalesforceClient()
    account_metadata = sf_.Account.describe()
    field_names = [field["name"] for field in account_metadata["fields"]]
    query = f"SELECT {', '.join(field_names)} FROM Account WHERE Name = '{Name}'"
    accounts = sf_.query(query).get("records", "")
    if len(accounts):
        account = accounts[0]
        print(f"{account["Name"]} account fetched.")

    return account


@task
def select_random_account(accounts: List[Account]) -> Optional[Account]:
    account = random.choice(accounts)

    print(f"{account["Name"]} account randomly selected.")

    return account


@task
def upload_report_to_notion(report: str, report_name: str):
    notion_ = NotionClient()
    response = notion_.create_page("ec700574c0c14876b80260a32f13d1c9", report_name, report)
    print(f"Page created {response.get('url')}")
    return response


@cf.flow
def analyze_accounts(account_name: Optional[str] = None) -> None:
    account = None
    if not account_name:
        accounts = fetch_accounts()
        account = select_random_account(accounts)
    else:
        account = fetch_account(account_name)

    if account:
        opportunity = fetch_opportunity(account["Id"])

    if not account:
        raise ValueError("No accounts found")

    approved = False

    while not approved:
        analysis = cf.Task(
            f"""
                You are provided with data from Salesforce for the account: {account['Name']}.
                Using this data, along with any available opportunity information, write a 
                draft detailed sales summary.
                Ensure the summary is comprehensive, covering key players, use cases, 
                expansion opportunities, recent interactions, and knowledge gaps as per the 
                provided guidelines.
            """,
            context=dict(data={"account": account, "opportunity": opportunity}),
            agents=[analyst],
        )

        # # Write the report
        write_report = cf.Task(
            """Take the preliminary analysis and craft a polished, well-structured 
            account report.""",
            agents=[writer],
            context=dict(
                analysis=analysis, data={"account": account, "opportunity": opportunity}
            ),
        )

        edit_report = cf.Task(
            """
                Review the polished report crafted by the Writer and reference the underlying data. Ensure that it adheres to all 
                guidelines and instructions, including the identification of key players, use cases, 
                expansion opportunities, recent interactions, and knowledge gaps are present. If not, add them. 

                Additionally, assess the overall writing quality, structure, formatting, data availability. Confirm that 
                the report is clear, cohesive, professional, error-free and contains all necessary data. You have full power to make the necessary
                changes to enhance this report. 

                And finally, please ensure the report adheres to Notion's markdown requirements as illustrated here: 
                https://cheatsheets.namaraii.com/notion.html. This report will ultimately be uploaded to notion. 
            """,
            context=dict(
                draft_report=write_report,
                data={"account": account, "opportunity": opportunity},
            ),
            agents=[staff_editor],
        )

        approve = cf.Task(
            """
                "What do think? Do you approve?",
            """,
            result_type=ResultType,
            context=dict(edit_report),
            agents=[chief_editor],
        )

        analysis.run()

        write_report.run()

        report = edit_report.run()

        confirm = approve.run()

        approved = confirm.success

    if approved:
        upload_report_to_notion(
            report=report, report_name=f"{account["Name"]} Account Analysis"
        )

    return report


if __name__ == "__main__":
    report = analyze_accounts(account_name="Two Sigma")
