import csv
from app.services.visual_reporting_service import VisualReportingService

csv_path = "results/benchmark_report.csv"
chart_path = "results/complexity_maintainability_delta.png"

with open(csv_path, newline="", encoding="utf-8") as file:
    records = list(csv.DictReader(file))

if not records:
    raise SystemExit("The benchmark CSV contains no records.")

numeric_fields = [
    "delta_complexity",
    "delta_maintainability_index",
]

for record in records:
    for field in numeric_fields:
        record[field] = float(record[field])

output = VisualReportingService.generate_delta_bar_chart(
    records,
    output_filepath=chart_path,
)

print(f"Chart regenerated successfully: {output}")
print(f"Records plotted: {len(records)}")
print(f"Gemini records: {sum('GeminiProvider' in r['model_name'] for r in records)}")
