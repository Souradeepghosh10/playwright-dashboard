
import os
import json
from datetime import datetime, timedelta
from jinja2 import Template

reports_dir = "Reports"
today = datetime.now().date()
days = [(today - timedelta(days=i)).isoformat() for i in range(30)]
data = []

for day in days:
    path = os.path.join(reports_dir, day, "report.json")
    if os.path.exists(path):
        with open(path) as f:
            report = json.load(f)
            passed = len([t for t in report['suites'][0]['specs'] if t['ok']])
            failed = len([t for t in report['suites'][0]['specs'] if not t['ok']])
            data.append({'date': day, 'passed': passed, 'failed': failed})

# Top unstable logic here later
unstable_tests = [{"name": "Test A", "failures": 5}, {"name": "Test B", "failures": 4}]

with open("templates/index.html") as f:
    template = Template(f.read())

rendered = template.render(trends=data, unstable=unstable_tests, report_days=days)
with open("index.html", "w") as f:
    f.write(rendered)
