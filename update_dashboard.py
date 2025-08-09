import os
import json
from datetime import datetime
from jinja2 import Template

reports_dir = "Reports"
output_html = "index.html"
trend_file = "trend.json"

# --- Step 1: Scan report folders ---
report_links = []
trend_data = []

for date_folder in sorted(os.listdir(reports_dir)):
    date_path = os.path.join(reports_dir, date_folder)
    if not os.path.isdir(date_path):
        continue

    report_json_path = os.path.join(date_path, "report.json")
    html_report_path = os.path.join(date_path, "html-report", "index.html")

    if os.path.exists(report_json_path) and os.path.exists(html_report_path):
        # Link for dashboard
        report_links.append({
            "date": date_folder,
            "html_link": f"{reports_dir}/{date_folder}/html-report/index.html"
        })

        # Step 2: Extract pass/fail counts correctly counting only last result per test
        with open(report_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            passed = 0
            failed = 0
            for suite in data.get("suites", []):
                for spec in suite.get("specs", []):
                    for test in spec.get("tests", []):
                        results = test.get("results", [])
                        if not results:
                            continue
                        last_result = results[-1]  # final result of the test
                        status = last_result.get("status")
                        if status == "passed":
                            passed += 1
                        elif status == "failed":
                            failed += 1

        trend_data.append({
            "date": date_folder,
            "passed": passed,
            "failed": failed
        })

# --- Step 3: Write trend.json ---
with open(trend_file, "w", encoding="utf-8") as f:
    json.dump(trend_data, f, indent=2)

# --- Step 4: Build HTML using Jinja2 ---
template_str = """
<!DOCTYPE html>
<html>
<head>
    <title>Playwright Reports Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>Playwright Reports Dashboard</h1>

    <h2>Test Execution History</h2>
    <ul>
    {% for report in reports %}
        <li><a href="{{ report.html_link }}" target="_blank">{{ report.date }}</a> &nbsp;✅ {{ trend_data[loop.index0].passed }} ❌ {{ trend_data[loop.index0].failed }}</li>
    {% endfor %}
    </ul>

    <h2>Test Trends</h2>
    <canvas id="trendChart" width="800" height="400"></canvas>

    <script>
        const trendData = {{ trend_data | tojson }};
        const labels = trendData.map(d => d.date);
        const passed = trendData.map(d => d.passed);
        const failed = trendData.map(d => d.failed);

        new Chart(document.getElementById('trendChart'), {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Passed',
                        backgroundColor: 'green',
                        data: passed
                    },
                    {
                        label: 'Failed',
                        backgroundColor: 'red',
                        data: failed
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    </script>
</body>
</html>
"""

template = Template(template_str)
html_content = template.render(reports=report_links, trend_data=trend_data)

with open(output_html, "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ Dashboard updated: index.html + trend.json")
