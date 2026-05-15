import asyncio
from .config import (
    MODEL_PROVIDER, 
    MODEL_NAME, 
    GOOGLE_API_KEY, 
    OPENAI_API_KEY, 
    ANTHROPIC_API_KEY
)
from .env_setup import apply_env


def get_deepeval_llm():
    """Factory for DeepEval judge models."""
    apply_env()
    provider = MODEL_PROVIDER.lower()

    if provider == "google":
        try:
            from deepeval.models import GeminiModel
            return GeminiModel(model=MODEL_NAME, api_key=GOOGLE_API_KEY, temperature=0)
        except Exception:
            return _get_fallback_gemini(MODEL_NAME)
            
    elif provider == "openai":
        from deepeval.models import GPTModel
        return GPTModel(model=MODEL_NAME, api_key=OPENAI_API_KEY, temperature=0)
        
    elif provider == "anthropic":
        from deepeval.models import AnthropicModel
        return AnthropicModel(model=MODEL_NAME, api_key=ANTHROPIC_API_KEY, temperature=0)
        
    else:
        # For Ollama or other custom providers in DeepEval
        from deepeval.models.base_model import DeepEvalBaseLLM
        
        class CustomDeepEvalLLM(DeepEvalBaseLLM):
            def __init__(self, model_name: str):
                self.model_name = model_name
                from .models import _instantiate_llm
                self.llm = _instantiate_llm(MODEL_PROVIDER, model_name)

            def load_model(self):
                return self.llm

            def generate(self, prompt: str, schema=None):
                res = self.llm.invoke(prompt)
                return res.content

            async def a_generate(self, prompt: str, schema=None):
                res = await self.llm.ainvoke(prompt)
                return res.content

            def get_model_name(self):
                return self.model_name
                
        return CustomDeepEvalLLM(MODEL_NAME)


def _get_fallback_gemini(model_name: str):
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

    return GeminiDeepEvalFallback(model_name)
