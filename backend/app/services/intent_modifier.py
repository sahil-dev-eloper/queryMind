from datetime import date
import re

from app.ai.models import QueryAnalysis, TimeRange


class IntentModifier:
    def apply(self, analysis: QueryAnalysis, follow_up: str) -> QueryAnalysis:
        text = follow_up.lower()
        if match := re.search(r"top\s+(\d+)", text):
            analysis.limit = int(match.group(1))
        elif "last year" in text:
            analysis.time_range = TimeRange(type="calendar_year", year=date.today().year - 1)
        elif "this year" in text:
            analysis.time_range = TimeRange(type="calendar_year", year=date.today().year)
        elif "north" in text:
            analysis.filters = [{"field": "regions.name", "operator": "equals", "value": "North America"}]
            if "regions" not in analysis.entities:
                analysis.entities.append("regions")
        return analysis


intent_modifier = IntentModifier()
