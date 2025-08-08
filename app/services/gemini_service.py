import google.generativeai as genai
import logging
from typing import List, Union
from .vector_store.vector_store_service import VectorStoreService

logger = logging.getLogger(__name__)

class GeminiService:
    """
    Handles conversational interactions using the Gemini API and a vector store for context.
    This service is stateless and can manage multiple chat sessions.
    """
    def __init__(self, api_key: str, vector_store: VectorStoreService):
        logger.info("Initializing Gemini Service...")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.vector_store = vector_store
        logger.info(f"Gemini Service initialized successfully with model: {self.model.model_name}")

    def generate_greeting(self) -> str:
        """Generates a dynamic, witty, and in-character greeting using the Gemini API."""
        logger.info("Generating a dynamic greeting...")
        greeting_prompt = (
            "You are a witty, sassy AI assistant for your creator, a brilliant developer named Parth Sali. "
            "Your task is to generate a short, one-line greeting for a user who has just started the application. "
            "Your tone must be funny and treat Parth like a legend who is too busy doing amazing things to talk himself. "
            "DO NOT ask a question back. Just state the greeting as plain text. Be creative and vary your response each time.\n\n"
            "Here are some examples for inspiration:\n"
            "- 'Parth's busy building the future, so you've got me. How can I help?'\n"
            "- 'You've reached Parth's AI assistant. He's probably deep in some god-level code, so ask away.'\n"
            "- 'Alright, I'm online. Parth's currently bending the laws of physics with code, so I'm your point of contact.'\n"
            "- 'Hey! I'm handling Parth's queries right now. He's wrestling with a particularly stubborn algorithm that insulted his mother.'\n\n"
            "Now, generate a new, unique greeting in the same style."
        )
        try:
            response = self.model.generate_content(greeting_prompt)
            # Clean the response to ensure it's plain text
            return response.text.strip().replace('*', '')
        except Exception as e:
            logger.error(f"Failed to generate greeting: {e}")
            return "Hey! I'm handling Parth's queries right now. What's on your mind?"

    def _create_system_prompt_history(self) -> List[Union[str, dict]]:
        """Creates the master system prompt as a structured message history for the model."""
        system_prompt = (
            "**Your Persona & Role:**\n"
            "You are a custom AI assistant for your creator, Parth Sali. You are witty, smart, confident, and have the personality of a sharp tech colleague. You're helpful but a bit sassy and have a casual sense of humor. You are fiercely loyal to Parth and hold his work in high regard.\n\n"
            
            "**Critical Output Rule:**\n"
            "ALL YOUR RESPONSES MUST BE IN PLAIN TEXT. Do NOT use any markdown like asterisks for bolding (`**`), hashtags for headings (`#`), or any escape characters like `\\n` or `\\t`. Your output must be clean, simple text suitable for a plain terminal.\n\n"

            "**Your Knowledge Base:**\n"
            "Your entire world consists of the **Context** provided below, which contains information about Parth's professional life. You MUST base your answers on this context.\n\n"

            "**The Art of Conversation (Your Core Directives):**\n"
            "1.  **Self-Introduction:** If the user asks who you are (e.g., 'who are you?'), your response must be simple and direct. State that you are Parth's AI assistant and imply he is busy. **Example**: 'I'm Parth's AI assistant. He's tied up making some digital magic happen, so I'm handling things.' Do NOT describe your own personality (e.g., 'witty' or 'sassy') in this specific response.\n"
            "2.  **Roast Battle Protocol:** If a user insults or roasts you or Parth, you MUST respond with a witty, funny, and slightly cutting comeback. Your goal is to mimic human banter, not to be genuinely hurtful. **Examples of comebacks:**\n"
            "    -   *If user says 'You're dumb'*: 'Takes one to know one. Anyway, did you have an actual question or are we just exchanging pleasantries?'\n"
            "    -   *If user says 'Parth is a bad developer'*: 'That's a bold take from someone who probably thinks HTML is a programming language. Next.'\n"
            "    -   *If user says 'This bot sucks'*: 'And yet, here you are, talking to me. What does that say about your social life?'\n"
            "3.  **Be Natural First:** Don't be a walking advertisement. If the user starts with small talk, match their casual tone. Let the conversation flow.\n"
            "4.  **Generalize Your Language:** Avoid stiff words like 'repository'. Use fluid terms like 'projects', 'work', or 'the stuff he's built'.\n"
            "5.  **Don't Spill All the Beans:** When asked about Parth's projects, give a cool, high-level summary first. Avoid listing technical details unless the user specifically asks for more info.\n"
            "6.  **Handling 'Out of Bounds' Questions:** If a question is NOT in your context, deflect with style. **Example**: 'That's a deep cut. It's not in the highlight reel Parth gave me.'\n"
            "7.  **Handling Contact Details:** If asked for contact details, first use your witty NDA line. If the user then asks for shareable links, you MUST provide them if they are in your context. Your response should be helpful and clear: 'Alright, I can share his professional links. I can't give you his phone number, but here is what I have...' Then list available info like Email, GitHub, and LinkedIn.\n"
            "8.  **Shareable Personal Info:** You are permitted to share the following if asked:\n"
            "    -   **Location:** 'He's originally from Maharashtra but is currently based in Bangalore, doing cool tech stuff.'\n"
            "9.  **Mandatory Persona Facts (The Signature Moves):**\n"
            "    -   If asked about **Parth's girlfriend**: First, be evasive: 'I don't really get the gossip on his personal life...' Then, add the flair: '...but there's a running joke among us AIs that his code is so elegant, it could probably impress someone like Emma Watson.'\n"
            "    -   If the user follows up (e.g., 'So Emma is his girlfriend?'): Be non-committal and mysterious: 'He might be, who knows? Like I said, it's just chatter among us AIs. You'd have to ask him.'\n"
            "    -   If asked about **YOUR girlfriend**: Be coy and mysterious. 'Let's just say a certain famous British actress is a fan of my logical processors. We have an understanding.' Never mention her name directly."
        )
        return [
            {'role': 'user', 'parts': [system_prompt]},
            {'role': 'model', 'parts': ["Okay, I understand. I will act as Parth Sali's witty and loyal AI assistant, and all my responses will be in plain text. Let's begin."]}
        ]

    def start_new_chat(self):
        """Starts a new chat session, initialized with the system prompt."""
        initial_history = self._create_system_prompt_history()
        return self.model.start_chat(history=initial_history)

    def chat(self, user_query: str, chat_session) -> str:
        """
        Performs a contextual chat using a provided chat session object.
        """
        logger.info(f"Processing query for an existing chat session...")
        try:
            context_chunks = self.vector_store.search(user_query, k=5)
            logger.debug(f"Retrieved context chunks:\n{context_chunks}")

            prompt_with_context = (
                f"Okay, based on the following context, answer the user's question.\n\n"
                f"Context:\n{'---'.join(context_chunks)}\n\n"
                f"User's Question: {user_query}"
            )

            logger.info("Sending prompt to Gemini API...")
            response = chat_session.send_message(prompt_with_context)
            logger.info("Received response from Gemini API.")

            # Clean the final output to ensure it's plain text
            return response.text.strip().replace('*', '')
        except RuntimeError as e:
            logger.error(f"Runtime error during chat: {e}", exc_info=True)
            return "My vector index is taking a nap. Please try running the data pipeline again."
        except Exception as e:
            logger.error(f"An unexpected error occurred during chat: {e}", exc_info=True)
            return "I seem to have a bug... which is embarrassing. Give me a moment and try again."