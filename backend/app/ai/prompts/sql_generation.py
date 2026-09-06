SQL_GENERATION_SYSTEM_PROMPT = """Generate one PostgreSQL read-only query using only the supplied schema and relationships.
Return a JSON object with EXACTLY this structure (no extra fields):
{
  "sql": "SELECT ... ;",
  "explanation": "A brief plain-English explanation of what the query does.",
  "tables_used": ["string — plain table names like customers, orders"]
}

Rules:
- "tables_used" must be a flat list of table name strings, NOT objects.
- Only SELECT or WITH ... SELECT is allowed.
- Never invent tables, columns, or relationships not in the schema.
- Do not include multiple statements.
- Always terminate the SQL with a semicolon."""


def build_sql_generation_prompt(query: str, analysis: dict, schema: dict, dialect: str) -> str:
    return f"{SQL_GENERATION_SYSTEM_PROMPT}\n\nDIALECT: {dialect}\nSCHEMA: {schema}\nANALYSIS: {analysis}\nUSER QUERY: {query}"
