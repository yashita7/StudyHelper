import os
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Error: GEMINI_API_KEY is missing from the .env file.")

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM with Gemini
llm = LLM(model="gemini/gemini-1.5-pro", api_key=api_key, verbose=True)

# Define AI Agents
chatbot_agent = Agent(
    name="Study Assistant",
    role="Conversational AI",
    goal="Assist students with study planning, scheduling, and stress management.",
    backstory="An AI assistant dedicated to helping students organize their studies and maintain productivity.",
    llm=llm,
    memory=True,
    verbose=True
)

task_manager = Agent(
    name="Task Manager",
    role="Task & Assignment Tracker",
    goal="Monitor assignments, deadlines, and tasks.",
    backstory="Keeps students updated on their upcoming tasks and pending assignments.",
    llm=llm
)

stress_predictor = Agent(
    name="Stress Predictor",
    role="Workload & Stress Analyzer",
    goal="Analyze student workload and predict stress levels.",
    backstory="Monitors study schedules and predicts potential stress levels to prevent burnout.",
    llm=llm
)

adaptive_scheduler = Agent(
    name="Adaptive Scheduler",
    role="Smart Study Planner",
    goal="Modify study plans based on workload and stress levels.",
    backstory="Ensures students stay on track without overwhelming themselves.",
    llm=llm
)

# Request model
class ChatRequest(BaseModel):
    message: str

# API endpoint for chat requests
@app.post("/chat")
async def chat(request: ChatRequest):
    user_input = request.message.lower()

    if any(keyword in user_input for keyword in ["schedule", "plan", "study plan"]):
        agent = chatbot_agent
        description = f"Create a study schedule based on this request: {request.message}"
        expected_output = "A well-structured study plan."
    elif any(keyword in user_input for keyword in ["assignment", "deadline", "due", "task"]):
        agent = task_manager
        description = f"Check for pending assignments based on this request: {request.message}"
        expected_output = "A list of pending assignments."
    elif any(keyword in user_input for keyword in ["stress", "overwork", "burnout", "overwhelm"]):
        agent = stress_predictor
        description = f"Analyze workload and predict stress levels based on this request: {request.message}"
        expected_output = "A stress level assessment."
    else:
        agent = chatbot_agent
        description = f"Respond to this student query: {request.message}"
        expected_output = "A helpful response."

    # Create a task for the agent
    current_task = Task(description=description, agent=agent, expected_output=expected_output)
    crew = Crew(agents=[agent], tasks=[current_task])

    try:
        response = await asyncio.create_task(crew.kickoff_async())
        return {"response": response.raw}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
