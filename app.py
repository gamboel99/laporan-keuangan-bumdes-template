import os
import base64
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

# Dropdown pilihan laporan
menu = st.selectbox("Pilih Laporan", [
    "Laporan Posisi Keuangan",
    "Laporan Laba Rugi",
    "Laporan Arus Kas",
    "Laporan Perubahan Ekuitas"
])

# Inisialisasi data di session_state
if "data" not in st.session_state:
    st.session_state.data = {}

if menu not in st.session_state.data:
    st.session_state.data[menu] = pd.DataFrame(columns=["Uraian", "Kategori", "Jumlah"])

# Form tambah data
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

# Tampilkan tabel laporan
st.dataframe(st.session_state.data[menu], use_container_width=True)

# Fungsi Export HTML (yang bisa dicetak ke PDF manual)
def export_pdf():
    html_out = f"""
    <html>
    <head><meta charset="utf-8"></head>
    <body>
        <h2>{menu}</h2>
        <p><strong>BUMDes:</strong> {nama_bumdes}<br>
           <strong>Desa:</strong> {desa}<br>
           <strong>Tahun:</strong> {tahun}</p>
        <table border="1" cellpadding="4" cellspacing="0">
            <tr><th>Uraian</th><th>Kategori</th><th>Jumlah</th></tr>
            {''.join(f"<tr><td>{row['Uraian']}</td><td>{row['Kategori']}</td><td>{row['Jumlah']}</td></tr>" for i, row in st.session_state.data[menu].iterrows())}
        </table>
    </body>
    </html>
    """
    b64 = base64.b64encode(html_out.encode()).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="laporan_keuangan.html">📥 Unduh versi HTML (bisa cetak ke PDF)</a>'
    st.markdown(href, unsafe_allow_html=True)

# Panggil fungsi export
export_pdf()
