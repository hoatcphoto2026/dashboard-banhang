import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Dashboard doanh thu", layout="wide")
st.title("Dashboard doanh thu bán hàng")

# ----- Đọc và chuẩn bị dữ liệu -----
df = pd.read_excel("DATA_DT.xlsx")
df["ngay"] = pd.to_datetime(df["ngay"])
df["san_pham"] = df["san_pham"].astype(str).str.strip().str.title()
df["khu_vuc"] = df["khu_vuc"].astype(str).str.strip().str.title()
df["doanh_thu"] = df["so_luong"] * df["gia_ban"]

# ----- Bộ lọc ở thanh bên -----
st.sidebar.header("Bộ lọc")
san_pham_chon = st.sidebar.multiselect(
    "Sản phẩm", options=sorted(df["san_pham"].unique()), default=sorted(df["san_pham"].unique())
)
khu_vuc_chon = st.sidebar.multiselect(
    "Khu vực", options=sorted(df["khu_vuc"].unique()), default=sorted(df["khu_vuc"].unique())
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

# ----- Dữ liệu tổng hợp -----
doanh_thu_sp = (
    df_loc.groupby("san_pham", as_index=False)["doanh_thu"].sum()
    .sort_values("doanh_thu", ascending=True)  # ascending=True để thanh lớn nhất nằm trên cùng
)
doanh_thu_kv = (
    df_loc.groupby("khu_vuc", as_index=False)["doanh_thu"].sum()
    .sort_values("doanh_thu", ascending=False)
)
doanh_thu_ngay = df_loc.groupby("ngay", as_index=False)["doanh_thu"].sum()

# ----- Hàng 1: Sản phẩm (cột ngang) và biểu đồ tròn -----
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("Doanh thu theo sản phẩm")
    fig_sp = px.bar(
        doanh_thu_sp, x="doanh_thu", y="san_pham", orientation="h",
        text="doanh_thu", labels={"doanh_thu": "Doanh thu (VNĐ)", "san_pham": "Sản phẩm"},
    )
    fig_sp.update_traces(texttemplate="%{x:,.0f}", textposition="outside", marker_color="#2468C8")
    fig_sp.update_layout(
        xaxis_tickformat=",.0f", margin=dict(l=10, r=10, t=10, b=10), height=400,
        yaxis_title=None,
    )
    st.plotly_chart(fig_sp, use_container_width=True)

with col2:
    st.subheader("Tỉ lệ doanh thu theo sản phẩm")
    fig_pie = px.pie(
        doanh_thu_sp, names="san_pham", values="doanh_thu", hole=0.4,
    )
    fig_pie.update_traces(
        textinfo="percent+label", texttemplate="%{percent:.1%}",
        hovertemplate="%{label}: %{value:,.0f} VNĐ (%{percent:.1%})<extra></extra>",
    )
    fig_pie.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=400, showlegend=True)
    st.plotly_chart(fig_pie, use_container_width=True)

# ----- Hàng 2: Khu vực và doanh thu theo ngày -----
col3, col4 = st.columns(2)

with col3:
    st.subheader("Doanh thu theo khu vực")
    fig_kv = px.bar(
        doanh_thu_kv, x="khu_vuc", y="doanh_thu", text="doanh_thu",
        labels={"doanh_thu": "Doanh thu (VNĐ)", "khu_vuc": "Khu vực"},
    )
    fig_kv.update_traces(texttemplate="%{y:,.0f}", textposition="outside", marker_color="#2468C8")
    fig_kv.update_layout(
        yaxis_tickformat=",.0f", margin=dict(l=10, r=10, t=30, b=10), height=400,
        xaxis_title=None,
    )
    st.plotly_chart(fig_kv, use_container_width=True)

with col4:
    st.subheader("Doanh thu theo ngày")
    fig_ngay = px.line(
        doanh_thu_ngay, x="ngay", y="doanh_thu", markers=True,
        labels={"doanh_thu": "Doanh thu (VNĐ)", "ngay": "Ngày"},
    )
    fig_ngay.update_traces(line_color="#2468C8")
    fig_ngay.update_layout(
        yaxis_tickformat=",.0f", margin=dict(l=10, r=10, t=30, b=10), height=400,
    )
    st.plotly_chart(fig_ngay, use_container_width=True)

# ----- Bảng dữ liệu -----
with st.expander("Xem bảng dữ liệu chi tiết"):
    st.dataframe(df_loc, use_container_width=True)