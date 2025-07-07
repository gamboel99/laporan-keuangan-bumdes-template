import os
import streamlit as st
import pandas as pd
from jinja2 import Template

st.set_page_config(page_title="Laporan Keuangan BUMDes", layout="wide")

# Identitas BUMDes
st.sidebar.title("Identitas BUMDes")
nama_bumdes = st.sidebar.text_input("Nama BUMDes", "Buwana Raharja")
desa = st.sidebar.text_input("Desa", "Keling")
tahun = st.sidebar.number_input("Tahun Laporan", 2025, step=1)

st.title("📊 Laporan Keuangan BUMDes")

menu = st.selectbox("Pilih Laporan", [
    "Laporan Posisi Keuangan",
    "Laporan Laba Rugi",
    "Laporan Arus Kas",
    "Laporan Perubahan Ekuitas"
])

if "data" not in st.session_state:
    st.session_state.data = {}

if menu not in st.session_state.data:
    st.session_state.data[menu] = pd.DataFrame(columns=["Uraian", "Kategori", "Jumlah"])

with st.expander("➕ Tambah Data"):
    col1, col2, col3 = st.columns(3)
    with col1:
        uraian = st.text_input("Uraian")
    with col2:
        kategori = st.text_input("Kategori")
    with col3:
        jumlah = st.number_input("Jumlah", value=0.0)
    if st.button("Tambah"):
        if uraian and kategori:
            st.session_state.data[menu] = pd.concat([
                st.session_state.data[menu],
                pd.DataFrame([{"Uraian": uraian, "Kategori": kategori, "Jumlah": jumlah}])
            ], ignore_index=True)
        else:
            st.warning("Mohon lengkapi uraian dan kategori.")

st.dataframe(st.session_state.data[menu], use_container_width=True)

# Export PDF
def export_pdf():
    import base64
    html_out = """
    <html>
    <head><meta charset="utf-8"></head>
    <body>
        <h2>Laporan Keuangan BUMDes</h2>
        <p>Fitur PDF belum aktif di versi online. Silakan gunakan tombol ekspor Excel atau download versi HTML ini dan cetak ke PDF secara manual.</p>
    </body>
    </html>
    """
    b64 = base64.b64encode(html_out.encode()).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="laporan_keuangan.html">📥 Unduh versi HTML</a>'
    st.markdown(href, unsafe_allow_html=True)
