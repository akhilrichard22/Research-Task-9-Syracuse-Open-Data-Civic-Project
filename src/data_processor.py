"""
Data loading and preprocessing module for SYRCityline data
"""
import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st

class DataProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def load_raw_data(_self, file_path):
        """Load raw CSV data with caching"""
        try:
            df = pd.read_csv(file_path)
            print(f"Loaded {len(df)} records from {file_path}")
            return df
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return None
    
    def parse_datetime(self, date_str):
        """Parse SYRCityline datetime format"""
        if pd.isna(date_str):
            return pd.NaT
        
        try:
            # Handle format: "01/14/2025 - 11:19AM"
            date_str = str(date_str).strip()
            if ' - ' in date_str:
                date_part, time_part = date_str.split(' - ')
                return pd.to_datetime(f"{date_part} {time_part}", 
                                     format='%m/%d/%Y %I:%M%p', errors='coerce')
            else:
                return pd.to_datetime(date_str, errors='coerce')
        except:
            return pd.NaT
    
    def clean_and_preprocess(self, df):
        """Clean and preprocess the dataset"""
        # Make a copy to avoid modifying the original
        df_clean = df.copy()
        
        # Clean column names
        df_clean.columns = [col.strip().replace(' ', '_') for col in df_clean.columns]
        
        # Parse datetime columns
        date_columns = ['Created_at_local', 'Acknowledged_at_local', 'Closed_at_local']
        for col in date_columns:
            if col in df_clean.columns:
                df_clean[f'{col}_parsed'] = df_clean[col].apply(self.parse_datetime)
        
        # Create analysis columns
        if 'Created_at_local_parsed' in df_clean.columns:
            df_clean['created_datetime'] = df_clean['Created_at_local_parsed']
            df_clean['created_date'] = df_clean['created_datetime'].dt.date
            df_clean['created_year'] = df_clean['created_datetime'].dt.year
            df_clean['created_month'] = df_clean['created_datetime'].dt.month
            df_clean['created_day'] = df_clean['created_datetime'].dt.day
            df_clean['created_dayofweek'] = df_clean['created_datetime'].dt.dayofweek
            df_clean['created_hour'] = df_clean['created_datetime'].dt.hour
            df_clean['created_day_name'] = df_clean['created_datetime'].dt.day_name()
            df_clean['created_month_name'] = df_clean['created_datetime'].dt.month_name()
        
        # Calculate response times
        if 'Acknowledged_at_local_parsed' in df_clean.columns and 'Created_at_local_parsed' in df_clean.columns:
            df_clean['acknowledge_time_minutes'] = (
                df_clean['Acknowledged_at_local_parsed'] - df_clean['Created_at_local_parsed']
            ).dt.total_seconds() / 60
        
        if 'Closed_at_local_parsed' in df_clean.columns and 'Created_at_local_parsed' in df_clean.columns:
            df_clean['close_time_minutes'] = (
                df_clean['Closed_at_local_parsed'] - df_clean['Created_at_local_parsed']
            ).dt.total_seconds() / 60
        
        # Convert numeric columns
        numeric_cols = ['Minutes_to_Acknowledge', 'Minutes_to_Close', 'Sla_in_hours', 'Lat', 'Lng']
        for col in numeric_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # Create SLA status
        if 'Sla_in_hours' in df_clean.columns and 'close_time_minutes' in df_clean.columns:
            df_clean['sla_status'] = df_clean.apply(
                lambda row: 'met' if row['close_time_minutes'] <= (row['Sla_in_hours'] * 60) 
                else 'breached' if pd.notna(row['close_time_minutes']) 
                else 'pending', axis=1
            )
        
        # Clean text columns
        text_columns = ['Category', 'Agency_Name', 'Summary', 'Assignee_name']
        for col in text_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype(str).str.strip()
        
        print(f"Cleaned dataset shape: {df_clean.shape}")
        return df_clean
    
    def get_data_summary(self, df):
        """Generate summary statistics for the dataset"""
        summary = {
            'total_records': len(df),
            'date_range': (df['created_datetime'].min(), df['created_datetime'].max()),
            'unique_categories': df['Category'].nunique(),
            'unique_agencies': df['Agency_Name'].nunique(),
            'closed_requests': df['Closed_at_local_parsed'].notna().sum(),
            'acknowledged_requests': df['Acknowledged_at_local_parsed'].notna().sum(),
            'pending_requests': df['Closed_at_local_parsed'].isna().sum(),
        }
        return summary
    
    def filter_data(self, df, filters):
        """Apply filters to the dataset"""
        df_filtered = df.copy()
        
        # Date range filter
        if 'date_range' in filters and filters['date_range']:
            start_date, end_date = filters['date_range']
            if start_date and end_date:
                df_filtered = df_filtered[
                    (df_filtered['created_date'] >= start_date) & 
                    (df_filtered['created_date'] <= end_date)
                ]
        
        # Category filter
        if 'categories' in filters and filters['categories']:
            df_filtered = df_filtered[df_filtered['Category'].isin(filters['categories'])]
        
        # Agency filter
        if 'agencies' in filters and filters['agencies']:
            df_filtered = df_filtered[df_filtered['Agency_Name'].isin(filters['agencies'])]
        
        # Status filter
        if 'status' in filters and filters['status']:
            if filters['status'] == 'closed':
                df_filtered = df_filtered[df_filtered['Closed_at_local_parsed'].notna()]
            elif filters['status'] == 'open':
                df_filtered = df_filtered[df_filtered['Closed_at_local_parsed'].isna()]
        
        return df_filtered
