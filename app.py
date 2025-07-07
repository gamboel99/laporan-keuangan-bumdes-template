import streamlit as st
import pandas as pd
import base64

st.set_page_config(page_title="Laporan Keuangan BUMDes", layout="wide")

# Identitas
st.sidebar.title("Identitas BUMDes")
nama_bumdes = st.sidebar.text_input("Nama BUMDes", "Buwana Raharja")
desa = st.sidebar.text_input("Desa", "Keling")
tahun = st.sidebar.number_input("Tahun", 2025, step=1)

st.title("📊 Laporan Keuangan BUMDes (Terintegrasi)")

# Akun default
akun_default = {
    "Laporan Laba Rugi": [
        ("Pendapatan Usaha", "Pendapatan"),
        ("Beban Operasional", "Beban"),
        ("Beban Administrasi", "Beban")
    ],
    "Laporan Perubahan Ekuitas": [
        ("Modal Awal", "Ekuitas"),
        ("Laba Tahun Berjalan", "Ekuitas"),
        ("Penambahan Modal", "Ekuitas"),
        ("Pengambilan Prive", "Ekuitas"),
        ("Modal Akhir", "Ekuitas (Hitung Otomatis)")
    ],
    "Laporan Arus Kas": [
        ("Kas dari Aktivitas Operasi", "Operasi"),
        ("Kas dari Aktivitas Investasi", "Investasi"),
        ("Kas dari Aktivitas Pendanaan", "Pendanaan"),
        ("Kenaikan/Penurunan Kas", "Total (Otomatis)"),
        ("Kas Akhir", "Total (Otomatis)")
    ],
    "Laporan Posisi Keuangan": [
        ("Kas", "Aset"),
        ("Piutang", "Aset"),
        ("Peralatan", "Aset"),
        ("Utang Usaha", "Kewajiban"),
        ("Modal Akhir", "Ekuitas (Otomatis)")
    ]
}

# Inisialisasi data
if "data" not in st.session_state:
    st.session_state.data = {}
    for laporan, akun_list in akun_default.items():
        df = pd.DataFrame(akun_list, columns=["Uraian", "Kategori"])
        df["Jumlah"] = 0.0
        st.session_state.data[laporan] = df

# Fungsi perhitungan otomatis
def hitung_otomatis():
    # Laba Bersih
    df_lr = st.session_state.data["Laporan Laba Rugi"]
    pendapatan = df_lr[df_lr["Kategori"] == "Pendapatan"]["Jumlah"].sum()
    beban = df_lr[df_lr["Kategori"] == "Beban"]["Jumlah"].sum()
    laba_bersih = pendapatan - beban

    # Update ke Perubahan Ekuitas
    df_pe = st.session_state.data["Laporan Perubahan Ekuitas"]
    df_pe.loc[df_pe["Uraian"] == "Laba Tahun Berjalan", "Jumlah"] = laba_bersih

    # Hitung Modal Akhir
    modal_awal = df_pe.loc[df_pe["Uraian"] == "Modal Awal", "Jumlah"].sum()
    penambahan = df_pe.loc[df_pe["Uraian"] == "Penambahan Modal", "Jumlah"].sum()
    prive = df_pe.loc[df_pe["Uraian"] == "Pengambilan Prive", "Jumlah"].sum()
    modal_akhir = modal_awal + laba_bersih + penambahan - prive
    df_pe.loc[df_pe["Uraian"] == "Modal Akhir", "Jumlah"] = modal_akhir

    # Update Arus Kas
    df_kas = st.session_state.data["Laporan Arus Kas"]
    kas_operasi = df_kas.loc[df_kas["Uraian"] == "Kas dari Aktivitas Operasi", "Jumlah"].sum()
    kas_investasi = df_kas.loc[df_kas["Uraian"] == "Kas dari Aktivitas Investasi", "Jumlah"].sum()
    kas_pendanaan = df_kas.loc[df_kas["Uraian"] == "Kas dari Aktivitas Pendanaan", "Jumlah"].sum()
    kenaikan_kas = kas_operasi + kas_investasi + kas_pendanaan
    df_kas.loc[df_kas["Uraian"] == "Kenaikan/Penurunan Kas", "Jumlah"] = kenaikan_kas
    df_kas.loc[df_kas["Uraian"] == "Kas Akhir", "Jumlah"] = kenaikan_kas  # Sederhana: diasumsikan kas awal 0

    # Update ke Neraca
    df_nr = st.session_state.data["Laporan Posisi Keuangan"]
    df_nr.loc[df_nr["Uraian"] == "Kas", "Jumlah"] = kenaikan_kas
    df_nr.loc[df_nr["Uraian"] == "Modal Akhir", "Jumlah"] = modal_akhir

# Fungsi export HTML
def export_html(nama_laporan, df):
    html = f"""
    <h3>{nama_laporan}</h3>
    <table border="1" cellspacing="0" cellpadding="5">
    <tr><th>Uraian</th><th>Kategori</th><th>Jumlah</th></tr>
    {''.join(f"<tr><td>{row['Uraian']}</td><td>{row['Kategori']}</td><td>{row['Jumlah']}</td></tr>" for _, row in df.iterrows())}
    </table><br>
    """
    return html

# Jalankan perhitungan otomatis
hitung_otomatis()

# Tampilkan semua laporan
laporan_order = [
    "Laporan Laba Rugi",
    "Laporan Perubahan Ekuitas",
    "Laporan Arus Kas",
    "Laporan Posisi Keuangan"
]

html_full = ""

for nama in laporan_order:
    st.subheader(nama)

    # Edit data
    df = st.session_state.data[nama]
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic", key=f"edit_{nama}")
    st.session_state.data[nama] = edited_df

    # Tambah akun
    with st.expander(f"➕ Tambah Akun ke {nama}"):
        col1, col2, col3 = st.columns(3)
        with col1:
            uraian = st.text_input("Uraian", key=f"uraian_{nama}")
        with col2:
            kategori = st.text_input("Kategori", key=f"kategori_{nama}")
        with col3:
            jumlah = st.number_input("Jumlah", key=f"jumlah_{nama}", value=0.0)
        if st.button("Tambah", key=f"tambah_{nama}"):
            if uraian and kategori:
                st.session_state.data[nama] = pd.concat([
                    st.session_state.data[nama],
                    pd.DataFrame([{"Uraian": uraian, "Kategori": kategori, "Jumlah": jumlah}])
                ], ignore_index=True)
            else:
                st.warning("Lengkapi uraian dan kategori.")

    html_full += export_html(nama, st.session_state.data[nama])

# Tombol unduh
html_final = f"""
<html><body>
<h2>Laporan Keuangan BUMDes</h2>
<p><strong>{nama_bumdes} - Desa {desa} - Tahun {tahun}</strong></p>
{html_full}
</body></html>
"""

b64 = base64.b64encode(html_final.encode()).decode()
href = f'<a href="data:text/html;base64,{b64}" download="laporan_keuangan.html">📥 Unduh Semua Laporan (HTML)</a>'
st.markdown(href, unsafe_allow_html=True)
