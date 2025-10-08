from typing import Annotated
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph , START , END 
from langchain_core.messages import HumanMessage , AIMessage , SystemMessage
from typing import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.prompts import PromptTemplate

# load the environment variables
load_dotenv()

#model definition
model = ChatOpenAI(model='gpt-4.1-mini', temperature=0)

class State(TypedDict):
    messages: Annotated[list, add_messages]


#defining the nodes 

def get_user_intent(state:State):
    """
    This function will get the user intent from the user input
    
    """

    user_input = state["messages"][0].content

    # Prompt template
    template = PromptTemplate(

        template="""You are a classifier. Classify the user query as either "complaint" or "query".

        Return ONLY one word: either "complaint" or "query", nothing else.

        User Query: {user_input}

        Classification:""",

        input_variables=['user_input'],
        validate_template=True
        )

    chain = template | model


    result = chain.invoke({
        "user_input": user_input
    })

    return {"messages": [result]}


def route_user_query(state:State):
    """
    This function will route the user query to the appropriate node
    """
    intent = state["messages"][-1].content.strip().lower()
    if "complaint" in intent:
        return "Complaint"
    else:
        return "Query"


def handle_complaint(state:State):
    """
    This function will handle the complaint
    """

    user_input = state["messages"][0].content
    
    complaint_template = PromptTemplate(
        template = """
        You are a helpful assistant , you will be given a user complaint and you will need to handle the complaint.
        User Complaint : {user_input}
        """,
        input_variables = ["user_input"],
        validate_template = True
    )

    chain = complaint_template | model

    result = chain.invoke({
        "user_input": user_input
    })

    return {"messages": [result]}

def handle_query(state:State):
    """
    This function will handle the query
    """

    user_input = state["messages"][0].content
    
    query_template = PromptTemplate(
        template = """
        You are a helpful assistant , you will be given a user query and you will need to handle the query.
        User Query : {user_input}
        """,
        input_variables = ["user_input"],
        validate_template = True
    )

    chain = query_template | model

    result = chain.invoke({
        "user_input": user_input
    })

    return {"messages": [result]}

graph = StateGraph(State)

graph.add_node("Get User Intent", get_user_intent)
graph.add_node("Complaint", handle_complaint)
graph.add_node("Query", handle_query)

graph.add_edge(START, "Get User Intent")
graph.add_conditional_edges(
    "Get User Intent",
    route_user_query
)
graph.add_edge("Complaint", END)
graph.add_edge("Query", END)

app = graph.compile()

if __name__ == "__main__":
    response = app.invoke({"messages": "I am not at all happy with the sofa that I purchased from Costco last week"})
    print(response["messages"][-1].content)


    print(response)