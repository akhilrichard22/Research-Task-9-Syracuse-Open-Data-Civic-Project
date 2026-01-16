"""
Configuration settings for Syracuse Service Request Analyzer
"""

# File paths
RAW_DATA_PATH = "data/raw/SYRCityline_Requests_2021_Present.csv"
PROCESSED_DATA_PATH = "data/processed/service_requests.parquet"

# Dashboard settings
DASHBOARD_TITLE = "Syracuse Service Request Trends Analyzer"
DASHBOARD_DESCRIPTION = "Interactive analysis of SYRCityline 311 service requests"

# Analysis settings
TOP_N_CATEGORIES = 15
TOP_N_AGENCIES = 10
DATE_FORMAT = "%m/%d/%Y - %I:%M%p"

# Color schemes
CATEGORY_COLORS = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
]

# Time thresholds (in minutes)
ACKNOWLEDGEMENT_THRESHOLDS = {
    'immediate': 60,      # < 1 hour
    'quick': 240,         # 1-4 hours
    'moderate': 1440,     # 4-24 hours
    'slow': 10080         # > 24 hours
}

# SLA categories
SLA_CATEGORIES = {
    'met': 'SLA Met',
    'warning': 'Approaching SLA',
    'breached': 'SLA Breached'
}
