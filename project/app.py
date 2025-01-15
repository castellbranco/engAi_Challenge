import streamlit as st
import pandas as pd
from src.Backend.snowflake_connection import get_snowflake_connection
from src.Backend.data_queries import (
    fetch_sector_list,
    calculate_top_sectors,
    fetch_top_companies,
    fetch_company_list,
    fetch_timeseries_data,
    fetch_latest_date
)
import plotly.express as px
import plotly.graph_objects as go


#add more details to the company information
def main():
    st.set_page_config(page_title="BI Dashboard", layout="wide")
    st.title("BI Dashboard")

    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        st.success("Connected to Snowflake successfully!")

        col1, col2 = st.columns(2)

        with col1:
            start_date = st.date_input("Start Date", value=pd.to_datetime(fetch_latest_date(cursor)) - pd.Timedelta(days=30))
            end_date = st.date_input("End Date", value=pd.to_datetime(fetch_latest_date(cursor)))

        with col2:
            sector_list = fetch_sector_list(cursor)
            sector_list = ['All'] + sector_list
            selected_sectors = st.multiselect("Select Sectors to Compare", sector_list, default=['All'])

            if 'All' in selected_sectors:
                selected_sectors = sector_list[1:]

        # Top 10 Sectors by Position
        st.header("Top 10 Sectors by Position")
        if len(selected_sectors) > 0:
            top_sectors = calculate_top_sectors(cursor, start_date, end_date, selected_sectors)
            
            if not top_sectors.empty:
                fig = px.bar(top_sectors, x='TOTAL_POSITION_USD', y='SECTOR_NAME', orientation='h',
                             labels={'TOTAL_POSITION_USD': 'Total Position (USD)', 'SECTOR_NAME': 'Sector'},
                             hover_data={'TOTAL_POSITION_USD': ':.2f'},
                             text='TOTAL_POSITION_USD',
                             text_auto='.2s',
                             color='SECTOR_NAME',
                             color_discrete_sequence=px.colors.qualitative.Plotly)
                
                fig.update_layout(title=f"Comparison of {', '.join(selected_sectors)}",
                                  yaxis=dict(autorange="reversed"),
                                  height=500)
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No data available for the selected sectors.")
        else:
            st.warning("Please select at least one sector to compare.")

        # Top 25% Companies Table
        st.header("Top 25% Companies")
        top_companies = fetch_top_companies(cursor)

        # KPI Highlights
        total_companies = top_companies.shape[0]
        top_sector = top_companies.groupby('SECTOR_NAME')['AVERAGE_POSITION_USD'].mean().idxmax()
        largest_position = top_companies['AVERAGE_POSITION_USD'].max()

        st.markdown(f"**Total Companies Listed:** {total_companies}")
        st.markdown(f"**Top Sector by Average Position (USD):** {top_sector}")
        st.markdown(f"**Largest Position Overall:** ${largest_position:,.2f}")

        # Multi-select sector filter
        sector_filter = st.multiselect("Filter by Sector", options=["All"] + top_companies['SECTOR_NAME'].unique().tolist(), default=["All"])

        # Filter companies by selected sectors
        if "All" in sector_filter:
            filtered_companies = top_companies
        else:
            filtered_companies = top_companies[top_companies['SECTOR_NAME'].isin(sector_filter)]

        # Search bar for Tickers
        search_term = st.text_input("Search by Ticker or Sector Name")
        if search_term:
            filtered_companies = filtered_companies[
                filtered_companies['TICKER'].str.contains(search_term, case=False) |
                filtered_companies['SECTOR_NAME'].str.contains(search_term, case=False)
            ]

        # Format the numerical columns
        formatted_companies = filtered_companies.copy()
        formatted_companies['SHARES'] = formatted_companies['SHARES'].map(lambda x: f"{x:,.0f}")
        formatted_companies['LAST_CLOSE_PRICE_USD'] = formatted_companies['LAST_CLOSE_PRICE_USD'].map(lambda x: f"${x:,.2f}")
        formatted_companies['AVERAGE_POSITION_USD'] = formatted_companies['AVERAGE_POSITION_USD'].map(lambda x: f"${x:,.2f}")

        # Larger expander for detailed company information
        with st.expander("Detailed Information for Individual Company", expanded=False):
            for index, row in formatted_companies.iterrows():
                st.write(f"### {row['TICKER']} - {row['SECTOR_NAME']}")
                st.write(f"**Shares:** {row['SHARES']}")
                st.write(f"**Last Close Price:** {row['LAST_CLOSE_PRICE_USD']}")
                st.write(f"**Average Position:** {row['AVERAGE_POSITION_USD']}")
                # Add more details as needed
                st.write("**CEO Name:** [CEO Name Here]")  # Replace with actual data
                st.write("**Headquarters:** [Headquarters Here]")  # Replace with actual data
                st.write("**Latest Earnings:** [Earnings Here]")  # Replace with actual data
                st.write("---")  # Separator for better readability

        # Optionally, display the formatted companies table
        st.dataframe(
            formatted_companies[['TICKER', 'SECTOR_NAME', 'SHARES', 'LAST_CLOSE_PRICE_USD', 'AVERAGE_POSITION_USD']],
            use_container_width=True
        )

        # Company Timeseries Line Chart
        st.header("Company Timeseries")

        # Allow multiple company selection
        company_list = fetch_company_list(cursor)
        selected_companies = st.multiselect("Select Companies to Compare", company_list, default=[company_list[0]])

        # Create columns for summary metrics
        if selected_companies:
            metrics_cols = st.columns(3)
            
            # Initialize figure for plotly
            fig = go.Figure()
            
            for company in selected_companies:
                timeseries_data = fetch_timeseries_data(cursor, company)
                
                # Calculate summary statistics
                highest_price = timeseries_data['CLOSE_USD'].max()
                lowest_price = timeseries_data['CLOSE_USD'].min()
                avg_price = timeseries_data['CLOSE_USD'].mean()
                
                # Display metrics in columns
                with metrics_cols[0]:
                    st.metric(f"{company} Highest Price", f"${highest_price:,.2f}")
                with metrics_cols[1]:
                    st.metric(f"{company} Lowest Price", f"${lowest_price:,.2f}")
                with metrics_cols[2]:
                    st.metric(f"{company} Average Price", f"${avg_price:,.2f}")
                
                # Add trace for each company
                fig.add_trace(go.Scatter(
                    x=timeseries_data['DATE'],
                    y=timeseries_data['CLOSE_USD'],
                    name=company,
                    mode='lines',
                ))
            
            # Toggle for annotations
            show_annotations = st.checkbox("Show Key Events")
            if show_annotations:
                # Add example annotations - replace with actual events from your data
                fig.add_annotation(
                    x=timeseries_data['DATE'].iloc[-1],
                    y=timeseries_data['CLOSE_USD'].iloc[-1],
                    text="Latest Price",
                    showarrow=True,
                    arrowhead=1,
                )
            
            # Update layout for better visualization
            fig.update_layout(
                title="Company Price Comparison",
                xaxis_title="Date",
                yaxis_title="Close Price (USD)",
                hovermode='x unified',
                height=600,
            )
            
            # Display the plot
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Please select at least one company to display")

        # Export Data
        st.header("Export Data")
        export_option = st.selectbox("Select Data to Export", ["Top 25% Companies", "Company Timeseries", "Top 10 Sectors"])

        if export_option == "Top 25% Companies":
            st.download_button(
                label="Export to CSV",
                data=top_companies.to_csv(index=False),
                file_name=f"{export_option}.csv",
                mime="text/csv"
            )
        elif export_option == "Company Timeseries":
            st.download_button(
                label="Export to CSV",
                data=timeseries_data.to_csv(index=False),
                file_name=f"{selected_company}_timeseries.csv",
                mime="text/csv"
            )
        elif export_option == "Top 10 Sectors":
            st.download_button(
                label="Export to CSV",
                data=top_sectors.to_csv(index=False),
                file_name="Top_10_Sectors.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"Error: {str(e)}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main() 