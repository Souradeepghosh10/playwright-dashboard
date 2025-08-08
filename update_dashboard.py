import os
import json
from datetime import datetime
from jinja2 import Template

# Folder containing date-wise test reports
data_folder = "Reports"
report_data = {}

# Ensure Reports folder exists to avoid FileNotFoundError
if not os.path.exists(data_folder):
    print(f"⚠️ '{data_folder}' folder not found. Exiting.")
    exit(0)

# Filter and sort only valid date folders (format: YYYY-MM-DD), newest first
date_folders = [
    d for d in os.listdir(data_folder)
    if os.path.isdir(os.path.join(data_folder, d))
    and len(d) == 10
    and d[4] == '-'
    and d[7] == '-'
]

sorted_dates = sorted(date_folders, key=lambda d: datetime.strptime(d, "%Y-%m-%d"), reverse=True)

# Collect passed/failed counts from each report.json
for date_dir in sorted_dates:
    full_path = os.path.join(data_folder, date_dir, "report.json")
    if os.path.exists(full_path):
        with open(full_path, "r") as f:
            data = json.load(f)
        passed = sum(1 for test in data["suites"][0]["specs"] if test.get("status") == "passed")
        failed = sum(1 for test in data["suites"][0]["specs"] if test.get("status") == "failed")
        report_data[date_dir] = {"passed": passed, "failed": failed}

# Jinja2 HTML Template
template_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Playwright Test Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        h1 { color: #333; }
        ul { list-style: none; padding: 0; }
        li { margin: 8px 0; }
        a { text-decoration: none; font-weight: bold; color: #007acc; }
    </style>
</head>
<body>
    <h1>📊 Playwright Test Dashboard</h1>
    <h2>📅 Daily Reports (Last {{ report_data|length }} Days)</h2>
    <ul>
    {% for date, stats in report_data.items() %}
        <li>
            <a href="Reports/{{ date }}/html-report/index.html" target="_blank">{{ date }}</a>
            &nbsp;✅ {{ stats.passed }} ❌ {{ stats.failed }}
        </li>
    {% endfor %}
    </ul>
</body>
</html>
"""

# Render and write to index.html
template = Template(template_html)
rendered = template.render(report_data=report_data)

with open("index.html", "w") as f:
    f.write(rendered)

print("✅ Dashboard generated successfully.")
