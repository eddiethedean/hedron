import pandas as pd
import streamlit as st


@st.cache_data
def load_sales() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"month": "Jan", "region": "North", "revenue": 3200, "orders": 32},
            {"month": "Feb", "region": "North", "revenue": 4100, "orders": 38},
            {"month": "Mar", "region": "North", "revenue": 4600, "orders": 41},
            {"month": "Jan", "region": "South", "revenue": 2800, "orders": 29},
            {"month": "Feb", "region": "South", "revenue": 3600, "orders": 34},
            {"month": "Mar", "region": "South", "revenue": 4300, "orders": 39},
        ]
    )


sales = load_sales()

st.title("Sales dashboard")
region = st.sidebar.selectbox("Region", ["All", "North", "South"])
minimum = st.sidebar.slider("Minimum revenue", 0, 5000, 0, step=500)

filtered = sales[((sales["region"] == region) | (region == "All")) & (sales["revenue"] >= minimum)]

revenue, orders = st.columns(2)
revenue.metric("Revenue", f"${filtered['revenue'].sum():,}")
orders.metric("Orders", int(filtered["orders"].sum()))

st.line_chart(filtered, x="month", y="revenue")
st.dataframe(filtered, width="stretch")
