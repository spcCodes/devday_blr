import os 
from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph , START , END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage , AIMessage , SystemMessage
from typing import TypedDict , Annotated
from pydantic import BaseModel , Field
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from typing import Annotated, Sequence, Literal
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langchain import hub
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field   

from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition

embeddings = OpenAIEmbeddings()
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

#data indexing: creating first database about langgraph
urls=[
    "https://langchain-ai.github.io/langgraph/tutorials/introduction/",
    "https://langchain-ai.github.io/langgraph/tutorials/workflows/",
    "https://langchain-ai.github.io/langgraph/how-tos/map-reduce/"
]

langgraph_docs=[WebBaseLoader(url).load() for url in urls]
langgraph_docs_list = [item for sublist in langgraph_docs for item in sublist]

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=100
)

doc_splits = text_splitter.split_documents(langgraph_docs_list)

# Save the vectorstore with a particular name, e.g., "bangladesh_economy"
db1 = Chroma.from_documents(doc_splits, embeddings, persist_directory="langgraph_documents")
langgraph_retriever = db1.as_retriever(search_kwargs={"k": 3})

#creating second database about langchain
langchain_urls=[
    "https://python.langchain.com/docs/tutorials/",
    "https://python.langchain.com/docs/tutorials/chatbot/",
    "https://python.langchain.com/docs/tutorials/qa_chat_history/"
]

langchain_docs=[WebBaseLoader(url).load() for url in langchain_urls]
langchain_docs_list = [item for sublist in langchain_docs for item in sublist]

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=100
)

doc_splits = text_splitter.split_documents(langchain_docs_list)

# Save the vectorstore with a particular name, e.g., "bangladesh_economy"
db2 = Chroma.from_documents(doc_splits, embeddings, persist_directory="langchain_documents")
langchain_retriever = db2.as_retriever(search_kwargs={"k": 3})

#creating a tool out of both
langgraph_retriever_tool=create_retriever_tool(
    langgraph_retriever,
    "retriever_langgraph",
    "Search and run information about Langgraph saved in the documents"
)

langchain_retriever_tool=create_retriever_tool(
    langchain_retriever,
    "retriever_langchain",
    "Search and run information about Langchain saved in the documents"
)
tool_list = [langgraph_retriever_tool , langchain_retriever_tool]

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    retry_count: int  # Add retry counter to prevent infinite loops

#defining the nodes
def agent(state):
    """
    Invokes the agent model to generate a response based on the current state. Given
    the question, it will decide to retrieve using the retriever tool, or simply end.

    Args:
        state (messages): The current state

    Returns:
        dict: The updated state with the agent response appended to messages
    """
    print("---CALL AGENT---")
    messages = state["messages"]
    llm_with_tools = model.bind_tools(tool_list)
    response = llm_with_tools.invoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}

### Edges
def grade_documents(state) -> Literal["generate_tool", "rewrite_tool"]:
    """
    Determines whether the retrieved documents are relevant to the question.
    If documents are not relevant and retry limit reached, generates anyway.

    Args:
        state (messages): The current state

    Returns:
        str: A decision for whether the documents are relevant or not
    """

    print("---CHECK RELEVANCE---")
    
    # Check retry limit first
    retry_count = state.get("retry_count", 0)
    MAX_RETRIES = 2  # Maximum number of rewrite attempts

    # Data model
    class grade(BaseModel):
        """Binary score for relevance check."""

        binary_score: str = Field(description="Relevance score 'yes' or 'no'")

    # LLM with tool and validation
    grading_tool = model.with_structured_output(grade)

    # Prompt
    prompt = PromptTemplate(
        template="""You are a grader assessing relevance of a retrieved document to a user question. \n 
        Here is the retrieved document: \n\n {context} \n\n
        Here is the user question: {question} \n
        If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
        Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question.
        """,
        input_variables=["context", "question"],
        validate_template=True)
        
    # Chain
    chain = prompt | grading_tool

    messages = state["messages"]
    last_message = messages[-1]

    question = messages[0].content
    docs = last_message.content

    scored_result = chain.invoke({"question": question, "context": docs})

    score = scored_result.binary_score

    if score == "yes":
        print("---DECISION: DOCS RELEVANT---")
        return "generate_tool"

    else:
        # Check if we've exceeded retry limit
        if retry_count >= MAX_RETRIES:
            print(f"---DECISION: MAX RETRIES ({MAX_RETRIES}) REACHED, GENERATING ANYWAY---")
            return "generate_tool"
        else:
            print(f"---DECISION: DOCS NOT RELEVANT (Retry {retry_count + 1}/{MAX_RETRIES})---")
            print(score)
            return "rewrite_tool"

def generate(state):
    """
    Generate answer

    Args:
        state (messages): The current state

    Returns:
         dict: The updated message
    """
    print("---GENERATE---")
    messages = state["messages"]
    question = messages[0].content
    last_message = messages[-1]

    docs = last_message.content

    # Prompt
    prompt = hub.pull("rlm/rag-prompt")

    # Post-processing
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Chain
    rag_chain = prompt | model | StrOutputParser()

    # Run
    response = rag_chain.invoke({"context": docs, "question": question})
    return {"messages": [response]}

def rewrite(state):
    """
    Transform the query to produce a better question.
    Increments retry counter.

    Args:
        state (messages): The current state

    Returns:
        dict: The updated state with re-phrased question and incremented retry count
    """

    print("---TRANSFORM QUERY---")
    messages = state["messages"]
    question = messages[0].content

    msg = [
        HumanMessage(
            content=f""" \n 
    Look at the input and try to reason about the underlying semantic intent / meaning. \n 
    Here is the initial question:
    \n ------- \n
    {question} 
    \n ------- \n
    Formulate an improved question: """,
        )
    ]

    # Grader
    response = model.invoke(msg)
    
    # Increment retry counter
    retry_count = state.get("retry_count", 0)
    return {"messages": [response], "retry_count": retry_count + 1}


# Define a new graph
workflow = StateGraph(AgentState)

# Define the nodes we will cycle between
workflow.add_node("agent", agent)  # agent
retrieve_tools = ToolNode(tool_list)
workflow.add_node("retrieve", retrieve_tools)  # retrieval
workflow.add_node("rewrite", rewrite)  # Re-writing the question
workflow.add_node("generate", generate) 

workflow.add_edge(START, "agent")

workflow.add_conditional_edges(
    "agent",
    tools_condition,
    {
        "tools": "retrieve",
        END: END,
    }
)
# Edges taken after the `action` node is called.
workflow.add_conditional_edges(
    "retrieve",
    grade_documents,
    {
        "generate_tool": "generate",
        "rewrite_tool": "rewrite"
    }
)
workflow.add_edge("generate", END)
workflow.add_edge("rewrite", "agent")

graph = workflow.compile()


if __name__ == "__main__":
    result = graph.invoke({
        "messages": [HumanMessage(content="What is Langchain?")],
        "retry_count": 0
        })
    print(result["messages"][-1].content)