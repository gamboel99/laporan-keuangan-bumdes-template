import os
import base64
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Laporan Keuangan BUMDes", layout="wide")

# Identitas BUMDes
st.sidebar.title("Identitas BUMDes")
nama_bumdes = st.sidebar.text_input("Nama BUMDes", "Buwana Raharja")
desa = st.sidebar.text_input("Desa", "Keling")
tahun = st.sidebar.number_input("Tahun Laporan", 2025, step=1)

st.title("📊 Laporan Keuangan BUMDes")

# Daftar semua laporan
laporan_list = [
    "Laporan Posisi Keuangan",
    "Laporan Laba Rugi",
    "Laporan Arus Kas",
    "Laporan Perubahan Ekuitas"
]

# Daftar akun default untuk neraca
akun_default_neraca = [
    ("Kas", "Aset"),
    ("Piutang", "Aset"),
    ("Persediaan", "Aset"),
    ("Peralatan", "Aset"),
    ("Utang Usaha", "Kewajiban"),
    ("Modal Awal", "Ekuitas"),
]

# Inisialisasi semua laporan di session_state
if "data" not in st.session_state:
    st.session_state.data = {}
    for nama in laporan_list:
        st.session_state.data[nama] = pd.DataFrame(columns=["Uraian", "Kategori", "Jumlah"])
    # Tambahkan akun default untuk neraca
    for akun, kategori in akun_default_neraca:
        st.session_state.data["Laporan Posisi Keuangan"] = pd.concat([
            st.session_state.data["Laporan Posisi Keuangan"],
            pd.DataFrame([{"Uraian": akun, "Kategori": kategori, "Jumlah": 0}])
        ], ignore_index=True)

# Fungsi Export HTML per laporan
def export_html(nama_laporan, df):
    html_out = f"""
    <html>
    <head><meta charset="utf-8"></head>
    <body>
        <h2>{nama_laporan}</h2>
        <p><strong>BUMDes:</strong> {nama_bumdes}<br>
           <strong>Desa:</strong> {desa}<br>
           <strong>Tahun:</strong> {tahun}</p>
        <table border="1" cellpadding="4" cellspacing="0">
            <tr><th>Uraian</th><th>Kategori</th><th>Jumlah</th></tr>
            {''.join(f"<tr><td>{row['Uraian']}</td><td>{row['Kategori']}</td><td>{row['Jumlah']}</td></tr>" for _, row in df.iterrows())}
        </table>
    </body>
    </html>
    """
    b64 = base64.b64encode(html_out.encode()).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="laporan_{nama_laporan.replace(" ", "_")}.html">📥 Unduh versi HTML</a>'
    st.markdown(href, unsafe_allow_html=True)

# Loop setiap jenis laporan
for nama_laporan in laporan_list:
    st.header(nama_laporan)

    # Tampilkan tabel
    df = st.session_state.data[nama_laporan]
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key=f"edit_{nama_laporan}")
    st.session_state.data[nama_laporan] = edited_df

    # Form tambahan akun
    with st.expander(f"➕ Tambah Akun atau Baris Baru: {nama_laporan}"):
        col1, col2, col3 = st.columns(3)
        with col1:
            uraian = st.text_input("Uraian", key=f"uraian_{nama_laporan}")
        with col2:
            kategori = st.text_input("Kategori", key=f"kategori_{nama_laporan}")
        with col3:
            jumlah = st.number_input("Jumlah", value=0.0, key=f"jumlah_{nama_laporan}")
        if st.button("Tambah", key=f"tambah_{nama_laporan}"):
            if uraian and kategori:
                st.session_state.data[nama_laporan] = pd.concat([
                    st.session_state.data[nama_laporan],
                    pd.DataFrame([{"Uraian": uraian, "Kategori": kategori, "Jumlah": jumlah}])
                ], ignore_index=True)
            else:
                st.warning("Mohon lengkapi uraian dan kategori.")

    export_html(nama_laporan, st.session_state.data[nama_laporan])
    st.markdown("---")
