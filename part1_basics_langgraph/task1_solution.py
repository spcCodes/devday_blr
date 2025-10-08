import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from IPython.display import Image, display

from langgraph.graph import StateGraph , START , END 
from langchain_core.messages import HumanMessage , AIMessage , SystemMessage
from typing import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain_core.prompts import PromptTemplate

# load the environment variables
load_dotenv()

#model definition
model = ChatOpenAI(model='gpt-4.1-mini', temperature=0)

# define the state
class State(TypedDict):
    messages:Annotated[list,add_messages]


#nodes definition

def get_user_intent(state: State):
    """
    This function will get the user intent from the message
    """
    user_input = state["messages"][0].content

    # Prompt template
    template = PromptTemplate(
        template = """
        You are a helpful assistant whose task is to identify user input intent . These may be question, feedback, help, complaint etc. 
        Identify the intent. It should be a single word and should be returned as string

        User input : {user_input}
        
        """,
        input_variables=['user_input'],
        validate_template=True
        )

    chain = template | model


    result = chain.invoke({
        'user_input': user_input
    })

    return {"messages": [result]}


def give_response(state:State):

    """
    This function will give the response to the user based on the intent
    """
    user_input = state["messages"][0].content
    intent = state["messages"][-1].content

    template = PromptTemplate(
        template = """
        You are a helpful assistant whose task is to give the response to the user based on the intent
        User input : {user_input}
        Intent : {intent}
        """,
        input_variables=['user_input', 'intent'],
        validate_template=True
    )

    chain = template | model


    response = chain.invoke({
        'user_input': user_input,
        'intent': intent
    })

    return {"messages": [response]}


# define the workflow
graph = StateGraph(State)
graph.add_node("Get User Intent" , get_user_intent)
graph.add_node("Give Response" , give_response)

graph.add_edge(START, "Get User Intent")
graph.add_edge("Get User Intent", "Give Response")
graph.add_edge("Give Response", END)

app = graph.compile()


if __name__ == "__main__":
    response = app.invoke({"messages": "I am not at all happy with the sofa that I purchased from Costco last week"})
    print(response["messages"][-1].content)

    print(response)