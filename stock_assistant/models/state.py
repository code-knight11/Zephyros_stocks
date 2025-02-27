from typing import Annotated, TypedDict,Dict,Any
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    context: Dict[str, Any]
