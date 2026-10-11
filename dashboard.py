import pandas as pd
import streamlit as st

st.set_page_config(page_title="Dashboard doanh thu", layout="wide")
st.title("Dashboard doanh thu bán hàng")

df = pd.read_excel("DATA_DT.xlsx")
df["ngay"] = pd.to_datetime(df["ngay"])
df["doanh_thu"] = df["so_luong"] * df["gia_ban"]


# ----- Bộ lọc ở thanh bên -----
st.sidebar.header("Bộ lọc")

df["san_pham"] = df["san_pham"].str.strip().str.title()
df["khu_vuc"] = df["khu_vuc"].str.strip().str.title()

san_pham_chon = st.sidebar.multiselect(
    "Sản phẩm", options=df["san_pham"].unique(), default=list(df["san_pham"].unique())
)
khu_vuc_chon = st.sidebar.multiselect(
    "Khu vực", options=df["khu_vuc"].unique(), default=list(df["khu_vuc"].unique())
)

df_loc = df[df["san_pham"].isin(san_pham_chon) & df["khu_vuc"].isin(khu_vuc_chon)]

if df_loc.empty:
    st.warning("Không có dữ liệu phù hợp với bộ lọc đã chọn.")
    st.stop()

# ----- Chỉ số tổng quan -----
c1, c2, c3 = st.columns(3)
c1.metric("Tổng doanh thu", f"{df_loc['doanh_thu'].sum():,.0f} VNĐ")
c2.metric("Tổng số lượng", f"{df_loc['so_luong'].sum():,}")
c3.metric("Số giao dịch", len(df_loc))

st.divider()

# ----- Biểu đồ -----
col1, col2 = st.columns(2)

with col1:
    st.subheader("Doanh thu theo sản phẩm")
    doanh_thu_sp = df_loc.groupby("san_pham")["doanh_thu"].sum().sort_values(ascending=False)
    st.bar_chart(doanh_thu_sp)

with col2:
    st.subheader("Doanh thu theo khu vực")
    doanh_thu_kv = df_loc.groupby("khu_vuc")["doanh_thu"].sum()
    st.bar_chart(doanh_thu_kv)

st.subheader("Doanh thu theo ngày")
doanh_thu_ngay = df_loc.groupby("ngay")["doanh_thu"].sum()
st.line_chart(doanh_thu_ngay)

# ----- Bảng dữ liệu -----
with st.expander("Xem bảng dữ liệu chi tiết"):
    st.dataframe(df_loc, use_container_width=True)
