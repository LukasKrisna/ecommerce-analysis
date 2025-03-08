import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from babel.numbers import format_currency

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_approved_at').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
        
    return daily_orders_df

def create_sum_spend_df(df):
    sum_spend_df = df.resample(rule='D', on='order_approved_at').agg({
        "payment_value": "sum"
    })
    sum_spend_df = sum_spend_df.reset_index()
    sum_spend_df.rename(columns={
        "payment_value": "total_spend"
    }, inplace=True)

    return sum_spend_df

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name_english")["product_id"].count().reset_index()
    sum_order_items_df.rename(columns={
        "product_id": "product_count"
    }, inplace=True)
    sum_order_items_df = sum_order_items_df.sort_values(by='product_count', ascending=False)

    return sum_order_items_df

def review_score_df(df):
    review_scores = df['review_score'].value_counts().sort_values(ascending=False)
    most_common_score = review_scores.idxmax()

    return review_scores, most_common_score

def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    most_common_state = bystate_df.loc[bystate_df['customer_count'].idxmax(), 'customer_state']
    bystate_df = bystate_df.sort_values(by='customer_count', ascending=False)

    return bystate_df, most_common_state

def create_bycity_df(df):
    bycity_df = df.groupby(by="customer_city").customer_id.nunique().reset_index()
    bycity_df.rename(columns={
        "customer_id": "total_customer"
    }, inplace=True)
    most_common_city = bycity_df.loc[bycity_df['total_customer'].idxmax(), 'customer_city']
    bycity_df = bycity_df.sort_values(by='total_customer', ascending=False)

    return bycity_df, most_common_city

def create_order_status(df):
    order_status_df = df["order_status"].value_counts().sort_values(ascending=False)
    most_common_status = order_status_df.idxmax()

    return order_status_df, most_common_status

def create_rm_df(df):
    rfm_df = df
    rfm_df['order_purchase_timestamp'] = pd.to_datetime(rfm_df['order_purchase_timestamp'])
    rfm_df['payment_value'] = pd.to_numeric(rfm_df['payment_value'], errors='coerce')
    df_clean = rfm_df.dropna(subset=['payment_value'])

    max_date = df_clean['order_purchase_timestamp'].max() + pd.Timedelta(days=1)

    rfm = df_clean.groupby('customer_id').agg({
        'order_purchase_timestamp': lambda x: (max_date - x.max()).days,  # Recency
        'order_id': 'nunique',  # Frequency
        'payment_value': 'sum'  # Monetary
    }).reset_index()

    rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
    top_recency = rfm.sort_values('recency', ascending=True).head(5)
    top_frequency = rfm.sort_values('frequency', ascending=False).head(5)
    top_monetary = rfm.sort_values('monetary', ascending=False).head(5)

    return top_recency, top_frequency, top_monetary


datetime_columns = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_df = pd.read_csv(r'dashboard/all_data.csv')
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

for col in datetime_columns:
    all_df[col] = pd.to_datetime(all_df[col])


min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

st.set_page_config(
    page_title="Brazil E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem !important;
        color: #1E88E5;
    }
    .sub-header {
        font-size: 1.8rem !important;
        color: #1976D2;
    }
    .metric-card {
        background-color: #f0f8ff;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .metric-label {
        font-size: 1rem !important;
        color: #333333;
        font-weight: normal;
    }
    .metric-value {
        font-size: 1.5rem !important;
        font-weight: bold;
        color: #1E88E5;
    }
    .expander-text {
        color: #ffffff;
        font-size: 1rem !important;
    }
    p {
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<h1 class="main-header">Brazil E-Commerce</h1>', unsafe_allow_html=True)
    st.image("dashboard/logo.svg")

    start_date, end_date = st.date_input(
        label="Date Range",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & 
                 (all_df["order_approved_at"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
sum_spend_df = create_sum_spend_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
review_score, common_score = review_score_df(main_df)
state, most_common_state = create_bystate_df(main_df)
city, most_common_city = create_bycity_df(main_df)
order_status, common_status = create_order_status(main_df)
top_recency, top_frequency, top_monetary = create_rm_df(main_df)

st.markdown('<h2 class="sub-header">E-commerce Income</h2>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    total_spend = format_currency(sum_spend_df["total_spend"].sum(), "BRL", locale="pt_BR")
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-label">Total Income</p>
        <p class="metric-value">{total_spend}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    avg_spend = format_currency(sum_spend_df["total_spend"].mean(), "BRL", locale="pt_BR")
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-label">Average Daily Income</p>
        <p class="metric-value">{avg_spend}</p>
    </div>
    """, unsafe_allow_html=True)

fig_income = px.line(
    sum_spend_df, 
    x="order_approved_at", 
    y="total_spend",
    labels={"order_approved_at": "Date", "total_spend": "Total Income (BRL)"},
    title="Daily Income Timeline"
)
fig_income.update_traces(line_color='#1E88E5', line_width=2)
fig_income.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor='rgba(230, 230, 230, 0.6)'),
    margin=dict(l=20, r=20, t=40, b=20),
    height=400
)
st.plotly_chart(fig_income, use_container_width=True)

with st.expander("Bagaimana tren performa penjualan E-commerce dari waktu ke waktu?"):
    st.markdown('<p class="expander-text">Performa penjualan E-commerce menunjukkan tren pertumbuhan signifikan dari waktu ke waktu. Pada periode awal (2016 hingga awal 2017), penjualan masih rendah dengan sedikit aktivitas. Memasuki pertengahan 2017, terjadi peningkatan bertahap. Lonjakan besar mulai terlihat pada akhir 2017 hingga awal 2018, kemungkinan dipengaruhi oleh promosi atau event belanja spesial. Menjelang akhir 2018, performa cenderung menurun atau stabil, kemungkinan karena faktor musiman atau penyesuaian pasar.</p>', unsafe_allow_html=True)

st.markdown('<hr>', unsafe_allow_html=True)
st.markdown('<h2 class="sub-header">Product Sales Chart</h2>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    total_items = sum_order_items_df["product_count"].sum()
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-label">Total Product Sales</p>
        <p class="metric-value">{total_items:,}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    avg_items = sum_order_items_df["product_count"].mean()
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-label">Average Item Sales Per Category</p>
        <p class="metric-value">{avg_items:.2f}</p>
    </div>
    """, unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    top_products = sum_order_items_df.head(5)
    fig_top = px.bar(
        top_products,
        x="product_count",
        y="product_category_name_english",
        title="Top 5 Best-Selling Products",
        orientation='h',
        color_discrete_sequence=['#1E88E5'] * len(top_products),
        text="product_count"
    )
    fig_top.update_traces(textposition='outside')
    fig_top.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='rgba(230, 230, 230, 0.6)'),
        yaxis_title=None,
        xaxis_title="Number of Sales",
        margin=dict(l=20, r=20, t=40, b=20),
        height=400
    )
    st.plotly_chart(fig_top, use_container_width=True)

with col2:
    bottom_products = sum_order_items_df.sort_values(by="product_count", ascending=True).head(5)
    fig_bottom = px.bar(
        bottom_products,
        x="product_count",
        y="product_category_name_english",
        title="5 Least-Selling Products",
        orientation='h',
        color_discrete_sequence=['#90CAF9'] * len(bottom_products),
        text="product_count"
    )
    fig_bottom.update_traces(textposition='outside')
    fig_bottom.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='rgba(230, 230, 230, 0.6)'),
        yaxis_title=None,
        xaxis_title="Number of Sales",
        margin=dict(l=20, r=20, t=40, b=20),
        height=400
    )
    st.plotly_chart(fig_bottom, use_container_width=True)

with st.expander("Produk mana yang paling banyak dan paling sedikit terjual di E-commerce?"):
    st.markdown('<p class="expander-text">Produk kategori bed_bath_table yang sangat laris menunjukkan permintaan tinggi yang berkelanjutan, yang bisa dijadikan peluang untuk meningkatkan inventori dan promosi, sedangkan penjualan rendah pada kategori auto dan garden_tools memerlukan pengembangan strategi pemasaran yang lebih kreatif dan penyesuaian produk untuk meningkatkan penjualan.</p>', unsafe_allow_html=True)

st.markdown('<hr>', unsafe_allow_html=True)
st.markdown('<h2 class="sub-header">Distribution of Customers</h2>', unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["State", "Top 10 City", "Order Status"])

with tab1:
    st.markdown(f"<p>Most Common State: <strong>{most_common_state}</strong></p>", unsafe_allow_html=True)
    st.markdown("<p>Jumlah pelanggan berdasarkan negara bagian dengan Sao Paulo sebanyak 41.666 pelanggan.</p>", unsafe_allow_html=True)
    
    state_sorted = state.sort_values(by='customer_count', ascending=False)
    fig_state = px.bar(
        state_sorted,
        x="customer_count",
        y="customer_state",
        title="Customers from Each State",
        orientation='h',
        color_discrete_sequence=['#1E88E5'] * len(state_sorted),
        text="customer_count"
    )
    fig_state.update_traces(
        marker_color=['#1E88E5' if x == most_common_state else '#90CAF9' for x in state_sorted.customer_state],
        textposition='outside'
    )
    fig_state.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='rgba(230, 230, 230, 0.6)'),
        yaxis_title=None,
        xaxis_title="Number of Customers",
        height=600,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_state, use_container_width=True)

with tab2:
    st.markdown(f"<p>Most Common City: <strong>{most_common_city}</strong></p>", unsafe_allow_html=True)
    st.markdown("<p>10 besar kota dengan jumlah pelanggan. Kota Sao Paulo menempati urutan 1.</p>", unsafe_allow_html=True)
    
    city_sorted = city.sort_values(by='total_customer', ascending=False)
    top_10_cities = city_sorted.head(10)
    fig_city = px.bar(
        top_10_cities,
        x="total_customer",
        y="customer_city",
        title="Top 10 Cities by Customer Count",
        orientation='h',
        color_discrete_sequence=['#1E88E5'] * len(top_10_cities),
        text="total_customer"
    )
    fig_city.update_traces(
        marker_color=['#1E88E5' if x == most_common_city else '#90CAF9' for x in top_10_cities.customer_city],
        textposition='outside'
    )
    fig_city.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='rgba(230, 230, 230, 0.6)'),
        yaxis_title=None,
        xaxis_title="Number of Customers",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_city, use_container_width=True)

with tab3:
    common_status_ = order_status.index[0] if isinstance(order_status, pd.Series) else ""
    st.markdown(f"<p>Most Common Order Status: <strong>{common_status_}</strong></p>", unsafe_allow_html=True)
    st.markdown("<p>Visualisasi ini menunjukkan distribusi status pesanan dalam sistem E-commerce, dengan jumlah pesanan dalam berbagai status. Mayoritas pesanan berada dalam status delivered (115.708).</p>", unsafe_allow_html=True)
    
    order_status_df = pd.DataFrame({
        'status': order_status.index,
        'count': order_status.values
    })
    
    fig_status = px.bar(
        order_status_df,
        x="count",
        y="status",
        title="Order Status Distribution",
        orientation='h',
        color_discrete_sequence=['#1E88E5'] * len(order_status_df),
        text="count"
    )
    fig_status.update_traces(textposition='outside')
    fig_status.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='rgba(230, 230, 230, 0.6)'),
        yaxis_title=None,
        xaxis_title="Count",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_status, use_container_width=True)

st.markdown('<hr>', unsafe_allow_html=True)
st.markdown('<h2 class="sub-header">Best Customer Based on RFM Analysis</h2>', unsafe_allow_html=True)

rfm_tab1, rfm_tab2, rfm_tab3 = st.tabs(["Recency", "Frequency", "Monetary"])

with rfm_tab1:
    fig_recency = px.bar(
        top_recency,
        x="recency",
        y="customer_id",
        title="Top Customers by Recency (Lower is Better)",
        orientation='h',
        color_discrete_sequence=['#1E88E5'] * len(top_recency),
        text="recency"
    )
    fig_recency.update_traces(textposition='outside')
    fig_recency.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='rgba(230, 230, 230, 0.6)'),
        yaxis_title=None,
        xaxis_title="Days Since Last Purchase",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_recency, use_container_width=True)
    
    with st.expander("Kapan terakhir seorang pelanggan melakukan transaksi?"):
        st.markdown('<p class="expander-text">Pelanggan 856336203359aa6a61bf3826f7d84c49 dan a4b417188addbc05b26b72d5e44837a1 merupakan pelanggan yang paling terakhir melakukan transaksi.</p>', unsafe_allow_html=True)

with rfm_tab2:
    fig_frequency = px.bar(
        top_frequency,
        x="frequency",
        y="customer_id",
        title="Top Customers by Purchase Frequency",
        orientation='h',
        color_discrete_sequence=['#1E88E5'] * len(top_frequency),
        text="frequency"
    )
    fig_frequency.update_traces(textposition='outside')
    fig_frequency.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='rgba(230, 230, 230, 0.6)'),
        yaxis_title=None,
        xaxis_title="Number of Purchases",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_frequency, use_container_width=True)
    
    with st.expander("Seberapa sering seorang pelanggan melakukan transaksi?"):
        st.markdown('<p class="expander-text">Setelah dianalisis dan divisualisasikan, ternyata setiap pelanggan hanya melakukan pembelian sekali.</p>', unsafe_allow_html=True)

with rfm_tab3:
    fig_monetary = px.bar(
        top_monetary,
        x="monetary",
        y="customer_id",
        title="Top Customers by Total Spending",
        orientation='h',
        color_discrete_sequence=['#1E88E5'] * len(top_monetary),
        text=top_monetary["monetary"].apply(lambda x: f"R${x:,.2f}")
    )
    fig_monetary.update_traces(textposition='outside')
    fig_monetary.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='rgba(230, 230, 230, 0.6)'),
        yaxis_title=None,
        xaxis_title="Total Spend (BRL)",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_monetary, use_container_width=True)
    
    with st.expander("Berapa total pengeluaran tertinggi dari seorang pelanggan?"):
        st.markdown('<p class="expander-text">Pelanggan 1617b1357756262bfa56ab541c47bc16 merupakan pelanggan dengan total pengeluaran tertinggi, yaitu sejumlah 109.312 ribu.</p>', unsafe_allow_html=True)

st.markdown('<hr>', unsafe_allow_html=True)
st.markdown('<h2 class="sub-header">Review Score Distribution</h2>', unsafe_allow_html=True)

review_df = pd.DataFrame({
    'score': review_score.index,
    'count': review_score.values
})

fig_review = px.bar(
    review_df,
    x="score",
    y="count",
    title="Distribution of Customer Review Scores",
    color="score",
    color_continuous_scale=px.colors.sequential.Blues,
    text="count"
)
fig_review.update_traces(textposition='outside')
fig_review.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(
        title="Review Score",
        tickmode='linear',
        dtick=1,
        showgrid=False
    ),
    yaxis=dict(
        title="Number of Reviews",
        showgrid=True,
        gridcolor='rgba(230, 230, 230, 0.6)'
    ),
    height=400,
    margin=dict(l=20, r=20, t=40, b=20),
    coloraxis_showscale=False
)
st.plotly_chart(fig_review, use_container_width=True)

with st.expander("Bagaimana distribusi skor ulasan pelanggan?"):
    st.markdown('<p class="expander-text">Distribusi skor ulasan pelanggan menunjukkan bahwa mayoritas pelanggan memberikan skor 5 dengan jumlah lebih dari 66.000 pelanggan, yang menunjukkan kepuasan pelanggan yang tinggi terhadap layanan E-commerce.</p>', unsafe_allow_html=True)

st.caption('Copyright © Lukas Krisna 2025')