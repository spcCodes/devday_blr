import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from IPython.display import Image, display

from langgraph.graph import StateGraph , START , END 
from langchain_core.messages import HumanMessage , AIMessage , SystemMessage
from typing import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages


# load the environment variables
load_dotenv()

#model definition
model = ChatOpenAI(model='gpt-4.1-mini', temperature=0)

# define the state
class State(TypedDict):
    messages:Annotated[list,add_messages]

#nodes definition
def get_response_from_llm(state: State):
    """
    This function will get the response from the LLM
    """
    user_input = state["messages"][0].content
    response = model.invoke(user_input)
    return {"messages": [response]}


def convert_to_uppercase(state:State):
    """
    This function will convert the message to uppercase
    """
    response_from_llm = state["messages"][-1].content
    uppercase_output = response_from_llm.upper()
    
    return {"messages": [uppercase_output]}

# define the workflow
graph = StateGraph(State)
graph.add_node("Get Response from LLM" , get_response_from_llm)
graph.add_node("Convert to Uppercase" , convert_to_uppercase)

graph.add_edge(START, "Get Response from LLM")
graph.add_edge("Get Response from LLM", "Convert to Uppercase")
graph.add_edge("Convert to Uppercase", END)

app = graph.compile()


if __name__ == "__main__":
    response = app.invoke({"messages": "Who built the Taj mahal?"})
    print(response["messages"][-1].content)