from datetime import date, datetime
from decimal import Decimal


class ResultAnalyzer:
    def analyze(self, columns: list[str], rows: list[list]) -> dict:
        numeric = []
        temporal = []
        categorical = []
        for index, name in enumerate(columns):
            values = [row[index] for row in rows if row[index] is not None]
            if values and all(isinstance(value, (int, float, Decimal)) and not isinstance(value, bool) for value in values):
                numeric.append(name)
            elif values and all(isinstance(value, (date, datetime, str)) for value in values):
                if name.lower() in {"date", "month", "year", "created_at", "order_date"} or "date" in name.lower():
                    temporal.append(name)
                else:
                    categorical.append(name)
        if len(rows) == 1 and len(numeric) == 1:
            visualization = {"type": "KPI", "y": numeric[0]}
        elif temporal and numeric:
            visualization = {"type": "LINE", "x": temporal[0], "y": numeric[0]}
        elif categorical and numeric and len(rows) <= 100:
            visualization = {"type": "BAR", "x": categorical[0], "y": numeric[0]}
        else:
            visualization = {"type": "TABLE"}
        summary = "No results found." if not rows else f"Returned {len(rows)} row{'s' if len(rows) != 1 else ''}."
        if numeric and rows:
            values = [float(row[columns.index(numeric[0])]) for row in rows if row[columns.index(numeric[0])] is not None]
            if values:
                summary += f" {numeric[0]} ranges from {min(values):g} to {max(values):g}."
        return {"row_count": len(rows), "numeric_columns": numeric, "temporal_columns": temporal, "categorical_columns": categorical, "visualization": visualization, "summary": summary}


result_analyzer = ResultAnalyzer()
