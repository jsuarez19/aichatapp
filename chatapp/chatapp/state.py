import reflex as rx
import asyncio
import os
from openai import AsyncOpenAI

class State(rx.State):
    # The current question being asked.
    question: str

    # Keep track of the chat history as a list of (question, answer) tuples.
    chat_history: list[tuple[str, str]]

    @rx.event
    async def answer(self):
        # Our chatbot has some brains now!
        client = AsyncOpenAI(
            api_key=os.environ["GITHUB_TOKEN"],
            base_url="https://openrouter.ai/api/v1",
        )

        session = await client.chat.completions.create(
            model="deepseek/deepseek-r1:free",
            messages=[
                {"role": "user", "content": self.question},
            ],
            stop=None,
            temperature=0.7,
            stream=True,
        )

        # Add to the answer as the chatbot responds.
        answer = ""
        self.chat_history.append((self.question, answer))
        
        # Clear the question input
        self.question = ""
        # Yield here to clear the frontend input before continuing.
        yield

        async for item in session:
            if hasattr(item.choices[0].delta, "content"):
                if item.choices[0].delta.content is None:
                    # presence of 'None' indicates the end of response
                    break
                answer += item.choices[0].delta.content
                self.chat_history[-1] = (
                    self.chat_history[-1][0],
                    answer[:i + 1],
                )
                yield
