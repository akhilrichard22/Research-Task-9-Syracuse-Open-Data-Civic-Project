"""
Unit tests for the analytics module
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_processor import DataProcessor
from src.analytics import ServiceAnalytics

class TestServiceAnalytics:
    def setup_method(self):
        """Set up test data"""
        # Create sample data for testing
        self.sample_data = pd.DataFrame({
            'Created_at_local': ['01/01/2025 - 09:00AM', '01/01/2025 - 10:00AM', '01/02/2025 - 11:00AM'],
            'Acknowledged_at_local': ['01/01/2025 - 09:30AM', '01/01/2025 - 10:30AM', '01/02/2025 - 11:30AM'],
            'Closed_at_local': ['01/01/2025 - 10:00AM', '01/01/2025 - 11:00AM', '01/02/2025 - 12:00PM'],
            'Category': ['Potholes', 'Street Lights', 'Potholes'],
            'Agency_Name': ['Public Works', 'Public Works', 'Transportation'],
            'Report_Source': ['iPhone', 'Android', 'Portal'],
            'Minutes_to_Acknowledge': [30, 30, 30],
            'Minutes_to_Close': [60, 60, 60],
            'Sla_in_hours': [24, 24, 24],
            'Lat': [43.0, 43.1, 43.2],
            'Lng': [-76.0, -76.1, -76.2]
        })
        
        # Create processor and analytics objects
        self.processor = DataProcessor("test_path.csv")
        self.analytics = ServiceAnalytics(self.processor)
        self.analytics.df = self.processor.clean_and_preprocess(self.sample_data)
    
    def test_data_loading(self):
        """Test data loading and preprocessing"""
        assert self.analytics.df is not None
        assert len(self.analytics.df) == 3
        assert 'created_datetime' in self.analytics.df.columns
        assert 'acknowledge_time_minutes' in self.analytics.df.columns
    
    def test_trend_analysis(self):
        """Test trend analysis function"""
        trend_data = self.analytics.get_trend_analysis('D')
        assert trend_data is not None
        assert 'date' in trend_data.columns
        assert 'volume' in trend_data.columns
        assert len(trend_data) > 0
    
    def test_category_analysis(self):
        """Test category analysis function"""
        category_data = self.analytics.get_category_analysis(5)
        assert category_data is not None
        assert 'top_categories' in category_data
        assert 'response_stats' in category_data
        assert len(category_data['top_categories']) <= 5
    
    def test_agency_performance(self):
        """Test agency performance analysis"""
        performance_df = self.analytics.get_agency_performance()
        assert performance_df is not None
        assert 'agency' in performance_df.columns
        assert 'total_requests' in performance_df.columns
        assert len(performance_df) > 0
    
    def test_channel_analysis(self):
        """Test channel analysis function"""
        channel_data = self.analytics.get_channel_analysis()
        assert channel_data is not None
        assert len(channel_data) > 0
        # Check that each channel has expected keys
        for channel, data in channel_data.items():
            assert 'count' in data
            assert 'percentage' in data
    
    def test_sla_analysis(self):
        """Test SLA analysis function"""
        sla_data = self.analytics.get_sla_analysis()
        assert sla_data is not None
        assert 'overall' in sla_data
        assert 'by_category' in sla_data
    
    def test_filter_data(self):
        """Test data filtering"""
        filters = {
            'categories': ['Potholes'],
            'agencies': ['Public Works']
        }
        
        filtered = self.processor.filter_data(self.analytics.df, filters)
        assert len(filtered) == 1  # Only one record matches both filters
    
    def test_data_summary(self):
        """Test data summary generation"""
        summary = self.processor.get_data_summary(self.analytics.df)
        assert summary is not None
        assert 'total_records' in summary
        assert 'date_range' in summary
        assert summary['total_records'] == 3

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
