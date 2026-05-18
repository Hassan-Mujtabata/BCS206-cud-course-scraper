import asyncio
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr, BaseModel
from browser_use import Agent, BrowserConfig, Controller
from browser_use.browser.browser import Browser
from browser_use.browser.context import BrowserContextConfig
from typing import List
import csv
import json
import re

PORTAL_USERNAME = os.getenv('PORTAL_USERNAME')
PORTAL_PASSWORD = os.getenv('PORTAL_PASSWORD')
PORTAL_TERM = os.getenv("SELECTED_TERM")
API_KEY = "AIzaSyDRgBe9XLaO9iExP3e8Xsnit5smgiqylYA"
json_str = ""
load_dotenv()

async def main():
    
    os.environ["ANONYMIZED_TELEMETRY"] = "false"

    

    #this function was just a method of obtaining the information at each step, which might be needed if using a lesser model

    #async def step_callback(browser_state, agent_output, step_number: int) -> None:
        # print("at current step")
        # print(agent.state.last_result)
        # local_agent_output = agent.state.last_result
        # print(local_agent_output)
        
        #print("=================================")
        #check's if agent is outputting json
        # if (re.search(r"```json",local_agent_output)) == None:
        #     return None
        
        # json_reg_match = re.search(r"```json(.*)",local_agent_output)
        # json_string = json_reg_match.group(0).strip()
        # json_str += json_string
        # return None
    
    


    llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-lite', api_key=SecretStr(API_KEY)) #you can alternate between different models

    browser = Browser(
        config=BrowserConfig(
            new_context_config=BrowserContextConfig(
                viewport_expansion=0,
            )
        )
    )
    
    #Course,Course Name,Credits,Instructor,
    # Room,Days,Start Time,End Time,
    # Max Enrollment,Total Enrollment

    class Course(BaseModel):
        course_code: str
        course_name: str
        credits: str
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
    #supposed to put SEAST in filter 
    agent = Agent( 
        task = f'''
        1.Go to 'https://cudportal.cud.ac.ae/student/login.asp' Select FA 2025-26 Term 
        2.Find the username field and type the username.
        3.Find the password field and type the password.
        4.Find the "Term:" field and select {PORTAL_TERM}.
        5.Click the login button. Wait for the page to load after login.
        6.navigate to Course Offerings → Show Filter → SEAST → Apply Filter 
        7.Wait 5 seconds
    **BEGIN EXTRACTION**
    8.***TURN INTO JSON FORMAT**  ONLY extract Course data of each page until page FINAL page in JSON format with fields of 'course_code', 'course_name', 'credits', 'instructor', 'room', 'days', 'start_time', 'end_time', 'max_enroll', 'total_enroll', only output in JSON format
    ''',
        llm=llm,
        browser=browser,
        controller = controller,
        sensitive_data = {"username": PORTAL_USERNAME, "password": PORTAL_PASSWORD}, #attempt not to leak info(They probabaly alreay have it anyway)
        use_vision=True,
        max_failures=2,
        #register_new_step_callback=step_callback, #fallback method of obtaining results at each step
        

        

    )
    
    result = await agent.run()
   # print("beginnning sequence", result.extracted_content(), "end sequence")
    print("---------------------------------------------------------------------------------------------------------------------------------------------------")
    print(result.final_result()) 
    print("================================================================================================================================================")
    #
    #Most of these comments are for testing the output
    #
    #total_extracted = result.extracted_content()

    # print("-------------")
    # print("extracted content is:", result.extracted_content())
    # agent_output_raw= re.findall(r"```json\n*```\n,'",result.final_result(), re.DOTALL) #re dotall also matches newline chars
    # regex_string = ""
    # for _ in agent_output_raw:
    #     regex_string += _
    # print("-------------")
    #reg_json = regex_string.replace(r"```json\n", "").replace(r"```\n", "").replace(r"\n  ", "")
    #print("answer?:", reg_json)

    agent_output = result.final_result()
    await browser.close()
    dict_data = json.loads(agent_output)
    #print(dict_data["courses"])

    #print(json)
    #print(json_str)
    
    with open("course_data.csv", "w") as file:
        field_names = ['course_code', 'course_name', 'credits', 'instructor', 'room', 'days', 'start_time', 'end_time', 'max_enroll', 'total_enroll']

        writer = csv.DictWriter(file, fieldnames=field_names)
        unformatted_data = dict_data["courses"]
        writer.writeheader()
        for row in unformatted_data:
            writer.writerow(row)


if __name__ == "__main__":
    asyncio.run(main())