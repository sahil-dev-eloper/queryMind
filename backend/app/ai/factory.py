from app.ai.mock_provider import MockAIProvider
from app.ai.openai_provider import OpenAIProvider
from app.ai.provider import AIProvider
from app.core.config import settings


def get_ai_provider() -> AIProvider:
    if settings.ai_provider.lower() == "openai":
        if not settings.ai_api_key or not settings.ai_model:
            raise ValueError("AI_PROVIDER=openai requires AI_API_KEY and AI_MODEL.")
        return OpenAIProvider()
    return MockAIProvider()
