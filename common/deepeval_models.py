import asyncio

from .config import GEMINI_MODEL_NAME, GOOGLE_API_KEY
from .env_setup import apply_env


def get_deepeval_llm():
    apply_env()

    try:
        from deepeval.models import GeminiModel

        return GeminiModel(
            model=GEMINI_MODEL_NAME,
            api_key=GOOGLE_API_KEY,
            temperature=0,
        )
    except Exception:
        from deepeval.models.base_model import DeepEvalBaseLLM
        import google.generativeai as genai

        class GeminiDeepEvalFallback(DeepEvalBaseLLM):
            def __init__(self, model_name: str):
                self.model_name = model_name
                genai.configure(api_key=GOOGLE_API_KEY)

            def load_model(self):
                return genai.GenerativeModel(self.model_name)

            def generate(self, prompt: str, schema=None):
                response = self.load_model().generate_content(prompt)
                text = getattr(response, "text", str(response))
                if schema is not None and hasattr(schema, "model_validate_json"):
                    return schema.model_validate_json(text)
                return text

            async def a_generate(self, prompt: str, schema=None):
                return await asyncio.to_thread(self.generate, prompt, schema)

            def get_model_name(self):
                return self.model_name

        return GeminiDeepEvalFallback(GEMINI_MODEL_NAME)
