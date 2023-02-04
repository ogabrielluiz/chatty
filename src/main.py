from __future__ import annotations

import asyncio
import contextlib
import os

from rich.markdown import Markdown

from textual.app import App, ComposeResult
from textual.containers import Content, Container, Horizontal
from textual.reactive import reactive
from textual.widgets import Static, Input, Header, Footer, Button
from chain.chain import get_chat_gpt_chain
from dotenv import load_dotenv


class ChatApp(App):
    """Talk to GPT-3"""

    TITLE = "Chat with GPT-3"
    SUB_TITLE = "Powered by OpenAI API"

    CSS_PATH = "chat.css"
    chat_history = reactive("")

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        load_dotenv()
        self.chat_history = ""

        self.chain = get_chat_gpt_chain()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        if os.getenv("OPENAI_API_KEY") is None:
            yield Content(
                Static("OPENAI_API_KEY not set in .env file"), id="results-container"
            )
            return
        else:
            yield Input(placeholder="Write your message here.")
            yield Button("Save conversation")
            yield Content(Static(id="results"), id="results-container")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        # Save the chat history to a file in the current directory
        with open("chat_history.md", "w") as f:
            f.write(self.chat_history)

    def on_mount(self) -> None:
        """Called when app starts."""
        with contextlib.suppress(Exception):
            # Give the input focus, so we can start typing straight away
            self.query_one(Input).focus()

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        """A coroutine to handle a text entered message."""
        if message.value:
            self.query_one(Input).placeholder = "Processing..."
            hinput_markdown = self.make_human_input_markdown(message.value)
            self.chat_history = self.chat_history + hinput_markdown
            asyncio.create_task(self.get_response_and_print_results(message.value))
        else:
            # Clear the results
            self.query_one("#results", Static).update()
            self.chat_history = ""

    async def get_response_and_print_results(self, message: str) -> None:
        """Get the response from the API and print the results."""

        self.query_one(Input).value = ""

        results = self.chain.predict(human_input=message)
        self.query_one(Input).placeholder = "Write your message here."
        chat_gpt_markdown = self.make_chat_gpt_markdown(results)
        self.chat_history = self.chat_history + chat_gpt_markdown

    def watch_chat_history(self, value: str) -> None:
        """Called when chat_history changes."""
        with contextlib.suppress(Exception):
            self.query_one("#results", Static).update(Markdown(value))
            self.query_one("#results-container").scroll_end()

    def make_chat_gpt_markdown(self, results: str) -> str:
        """Convert the results in to markdown."""
        lines = ["", results]
        return "\n".join(lines)

    def make_human_input_markdown(self, message: str) -> str:
        """Convert the results in to markdown."""
        lines = ["", f"> {message}", ""]
        return "\n".join(lines)


if __name__ == "__main__":
    app = ChatApp()
    app.run()
