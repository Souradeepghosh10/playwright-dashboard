name: Update Dashboard

on:
  push:
    paths:
      - 'Reports/**'

permissions:
  contents: read  # read access still required to checkout

jobs:
  update:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11

      - name: Install dependencies
        run: pip install jinja2

      - name: Generate dashboard
        run: python update_dashboard.py

      - name: Commit and push dashboard
        run: |
          git config user.email "github-actions@github.com"
          git config user.name "github-actions"
          git add index.html
          git commit -m "Update dashboard"
          git push https://x-access-token:${{ secrets.GH_PAT }}@github.com/Souradeepghosh10/playwright-dashboard.git HEAD:${{ github.ref }}
