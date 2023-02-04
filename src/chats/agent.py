from langchain.agents import Tool
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain import OpenAI
from langchain.agents import initialize_agent
from langchain.utilities import BashProcess, PythonREPL
from langchain.agents import Agent


def get_chat_agent(verbose: bool = False) -> Agent:
    """Get the chat agent."""
    bash = BashProcess()
    python_repl = PythonREPL()
    tools = [
        Tool(
            name="bash",
            description="Use this to run bash commands",
            func=bash.run,
        ),
        Tool(
            name="python",
            description="Use this to run python commands",
            func=python_repl.run,
        ),
    ]

    memory = ConversationBufferMemory(memory_key="chat_history")

    llm = OpenAI(temperature=0)
    return initialize_agent(tools, llm, agent="conversational-react-description", verbose=verbose, memory=memory)