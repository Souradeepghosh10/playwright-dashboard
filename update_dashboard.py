import os
import json
from datetime import datetime
from jinja2 import Template

data_folder = "data"
report_data = {}

# Scan all folders inside `data/` (e.g., '2025-08-07', '2025-08-08', etc.)
for date_dir in sorted(os.listdir(data_folder)):
    full_path = os.path.join(data_folder, date_dir, "report.json")
    if os.path.exists(full_path):
        with open(full_path, "r") as f:
            data = json.load(f)
        passed = sum(1 for test in data["suites"][0]["specs"] if test["status"] == "passed")
        failed = sum(1 for test in data["suites"][0]["specs"] if test["status"] == "failed")
        report_data[date_dir] = {"passed": passed, "failed": failed}

# Template rendering
template_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Playwright Test Dashboard</title>
</head>
<body>
    <h1>📊 Playwright Test Dashboard</h1>
    <h2>📅 Daily Reports</h2>
    <ul>
    {% for date, stats in report_data.items() %}
        <li>
            <a href="data/{{ date }}/index.html">{{ date }}</a>
            ✅ {{ stats.passed }} ❌ {{ stats.failed }}
        </li>
    {% endfor %}
    </ul>
</body>
</html>
"""

template = Template(template_html)
rendered = template.render(report_data=report_data)

with open("index.html", "w") as f:
    f.write(rendered)

print("✅ Dashboard generated with updated report links.")
