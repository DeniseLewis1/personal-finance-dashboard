import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


chart_width = 600
chart_height = 325
chart_margin = dict(l=10, r=10, t=50, b=20)
font_size = max(10, min(chart_width // 40, 30))
color_light_gray = "#f4f4f4"
color_black = "#333333"
color_green = "#4CAF50"
color_red = "#FF5733"

# Display metrics in three columns
def display_metrics(income_by_month, expenses_by_month, net_balance_by_month):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
            <div style="padding: 10px; margin-bottom: 30px; border: 1px solid #ccc; background-color: {color_light_gray}; text-align: center;">
                <strong>Avg. Monthly Income</strong><br>
                <span style="font-size: 24px; font-weight: bold">${income_by_month.mean():,.2f}</span>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
            <div style="padding: 10px; margin-bottom: 30px; border: 1px solid #ccc; background-color: {color_light_gray}; text-align: center;">
                <strong>Avg. Monthly Expenses</strong><br>
                <span style="font-size: 24px; font-weight: bold">${expenses_by_month.mean():,.2f}</span>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
            <div style="padding: 10px; margin-bottom: 30px; border: 1px solid #ccc; background-color: {color_light_gray}; text-align: center;">
                <strong>Avg. Monthly Net Balance</strong><br>
                <span style="font-size: 24px; font-weight: bold">${net_balance_by_month.mean():,.2f}</span>
            </div>
        """, unsafe_allow_html=True)

# Display dashboard in a 2x2 grid layout
def display_grid(current_year_data, last_year_data, expenses_by_category, current_year, last_year):
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    # First chart in top-left corner
    with col1:
        create_income_chart(current_year_data, last_year_data, current_year, last_year)

    # Second chart in top-right corner
    with col2:
        create_expenses_chart(current_year_data, last_year_data, current_year, last_year)

    # Third chart in bottom-left corner
    with col3:
        create_net_balance_chart(current_year_data, last_year_data)

    # Fourth chart in bottom-right corner
    with col4:
        create_spending_chart(expenses_by_category)

# Create and display income chart
def create_income_chart(current_year_data, last_year_data, current_year, last_year):
    # Create a bar chart for current year income
    bar_chart1 = go.Bar(
        x=current_year_data["month"],
        y=current_year_data["income"],
        name=str(current_year),
        marker=dict(color=color_green),
        hovertemplate=f"$%{{y:,.2f}}<extra>{current_year}</extra>"
    )

    # Create a line chart for last year income
    line_chart1 = go.Scatter(
        x=last_year_data["month"],
        y=last_year_data["income"],
        mode="lines+markers",
        name=str(last_year),
        line=dict(color=color_black, width=2, dash="dash"),
        marker=dict(size=6),
        hovertemplate=f"$%{{y:,.2f}}<extra>{last_year}</extra>"
    )

    # Combine charts into one figure
    fig = go.Figure()
    fig.add_trace(bar_chart1)
    fig.add_trace(line_chart1)

    # Update layout
    fig.update_layout(
        width=chart_width,
        height=chart_height,
        margin=chart_margin,
        title=dict(
            text="Income",
            font=dict(size=font_size),
            x=0.5,
            xanchor="center"
        ),
        xaxis=dict(
            title=None,
            tickmode="array",
            tickvals=last_year_data["month"],
            ticktext=last_year_data["month"],
        ),
        yaxis=dict(
            title=None,
            tickformat="$~s"
        ),
        legend=dict(title="Year"),
        barmode="overlay",
        paper_bgcolor=color_light_gray,
        plot_bgcolor=color_light_gray
    )
    st.plotly_chart(fig)
    
# Create and display expenses chart
def create_expenses_chart(current_year_data, last_year_data, current_year, last_year):
    # Create a bar chart for current year expenses
    bar_chart2 = go.Bar(
        x=current_year_data["month"],
        y=current_year_data["abs_expenses"],
        name=str(current_year),
        marker=dict(color=color_red),
        hovertemplate=f"$%{{y:,.2f}}<extra>{current_year}</extra>"
    )

    # Create a line chart for last year expenses
    line_chart2 = go.Scatter(
        x=last_year_data["month"],
        y=last_year_data["abs_expenses"],
        mode="lines+markers",
        name=str(last_year),
        line=dict(color=color_black, width=2, dash="dash"),
        marker=dict(size=6),
        hovertemplate=f"$%{{y:,.2f}}<extra>{last_year}</extra>"
    )

    # Combine charts into one figure
    fig = go.Figure()
    fig.add_trace(bar_chart2)
    fig.add_trace(line_chart2)

    # Update layout
    fig.update_layout(
        width=chart_width,
        height=chart_height,
        margin=chart_margin,
        title=dict(
            text="Expenses",
            font=dict(size=font_size),
            x=0.5,
            xanchor="center"
        ),
        xaxis=dict(
            title=None,
            tickmode="array",
            tickvals=last_year_data["month"],
            ticktext=last_year_data["month"],
        ),
        yaxis=dict(
            title=None,
            tickformat="$~s"
        ),
        legend=dict(title="Year"),
        barmode="overlay",
        paper_bgcolor=color_light_gray,
        plot_bgcolor=color_light_gray
    )
    st.plotly_chart(fig)

# Create and display net balance chart
def create_net_balance_chart(current_year_data, last_year_data):
    fig = px.line(current_year_data, x="month", y="net_balance")
    fig.update_layout(
        width=chart_width,
        height=chart_height,
        margin=chart_margin,
        xaxis_title=None, 
        yaxis_title=None, 
        xaxis=dict(tickmode="array",
            tickvals=current_year_data["month"],
            ticktext=current_year_data["month"],
        ),
        yaxis=dict(tickformat="$~s"),
        title=dict(text="Net Balance", font=dict(size=font_size), x=0.5, xanchor="center"),
        paper_bgcolor=color_light_gray,
        plot_bgcolor=color_light_gray
    )
    fig.update_traces(
        hovertemplate="$%{y:,.2f}<extra></extra>",
        fill="tozeroy",
    )
    st.plotly_chart(fig)

# Create and display spending chart
def create_spending_chart(expenses_by_category):
    fig = px.pie(expenses_by_category, values=expenses_by_category, names=expenses_by_category.index)
    fig.update_layout(
        width=chart_width,
        height=chart_height,
        margin=chart_margin,
        title=dict(text="Spending by Category", font=dict(size=font_size), x=0.5, xanchor="center"),
        paper_bgcolor=color_light_gray,
        plot_bgcolor=color_light_gray
    )
    fig.update_traces(
        hovertemplate="%{label}<extra></extra>"
    )
    st.plotly_chart(fig)
