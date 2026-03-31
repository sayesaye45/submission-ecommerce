import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")

# Load data
df = pd.read_csv("main_data.csv")
rfm_df = pd.read_csv("rfm_data.csv")

st.title("Brazilian E-Commerce Dashboard")

st.markdown("---")

# KPI
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Order", df['order_id'].nunique())
with col2:
    st.metric("Total Pelanggan", df['customer_id'].nunique())

st.markdown("---")

# Tren penjualan
st.subheader("Tren Penjualan Bulanan")
df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
df['order_month'] = df['order_purchase_timestamp'].dt.to_period('M').astype(str)
monthly = df.groupby('order_month')['order_id'].nunique()
fig, ax = plt.subplots(figsize=(12,4))
monthly.plot(kind='bar', ax=ax, color='steelblue')
plt.xticks(rotation=45)
st.pyplot(fig)

st.markdown("---")

# Distribusi negara bagian
st.subheader("Top 10 Negara Bagian")
state = df.groupby('customer_state')['order_id'].nunique().sort_values(ascending=False).head(10)
fig2, ax2 = plt.subplots(figsize=(10,4))
state.plot(kind='bar', ax=ax2, color='green')
plt.xticks(rotation=45)
st.pyplot(fig2)

st.markdown("---")

# RFM
st.subheader("Segmentasi Pelanggan (RFM)")
fig3, ax3 = plt.subplots(figsize=(10,4))
rfm_df['Segment'].value_counts().plot(kind='bar', ax=ax3, color='purple')
plt.xticks(rotation=45)
st.pyplot(fig3)