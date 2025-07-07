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

# Inisialisasi struktur data
if "data" not in st.session_state:
    st.session_state.data = {
        "Laporan Posisi Keuangan": pd.DataFrame(columns=["Uraian", "Kategori", "Jumlah"]),
        "Laporan Laba Rugi": pd.DataFrame(columns=["Uraian", "Kategori", "Jumlah"]),
        "Laporan Arus Kas": pd.DataFrame(columns=["Uraian", "Kategori", "Jumlah"]),
        "Laporan Perubahan Ekuitas": pd.DataFrame(columns=["Uraian", "Kategori", "Jumlah"]),
    }

# Form tambah data
with st.expander("➕ Tambah Data"):
    col1, col2, col3 = st.columns(3)
    with col1:
        uraian = st.text_input("Uraian", key=f"uraian_{menu}")
    with col2:
        kategori = st.text_input("Kategori", key=f"kategori_{menu}")
    with col3:
        jumlah = st.number_input("Jumlah", value=0.0, key=f"jumlah_{menu}")
    if st.button("Tambah", key=f"tambah_{menu}"):
        if uraian and kategori:
            st.session_state.data[menu] = pd.concat([
                st.session_state.data[menu],
                pd.DataFrame([{"Uraian": uraian, "Kategori": kategori, "Jumlah": jumlah}])
            ], ignore_index=True)
        else:
            st.warning("Mohon lengkapi uraian dan kategori.")

# Tampilkan tabel sesuai laporan yang dipilih
st.subheader(f"Tabel: {menu}")
st.dataframe(st.session_state.data[menu], use_container_width=True)

# Fungsi Export versi HTML
def export_pdf():
    df = st.session_state.data[menu]
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
            {''.join(f"<tr><td>{row['Uraian']}</td><td>{row['Kategori']}</td><td>{row['Jumlah']}</td></tr>" for i, row in df.iterrows())}
        </table>
    </body>
    </html>
    """
    b64 = base64.b64encode(html_out.encode()).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="laporan_{menu.replace(" ", "_")}.html">📥 Unduh versi HTML (bisa cetak ke PDF)</a>'
    st.markdown(href, unsafe_allow_html=True)

export_pdf()
