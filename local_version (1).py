import os
import asyncio
import csv
import json
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from pydantic import BaseModel
from browser_use import Agent, BrowserConfig, Controller
from browser_use.browser.browser import Browser
from browser_use.browser.context import BrowserContextConfig
from browser_use.agent.views import AgentHistoryList
from typing import List
# change port number by running "set OLLAMA_HOST=127.0.0.1:1111"
# Load environment variables
load_dotenv()

# Disable telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "false"
# Set OLLAMA host
os.environ["OLLAMA_HOST"] = "http://127.0.0.1:1111"

# Fetch portal credentials from environment variables
PORTAL_USERNAME = os.getenv('PORTAL_USERNAME')
PORTAL_PASSWORD = os.getenv('PORTAL_PASSWORD')
PORTAL_TERM = os.getenv("SELECTED_TERM")


async def run_search() -> AgentHistoryList:
    llm = ChatOllama(model="Mistral:latest", num_ctx=22000)

    browser = Browser(
        config=BrowserConfig(
            new_context_config=BrowserContextConfig(
                viewport_expansion=0,
            )
        )
    )

    class Course(BaseModel):
        course_code: str
        course_name: str
        credits: int
        instructor: str
        room: str
        days: str
        start_time: str
        end_time: str
        max_enroll: str
        total_enroll: str

    class Courses(BaseModel):
        courses: List[Course]

    controller = Controller(output_model=Courses)

    agent = Agent(
        task=f'''
        1.Go to 'https://cudportal.cud.ac.ae/student/login.asp' 
        2.Find the username field and type the username.
        3.Find the password field and type the password.
        4.Find the "Term:" field and select {PORTAL_TERM}. then verify if the correct Term: is selected which is {PORTAL_TERM}
        5.Click the login button. Wait for the page to load after login.
        6. Click exactly on "Course Offering" 
        7. Click "Show Filter"
        8. Click "Divisions:" go through the list and select "SEAST"
        9.Wait 5 seconds
        **BEGIN EXTRACTION**
        10.***TURN INTO JSON FORMAT**  ONLY extract Course data of each page until page FINAL page in JSON format with fields of 'course_code', 'course_name', 'credits', 'instructor', 'room', 'days', 'start_time', 'end_time', 'max_enroll', 'total_enroll', only output in JSON format
        ''',
        llm=llm,
        browser=browser,
        controller=controller,
        sensitive_data={"username": PORTAL_USERNAME, "password": PORTAL_PASSWORD},
        use_vision=False,
        max_failures=2,
    )

    result = await agent.run()

    print("---------------------------------------------------------------------------------------------------------------------------------------------------")
    print(result.final_result())  # Logging final agent result

    # Parse the JSON result
    agent_output = result.final_result()
    dict_data = json.loads(agent_output)

    await browser.close()

    # Write course data to CSV
    with open("course_data.csv", "w", newline="") as file:
        field_names = ['course_code', 'course_name', 'credits', 'instructor', 'room',
                       'days', 'start_time', 'end_time', 'max_enroll', 'total_enroll']
        writer = csv.DictWriter(file, fieldnames=field_names)
        writer.writeheader()
        for row in dict_data["courses"]:
            writer.writerow(row)

    return result


async def main():
    result = await run_search()
    print("\n\nFinal extracted result:\n", result)


if __name__ == "__main__":
    asyncio.run(main())
