import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency


sns.set_theme(style='dark')


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

with st.sidebar:

    st.title("Brazil E-Commerce")

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


st.subheader("E-commerce Income")
col1, col2 = st.columns(2)

with col1:
    total_spend = format_currency(sum_spend_df["total_spend"].sum(), "BRL", locale="pt_BR")
    st.markdown(f"Total Income: **{total_spend}**")

with col2:
    avg_spend = format_currency(sum_spend_df["total_spend"].mean(), "BRL", locale="pt_BR")
    st.markdown(f"Average Income: **{avg_spend}**")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    sum_spend_df["order_approved_at"],
    sum_spend_df["total_spend"],
    linewidth=1,
    color="#72BCD4"
)
ax.tick_params(axis="x", rotation=15)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

with st.expander("Bagaimana tren performa penjualan E-commerce dari waktu ke waktu?"):
    st.write("Performa penjualan E-commerce menunjukkan tren pertumbuhan signifikan dari waktu ke waktu. Pada periode awal (2016 hingga awal 2017), penjualan masih rendah dengan sedikit aktivitas. Memasuki pertengahan 2017, terjadi peningkatan bertahap. Lonjakan besar mulai terlihat pada akhir 2017 hingga awal 2018, kemungkinan dipengaruhi oleh promosi atau event belanja spesial. Menjelang akhir 2018, performa cenderung menurun atau stabil, kemungkinan karena faktor musiman atau penyesuaian pasar.")


with st.container():
    st.write("---")
    st.subheader("Product Sales Chart")
    col1, col2 = st.columns(2)

    with col1:
        total_items = sum_order_items_df["product_count"].sum()
        st.markdown(f"Total Product Sales: **{total_items}**")

    with col2:
        avg_items = sum_order_items_df["product_count"].mean()
        st.markdown(f"Average Item Sales: **{avg_items}**")

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(85, 25))

    colors = ["#72BCD4", "#90CCE0", "#ADE0EC", "#ADE0EC", "#ADE0EC"]

    sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.head(5), palette=colors,
                ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("Number of Sales", fontsize=70)
    ax[0].set_title("Produk Paling Laris", loc="center", fontsize=100)
    ax[0].tick_params(axis='y', labelsize=65)
    ax[0].tick_params(axis='x', labelsize=60)

    sns.barplot(x="product_count", y="product_category_name_english",
                data=sum_order_items_df.sort_values(by="product_count", ascending=True).head(5), palette=colors,
                ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel("Number of Sales", fontsize=70)
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].set_title("Produk Kurang Laris", loc="center", fontsize=100)
    ax[1].tick_params(axis='y', labelsize=65)
    ax[1].tick_params(axis='x', labelsize=60)

    st.pyplot(fig)

    with st.expander("Produk mana yang paling banyak dan paling sedikit terjual di E-commerce?"):
        st.write("Produk kategori bed_bath_table yang sangat laris menunjukkan permintaan tinggi yang berkelanjutan, yang bisa dijadikan peluang untuk meningkatkan inventori dan promosi, sedangkan penjualan rendah pada kategori auto dan garden_tools memerlukan pengembangan strategi pemasaran yang lebih kreatif dan penyesuaian produk untuk meningkatkan penjualan.")


with st.container():
    st.write("---")
    st.subheader("Distribution of Customers")
    tab1, tab2, tab3 = st.tabs(["State", "Top 10 City", "Order Status"])

    with tab1:
        most_common_state = state.customer_state.value_counts().index[0]
        st.markdown(f"Most Common State: **{most_common_state}**")
        st.markdown("Jumlah pelanggan berdasarkan negara bagian dengan Sao Paulo sebanyak 41.666 pelanggan.")

        fig, ax = plt.subplots(figsize=(12, 12))

        green_palette = ["#72BCD4" if state == most_common_state else "#B1DEF0" for state in state.customer_state]

        sns.barplot(y=state.customer_state,
                    x=state.customer_count.values,
                    data=state,
                    palette=green_palette)

        plt.title("Customers from Each State", fontsize=15)
        plt.xlabel("Number of Customers")
        plt.ylabel("State")
        plt.xticks(fontsize=12)

        for i, v in enumerate(state.customer_count.values):
            ax.text(v + 1, i, str(v), color='black', va='center', ha='left')

        x_max = state.customer_count.max() + 3000
        plt.xlim(0, x_max)

        st.pyplot(fig)


    with tab2:
        st.markdown(f"Most Common City: **{most_common_city}**")
        st.markdown("10 besar kota dengan jumlah pelanggan. Kota Sao Paulo menempati urutan 1.")

        city_sorted = city.sort_values(by='total_customer', ascending=False)
        top_10_cities = city_sorted.head(10)

        fig, ax = plt.subplots(figsize=(12, 6))

        green_palette = ["#72BCD4" if city_name == most_common_city else "#B1DEF0" for city_name in
                         top_10_cities.customer_city]

        sns.barplot(y=top_10_cities.customer_city,
                    x=top_10_cities.total_customer,
                    palette=green_palette)

        plt.title("Top 10 Customers from Each City", fontsize=15)
        plt.xlabel("Number of Customers")
        plt.ylabel("City")
        plt.xticks(fontsize=12)

        for i, v in enumerate(top_10_cities.total_customer):
            ax.text(v + 1, i, str(v), color='black', va='center', ha='left')

        x_max = top_10_cities.total_customer.max() + 1500
        plt.xlim(0, x_max)

        st.pyplot(fig)


    with tab3:
        common_status_ = order_status.value_counts().index[0]
        st.markdown(f"Most Common Order Status: **{common_status_}**")
        st.markdown("Visualisasi ini menunjukkan distribusi status pesanan dalam sistem E-commerce, dengan jumlah pesanan dalam berbagai status. Mayoritas pesanan berada dalam status delivered (115.708).")

        fig, ax = plt.subplots(figsize=(6, 3))

        green_palette = ["#72BCD4" if status == common_status_ else "#72BCD4" for status in order_status.index]

        sns.barplot(y=order_status.index,
                    x=order_status.values,
                    order=order_status.index,
                    palette=green_palette)

        plt.title("Order Status", fontsize=15)
        plt.xlabel("Count")
        plt.ylabel("Status")
        plt.xticks(fontsize=12)

        for i, v in enumerate(order_status.values):
            ax.text(v + 1, i, str(v), color='black', va='center', ha='left')

        x_max = order_status.max() + 20000
        plt.xlim(0, x_max)

        st.pyplot(fig)

with st.container():
  st.write("---")

  st.subheader("Best Customer Based on RFM Analysis")

  fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(32, 6))

  colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

  sns.barplot(x="recency", y="customer_id", data=top_recency, palette=colors, ax=ax[0], orient='h')
  ax[0].set_ylabel(None)
  ax[0].set_xlabel(None)
  ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
  ax[0].tick_params(axis='x', labelsize=15)
  ax[0].tick_params(axis='y', labelsize=12)

  sns.barplot(x="frequency", y="customer_id", data=top_frequency, palette=colors, ax=ax[1], orient='h')
  ax[1].set_ylabel(None)
  ax[1].set_xlabel(None)
  ax[1].set_title("By Frequency", loc="center", fontsize=18)
  ax[1].tick_params(axis='x', labelsize=15)
  ax[1].tick_params(axis='y', labelsize=12)

  sns.barplot(x="monetary", y="customer_id", data=top_monetary, palette=colors, ax=ax[2], orient='h')
  ax[2].set_ylabel(None)
  ax[2].set_xlabel(None)
  ax[2].set_title("By Monetary", loc="center", fontsize=18)
  ax[2].tick_params(axis='x', labelsize=15)
  ax[2].tick_params(axis='y', labelsize=12)

  import matplotlib.ticker as mtick

  formatter = mtick.StrMethodFormatter('${x:,.0f}')
  ax[2].xaxis.set_major_formatter(formatter)

  plt.suptitle("Best Customer Based on RFM Parameters", fontsize=20)

  plt.tight_layout()
  plt.subplots_adjust(top=0.85)

  st.pyplot(fig)

  with st.expander("Kapan terakhir seorang pelanggan melakukan transaksi?"):
      st.write(
          "Pelanggan 856336203359aa6a61bf3826f7d84c49 dan a4b417188addbc05b26b72d5e44837a1 merupakan pelanggan yang paling terakhir melakukan transaksi.")

  with st.expander("Seberapa sering seorang pelanggan melakukan transaksi?"):
      st.write(
          "Setelah dianalisis dan divisualisasikan, ternyata setiap pelanggan hanya melakukan pembelian sekali.")

  with st.expander("Kapan terakhir seorang pelanggan melakukan transaksi?"):
      st.write(
          "Pelanggan 1617b1357756262bfa56ab541c47bc16 merupakan pelanggan dengan total pengeluaran tertinggi, yaitu sejumlah 109.312 ribu.")


st.caption('Copyright © Lukas Krisna 2025')