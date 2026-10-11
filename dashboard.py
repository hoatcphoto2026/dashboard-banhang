import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Dashboard doanh thu", layout="wide")
st.title("Dashboard doanh thu bán hàng")

# ----- Đọc và chuẩn bị dữ liệu -----
SHEET_ID = "14Rzxzx-1xTuSnQa-Fzfa0gVpEpALrOJeScHFMzp-Tp0"  # thay bằng ID của bạn
URL_SHEET = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet1"

@st.cache_data(ttl=300)  # làm mới dữ liệu sau 5 phút
def doc_du_lieu():
    return pd.read_csv(URL_SHEET)

df = doc_du_lieu()


df["ngay"] = pd.to_datetime(df["ngay"])
df["san_pham"] = df["san_pham"].astype(str).str.strip().str.title()
df["khu_vuc"] = df["khu_vuc"].astype(str).str.strip().str.title()
df["doanh_thu"] = df["so_luong"] * df["gia_ban"] / 1000  # đơn vị: nghìn đồng
df["thang"] = df["ngay"].dt.to_period("M")
df["quy"] = df["ngay"].dt.to_period("Q")

DS_SP = sorted(df["san_pham"].unique())
DS_KV = sorted(df["khu_vuc"].unique())

# ----- Bộ lọc thời gian -----
st.sidebar.header("Bộ lọc")
st.sidebar.subheader("Thời gian")
kieu_loc = st.sidebar.radio("Lọc theo", ["Tất cả", "Ngày", "Tháng", "Quý"])

if kieu_loc == "Ngày":
    ds_ngay = sorted(df["ngay"].dt.date.unique())
    chon_ngay = st.sidebar.selectbox(
        "Chọn ngày", ds_ngay, format_func=lambda d: d.strftime("%d/%m/%Y")
    )
    df_tg = df[df["ngay"].dt.date == chon_ngay]
    nhan_tg = f"Ngày {chon_ngay.strftime('%d/%m/%Y')}"
elif kieu_loc == "Tháng":
    ds_thang = sorted(df["thang"].unique())
    chon_thang = st.sidebar.selectbox(
        "Chọn tháng", ds_thang, format_func=lambda p: f"Tháng {p.month}/{p.year}"
    )
    df_tg = df[df["thang"] == chon_thang]
    nhan_tg = f"Tháng {chon_thang.month}/{chon_thang.year}"
elif kieu_loc == "Quý":
    ds_quy = sorted(df["quy"].unique())
    chon_quy = st.sidebar.selectbox(
        "Chọn quý", ds_quy, format_func=lambda p: f"Quý {p.quarter}/{p.year}"
    )
    df_tg = df[df["quy"] == chon_quy]
    nhan_tg = f"Quý {chon_quy.quarter}/{chon_quy.year}"
else:
    df_tg = df
    nhan_tg = "Tất cả dữ liệu"

# ----- Bộ lọc sản phẩm và khu vực -----
st.sidebar.subheader("Sản phẩm & khu vực")
sp_chon = st.sidebar.multiselect("Sản phẩm", options=DS_SP, default=DS_SP)
kv_chon = st.sidebar.multiselect("Khu vực", options=DS_KV, default=DS_KV)

df_loc = df_tg[df_tg["san_pham"].isin(sp_chon) & df_tg["khu_vuc"].isin(kv_chon)]

if df_loc.empty:
    st.warning("Không có dữ liệu phù hợp với bộ lọc đã chọn.")
    st.stop()

st.caption(f"Khoảng thời gian: {nhan_tg}")

# ----- Dữ liệu tổng hợp -----
sp_sl = (
    df_loc.groupby("san_pham", as_index=False)["so_luong"].sum()
    .sort_values("so_luong", ascending=False)
)
ban_chay = sp_sl.iloc[0]["san_pham"]
so_luong_ban_chay = int(sp_sl.iloc[0]["so_luong"])

doanh_thu_sp = (
    df_loc.groupby("san_pham", as_index=False)["doanh_thu"].sum()
    .sort_values("doanh_thu", ascending=True)
)
doanh_thu_kv = (
    df_loc.groupby("khu_vuc", as_index=False)["doanh_thu"].sum()
    .sort_values("doanh_thu", ascending=False)
)
doanh_thu_ngay = df_loc.groupby("ngay", as_index=False)["doanh_thu"].sum()

# ----- Chỉ số tổng quan -----
c1, c2, c3, c4 = st.columns(4)
c1.metric("Tổng doanh thu", f"{df_loc['doanh_thu'].sum():,.0f} (x1.000 VNĐ)")
c2.metric("Tổng số lượng", f"{df_loc['so_luong'].sum():,}")
c3.metric("Số giao dịch", len(df_loc))
c4.metric("Sản phẩm bán chạy nhất", ban_chay, f"{so_luong_ban_chay:,} sản phẩm")

st.divider()

# ----- Hàng 1: Doanh thu theo sản phẩm và tỉ lệ -----
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("Doanh thu theo sản phẩm")
    fig_sp = px.bar(
        doanh_thu_sp, x="doanh_thu", y="san_pham", orientation="h", text="doanh_thu",
        labels={"doanh_thu": "Doanh thu (x1.000 VNĐ)", "san_pham": "Sản phẩm"},
    )
    fig_sp.update_traces(texttemplate="%{x:,.0f}", textposition="outside", marker_color="#2468C8")
    fig_sp.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=400, yaxis_title=None)
    st.plotly_chart(fig_sp, use_container_width=True)

with col2:
    st.subheader("Tỉ lệ doanh thu theo sản phẩm")
    fig_pie = px.pie(doanh_thu_sp, names="san_pham", values="doanh_thu", hole=0.4)
    fig_pie.update_traces(
        textinfo="percent+label", texttemplate="%{percent:.1%}",
        hovertemplate="%{label}: %{value:,.0f} (x1.000 VNĐ) (%{percent:.1%})<extra></extra>",
    )
    fig_pie.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

# ----- Hàng 2: Số lượng bán theo sản phẩm (nổi bật bán chạy nhất) và khu vực -----
col3, col4 = st.columns(2)

with col3:
    st.subheader("Số lượng bán theo sản phẩm")
    sp_sl_asc = sp_sl.sort_values("so_luong", ascending=True)
    fig_sl = px.bar(
        sp_sl_asc, x="so_luong", y="san_pham", orientation="h", text="so_luong",
        labels={"so_luong": "Số lượng", "san_pham": "Sản phẩm"},
    )
    mau = ["#E4572E" if sp == ban_chay else "#2468C8" for sp in sp_sl_asc["san_pham"]]
    fig_sl.update_traces(texttemplate="%{x:,}", textposition="outside", marker_color=mau)
    fig_sl.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=400, yaxis_title=None)
    st.plotly_chart(fig_sl, use_container_width=True)
    st.caption(f"Màu cam: sản phẩm bán chạy nhất ({ban_chay})")

with col4:
    st.subheader("Doanh thu theo khu vực")
    fig_kv = px.bar(
        doanh_thu_kv, x="khu_vuc", y="doanh_thu", text="doanh_thu",
        labels={"doanh_thu": "Doanh thu (x1.000 VNĐ)", "khu_vuc": "Khu vực"},
    )
    fig_kv.update_traces(texttemplate="%{y:,.0f}", textposition="outside", marker_color="#2468C8")
    fig_kv.update_layout(margin=dict(l=10, r=10, t=30, b=10), height=400, xaxis_title=None)
    st.plotly_chart(fig_kv, use_container_width=True)

# ----- Hàng 3: Doanh thu theo ngày -----
st.subheader("Doanh thu theo ngày")
fig_ngay = px.line(
    doanh_thu_ngay, x="ngay", y="doanh_thu", markers=True,
    labels={"doanh_thu": "Doanh thu (x1.000 VNĐ)", "ngay": "Ngày"},
)
fig_ngay.update_traces(line_color="#2468C8")
fig_ngay.update_layout(margin=dict(l=10, r=10, t=30, b=10), height=350)
st.plotly_chart(fig_ngay, use_container_width=True)

# ----- Bảng dữ liệu -----
with st.expander("Xem bảng dữ liệu chi tiết"):
    st.dataframe(df_loc, use_container_width=True)