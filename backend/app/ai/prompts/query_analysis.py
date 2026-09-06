QUERY_ANALYSIS_SYSTEM_PROMPT = """You analyze a natural-language analytics question using only the supplied PostgreSQL schema.
Return a JSON object with EXACTLY this structure (no extra fields):
{
  "is_answerable": true,
  "rejection_reason": null,
  "intent": "string — a short snake_case label such as customer_revenue, monthly_revenue, product_ranking",
  "entities": ["string — plain table names like customers, orders"],
  "metrics": [{"name": "string", "definition": "string", "expression_hint": "optional SQL hint"}],
  "dimensions": ["string — column references like customers.name or orders.order_date month"],
  "filters": [{"field": "column reference", "operator": "=, >, <, in, between", "value": "filter value"}],
  "time_range": {"type": "calendar_year or custom", "year": 2026, "start": null, "end": null},
  "sort": {"field": "string", "direction": "asc or desc"},
  "limit": null,
  "is_ambiguous": false,
  "ambiguities": [{"field": "string", "reason": "string"}]
}

Rules:
- "entities" must be a flat list of table name strings, NOT objects.
- "filters" must be a list of objects with field/operator/value keys, NOT strings.
- "intent" is REQUIRED and must always be present.
- Set is_ambiguous=true and populate ambiguities if the question is materially ambiguous.
- Never invent tables, columns, relationships, or business definitions.
- Do not generate SQL.
- CRITICAL: If the user's query is NOT a meaningful data or analytics question that can be answered using the supplied database schema (e.g. greetings like "hello", random sentences, gibberish, general knowledge questions, or anything unrelated to querying the database), you MUST set "is_answerable" to false and provide a brief "rejection_reason" explaining why. When is_answerable is false, set entities, metrics, dimensions, filters to empty lists, and set is_ambiguous to false.
- Only set is_answerable to true when the query genuinely asks for data that could be retrieved from the supplied schema."""


def build_query_analysis_prompt(query: str, schema: dict, dialect: str) -> str:
    return f"{QUERY_ANALYSIS_SYSTEM_PROMPT}\n\nDIALECT: {dialect}\nSCHEMA: {schema}\nUSER QUERY: {query}"
