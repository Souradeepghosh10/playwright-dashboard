import os
import json
from datetime import datetime
from jinja2 import Template

reports_dir = "Reports"
output_html = "index.html"
trend_file = "trend.json"

def count_tests_in_suites(suites, seen_tests):
    passed = 0
    failed = 0

    for suite in suites:
        # Count tests directly inside this suite
        for test in suite.get("tests", []):
            test_id = test.get("id") or test.get("title")
            if test_id in seen_tests:
                continue
            seen_tests.add(test_id)
            results = test.get("results", [])
            if not results:
                continue
            final_status = results[-1].get("status")
            if final_status == "passed":
                passed += 1
            elif final_status == "failed":
                failed += 1

        # Count tests inside specs in this suite
        for spec in suite.get("specs", []):
            for test in spec.get("tests", []):
                test_id = test.get("id") or test.get("title")
                if test_id in seen_tests:
                    continue
                seen_tests.add(test_id)
                results = test.get("results", [])
                if not results:
                    continue
                final_status = results[-1].get("status")
                if final_status == "passed":
                    passed += 1
                elif final_status == "failed":
                    failed += 1

        # Recurse into nested suites if any
        if "suites" in suite:
            p, f = count_tests_in_suites(suite["suites"], seen_tests)
            passed += p
            failed += f

    return passed, failed

report_links = []
trend_data = []

for date_folder in sorted(os.listdir(reports_dir)):
    date_path = os.path.join(reports_dir, date_folder)
    if not os.path.isdir(date_path):
        continue

    report_json_path = os.path.join(date_path, "report.json")
    html_report_path = os.path.join(date_path, "html-report", "index.html")

    if os.path.exists(report_json_path) and os.path.exists(html_report_path):
        report_links.append({
            "date": date_folder,
            "html_link": f"{reports_dir}/{date_folder}/html-report/index.html"
        })

        with open(report_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        seen_tests = set()
        passed, failed = count_tests_in_suites(data.get("suites", []), seen_tests)

        trend_data.append({
            "date": date_folder,
            "passed": passed,
            "failed": failed
        })

# Write trend.json
with open(trend_file, "w", encoding="utf-8") as f:
    json.dump(trend_data, f, indent=2)

# Jinja2 HTML template
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
        <li>
            <a href="{{ report.html_link }}" target="_blank">{{ report.date }}</a>
            &nbsp;✅ {{ trend_data[loop.index0].passed }} ❌ {{ trend_data[loop.index0].failed }}
        </li>
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
