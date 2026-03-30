# Parliview Benchmarks Viewer

A Streamlit application for viewing and evaluating benchmark results from the Parliview research system.

## Features

- View benchmark questions and answers
- Explore research process phases, tools, and sources
- Rate responses on completeness/correctness and satisfaction
- Collect feedback with comments
- Navigate through multiple responses per question

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the app:
```bash
streamlit run app.py
```

## Data

The app expects a CSV file named `benchmark_results_1.csv` in the root directory with the following columns:
- `question` - The benchmark question
- `overall_summary` - The answer/response
- `status` - Status of the request (completed, failed, etc.)
- `duration_seconds` - Time taken to generate the response
- `captured_sse_events` - JSON string containing research process events

## Deployment

This app can be deployed on Streamlit Cloud. Make sure to:
1. Push your code to GitHub
2. Connect your GitHub repository to Streamlit Cloud
3. Ensure `benchmark_results_1.csv` is included in the repository
