from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.messages import SystemMessage
from tools.db_tools import run_database_query
import json
import uuid

class DBAssistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable
        self.scratchpad = []
        
    def __call__(self, state, config: RunnableConfig):
        last_message = state["messages"][-1]

        if hasattr(last_message, "additional_kwargs") and last_message.additional_kwargs.get("tool_calls"):
            tool_calls = last_message.additional_kwargs["tool_calls"]

            for tool_call in tool_calls:
                function_name = tool_call["function"]["name"]
                arguments = json.loads(tool_call["function"]["arguments"])

                if function_name == "run_database_query":
                    query_result = run_database_query(arguments["query"])
                    return {"messages": SystemMessage(content=f"Query result: {query_result}")}

            return {"messages": SystemMessage(content=f"Query result: {last_message.content}")}

        message_content = None
        for message in reversed(state["messages"]):
            if hasattr(message, "content") and "route_to" not in message.content:
                message_content = message.content
                break

        if not message_content:
            return {"messages": SystemMessage(content="No valid message found")}

        state_with_message = {"messages": [("user", message_content)]}
        result = self.runnable.invoke(state_with_message)

        try:
            if hasattr(result, "content"):
                raw_result = result.content.strip()
                if raw_result.count("{") > 1:
                    fixed_json = f"[{raw_result.replace('}\n{', '},{')}]"
                    parsed_results = json.loads(fixed_json)
                    parsed_result = parsed_results[0]
                else:
                    parsed_result = json.loads(raw_result)

                if parsed_result.get("tool_calls"):
                    tool_call = parsed_result["tool_calls"][0]
                    result.additional_kwargs = {
                        "tool_calls": [{
                            "function": {
                                "name": tool_call["name"],
                                "arguments": json.dumps(tool_call["args"])
                            },
                            "type": "function",
                            "id": str(uuid.uuid4())
                        }]
                    }
        except json.JSONDecodeError as e:
            print(f"Error processing result: {e}")

        return {"messages": result}
