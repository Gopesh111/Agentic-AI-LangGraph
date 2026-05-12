from langgraph.graph import StateGraph, END
from typing import TypedDict
from pydantic import BaseModel, Field
import time

# 1. Define the exact strict schema we want
class UserExtraction(BaseModel):
    name: str = Field(description="The user's full name")
    age: int = Field(description="The user's age in numbers")
    skills: list[str] = Field(description="List of technical skills")

# 2. State Memory
class AgentState(TypedDict):
    raw_text: str
    parsed_data: dict

# 3. Data Extraction Node
def extract_data(state: AgentState):
    print("\033[94m[NODE]\033[0m Extracting entities using Pydantic schema...")
    time.sleep(1.5)
    
    # In a real app, you do: llm.with_structured_output(UserExtraction)
    # Mocking the perfect JSON return for the demo
    structured_result = {
        "name": "Gopesh Pandey",
        "age": 21,
        "skills": ["Python", "LangGraph", "Machine Learning"]
    }
    
    print("\033[92m[NODE]\033[0m Successfully extracted valid JSON.")
    return {"parsed_data": structured_result}

# 4. Build Graph
workflow = StateGraph(AgentState)

workflow.add_node("extract_data", extract_data)
workflow.set_entry_point("extract_data")
workflow.add_edge("extract_data", END)

app = workflow.compile()

if __name__ == "__main__":
    print("\n\033[1;96m--- STARTING STRUCTURED EXTRACTION ---\033[0m\n")
    
    input_state = {
        "raw_text": "Hi, I am Gopesh Pandey. I am 21 years old and I code in Python and LangGraph.",
        "parsed_data": {}
    }
    
    final_state = app.invoke(input_state)
    
    print("\n\033[95m[FINAL OUTPUT SENT TO DATABASE]\033[0m")
    print(final_state["parsed_data"])
    print()
