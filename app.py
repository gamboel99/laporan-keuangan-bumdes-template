import os
import base64
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Laporan Keuangan BUMDes", layout="wide")

# ===== Sidebar Identitas BUMDes =====
st.sidebar.title("Identitas BUMDes")
nama_bumdes = st.sidebar.text_input("Nama BUMDes", "Buwana Raharja")
desa = st.sidebar.text_input("Desa", "Keling")
tahun = st.sidebar.number_input("Tahun Laporan", 2025, step=1)

st.title("📊 Laporan Keuangan BUMDes")

# ===== Jenis Laporan =====
laporan_list = [
    "Laporan Posisi Keuangan",
    "Laporan Laba Rugi",
    "Laporan Arus Kas",
    "Laporan Perubahan Ekuitas"
]

# ===== Akun Default per Laporan =====
akun_default = {
    "Laporan Posisi Keuangan": [
        ("Kas", "Aset"),
        ("Piutang", "Aset"),
        ("Persediaan", "Aset"),
        ("Peralatan", "Aset"),
        ("Utang Usaha", "Kewajiban"),
        ("Modal Awal", "Ekuitas")
    ],
    "Laporan Laba Rugi": [
        ("Pendapatan Usaha", "Pendapatan"),
        ("Pendapatan Lainnya", "Pendapatan"),
        ("Beban Operasional", "Beban"),
        ("Beban Administrasi", "Beban"),
        ("Beban Lainnya", "Beban")
    ],
    "Laporan Arus Kas": [
        ("Kas dari Aktivitas Operasi", "Operasi"),
        ("Kas dari Aktivitas Investasi", "Investasi"),
        ("Kas dari Aktivitas Pendanaan", "Pendanaan"),
        ("Kenaikan/Penurunan Kas", "Total")
    ],
    "Laporan Perubahan Ekuitas": [
        ("Modal Awal", "Ekuitas"),
        ("Laba Tahun Berjalan", "Laba Ditahan"),
        ("Penambahan Modal", "Ekuitas"),
        ("Pengambilan Prive", "Prive"),
        ("Modal Akhir", "Ekuitas")
    ]
}

# ===== Inisialisasi Session State =====
if "data" not in st.session_state:
    st.session_state.data = {}
    for laporan in laporan_list:
        df = pd.DataFrame(akun_default[laporan], columns=["Uraian", "Kategori"])
        df["Jumlah"] = 0
        st.session_state.data[laporan] = df

# ===== Fungsi Export ke HTML =====
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
    href = f'<a href="data:text/html;base64,{b64}" download="laporan_{nama_laporan.replace(" ", "_")}.html">📥 Unduh versi HTML (bisa cetak PDF)</a>'
    st.markdown(href, unsafe_allow_html=True)

# ===== Tampilan Laporan =====
for nama_laporan in laporan_list:
    st.header(nama_laporan)

    # Tampilkan tabel editable
    st.session_state.data[nama_laporan] = st.data_editor(
        st.session_state.data[nama_laporan],
        num_rows="dynamic",
        use_container_width=True,
        key=f"edit_{nama_laporan}"
    )

    # Tambah baris (akun) baru
    with st.expander(f"➕ Tambah Akun Baru: {nama_laporan}"):
        col1, col2, col3 = st.columns(3)
        with col1:
            uraian = st.text_input("Uraian", key=f"uraian_{nama_laporan}")
        with col2:
            kategori = st.text_input("Kategori", key=f"kategori_{nama_laporan}")
        with col3:
            jumlah = st.number_input("Jumlah", value=0.0, key=f"jumlah_{nama_laporan}")
        if st.button("Tambah", key=f"tambah_{nama_laporan}"):
            if uraian and kategori:
                new_row = pd.DataFrame([{"Uraian": uraian, "Kategori": kategori, "Jumlah": jumlah}])
                st.session_state.data[nama_laporan] = pd.concat([
                    st.session_state.data[nama_laporan],
                    new_row
                ], ignore_index=True)
            else:
                st.warning("Mohon lengkapi uraian dan kategori.")

    # Tombol Export HTML
    export_html(nama_laporan, st.session_state.data[nama_laporan])
    st.markdown("---")
