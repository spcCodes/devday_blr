# LangGraph Basics - Session 1

A comprehensive guide to building workflows with LangGraph and LangChain, from simple greetings to real-world applications.

## Table of Contents

1. [Overview](#overview)
2. [Setup](#setup)
3. [Core Concepts](#core-concepts)
4. [Workflow Levels](#workflow-levels)
5. [Prompts in LangChain](#prompts-in-langchain)
6. [Chat History Management](#chat-history-management)
7. [Key Takeaways](#key-takeaways)

## Overview

This notebook demonstrates the fundamentals of LangGraph, a framework for building stateful, multi-step workflows with Language Models. You'll learn how to:

- Create state graphs with nodes and edges
- Manage conversation state
- Integrate LLMs into workflows
- Build real-world applications like sentiment classifiers
- Work with prompts and chat history


### Environment Variables

Create a `.env` file with your API keys:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Import Required Packages

```python
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

load_dotenv()
```

## Core Concepts

### State Management

LangGraph uses a state dictionary to pass data between nodes. The state is defined using `TypedDict`:

```python
from typing import Annotated
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]
```

The `add_messages` reducer automatically handles message aggregation.

### Graph Components

1. **Nodes**: Functions that process state
2. **Edges**: Connections between nodes
3. **START/END**: Special nodes marking workflow boundaries

### Utility Functions

```python
# Display graph visualization
def display_graph(app):
    try:
        display(Image(app.get_graph().draw_mermaid_png()))
    except Exception as e:
        print(e)

# Stream workflow output
def stream_output(app, input):
    for output in app.stream(input):
        for key, value in output.items():
            print(f"here is output from {key}")
            print("_______")
            print(value)
            print("\n")
```

## Workflow Levels

### Level 0: Basic Workflow

**Concept**: A simple single-node workflow that greets users.

```python
def greet_user(state: State):
    """Greet the user with a message"""
    user_message = state["messages"][0].content
    return {"messages": [f"Hello {user_message}!"]}

# Build the graph
graph = StateGraph(State)
graph.add_node("User Greetings", greet_user)
graph.add_edge(START, "User Greetings")
graph.add_edge("User Greetings", END)
app = graph.compile()

# Run it
result = app.invoke({"messages": "Suman"})
```

**Output**: `Hello Suman!`

---

### Level 1: Two-Node Workflow

**Concept**: Chain multiple operations together.

```python
def greet_user(state: State):
    user_message = state["messages"][0].content
    return {"messages": [f"Hello {user_message}!"]}

def convert_to_uppercase(state: State):
    last_message = state["messages"][-1].content
    return {"messages": [last_message.upper()]}

# Build the graph
graph = StateGraph(State)
graph.add_node("User Greetings", greet_user)
graph.add_node("Convert to Uppercase", convert_to_uppercase)

graph.add_edge(START, "User Greetings")
graph.add_edge("User Greetings", "Convert to Uppercase")
graph.add_edge("Convert to Uppercase", END)
app = graph.compile()
```

**Output**: `HELLO SUMAN!`

---

### Level 2: LLM Integration

**Concept**: Use an actual Language Model in your workflow.

```python
model = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

def get_response_from_llm(state: State):
    """Get response from LLM"""
    user_input = state["messages"][0].content
    response = model.invoke(user_input)
    return {"messages": [response]}

def convert_to_uppercase(state: State):
    """Convert LLM response to uppercase"""
    response_from_llm = state["messages"][-1].content
    uppercase_output = response_from_llm.upper()
    return {"messages": [uppercase_output]}

# Build the graph
graph = StateGraph(State)
graph.add_node("Get Response from LLM", get_response_from_llm)
graph.add_node("Convert to Uppercase", convert_to_uppercase)

graph.add_edge(START, "Get Response from LLM")
graph.add_edge("Get Response from LLM", "Convert to Uppercase")
graph.add_edge("Convert to Uppercase", END)
app = graph.compile()
```

---

### Level 3: Real-World Use Case

**Concept**: Build a sentiment classifier with word counter.

```python
def classify_sentiment(state: State):
    """Classify sentiment using LLM"""
    user_input = state["messages"][0].content
    prompt = """You are a sentiment classifier. 
    Classify the sentiment as positive, negative or neutral. 
    Return only the sentiment as a string."""
    final_message = user_input + prompt
    response = model.invoke(final_message)
    return {"messages": [response]}

def get_total_word_count(state):
    """Count words in original message"""
    user_input = state["messages"][0].content
    word_count = len(user_input.split())
    return {"messages": [f"Total word count: {word_count}"]}

# Build the graph
graph = StateGraph(State)
graph.add_node("Classify Sentiment", classify_sentiment)
graph.add_node("Get Total Word Count", get_total_word_count)

graph.add_edge(START, "Classify Sentiment")
graph.add_edge("Classify Sentiment", "Get Total Word Count")
graph.add_edge("Get Total Word Count", END)
app = graph.compile()

# Example
result = app.invoke({
    "messages": "I am happy with the quality of the product and the service"
})
# Output: Sentiment: positive, Word count: 12
```

## Prompts in LangChain

### 1. Static Prompts (Simple Invocation)

```python
model = ChatOpenAI(model='gpt-4.1-mini', temperature=0)
result = model.invoke("Write a 5 line description on cricket")
print(result.content)
```

### 2. Dynamic Prompts (PromptTemplate)

**Single Variable**:

```python
from langchain_core.prompts import PromptTemplate

template = PromptTemplate(
    template="Write a 5 line description on {topic}",
    input_variables=['topic']
)

prompt = template.invoke({'topic': 'table tennis'})
result = model.invoke(prompt)
```

**Multiple Variables**:

```python
template = PromptTemplate(
    template="""
    You are a detailed content creation agent.
    
    Your task is to write content about: {topic_input}.
    Writing style: {style_input}
    Desired length: {length_input}
    
    Generate engaging content matching the requested style and length.
    """,
    input_variables=['topic_input', 'style_input', 'length_input'],
    validate_template=True
)

# Use with chains
chain = template | model

result = chain.invoke({
    'topic_input': 'India\'s economic growth',
    'style_input': 'Conversational',
    'length_input': '200 words'
})
```

### 3. ChatPromptTemplate

**For Conversational AI**:

```python
from langchain_core.prompts import ChatPromptTemplate

chat_template = ChatPromptTemplate([
    ("system", "You are a helpful {domain} expert"),
    ("human", "Explain {topic} in simple terms")
])

prompt = chat_template.invoke({
    "domain": "AI",
    "topic": "Machine Learning"
})

result = model.invoke(prompt)
```

### 4. MessagesPlaceholder

**For Chat History**:

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

chat_history = [
    HumanMessage(content="I want to request a refund for order 11564."),
    AIMessage(content="Your refund has been initiated. Processing in 3-5 days.")
]

chat_template = ChatPromptTemplate([
    ('system', 'You are a helpful customer support agent'),
    MessagesPlaceholder(variable_name='chat_history'),
    ('human', '{query}')
])

prompt = chat_template.invoke({
    'chat_history': chat_history,
    'query': 'Where is my refund? I haven\'t received it yet.'
})

result = model.invoke(prompt)
```

## Chat History Management

### Basic Chatbot (No Memory)

**Problem**: Each query is independent - no context retention.

```python
model = ChatOpenAI(model='gpt-4.1-mini', temperature=0)

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    response = model.invoke(user_input)
    print("AI:", response.content)
```

**Issue**: Follow-up questions like "when was he born?" won't work.

---

### Improved: With Chat History

```python
chat_history = []

while True:
    user_input = input("You: ")
    chat_history.append(user_input)
    if user_input.lower() == "exit":
        break
    response = model.invoke(chat_history)
    chat_history.append(response.content)
    print("AI:", response.content)
```

**Better**: Context is maintained, but format is basic.

---

### Best Practice: Using Message Types

```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

chat_history = [
    SystemMessage(content='You are a helpful AI assistant')
]

while True:
    user_input = input('You: ')
    chat_history.append(HumanMessage(content=user_input))
    
    if user_input == 'exit':
        break
        
    result = model.invoke(chat_history)
    chat_history.append(AIMessage(content=result.content))
    print("AI:", result.content)
```

**Example Conversation**:
```
You: hi
AI: Hello! How can I assist you today?

You: who built the taj mahal
AI: The Taj Mahal was built by Mughal Emperor Shah Jahan...

You: when was he born
AI: Shah Jahan was born on January 5, 1592.
```

## Key Takeaways

### LangGraph Benefits

✅ **State Management**: Automatic state passing between nodes  
✅ **Modularity**: Break complex workflows into simple functions  
✅ **Visualization**: Built-in graph visualization  
✅ **Flexibility**: Easy to add/remove nodes and change flow  
✅ **Streaming**: Stream outputs from each node

### Message Types

- **SystemMessage**: Set AI behavior and context
- **HumanMessage**: User inputs
- **AIMessage**: AI responses

### Best Practices

1. **Use TypedDict for State**: Clear type definitions prevent errors
2. **Add Reducers**: Use `add_messages` for automatic message handling
3. **Modular Nodes**: Keep node functions simple and focused
4. **Prompt Templates**: Use templates for dynamic, reusable prompts
5. **Chat History**: Always include system messages for context

