import os
import asyncio
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM

# Set API Key (Replace with your actual Gemini API key)

# Load environment variables (optional if using .env)
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Error: GEMINI_API_KEY is missing from the .env file.")

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

# Asynchronous Chat Function
async def chat():
    print("📚 Study Manager is ready! Type 'exit' to quit.")

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break
        
        if not user_input:
            print("⚠️ Please enter a question!")
            continue

        # Determine which task to execute based on user input
        if any(keyword in user_input.lower() for keyword in ["schedule", "plan", "study plan"]):
            # Create study schedule task
            current_task = Task(
                description=f"Create a study schedule based on this request: {user_input}",
                agent=chatbot_agent,
                expected_output="A well-structured study plan."
            )
            
            crew = Crew(
                agents=[chatbot_agent],
                tasks=[current_task]
            )
            
            try:
                response = await crew.kickoff_async()
                print(f"\n📖 Study Plan: {response.raw}\n")
            except Exception as e:
                print(f"⚠️ Error: {e}")
                
        elif any(keyword in user_input.lower() for keyword in ["assignment", "deadline", "due", "task"]):
            # Check assignments task
            current_task = Task(
                description=f"Check for pending assignments and upcoming deadlines based on this request: {user_input}",
                agent=task_manager,
                expected_output="A list of pending assignments."
            )
            
            crew = Crew(
                agents=[task_manager],
                tasks=[current_task]
            )
            
            try:
                response = await crew.kickoff_async()
                print(f"\n✅ Pending Assignments: {response.raw}\n")
            except Exception as e:
                print(f"⚠️ Error: {e}")
                
        elif any(keyword in user_input.lower() for keyword in ["stress", "overwork", "burnout", "overwhelm"]):
            # Stress analysis task
            current_task = Task(
                description=f"Analyze workload and predict stress levels based on this request: {user_input}",
                agent=stress_predictor,
                expected_output="A stress level assessment and recommendations."
            )
            
            crew = Crew(
                agents=[stress_predictor],
                tasks=[current_task]
            )
            
            try:
                response = await crew.kickoff_async()
                print(f"\n⚠️ Stress Analysis: {response.raw}\n")
                
                # If there are signs of high stress, offer schedule adjustment
                if any(word in response.raw.lower() for word in ["high stress", "overworked", "too much"]):
                    adjustment_task = Task(
                        description=f"Suggest schedule adjustments to reduce stress based on: {response.raw}",
                        agent=adaptive_scheduler,
                        expected_output="An optimized study plan with balanced workload."
                    )
                    
                    adjustment_crew = Crew(
                        agents=[adaptive_scheduler],
                        tasks=[adjustment_task]
                    )
                    
                    adjustment_response = await adjustment_crew.kickoff_async()
                    print(f"\n✅ Suggested Adjustments: {adjustment_response.raw}\n")
                    
            except Exception as e:
                print(f"⚠️ Error: {e}")
        
        else:
            # General assistance for other queries
            general_task = Task(
                description=f"Respond to this student query: {user_input}",
                agent=chatbot_agent,
                expected_output="A helpful response to the student's question."
            )
            
            crew = Crew(
                agents=[chatbot_agent],
                tasks=[general_task]
            )
            
            try:
                response = await crew.kickoff_async()
                print(f"\n🤖 Response: {response.raw}\n")
            except Exception as e:
                print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    asyncio.run(chat())