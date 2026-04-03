import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

st.set_page_config(
    page_title="Brazilian E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide"
)

# ============================================================
# LOAD DATA dengan cache agar hemat RAM
# ============================================================
@st.cache_data
def load_main():
    df = pd.read_csv("dashboard/main_data.csv")
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    return df

@st.cache_data
def load_rfm():
    return pd.read_csv("dashboard/rfm_data.csv")

df = load_main()
rfm_df = load_rfm()

# ============================================================
# SIDEBAR — FILTER INTERAKTIF (KRITERIA WAJIB)
# ============================================================
st.sidebar.title("🔽 Filter Data")
st.sidebar.markdown("Gunakan filter di bawah untuk menyaring data pada semua visualisasi.")
st.sidebar.markdown("---")

# Filter 1: Rentang Tanggal
min_date = df['order_purchase_timestamp'].min().date()
max_date = df['order_purchase_timestamp'].max().date()

date_range = st.sidebar.date_input(
    "📅 Rentang Tanggal Order",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

# Filter 2: Negara Bagian
all_states = sorted(df['customer_state'].unique().tolist())
selected_states = st.sidebar.multiselect(
    "🗺️ Pilih Negara Bagian",
    options=all_states,
    default=all_states
)

# Filter 3: Segmen RFM
all_segments = sorted(rfm_df['Segment'].unique().tolist())
selected_segments = st.sidebar.multiselect(
    "👥 Pilih Segmen Pelanggan",
    options=all_segments,
    default=all_segments
)

st.sidebar.markdown("---")
st.sidebar.caption("📦 Brazilian E-Commerce Public Dataset © Olist")
st.sidebar.caption("🔗 [Sumber Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)")

# ============================================================
# TERAPKAN FILTER KE DATA MENTAH
# ============================================================
df_filtered = df[
    (df['order_purchase_timestamp'].dt.date >= start_date) &
    (df['order_purchase_timestamp'].dt.date <= end_date) &
    (df['customer_state'].isin(selected_states) if selected_states else df['customer_state'].notna())
]

rfm_filtered = rfm_df[
    rfm_df['Segment'].isin(selected_segments) if selected_segments else rfm_df['Segment'].notna()
]

# ============================================================
# HEADER
# ============================================================
st.title("🛒 Brazilian E-Commerce Dashboard")
st.markdown("""
Dashboard ini menyajikan analisis data transaksi e-commerce Brasil dari platform **Olist** (2016–2018).  
Gunakan **filter di sidebar kiri** untuk menyaring data berdasarkan tanggal, wilayah, dan segmen pelanggan.
""")

total_orders = df_filtered['order_id'].nunique()
total_customers = df_filtered['customer_id'].nunique()
st.caption(f"📊 Menampilkan **{total_orders:,}** order dari **{total_customers:,}** pelanggan sesuai filter.")
st.markdown("---")

# ============================================================
# KPI METRICS
# ============================================================
st.subheader("📊 Ringkasan Performa")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🛍️ Total Order", f"{total_orders:,}")
with col2:
    st.metric("👥 Total Pelanggan", f"{total_customers:,}")
with col3:
    if 'payment_value' in df_filtered.columns:
        total_rev = df_filtered['payment_value'].sum()
        st.metric("💰 Total Pendapatan", f"R$ {total_rev:,.0f}")
with col4:
    if 'payment_value' in df_filtered.columns and total_orders > 0:
        avg_order = df_filtered['payment_value'].mean()
        st.metric("🧾 Rata-rata per Order", f"R$ {avg_order:,.0f}")

st.markdown("---")

# ============================================================
# VISUALISASI 1: TREN PENJUALAN BULANAN
# ============================================================
st.subheader("📈 Tren Penjualan Bulanan")
st.markdown("""
**Tujuan:** Melihat pola penjualan dari waktu ke waktu untuk mengidentifikasi tren pertumbuhan,  
penurunan, serta momen puncak yang dapat dimanfaatkan untuk strategi promosi.
""")

df_filtered['order_month_str'] = df_filtered['order_purchase_timestamp'].dt.to_period('M').astype(str)
monthly = df_filtered.groupby('order_month_str')['order_id'].nunique().sort_index()

if monthly.empty:
    st.warning("⚠️ Tidak ada data untuk filter yang dipilih.")
else:
    fig, ax = plt.subplots(figsize=(12, 4))

    # Highlight bulan terbaik
    colors = ['#1565C0' if v == monthly.max() else '#90CAF9' for v in monthly.values]
    bars = ax.bar(range(len(monthly)), monthly.values, color=colors, edgecolor='none')

    ax.set_xticks(range(len(monthly)))
    ax.set_xticklabels(monthly.index, rotation=45, ha='right', fontsize=8)
    ax.set_xlabel("Bulan", fontsize=11)
    ax.set_ylabel("Jumlah Order", fontsize=11)
    ax.set_title("Jumlah Order per Bulan", fontsize=13, fontweight='bold')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    # Hapus border atas & kanan (prinsip visualisasi bersih)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    peak = monthly.idxmax()
    st.info(f"💡 **Insight:** Penjualan tertinggi terjadi pada **{peak}** dengan **{monthly.max():,}** order "
            f"(ditandai warna biru tua). Kemungkinan bertepatan dengan event promosi nasional Brasil.")

st.markdown("---")

# ============================================================
# VISUALISASI 2: TOP KATEGORI PRODUK
# ============================================================
if 'product_category_name_english' in df_filtered.columns:
    st.subheader("📦 Top 10 Kategori Produk Terlaris")
    st.markdown("""
    **Tujuan:** Mengidentifikasi kategori produk dengan permintaan tertinggi  
    untuk mendukung keputusan manajemen stok dan strategi pemasaran produk.
    """)

    cat_orders = (
        df_filtered.groupby('product_category_name_english')['order_id']
        .nunique()
        .sort_values(ascending=True)
        .tail(10)
    )

    if cat_orders.empty:
        st.warning("⚠️ Tidak ada data kategori untuk filter yang dipilih.")
    else:
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        colors_cat = ['#1B5E20' if i == len(cat_orders) - 1 else '#A5D6A7' for i in range(len(cat_orders))]
        ax2.barh(cat_orders.index, cat_orders.values, color=colors_cat, edgecolor='none')
        ax2.set_xlabel("Jumlah Order", fontsize=11)
        ax2.set_title("Top 10 Kategori Produk berdasarkan Jumlah Order", fontsize=13, fontweight='bold')
        ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close()

        top_cat = cat_orders.idxmax()
        st.info(f"💡 **Insight:** Kategori **{top_cat}** (perlengkapan rumah tangga) menjadi yang paling banyak dipesan. "
                f"Fokuskan stok dan promosi pada kategori ini, terutama menjelang akhir tahun.")

    st.markdown("---")

# ============================================================
# VISUALISASI 3: TOP 10 NEGARA BAGIAN
# ============================================================
st.subheader("🗺️ Distribusi Order per Negara Bagian (Top 10)")
st.markdown("""
**Tujuan:** Mengidentifikasi wilayah dengan konsentrasi pelanggan terbesar  
untuk mendukung keputusan distribusi, logistik, dan pemasaran regional.
""")

state = (
    df_filtered.groupby('customer_state')['order_id']
    .nunique()
    .sort_values(ascending=False)
    .head(10)
)

if state.empty:
    st.warning("⚠️ Tidak ada data untuk filter yang dipilih.")
else:
    fig3, ax3 = plt.subplots(figsize=(10, 4))
    colors_state = ['#1B5E20' if i == 0 else '#81C784' for i in range(len(state))]
    ax3.bar(state.index, state.values, color=colors_state, edgecolor='none')
    ax3.set_xlabel("Negara Bagian", fontsize=11)
    ax3.set_ylabel("Jumlah Order", fontsize=11)
    ax3.set_title("Top 10 Negara Bagian berdasarkan Jumlah Order", fontsize=13, fontweight='bold')
    ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    plt.xticks(rotation=0)
    plt.tight_layout()
    st.pyplot(fig3)
    plt.close()

    top_state = state.index[0]
    pct = (state.iloc[0] / total_orders * 100) if total_orders > 0 else 0
    st.info(f"💡 **Insight:** **{top_state} (São Paulo)** mendominasi dengan **{state.iloc[0]:,}** order "
            f"({pct:.1f}% dari total). Lima negara bagian teratas menyumbang lebih dari 70% total order.")

st.markdown("---")

# ============================================================
# VISUALISASI 4: RFM ANALYSIS
# ============================================================
st.subheader("👥 Analisis RFM — Segmentasi Pelanggan")
st.markdown("""
**Teknik Analisis:** RFM Analysis (Recency, Frequency, Monetary)  
**Tujuan:** Mengelompokkan pelanggan berdasarkan perilaku transaksi untuk mendukung strategi retensi dan akuisisi yang lebih personal.

| Dimensi | Penjelasan |
|---|---|
| **Recency (R)** | Seberapa baru pelanggan melakukan pembelian terakhir (hari) |
| **Frequency (F)** | Seberapa sering pelanggan melakukan transaksi (jumlah order) |
| **Monetary (M)** | Seberapa besar total pengeluaran pelanggan (R$) |
""")

if rfm_filtered.empty:
    st.warning("⚠️ Tidak ada data untuk segmen yang dipilih.")
else:
    col_l, col_r = st.columns([1, 1])

    with col_l:
        seg_count = rfm_filtered['Segment'].value_counts().sort_values(ascending=True)
        palette = sns.color_palette("RdYlGn", len(seg_count))
        fig4, ax4 = plt.subplots(figsize=(6, 4))
        ax4.barh(seg_count.index, seg_count.values, color=palette, edgecolor='none')
        ax4.set_xlabel("Jumlah Pelanggan", fontsize=11)
        ax4.set_title("Distribusi Segmen Pelanggan", fontsize=12, fontweight='bold')
        ax4.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
        ax4.spines['top'].set_visible(False)
        ax4.spines['right'].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig4)
        plt.close()

    with col_r:
        st.markdown("#### 📋 Ringkasan per Segmen")
        cols_available = ['Segment']
        if 'Monetary' in rfm_filtered.columns:
            cols_available.append('Monetary')
        if 'Frequency' in rfm_filtered.columns:
            cols_available.append('Frequency')
        if 'Recency' in rfm_filtered.columns:
            cols_available.append('Recency')

        agg_dict = {'Segment': 'count'}
        if 'Monetary' in rfm_filtered.columns:
            agg_dict['Monetary'] = 'mean'
        if 'Frequency' in rfm_filtered.columns:
            agg_dict['Frequency'] = 'mean'
        if 'Recency' in rfm_filtered.columns:
            agg_dict['Recency'] = 'mean'

        rfm_summary = rfm_filtered.groupby('Segment').agg(agg_dict).rename(
            columns={'Segment': 'Jumlah', 'Monetary': 'Avg Spend (R$)',
                     'Frequency': 'Avg Order', 'Recency': 'Avg Recency (hari)'}
        ).sort_values('Jumlah', ascending=False).reset_index()

        if 'Avg Spend (R$)' in rfm_summary.columns:
            rfm_summary['Avg Spend (R$)'] = rfm_summary['Avg Spend (R$)'].map(lambda x: f"R$ {x:,.0f}")
        if 'Avg Order' in rfm_summary.columns:
            rfm_summary['Avg Order'] = rfm_summary['Avg Order'].map(lambda x: f"{x:.1f}x")
        if 'Avg Recency (hari)' in rfm_summary.columns:
            rfm_summary['Avg Recency (hari)'] = rfm_summary['Avg Recency (hari)'].map(lambda x: f"{x:.0f} hari")

        st.dataframe(rfm_summary, use_container_width=True, hide_index=True)

        st.markdown("""
        **Rekomendasi Strategi:**
        - 🏆 **Champions** → Program VIP & reward eksklusif
        - ⚠️ **At Risk** → Re-engagement campaign
        - 🆕 **Recent** → Email nurturing & diskon repeat order
        - ❌ **Lost** → Win-back campaign dengan insentif besar
        """)

    top_seg = rfm_filtered['Segment'].value_counts().idxmax()
    st.info(f"💡 **Insight:** Segmen terbesar adalah **{top_seg}** — menunjukkan tantangan customer retention yang perlu segera diatasi. "
            f"Fokuskan budget pada program re-engagement dan loyalitas.")

st.markdown("---")

# ============================================================
# FOOTER
# ============================================================
st.markdown("""
<div style='text-align: center; color: grey; font-size: 13px; padding: 10px;'>
    🛒 Brazilian E-Commerce Dashboard &nbsp;|&nbsp; Dibuat dengan Streamlit &nbsp;|&nbsp;
    Data: <a href='https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce' target='_blank'>Olist Public Dataset</a>
</div>
""", unsafe_allow_html=True)
