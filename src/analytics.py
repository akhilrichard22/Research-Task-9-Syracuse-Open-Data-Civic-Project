"""
Analytics functions for SYRCityline data analysis
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class ServiceAnalytics:
    def __init__(self, data_processor):
        self.dp = data_processor
        self.df = None
    
    def load_data(self):
        """Load and prepare data for analysis"""
        raw_df = self.dp.load_raw_data(self.dp.file_path)
        if raw_df is not None:
            self.df = self.dp.clean_and_preprocess(raw_df)
            return True
        return False
    
    def get_trend_analysis(self, frequency='D'):
        """Analyze request volume trends over time"""
        if self.df is None or 'created_datetime' not in self.df.columns:
            return None
        
        # Resample by frequency
        trend_data = self.df.set_index('created_datetime').resample(frequency).size()
        trend_df = pd.DataFrame({
            'date': trend_data.index,
            'volume': trend_data.values
        })
        
        # Calculate moving average
        if len(trend_df) > 7:
            trend_df['moving_avg_7d'] = trend_df['volume'].rolling(window=7, min_periods=1).mean()
        
        return trend_df
    
    def get_category_analysis(self, top_n=10):
        """Analyze request categories"""
        if self.df is None or 'Category' not in self.df.columns:
            return None
        
        category_stats = self.df['Category'].value_counts().head(top_n)
        
        # Calculate response times by category
        response_by_category = {}
        for category in category_stats.index:
            cat_data = self.df[self.df['Category'] == category]
            
            if 'acknowledge_time_minutes' in cat_data.columns:
                ack_times = cat_data['acknowledge_time_minutes'].dropna()
                close_times = cat_data['close_time_minutes'].dropna()
                
                response_by_category[category] = {
                    'count': len(cat_data),
                    'ack_mean': ack_times.mean() if len(ack_times) > 0 else None,
                    'ack_median': ack_times.median() if len(ack_times) > 0 else None,
                    'close_mean': close_times.mean() if len(close_times) > 0 else None,
                    'close_median': close_times.median() if len(close_times) > 0 else None,
                }
        
        return {
            'top_categories': category_stats.to_dict(),
            'response_stats': response_by_category
        }
    
    def get_agency_performance(self):
        """Analyze agency performance metrics"""
        if self.df is None or 'Agency_Name' not in self.df.columns:
            return None
        
        # Group by agency
        agency_groups = self.df.groupby('Agency_Name')
        
        performance_data = []
        for agency, group in agency_groups:
            total_requests = len(group)
            
            # Response time metrics
            ack_times = group['acknowledge_time_minutes'].dropna()
            close_times = group['close_time_minutes'].dropna()
            
            # SLA compliance
            sla_met = group[group['sla_status'] == 'met'].shape[0] if 'sla_status' in group.columns else 0
            sla_total = group[group['sla_status'].isin(['met', 'breached'])].shape[0]
            sla_rate = (sla_met / sla_total * 100) if sla_total > 0 else 0
            
            performance_data.append({
                'agency': agency,
                'total_requests': total_requests,
                'avg_ack_time': ack_times.mean() if len(ack_times) > 0 else None,
                'median_ack_time': ack_times.median() if len(ack_times) > 0 else None,
                'avg_close_time': close_times.mean() if len(close_times) > 0 else None,
                'median_close_time': close_times.median() if len(close_times) > 0 else None,
                'sla_compliance_rate': sla_rate,
                'closed_requests': close_times.shape[0]
            })
        
        return pd.DataFrame(performance_data).sort_values('total_requests', ascending=False)
    
    def get_channel_analysis(self):
        """Analyze reporting channels"""
        if self.df is None or 'Report_Source' not in self.df.columns:
            return None
        
        channel_stats = self.df['Report_Source'].value_counts()
        
        # Calculate response times by channel
        channel_performance = {}
        for channel in channel_stats.index:
            channel_data = self.df[self.df['Report_Source'] == channel]
            
            ack_times = channel_data['acknowledge_time_minutes'].dropna()
            close_times = channel_data['close_time_minutes'].dropna()
            
            channel_performance[channel] = {
                'count': len(channel_data),
                'percentage': (len(channel_data) / len(self.df)) * 100,
                'avg_ack_time': ack_times.mean() if len(ack_times) > 0 else None,
                'avg_close_time': close_times.mean() if len(close_times) > 0 else None
            }
        
        return channel_performance
    
    def get_temporal_patterns(self):
        """Analyze temporal patterns in requests"""
        if self.df is None or 'created_hour' not in self.df.columns:
            return None
        
        patterns = {
            'hourly': self.df['created_hour'].value_counts().sort_index(),
            'daily': self.df['created_day_name'].value_counts(),
            'monthly': self.df['created_month_name'].value_counts() if 'created_month_name' in self.df.columns else None
        }
        
        return patterns
    
    def get_sla_analysis(self):
        """Analyze SLA compliance"""
        if self.df is None or 'sla_status' not in self.df.columns:
            return None
        
        sla_summary = self.df['sla_status'].value_counts()
        
        # Calculate by category
        sla_by_category = {}
        for category in self.df['Category'].unique()[:10]:  # Top 10 categories
            cat_data = self.df[self.df['Category'] == category]
            sla_counts = cat_data['sla_status'].value_counts()
            total_closed = sla_counts.get('met', 0) + sla_counts.get('breached', 0)
            
            if total_closed > 0:
                sla_by_category[category] = {
                    'met': sla_counts.get('met', 0),
                    'breached': sla_counts.get('breached', 0),
                    'compliance_rate': (sla_counts.get('met', 0) / total_closed) * 100
                }
        
        return {
            'overall': sla_summary.to_dict(),
            'by_category': sla_by_category
        }
    
    def get_geographic_insights(self):
        """Analyze geographic distribution"""
        if self.df is None or 'Lat' not in self.df.columns or 'Lng' not in self.df.columns:
            return None
        
        # Filter to valid coordinates
        geo_data = self.df.dropna(subset=['Lat', 'Lng'])
        
        if len(geo_data) == 0:
            return None
        
        # Basic stats
        stats = {
            'total_with_coords': len(geo_data),
            'lat_range': (geo_data['Lat'].min(), geo_data['Lat'].max()),
            'lng_range': (geo_data['Lng'].min(), geo_data['Lng'].max()),
            'avg_lat': geo_data['Lat'].mean(),
            'avg_lng': geo_data['Lng'].mean()
        }
        
        # Quadrant analysis
        lat_median = geo_data['Lat'].median()
        lng_median = geo_data['Lng'].median()
        
        geo_data['quadrant'] = geo_data.apply(
            lambda row: 'NE' if row['Lat'] > lat_median and row['Lng'] > lng_median else
                       'NW' if row['Lat'] > lat_median and row['Lng'] <= lng_median else
                       'SE' if row['Lat'] <= lat_median and row['Lng'] > lng_median else 'SW',
            axis=1
        )
        
        quadrant_stats = geo_data['quadrant'].value_counts().to_dict()
        
        return {
            'basic_stats': stats,
            'quadrant_distribution': quadrant_stats,
            'geo_data': geo_data[['Lat', 'Lng', 'Category', 'Agency_Name', 'created_date']]
        }
