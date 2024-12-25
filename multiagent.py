import os
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.graph import MermaidDrawMethod
from IPython.display import display, Image
from dotenv import load_dotenv


load_dotenv()

class PlannerState(TypedDict):
    messages : Annotated[List[HumanMessage | AIMessage], "the messages in the conversation"]
    city : str
    interests: List[str]
    itinerary: str
from langchain_groq import ChatGroq
llm = ChatGroq(
    temperature = 0,
    model_name = "llama-3.3-70b-versatile"
)

#result = llm.invoke("What is Multi AI Agent")
#print (result.content)

itinerary_prompt=ChatPromptTemplate.from_messages([
    ("system","You are a helpful travel assistant. Create a day trip itineray for {city} based on the user's interests: {interests}. Provide a brief bulleted itinerary "),
    ("human","Create an itinerary for my day trip")

])

def input_city(state: PlannerState) -> PlannerState:
    print("Please enter the city you want to visit for your day trip: ")
    user_message  = input("Your Input: ")
    return {
        **state,
        "city": user_message,
        "messages":state["messages"]+[HumanMessage(content=user_message)]
    }

def input_interest(state: PlannerState) -> PlannerState:
    print(f"Please enter your interest for the trip to : {state['city']} (comma-separated):")
    user_message  = input("Your Input: ")
    return {
        **state,
        "interests": [interest.strip() for interest in user_message.split(",")],
        "messages":state["messages"]+[HumanMessage(content=user_message)]
    }

def create_itinerary(state: PlannerState) -> PlannerState:
    print(f"Creating an itinerary for {state['city']} based on interests :{', '.join(state['interests'])}")
    response = llm.invoke(itinerary_prompt.format_messages(city = state['city'],interests=','.join(state['interests'])))
    print("Final Itinerary : ")
    print(response.content)
    return {
        **state,
        "messages":state["messages"]+[HumanMessage(content=response.content)],
        "itinerary": response.content

    }

workflow = StateGraph(PlannerState)

workflow.add_node("input_city",input_city)
workflow.add_node("input_interest",input_interest)
workflow.add_node("create_itinerary",create_itinerary)

workflow.set_entry_point("input_city")
workflow.add_edge("input_city","input_interest")
workflow.add_edge("input_interest", "create_itinerary")
workflow.add_edge("create_itinerary",END)

app = workflow.compile()


display(
    Image(app.get_graph().draw_mermaid_png(
        draw_method=MermaidDrawMethod.API
    ))
)

def travel_planner(user_request:str):
    print(f"Initial request: {user_request}\n")
    state = {
        "messages" : [HumanMessage(content = user_request)],
        "city": "",
        "interests":[],
        "itinerary": "",
    }

    for output in app.stream(state):
        pass

user_request = travel_planner("I want to plan a day trip")

