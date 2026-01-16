"""
Visualization components for the dashboard
"""
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import pandas as pd
import numpy as np

class DashboardVisualizations:
    def __init__(self):
        # Set color scheme
        self.color_palette = px.colors.qualitative.Set3
        
    def create_trend_chart(self, trend_data, title="Request Volume Trends"):
        """Create time series trend chart"""
        fig = go.Figure()
        
        # Add volume bars
        fig.add_trace(go.Bar(
            x=trend_data['date'],
            y=trend_data['volume'],
            name='Daily Volume',
            marker_color='lightblue',
            opacity=0.7
        ))
        
        # Add moving average line
        if 'moving_avg_7d' in trend_data.columns:
            fig.add_trace(go.Scatter(
                x=trend_data['date'],
                y=trend_data['moving_avg_7d'],
                name='7-Day Moving Avg',
                line=dict(color='darkblue', width=3),
                mode='lines'
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Date',
            yaxis_title='Number of Requests',
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def create_category_chart(self, category_data, title="Top Request Categories"):
        """Create horizontal bar chart for categories"""
        categories = list(category_data.keys())[:15]
        counts = list(category_data.values())[:15]
        
        fig = go.Figure(go.Bar(
            x=counts,
            y=categories,
            orientation='h',
            marker_color=self.color_palette[:len(categories)],
            text=counts,
            textposition='outside'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Number of Requests',
            yaxis_title='Category',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def create_heatmap(self, df, title="Requests by Day and Hour"):
        """Create heatmap of requests by day and hour"""
        if 'created_day_name' not in df.columns or 'created_hour' not in df.columns:
            return None
        
        # Create pivot table
        pivot_data = df.groupby(['created_day_name', 'created_hour']).size().unstack().fillna(0)
        
        # Reorder days
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        pivot_data = pivot_data.reindex(day_order)
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_data.values,
            x=[f"{h:02d}:00" for h in pivot_data.columns],
            y=pivot_data.index,
            colorscale='YlOrRd',
            colorbar=dict(title='Requests')
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Hour of Day',
            yaxis_title='Day of Week',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def create_performance_chart(self, performance_df, title="Agency Performance"):
        """Create performance comparison chart"""
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=performance_df['agency'],
            y=performance_df['total_requests'],
            name='Total Requests',
            marker_color='lightblue'
        ))
        
        if 'sla_compliance_rate' in performance_df.columns:
            fig.add_trace(go.Scatter(
                x=performance_df['agency'],
                y=performance_df['sla_compliance_rate'],
                name='SLA Compliance %',
                yaxis='y2',
                line=dict(color='darkgreen', width=3),
                mode='lines+markers'
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Agency',
            yaxis_title='Total Requests',
            yaxis2=dict(
                title='SLA Compliance %',
                overlaying='y',
                side='right',
                range=[0, 100]
            ),
            template='plotly_white',
            height=500,
            showlegend=True
        )
        
        return fig
    
    def create_channel_analysis_chart(self, channel_data, title="Reporting Channel Analysis"):
        """Create donut chart for channel distribution"""
        channels = list(channel_data.keys())
        counts = [data['count'] for data in channel_data.values()]
        percentages = [data['percentage'] for data in channel_data.values()]
        
        fig = go.Figure(data=[go.Pie(
            labels=channels,
            values=counts,
            hole=0.3,
            textinfo='label+percent',
            marker_colors=self.color_palette[:len(channels)]
        )])
        
        fig.update_layout(
            title=title,
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def create_sla_chart(self, sla_data, title="SLA Compliance Overview"):
        """Create gauge chart for SLA compliance"""
        if 'overall' not in sla_data:
            return None
        
        met = sla_data['overall'].get('met', 0)
        breached = sla_data['overall'].get('breached', 0)
        total = met + breached
        
        compliance_rate = (met / total * 100) if total > 0 else 0
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=compliance_rate,
            title={'text': "SLA Compliance Rate"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 70], 'color': "red"},
                    {'range': [70, 90], 'color': "yellow"},
                    {'range': [90, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            title=title,
            template='plotly_white',
            height=300
        )
        
        return fig
    
    def create_response_time_chart(self, df, title="Response Time Distribution"):
        """Create histogram of response times"""
        if 'acknowledge_time_minutes' not in df.columns:
            return None
        
        ack_times = df['acknowledge_time_minutes'].dropna()
        
        if len(ack_times) == 0:
            return None
        
        fig = go.Figure()
        
        # Use log scale for better visualization if data is skewed
        fig.add_trace(go.Histogram(
            x=ack_times,
            nbinsx=50,
            name='Acknowledgment Time',
            marker_color='lightblue',
            opacity=0.7
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Minutes to Acknowledge',
            yaxis_title='Frequency',
            template='plotly_white',
            height=400
        )
        
        # Set x-axis to log scale if large range
        if ack_times.max() > 1000:
            fig.update_xaxes(type="log")
        
        return fig
    
    def create_geographic_map(self, geo_data, title="Geographic Distribution"):
        """Create scatter map of requests"""
        if geo_data is None or len(geo_data) == 0:
            return None
        
        fig = px.scatter_mapbox(
            geo_data,
            lat="Lat",
            lon="Lng",
            hover_name="Category",
            hover_data=["Agency_Name", "created_date"],
            color_discrete_sequence=["blue"],
            zoom=11,
            height=500
        )
        
        fig.update_layout(
            title=title,
            mapbox_style="open-street-map",
            margin={"r":0,"t":40,"l":0,"b":0}
        )
        
        return fig
    
    def create_status_flow_chart(self, df, title="Request Status Flow"):
        """Create Sankey diagram for request status flow"""
        created = len(df)
        acknowledged = df['Acknowledged_at_local_parsed'].notna().sum()
        closed = df['Closed_at_local_parsed'].notna().sum()
        
        # Create simple flow chart
        labels = ['Created', 'Acknowledged', 'Closed']
        source = [0, 1]  # Created->Acknowledged, Acknowledged->Closed
        target = [1, 2]
        value = [acknowledged, closed]
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
                color=["blue", "orange", "green"]
            ),
            link=dict(
                source=source,
                target=target,
                value=value
            )
        )])
        
        fig.update_layout(
            title=title,
            font_size=10,
            height=300
        )
        
        return fig
