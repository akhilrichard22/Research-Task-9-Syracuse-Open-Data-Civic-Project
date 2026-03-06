# Syracuse Service Request Trends Analyzer

An interactive dashboard for analyzing SYRCityline (311) service requests in Syracuse, NY. Built with Streamlit and Plotly, this tool helps residents and city officials understand request patterns, department performance, and service trends.

![Dashboard Screenshot](screenshot.png) <!-- Add a screenshot of your dashboard -->

## Features

- **Trends Over Time**: View daily request volume with 7-day moving average.
- **Department Performance**: Compare agencies by workload, response times, and SLA compliance.
- **Reporting Channels**: Analyze how residents submit requests (mobile, web, phone).
- **SLA Compliance**: Monitor Service Level Agreement adherence and identify at-risk requests.
- **Geographic Analysis**: Explore request distribution across Syracuse.
- **Category Insights**: Dive into the most common request types.

## Live Demo

[Insert link to hosted version if available]

## Quick Start

### Prerequisites
- Python 3.9 or higher
- pip

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/[your-username]/syracuse-311-analyzer.git
   cd syracuse-311-analyzer
   python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt

streamlit run src/dashboard.py
