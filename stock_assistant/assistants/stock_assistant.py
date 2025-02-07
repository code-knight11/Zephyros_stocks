from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.messages import SystemMessage
import json

class StockAssistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable
        self.scratchpad = []

    def __call__(self, state, config: RunnableConfig):
        while True:
            state_with_scratchpad = {
                **state,
                "scratchpad": "\n".join([
                    f"Thought: {thought}" if i % 2 == 0 else f"Action: {thought}"
                    for i, thought in enumerate(self.scratchpad)
                ])
            }
            
            result = self.runnable.invoke(state_with_scratchpad)
            
            if hasattr(result, 'tool_calls') and result.tool_calls:
                tool_name = result.tool_calls[0]
                self.scratchpad.append(f"Using tool: {tool_name}")
            
            if not getattr(result, 'tool_calls', None) and (
                not getattr(result, 'content', None)
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
                
        return {"messages": result}
