"""
Main Streamlit dashboard for Syracuse Service Request Trends Analyzer
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_processor import DataProcessor
from src.analytics import ServiceAnalytics
from src.visualizations import DashboardVisualizations
import config.settings as settings

class SyracuseServiceDashboard:
    def __init__(self):
        st.set_page_config(
            page_title=settings.DASHBOARD_TITLE,
            page_icon="🏙️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Initialize components
        self.dp = DataProcessor(settings.RAW_DATA_PATH)
        self.analytics = ServiceAnalytics(self.dp)
        self.viz = DashboardVisualizations()
        
        # Load data
        self.load_data()
    
    def load_data(self):
        """Load data with progress indicator"""
        with st.spinner('Loading and processing data...'):
            success = self.analytics.load_data()
            if success:
                st.success(f"✅ Loaded {len(self.analytics.df)} service requests")
                self.data_summary = self.dp.get_data_summary(self.analytics.df)
            else:
                st.error("❌ Failed to load data. Please check the data file.")
                st.stop()
    
    def create_sidebar(self):
        """Create sidebar with filters and controls"""
        st.sidebar.title("🔍 Filters & Controls")
        
        # Date range filter
        st.sidebar.subheader("Date Range")
        min_date = self.analytics.df['created_date'].min()
        max_date = self.analytics.df['created_date'].max()
        
        date_range = st.sidebar.date_input(
            "Select date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Category filter
        st.sidebar.subheader("Category Filter")
        all_categories = sorted(self.analytics.df['Category'].unique())
        selected_categories = st.sidebar.multiselect(
            "Select categories",
            options=all_categories,
            default=all_categories[:5] if len(all_categories) > 5 else all_categories
        )
        
        # Agency filter
        st.sidebar.subheader("Agency Filter")
        all_agencies = sorted(self.analytics.df['Agency_Name'].unique())
        selected_agencies = st.sidebar.multiselect(
            "Select agencies",
            options=all_agencies,
            default=all_agencies[:3] if len(all_agencies) > 3 else all_agencies
        )
        
        # Status filter
        st.sidebar.subheader("Status Filter")
        status_options = ['All', 'Open', 'Closed']
        selected_status = st.sidebar.selectbox(
            "Request status",
            options=status_options,
            index=0
        )
        
        # Analysis options
        st.sidebar.subheader("Analysis Options")
        top_n = st.sidebar.slider(
            "Number of top categories to show",
            min_value=5,
            max_value=20,
            value=10
        )
        
        # Create filters dictionary
        filters = {
            'date_range': date_range if len(date_range) == 2 else None,
            'categories': selected_categories,
            'agencies': selected_agencies,
            'status': selected_status.lower() if selected_status != 'All' else None
        }
        
        # Apply filters
        filtered_data = self.dp.filter_data(self.analytics.df, filters)
        
        # Display filter summary
        st.sidebar.markdown("---")
        st.sidebar.metric("Filtered Requests", len(filtered_data))
        st.sidebar.metric(
            "Filter Reduction", 
            f"{((1 - len(filtered_data)/len(self.analytics.df)) * 100):.1f}%"
        )
        
        return filtered_data, {'top_n': top_n}
    
    def display_summary_metrics(self, filtered_data):
        """Display summary metrics at the top of the dashboard"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_requests = len(filtered_data)
            st.metric("Total Requests", total_requests)
        
        with col2:
            closed_requests = filtered_data['Closed_at_local_parsed'].notna().sum()
            closure_rate = (closed_requests / total_requests * 100) if total_requests > 0 else 0
            st.metric("Closed Requests", f"{closed_requests} ({closure_rate:.1f}%)")
        
        with col3:
            if 'acknowledge_time_minutes' in filtered_data.columns:
                avg_ack_time = filtered_data['acknowledge_time_minutes'].mean()
                if pd.notna(avg_ack_time):
                    hours = avg_ack_time / 60
                    st.metric("Avg Ack Time", f"{hours:.1f} hours")
                else:
                    st.metric("Avg Ack Time", "N/A")
        
        with col4:
            if 'sla_status' in filtered_data.columns:
                sla_met = filtered_data[filtered_data['sla_status'] == 'met'].shape[0]
                sla_total = filtered_data[filtered_data['sla_status'].isin(['met', 'breached'])].shape[0]
                sla_rate = (sla_met / sla_total * 100) if sla_total > 0 else 0
                st.metric("SLA Compliance", f"{sla_rate:.1f}%")
    
    def display_trends_tab(self, filtered_data, options):
        """Display trends over time analysis"""
        st.header("📈 Trends Over Time")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Time series trend
            trend_data = self.analytics.get_trend_analysis('D')
            if trend_data is not None:
                fig = self.viz.create_trend_chart(trend_data)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Temporal patterns
            patterns = self.analytics.get_temporal_patterns()
            if patterns and 'hourly' in patterns:
                st.subheader("Hourly Distribution")
                hourly_df = pd.DataFrame({
                    'Hour': patterns['hourly'].index,
                    'Requests': patterns['hourly'].values
                })
                st.dataframe(hourly_df, height=300)
        
        # Heatmap
        st.subheader("Request Patterns by Day and Hour")
        heatmap_fig = self.viz.create_heatmap(filtered_data)
        if heatmap_fig:
            st.plotly_chart(heatmap_fig, use_container_width=True)
    
    def display_performance_tab(self, filtered_data, options):
        """Display department performance analysis"""
        st.header("⚙️ Department Performance")
        
        # Agency performance metrics
        performance_df = self.analytics.get_agency_performance()
        if performance_df is not None:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Performance chart
                fig = self.viz.create_performance_chart(performance_df.head(10))
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Performance table
                st.subheader("Top Performers")
                top_performers = performance_df.nlargest(5, 'sla_compliance_rate')
                st.dataframe(
                    top_performers[['agency', 'sla_compliance_rate', 'total_requests']],
                    height=300
                )
        
        # Response time analysis
        st.subheader("Response Time Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            # Response time distribution
            fig = self.viz.create_response_time_chart(filtered_data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Status flow
            fig = self.viz.create_status_flow_chart(filtered_data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
    
    def display_channels_tab(self, filtered_data, options):
        """Display reporting channels analysis"""
        st.header("📱 Reporting Channels")
        
        # Channel distribution
        channel_data = self.analytics.get_channel_analysis()
        if channel_data:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Channel distribution chart
                fig = self.viz.create_channel_analysis_chart(channel_data)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Channel performance table
                st.subheader("Channel Performance")
                channel_df = pd.DataFrame([
                    {
                        'Channel': channel,
                        'Requests': data['count'],
                        'Share': f"{data['percentage']:.1f}%",
                        'Avg Ack Time': f"{data['avg_ack_time']/60:.1f} hrs" if data['avg_ack_time'] else 'N/A'
                    }
                    for channel, data in channel_data.items()
                ])
                st.dataframe(channel_df, height=400)
    
    def display_sla_tab(self, filtered_data, options):
        """Display SLA compliance analysis"""
        st.header("⏱️ SLA Compliance Monitor")
        
        # SLA overview
        sla_data = self.analytics.get_sla_analysis()
        if sla_data:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # SLA gauge
                fig = self.viz.create_sla_chart(sla_data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # SLA by category
                if 'by_category' in sla_data and sla_data['by_category']:
                    st.subheader("SLA by Category")
                    sla_cat_df = pd.DataFrame([
                        {
                            'Category': cat,
                            'SLA Met': data['met'],
                            'SLA Breached': data['breached'],
                            'Compliance Rate': f"{data['compliance_rate']:.1f}%"
                        }
                        for cat, data in sla_data['by_category'].items()
                    ])
                    st.dataframe(sla_cat_df, height=300)
            
            with col3:
                # SLA trends
                st.subheader("SLA Insights")
                if 'overall' in sla_data:
                    met = sla_data['overall'].get('met', 0)
                    breached = sla_data['overall'].get('breached', 0)
                    total = met + breached
                    
                    if total > 0:
                        st.metric("SLA Met", met)
                        st.metric("SLA Breached", breached)
                        st.metric("Total Analyzed", total)
        
        # At-risk requests
        st.subheader("Requests Approaching SLA Limit")
        if 'Sla_in_hours' in filtered_data.columns and 'close_time_minutes' in filtered_data.columns:
            # Calculate time remaining
            filtered_data['time_remaining'] = (filtered_data['Sla_in_hours'] * 60) - filtered_data['close_time_minutes']
            
            # Find requests approaching SLA
            approaching_sla = filtered_data[
                (filtered_data['time_remaining'] > 0) & 
                (filtered_data['time_remaining'] < 24 * 60)  # Less than 24 hours remaining
            ]
            
            if len(approaching_sla) > 0:
                st.warning(f"⚠️ {len(approaching_sla)} requests approaching SLA limit")
                st.dataframe(
                    approaching_sla[['Category', 'Agency_Name', 'created_date', 'time_remaining']].head(10),
                    height=200
                )
            else:
                st.success("✅ No requests currently approaching SLA limit")
    
    def display_geographic_tab(self, filtered_data, options):
        """Display geographic analysis"""
        st.header("🗺️ Geographic Analysis")
        
        # Geographic insights
        geo_insights = self.analytics.get_geographic_insights()
        
        if geo_insights:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Map visualization
                if 'geo_data' in geo_insights:
                    fig = self.viz.create_geographic_map(geo_insights['geo_data'])
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Geographic stats
                st.subheader("Geographic Stats")
                if 'basic_stats' in geo_insights:
                    stats = geo_insights['basic_stats']
                    st.metric("Requests with Coordinates", stats['total_with_coords'])
                    st.metric("Latitude Range", f"{stats['lat_range'][0]:.4f} - {stats['lat_range'][1]:.4f}")
                    st.metric("Longitude Range", f"{stats['lng_range'][0]:.4f} - {stats['lng_range'][1]:.4f}")
                
                if 'quadrant_distribution' in geo_insights:
                    st.subheader("Quadrant Distribution")
                    for quadrant, count in geo_insights['quadrant_distribution'].items():
                        st.metric(f"{quadrant} Quadrant", count)
    
    def display_category_tab(self, filtered_data, options):
        """Display detailed category analysis"""
        st.header("🏷️ Category Analysis")
        
        # Category analysis
        category_analysis = self.analytics.get_category_analysis(options['top_n'])
        
        if category_analysis:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Category chart
                if 'top_categories' in category_analysis:
                    fig = self.viz.create_category_chart(category_analysis['top_categories'])
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Category performance
                st.subheader("Category Performance")
                if 'response_stats' in category_analysis:
                    perf_data = []
                    for category, stats in list(category_analysis['response_stats'].items())[:10]:
                        perf_data.append({
                            'Category': category[:30] + '...' if len(category) > 30 else category,
                            'Requests': stats['count'],
                            'Avg Ack (hrs)': f"{stats['ack_mean']/60:.1f}" if stats['ack_mean'] else 'N/A',
                            'Avg Close (hrs)': f"{stats['close_mean']/60:.1f}" if stats['close_mean'] else 'N/A'
                        })
                    
                    perf_df = pd.DataFrame(perf_data)
                    st.dataframe(perf_df, height=400)
    
    def display_data_export(self, filtered_data):
        """Display data export options"""
        st.sidebar.markdown("---")
        st.sidebar.subheader("📊 Data Export")
        
        if st.sidebar.button("Export Filtered Data"):
            # Convert to CSV
            csv = filtered_data.to_csv(index=False)
            st.sidebar.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"syracuse_requests_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    def run(self):
        """Main dashboard execution"""
        # Dashboard header
        st.title(settings.DASHBOARD_TITLE)
        st.markdown(settings.DASHBOARD_DESCRIPTION)
        
        # Create sidebar and get filtered data
        filtered_data, options = self.create_sidebar()
        
        # Display summary metrics
        self.display_summary_metrics(filtered_data)
        
        # Create tabs for different analyses
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📈 Trends", "⚙️ Performance", "📱 Channels", 
            "⏱️ SLA", "🗺️ Geography", "🏷️ Categories"
        ])
        
        # Display each tab
        with tab1:
            self.display_trends_tab(filtered_data, options)
        
        with tab2:
            self.display_performance_tab(filtered_data, options)
        
        with tab3:
            self.display_channels_tab(filtered_data, options)
        
        with tab4:
            self.display_sla_tab(filtered_data, options)
        
        with tab5:
            self.display_geographic_tab(filtered_data, options)
        
        with tab6:
            self.display_category_tab(filtered_data, options)
        
        # Data export
        self.display_data_export(filtered_data)
        
        # Footer
        st.markdown("---")
        st.caption(f"Data Source: Syracuse Open Data Portal | Last Updated: {datetime.now().strftime('%Y-%m-%d')}")

# Main execution
if __name__ == "__main__":
    dashboard = SyracuseServiceDashboard()
    dashboard.run()
