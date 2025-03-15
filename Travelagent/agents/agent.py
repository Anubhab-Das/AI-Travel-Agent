import os
import uuid
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from agents.tools.flights_finder import flights_finder
from agents.tools.hotels_finder import hotels_finder

load_dotenv()

class Agent:
    def __init__(self):
        self._tools = {t.name: t for t in [flights_finder, hotels_finder]}
        self._tools_llm = ChatOpenAI(model='gpt-4o-mini').bind_tools([flights_finder, hotels_finder])

        builder = StateGraph(dict)
        builder.add_node("call_tools_llm", self.call_tools_llm)
        builder.add_node('invoke_tools', self.invoke_tools)
        builder.set_entry_point('call_tools_llm')  # Important: Define entry point clearly
        builder.add_edge('call_tools_llm', 'invoke_tools')
        builder.add_edge('invoke_tools', END)

        memory = MemorySaver()
        self.graph = builder.compile(checkpointer=memory)

    def call_tools_llm(self, state):
        messages = state['messages']
        message = self._tools_llm.invoke(messages)
        return {'messages': [message]}

    def invoke_tools(self, state):
        tool_calls = state['messages'][-1].tool_calls
        results = []
        for t in tool_calls:
            result = self._tools[t['name']].invoke(t['args'])
            results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))
        return {'messages': results}

    def invoke_agent(self, messages, thread_id):
        config = {'configurable': {'thread_id': thread_id}}
        result = self.graph.invoke({'messages': messages}, config=config)
        return result['messages'][-1].content

"""    def send_email(self, content):
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        message = Mail(
            from_email=os.getenv('FROM_EMAIL'),
            to_emails=os.getenv('TO_EMAIL'),
            subject=os.getenv('EMAIL_SUBJECT'),
            html_content=content
        )
        sg.send(message)
"""
