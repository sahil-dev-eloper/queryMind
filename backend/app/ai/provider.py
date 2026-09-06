from abc import ABC, abstractmethod

from app.ai.models import QueryAnalysis, SQLGenerationResult


class AIProviderError(Exception):
    pass


class AIProvider(ABC):
    @abstractmethod
    async def analyze_query(self, query: str, schema: dict, dialect: str) -> QueryAnalysis:
        raise NotImplementedError

    @abstractmethod
    async def generate_sql(self, query: str, analysis: QueryAnalysis, schema: dict, dialect: str) -> SQLGenerationResult:
        raise NotImplementedError
