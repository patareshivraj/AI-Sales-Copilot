from langchain_groq import ChatGroq
from core.config import config

class LLMService:
    def __init__(self, temperature: float = 0.1, api_key: str = None):
        """
        Initializes the LLM Service abstraction.
        Agents will call these methods instead of directly interacting with Groq or Langchain.
        """
        key_to_use = api_key if api_key is not None else config.GROQ_API_KEY
        self.llm = ChatGroq(
            api_key=key_to_use,
            model_name=config.MODEL_NAME,
            temperature=temperature
        )

    def generate(self, prompt: str) -> str:
        """
        Standard text completion for general queries.
        """
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"API Error: {str(e)}"

    def generate_structured(self, prompt: str, schema_class):
        """
        Structured generation utilizing a Pydantic schema.
        Ensures reliable, machine-readable JSON output.
        """
        try:
            structured_llm = self.llm.with_structured_output(schema_class)
            response = structured_llm.invoke(prompt)
            return response
        except Exception as e:
            return f"API Error: {str(e)}"
