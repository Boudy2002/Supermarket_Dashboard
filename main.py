import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
pd.options.display.max_columns = None
app = dash.Dash()
data = pd.read_csv('supermarket_sales.csv')
data["Date"] = pd.to_datetime(data["Date"])
unique_dates = sorted(data["Date"].unique())
data["Month"] = data["Date"].dt.to_period("M").astype(str)

# Get sorted unique months for the slider
unique_months = sorted(data["Month"].unique())

# Create a mapping for slider labels
month_marks = {i: m for i, m in enumerate(unique_months)}

app.layout = html.Div(
        children=[
                html.H1("Supermarket Sales Dashboard", style={"text-align": "center"}),
                html.Label("Select Date Range:"),
                dcc.Slider(
                        min=0,
                        max=len(unique_months) - 1,
                        value=len(unique_months) - 1,  # Default to latest month
                        marks=month_marks,
                        step=1,
                        id="month-slider"
                ),
                html.Label("Filter by Customer Type:"),
                dcc.Checklist(
                        options=[{"label": c, "value": c} for c in data["Customer type"].unique()],
                        value=data["Customer type"].unique().tolist(),
                        id="customer-checklist",
                        inline=False
                ),
                html.Label("Filter by Product Line:"),
                dcc.Checklist(
                        options=[{"label": c, "value": c} for c in data["Product line"].unique()],
                        value=data["Product line"].unique().tolist(),
                        id="product-checklist",
                        inline=False
                ),
                html.Div(
                        children=[
                                html.Div(
                                    children=[
                                        dcc.Graph(
                                            id="gender-pie-chart",
                                            style={
                                                'width': '50%',
                                                'display': 'inline-block'
                                            }
                                        ),
                                        dcc.Graph(
                                            id="branch-pie-chart",
                                            style={
                                                'width': '50%',
                                                'display': 'inline-block'
                                            }
                                        )
                                    ]
                                ),
                                html.Div(
                                    children=[
                                        dcc.Graph(
                                            id="product-sales-bar",
                                            style={
                                                'width': '50%',
                                                'display': 'inline-block'
                                            }
                                        ),
                                        dcc.Graph(
                                            id="total-sales-by-gender",
                                            style={
                                                'width': '50%',
                                                'display': 'inline-block'
                                            }
                                        )
                                    ]
                                ),
                                html.Div(
                                    children=[
                                        dcc.Graph(
                                            id="rating-leaderboard",
                                            style={
                                                'width': '50%',
                                                'display': 'inline-block'
                                            }
                                        ),
                                        dcc.Graph(
                                            id="payment-pie-chart",
                                            style={
                                                'width': '50%',
                                                'display': 'inline-block'
                                            }
                                        ),
                                    ]
                                ),
                                dcc.Graph(id="gross-income"),
                        ]
                )
        ]
)

@app.callback(
    [
        Output("gender-pie-chart", "figure"),
        Output("branch-pie-chart", "figure"),
        Output("product-sales-bar", "figure"),
        Output("rating-leaderboard", "figure"),
        Output("total-sales-by-gender", "figure"),
        Output("payment-pie-chart", "figure"),
        Output("gross-income", "figure")
     ],
    [Input("month-slider", "value"),
     Input("customer-checklist", "value"),
     Input("product-checklist", "value")]
)
def update_charts(selected_index, selected_customers, selected_products):
    print(selected_customers, selected_index, selected_products)
    # Get the selected month
    selected_month = unique_months[selected_index]

    # Filter Data for selected month and customer type
    filtered_data = data[(data["Month"] <= selected_month) & (data["Customer type"].isin(selected_customers)) & (data["Product line"].isin(selected_products))]

    # Gender Distribution
    gender_fig = px.sunburst(
        filtered_data,
        path=["Gender", "Customer type"],
        values="Total",
        title="Gender Distribution Split by Customer Type",
        color="Gender",
        color_discrete_map={"Male": "blue", "Female": "pink"},
    )

    # Branch Distribution
    branch_counts = filtered_data["City"].value_counts()
    branch_fig = px.pie(
        names=branch_counts.index,
        values=branch_counts.values,
        title="Branch Distribution",
        color=branch_counts.index,
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    # Product Sales
    product_sales = filtered_data.groupby("Product line")["Total"].sum().reset_index()
    product_fig = px.bar(
        product_sales,
        x="Product line",
        y="Total",
        title="Total Sales by Product Line",
        labels={"Total": "Total Sales"},
        color="Product line",
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    # Rating Leaderboard
    product_ratings = filtered_data.groupby("Product line")["Rating"].mean().reset_index()
    product_ratings = product_ratings.sort_values(by="Rating", ascending=True)
    rating_fig = px.bar(
        product_ratings,
        x="Rating",
        y="Product line",
        orientation="h",
        title="Leaderboard: Highest Rated Product Lines",
        labels={"Rating": "Average Rating"},
        color="Rating",
        color_continuous_scale="blues"
    )

    # Grouped bar chart
    product_gender_sales = filtered_data.groupby(["Product line", "Gender"])["Total"].sum().reset_index()
    product_gender_fig = px.bar(
            product_gender_sales,
            x="Product line",
            y="Total",
            color="Gender",
            barmode="group",
            title="Total Sales by Product Line and Gender",
            labels={"Total": "Total Sales", "Product line": "Product Line"},
            color_discrete_map={"Male": "blue", "Female": "pink"},
    )

    #Payment distribution
    payement_counts = filtered_data['Payment'].value_counts()
    payment_fig = px.pie(payement_counts, values=payement_counts.values, names=payement_counts.index, title='Payement Distribution')

    # Line chart
    product_gross_income = filtered_data.groupby("Product line")["gross income"].sum().reset_index()
    income_fig = px.line(
            product_gross_income,
            x="Product line",
            y="gross income",
            title="Gross Income by Product Line",
            markers=True,
            labels={"gross income": "Gross Income", "Product line": "Product Line"},
            line_shape="linear",
    )

    return gender_fig, branch_fig, product_fig, rating_fig, product_gender_fig, payment_fig, income_fig

if __name__ == '__main__':
        app.run_server(port=8002,host='127.0.0.10',debug=True)