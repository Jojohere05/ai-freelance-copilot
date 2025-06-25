import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from crewai import Agent, Task, Crew, Process
from utils.load_json import load_all_jobs

# Load environment variables and LLM
load_dotenv()
llm = ChatGroq(
    api_key=os.getenv("Groq_API"),
    model="mixtral-8x7b-32768"
)

# Load jobs (using your function)
jobs = load_all_jobs(r"C:\Users\Jhotika Raja\OneDrive\Documents\GitHub\ai-freelance-copilot\processed")

# Define the summarizer agent with LLM
summarizer = Agent(
    role='Job Summarizer',
    goal='Summarize job descriptions from freelance.com',
    backstory='You are an expert at condensing job postings into concise summaries.',
    llm=llm  # This is crucial!
)

# Define tasks for each job
tasks = []
for i, job in enumerate(jobs):
    title = job.get("title", "")
    desc = job.get("description", "")
    skills = ", ".join(job.get("skills", []))
    budget = f"₹{job.get('budget_min')}–₹{job.get('budget_max')} ({job.get('budget_type')})"
    deadline = f"{job.get('days_remaining', 'N/A')} days left"

    prompt = f"""
Job Details:
🔧 Title: {title}
📋 Description: {desc}
🛠️ Required Skills: {skills}
💰 Budget: {budget}
⏱️ Deadline: {deadline}
"""

    task = Task(
        description=f"Summarize the following job into main deliverables, core technical requirements, and potential red flags:\n{prompt}",
        agent=summarizer,
        expected_output="A summary of the job including main deliverables, core technical requirements, and potential red flags.",
        output_file=f"outputs/job_{i+1}_summary.txt"  # Optional
    )
    tasks.append(task)

# Create and run the crew
crew = Crew(
    agents=[summarizer],
    tasks=tasks,
    process=Process.sequential
)

result = crew.kickoff()
print(result)  # Or use output files for results
