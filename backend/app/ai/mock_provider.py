from datetime import date

from app.ai.models import Ambiguity, Metric, QueryAnalysis, SQLGenerationResult, SortSpec, TimeRange
from app.ai.provider import AIProvider


class MockAIProvider(AIProvider):
    async def analyze_query(self, query: str, schema: dict, dialect: str) -> QueryAnalysis:
        text = query.lower()
        if "active" in text:
            return QueryAnalysis(intent="customer_status", entities=["customers"], is_ambiguous=True, ambiguities=[Ambiguity(field="definition", reason="The schema does not define what makes a customer active.")])
        if "best" in text or "good" in text:
            entity = "products" if "product" in text else "customers"
            return QueryAnalysis(intent=f"{entity}_ranking", entities=[entity], is_ambiguous=True, ambiguities=[Ambiguity(field="metric", reason="The term 'best' could refer to revenue, order count, profit, or another metric.")])
        year = next((int(token) for token in text.split() if token.isdigit() and len(token) == 4), date.today().year)
        if "month" in text or "monthly" in text:
            return QueryAnalysis(intent="monthly_revenue", entities=["orders"], metrics=[Metric(name="revenue", definition="sum of order total amount", expression_hint="SUM(orders.total_amount)")], dimensions=["orders.order_date month"], time_range=TimeRange(type="calendar_year", year=year), sort=SortSpec(field="month", direction="asc"))
        return QueryAnalysis(intent="customer_revenue", entities=["customers", "orders"], metrics=[Metric(name="revenue", definition="sum of order total amount", expression_hint="SUM(orders.total_amount)")], dimensions=["customers.name"], time_range=TimeRange(type="calendar_year", year=year), sort=SortSpec(field="revenue", direction="desc"), limit=10)

    async def generate_sql(self, query: str, analysis: QueryAnalysis, schema: dict, dialect: str) -> SQLGenerationResult:
        year = analysis.time_range.year if analysis.time_range and analysis.time_range.year else date.today().year
        if analysis.intent == "monthly_revenue":
            sql = f"SELECT DATE_TRUNC('month', o.order_date)::date AS month, SUM(o.total_amount) AS revenue FROM orders o WHERE o.order_date >= '{year}-01-01' AND o.order_date < '{year + 1}-01-01' GROUP BY 1 ORDER BY 1;"
            return SQLGenerationResult(sql=sql, explanation="This query groups order revenue by calendar month.", tables_used=["orders"])
        if "products" in analysis.entities:
            sql = f"SELECT p.name AS product_name, SUM(oi.quantity * oi.unit_price) AS total_revenue FROM products p JOIN order_items oi ON p.id = oi.product_id JOIN orders o ON o.id = oi.order_id WHERE o.order_date >= '{year}-01-01' AND o.order_date < '{year + 1}-01-01' GROUP BY p.id, p.name ORDER BY total_revenue DESC LIMIT {analysis.limit or 10};"
            return SQLGenerationResult(sql=sql, explanation="This query joins products, order items, and orders and calculates total product revenue.", tables_used=["products", "order_items", "orders"])
        region_join = " JOIN regions r ON r.id = c.region_id" if any(item.get("field") == "regions.name" for item in analysis.filters) else ""
        region_filter = " AND r.name = 'North America'" if region_join else ""
        sql = f"SELECT c.name AS customer_name, SUM(o.total_amount) AS total_revenue FROM customers c JOIN orders o ON c.id = o.customer_id{region_join} WHERE o.order_date >= '{year}-01-01' AND o.order_date < '{year + 1}-01-01'{region_filter} GROUP BY c.id, c.name ORDER BY total_revenue DESC LIMIT {analysis.limit or 10};"
        return SQLGenerationResult(sql=sql, explanation="This query joins customers and orders and calculates total revenue per customer.", tables_used=["customers", "orders"])
