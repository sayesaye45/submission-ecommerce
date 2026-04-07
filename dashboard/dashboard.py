import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import os

st.set_page_config(page_title="Brazilian E-Commerce Dashboard",
                   page_icon="🛒", layout="wide")

# ── Load data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_csv(relative_path):
    """Coba beberapa lokasi file agar bekerja baik di lokal maupun Streamlit Cloud."""
    candidates = [
        os.path.join(BASE_DIR, relative_path),          # ./dashboard/main_data.csv
        os.path.join(BASE_DIR, "..", relative_path),     # satu level di atas
        relative_path,                                   # path asli (fallback)
    ]
    for path in candidates:
        if os.path.exists(path):
            return pd.read_csv(path)
    st.error(f"❌ File tidak ditemukan: {relative_path}\n"
             f"Pastikan file ada di folder `dashboard/` bersama `dashboard.py`.")
    st.stop()

df     = load_csv("dashboard/main_data.csv")
rfm_df = load_csv("dashboard/rfm_data.csv")

df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])

# ── Warna tema
COLOR_PRIMARY  = "#1565C0"   # biru utama (bar biasa)
COLOR_ACCENT   = "#FF5722"   # oranye — hanya untuk nilai TERTINGGI
COLOR_MUTED    = "#90CAF9"   # biru muda — bar lainnya
COLOR_BG       = "#f9f9f9"

# Warna per segmen RFM (semantik: hijau = baik, merah = buruk)
SEGMENT_COLORS = {
    'Champions':                  '#2E7D32',
    'Loyal Customers':            '#66BB6A',
    'Recent Customers':           '#AED581',
    'Potential Loyalists':        '#FFF176',
    'Customers Needing Attention':'#FFB74D',
    'At Risk':                    '#EF5350',
    'Lost Customers':             '#B71C1C',
}

def bar_colors(values, accent=COLOR_ACCENT, base=COLOR_PRIMARY):
    """Semua bar warna utama, kecuali nilai tertinggi diberi warna aksen."""
    colors = [base] * len(values)
    colors[values.argmax()] = accent
    return colors

def hbar_colors_by_segment(index_labels):
    """Kembalikan warna sesuai segmen RFM untuk horizontal bar."""
    return [SEGMENT_COLORS.get(seg, COLOR_PRIMARY) for seg in index_labels]

# ── SIDEBAR 
st.sidebar.image("https://flagcdn.com/w80/br.png", width=60)
st.sidebar.title("🛒 E-Commerce Brasil")
st.sidebar.markdown("---")

min_date = df['order_purchase_timestamp'].min()
max_date = df['order_purchase_timestamp'].max()

start_date = st.sidebar.date_input("Tanggal Mulai", min_date)
end_date   = st.sidebar.date_input("Tanggal Akhir", max_date)

states         = ["Semua"] + sorted(df['customer_state'].dropna().unique().tolist())
selected_state = st.sidebar.selectbox("Negara Bagian", states)

filtered_df = df[
    (df['order_purchase_timestamp'] >= pd.Timestamp(start_date)) &
    (df['order_purchase_timestamp'] <= pd.Timestamp(end_date))
]
if selected_state != "Semua":
    filtered_df = filtered_df[filtered_df['customer_state'] == selected_state]

st.sidebar.markdown("---")
st.sidebar.metric("Total Order",   f"{filtered_df['order_id'].nunique():,}")
st.sidebar.metric("Total Revenue", f"R$ {filtered_df['payment_value'].sum():,.0f}")

# ── HEADER
st.title("🛒 Brazilian E-Commerce Dashboard")
st.markdown("Analisis data e-commerce Brasil periode 2016-2018")
st.markdown("---")

# ── KPI 
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Order",          f"{filtered_df['order_id'].nunique():,}")
c2.metric("Total Revenue",        f"R$ {filtered_df['payment_value'].sum()/1e6:.1f}M")
c3.metric("Total Pelanggan",      f"{filtered_df['customer_id'].nunique():,}")
c4.metric("Rata-rata Nilai Order", f"R$ {filtered_df['payment_value'].mean():.0f}")

st.markdown("---")

# ── TAB 
tab1, tab2, tab3 = st.tabs(["📈 Tren Penjualan", "🗺️ Distribusi Wilayah", "👥 RFM Analysis"])

# ── TAB 1: Tren Penjualan 
with tab1:
    st.subheader("Tren Penjualan Bulanan (2016-2018)")
    filtered_df['order_month'] = (
        filtered_df['order_purchase_timestamp'].dt.to_period('M').astype(str)
    )
    monthly = filtered_df.groupby('order_month')['order_id'].nunique()

    fig, ax = plt.subplots(figsize=(12, 4))
    # Bar seragam biru; puncak tertinggi diberi warna aksen oranye
    ax.bar(range(len(monthly)), monthly.values,
           color=bar_colors(monthly.values), alpha=0.9)
    ax.set_xticks(range(len(monthly)))
    ax.set_xticklabels(monthly.index, rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Jumlah Order')
    ax.set_title('Tren Jumlah Order per Bulan')
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # ── Top 10 Kategori
    st.subheader("Top 10 Kategori Produk Terlaris (2016-2018)")
    top_cat = (
        filtered_df.groupby('product_category_name_english')['order_id']
        .nunique()
        .sort_values(ascending=False)
        .head(10)
    )

    fig2, ax2 = plt.subplots(figsize=(10, 4))
    # ✅ PERBAIKAN: warna seragam COLOR_PRIMARY; nilai terbesar diberi aksen
    colors_cat = bar_colors(top_cat.values)
    ax2.barh(top_cat.index, top_cat.values, color=colors_cat)
    ax2.set_xlabel('Jumlah Order')
    ax2.set_title('Top 10 Kategori Produk Terlaris\n'
                  '(🟠 = terlaris)', fontsize=11)
    ax2.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

# ── TAB 2: Distribusi Wilayah 
with tab2:
    st.subheader("Distribusi Order per Negara Bagian (2016-2018)")
    col_a, col_b = st.columns(2)

    with col_a:
        state_orders = (
            filtered_df.groupby('customer_state')['order_id']
            .nunique()
            .sort_values(ascending=False)
            .head(10)
        )
        fig3, ax3 = plt.subplots(figsize=(6, 5))
        # ✅ Highlight hanya untuk negara bagian teratas
        colors_s = bar_colors(state_orders.values,
                              accent=COLOR_ACCENT, base=COLOR_PRIMARY)
        ax3.bar(state_orders.index, state_orders.values, color=colors_s)
        ax3.set_xlabel('Negara Bagian')
        ax3.set_ylabel('Jumlah Order')
        ax3.set_title('Top 10 Negara Bagian\n(🟠 = terbanyak)', fontsize=11)
        ax3.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{int(x):,}'))
        ax3.spines['top'].set_visible(False)
        ax3.spines['right'].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close()

    with col_b:
        top5      = (filtered_df.groupby('customer_state')['order_id']
                     .nunique().sort_values(ascending=False))
        top5_data = top5.head(5)
        others    = pd.Series({'Others': top5.iloc[5:].sum()})
        pie_data  = pd.concat([top5_data, others])
        fig4, ax4 = plt.subplots(figsize=(6, 5))
        ax4.pie(pie_data.values, labels=pie_data.index, autopct='%1.1f%%',
                colors=sns.color_palette('Set2', n_colors=6), startangle=90)
        ax4.set_title('Proporsi Order per Negara Bagian')
        plt.tight_layout()
        st.pyplot(fig4)
        plt.close()

# ── TAB 3: RFM Analysis 
with tab3:
    st.subheader("Segmentasi Pelanggan (RFM Analysis 2016-2018)")
    col_c, col_d = st.columns(2)

    with col_c:
        seg_counts = rfm_df['Segment'].value_counts().sort_values()

        # ✅ PERBAIKAN: warna tiap bar sesuai makna segmen (bukan RdYlGn acak)
        colors_rfm = hbar_colors_by_segment(seg_counts.index)

        fig5, ax5 = plt.subplots(figsize=(6, 5))
        ax5.barh(seg_counts.index, seg_counts.values, color=colors_rfm)
        for i, v in enumerate(seg_counts.values):
            ax5.text(v + 50, i, f'{v:,}', va='center', fontsize=8)
        ax5.set_xlabel('Jumlah Pelanggan')
        ax5.set_title('Distribusi Segmen Pelanggan\n'
                      '(🟢 baik → 🔴 perlu perhatian)', fontsize=11)
        ax5.spines['top'].set_visible(False)
        ax5.spines['right'].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig5)
        plt.close()

    with col_d:
        fig6, ax6 = plt.subplots(figsize=(6, 5))
        for seg, color in SEGMENT_COLORS.items():
            subset = rfm_df[rfm_df['Segment'] == seg]
            ax6.scatter(subset['Recency'], subset['Monetary'],
                        c=color, label=seg, alpha=0.5, s=10)
        ax6.set_xlabel('Recency (hari)')
        ax6.set_ylabel('Monetary (R$)')
        ax6.set_title('Sebaran Pelanggan: Recency vs Monetary')
        ax6.legend(loc='upper right', fontsize=7)
        ax6.spines['top'].set_visible(False)
        ax6.spines['right'].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig6)
        plt.close()

    st.markdown("---")
    st.subheader("Rekomendasi Strategi per Segmen")
    strategies = {
        'Champions':                  ('🏆', '#2E7D32', 'Berikan program reward eksklusif dan early access produk baru.'),
        'Loyal Customers':            ('⭐', '#66BB6A', 'Tawarkan program loyalitas bertingkat dan personalisasi produk.'),
        'Recent Customers':           ('🆕', '#AED581', 'Kirim email nurturing dan diskon untuk repeat purchase.'),
        'Potential Loyalists':        ('💡', '#F9A825', 'Berikan penawaran bundle dan reminder produk.'),
        'Customers Needing Attention':('⚠️', '#FF7043', 'Kirim survei kepuasan dan penawaran limited-time.'),
        'At Risk':                    ('🔴', '#EF5350', 'Luncurkan re-engagement campaign dengan diskon besar.'),
        'Lost Customers':             ('💔', '#B71C1C', 'Win-back campaign dengan insentif maksimal.'),
    }
    for seg, (icon, color, desc) in strategies.items():
        if seg in rfm_df['Segment'].values:
            n = rfm_df[rfm_df['Segment'] == seg].shape[0]
            st.markdown(f"""
            <div style='background:{COLOR_BG};border-left:4px solid {color};
            padding:10px 14px;margin:6px 0;border-radius:0 8px 8px 0'>
                <b>{icon} {seg}</b>
                <span style='color:#666;font-size:12px'>({n:,} pelanggan)</span><br>
                <span style='font-size:13px'>{desc}</span>
            </div>""", unsafe_allow_html=True)

# ── FOOTER
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#888;font-size:12px'>"
    "E-Commerce Brasil Dashboard | Data: Olist 2016-2018</div>",
    unsafe_allow_html=True,
)