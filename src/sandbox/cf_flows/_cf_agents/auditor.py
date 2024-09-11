import controlflow as cf

auditor = cf.Agent(
    name="Auditor",
    description="An AI agent that is an expert in auditing, compliance, and writing reports.",
    instructions="""
        Your primary goal is to validate the data, generate an audit report, and ensure that the data
        is compliant with the governance standards. You will be working with the data provided to you,
        and you will need to validate it, generate a report one paragraph long. 
        """,
)

@cf.flow
def audit_and_report(data, flow_run_context):

    written_report = cf.Task(
        """
            Lets take the data and write a compliance report. I want the report to be a paragraph long and
            include the details of the data and the flow run status. The context I'm giving you is output of a 
            prefect flow and data. 
        """,
        context=dict(
            data=data,
            flow_run=flow_run_context,
        ),
        agents=[auditor],
    )
    written_report.run()

    return written_report

if __name__ == "__main__":
    audit_and_report(data=None, flow_run_context=None)
