# ================================================
#  APLIKASI ACCOUNTING: LAPORAN KEUANGAN BUMDes BUWANA RAHARJA
# ================================================

import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Laporan Keuangan BUMDes", layout="wide")

# ======== SIDEBAR IDENTITAS DESA/LEMBAGA ========
st.sidebar.title("🧾 Identitas Lembaga")
desa = st.sidebar.text_input("Nama Desa", "Keling")
lembaga = st.sidebar.selectbox("Nama Lembaga", ["BUMDes", "TPK", "LPMD", "Karang Taruna", "Posyandu", "TSBD", "Pokmas"])
nama_bumdes = st.sidebar.text_input("Nama Unit", "Buwana Raharja")
tahun = st.sidebar.number_input("Tahun Laporan", 2025, step=1)
bulan_filter = st.sidebar.selectbox("Filter Bulan", ["Semua", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"])

# === PEJABAT UNTUK PENGESAHAN ===
st.sidebar.markdown("---")
st.sidebar.subheader("Pejabat Tanda Tangan")
bendahara = st.sidebar.text_input("Bendahara", "Siti Aminah")
direktur = st.sidebar.text_input("Pimpinan", "Bambang Setiawan")
kepala_desa = st.sidebar.text_input("Kepala Desa", "Sugeng Riyadi")
ketua_bpd = st.sidebar.text_input("Ketua BPD", "Dwi Purnomo")

# ========= HEADER & LOGO =========
col1, col2, col3 = st.columns([1, 5, 1])
with col1:
    if os.path.exists("logo_pemdes.png"):
        st.image("logo_pemdes.png", width=80)
with col2:
    st.markdown(f"""
        <h3 style='text-align:center;'>Laporan Keuangan {lembaga} {nama_bumdes} Desa {desa}</h3>
        <h5 style='text-align:center;'>Alamat: Jl. Raya Keling, Bukaan, Keling, Kec. Kepung, Kabupaten Kediri, Jawa Timur 64293</h5>
        <hr>
    """, unsafe_allow_html=True)
with col3:
    if os.path.exists("logo_bumdes.png"):
        st.image("logo_bumdes.png", width=80)

# ========= PEDOMAN AKUN =========
pedoman_data = {
    "Nama Akun": [
        "Pendapatan Usaha", "Pendapatan Lainnya",
        "Beban Operasional", "Beban Administrasi",
        "Modal Awal", "Prive", "Penambahan Modal", "Laba Ditahan", "Laba Tahun Berjalan",
        "Kas", "Bank", "Piutang", "Persediaan", "Aset Tetap",
        "Utang Usaha", "Utang Jangka Panjang"
    ],
    "Posisi": [
        "Pendapatan", "Pendapatan",
        "Beban", "Beban",
        "Ekuitas", "Ekuitas", "Ekuitas", "Ekuitas", "Ekuitas",
        "Aset", "Aset", "Aset", "Aset", "Aset",
        "Kewajiban", "Kewajiban"
    ],
    "Tipe": [
        "Kredit", "Kredit",
        "Debit", "Debit",
        "Kredit", "Debit", "Kredit", "Kredit", "Kredit",
        "Debit", "Debit", "Debit", "Debit", "Debit",
        "Kredit", "Kredit"
    ]
}
pedoman_akun = pd.DataFrame(pedoman_data)

with st.expander("📚 Pedoman Akun (Panduan Posisi Debit/Kredit)"):
    st.dataframe(pedoman_akun, use_container_width=True)

# ========= JURNAL TRANSAKSI =========
st.markdown("## 📒 Jurnal Harian / Buku Besar")
key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Nama Akun", "Debit", "Kredit", "Keterangan", "Bukti"])

df_gl = st.session_state[key_gl]

with st.form("form_input"):
    tanggal = st.date_input("Tanggal", value=datetime.now())
    akun_nama = st.selectbox("Pilih Nama Akun", pedoman_akun["Nama Akun"])
    tipe = pedoman_akun[pedoman_akun["Nama Akun"] == akun_nama]["Tipe"].values[0]

    debit, kredit = 0.0, 0.0
    if tipe == "Debit":
        debit = st.number_input("Jumlah (Debit)", min_value=0.0, format="%.2f")
    else:
        kredit = st.number_input("Jumlah (Kredit)", min_value=0.0, format="%.2f")

    keterangan = st.text_input("Keterangan")
    bukti = st.file_uploader("Upload Bukti Transaksi", type=["jpg", "jpeg", "png", "pdf"])
    submitted = st.form_submit_button("✅ Tambah Transaksi")

    if submitted:
        new_row = {
            "Tanggal": tanggal.strftime("%Y-%m-%d"),
            "Nama Akun": akun_nama,
            "Debit": debit,
            "Kredit": kredit,
            "Keterangan": keterangan,
            "Bukti": bukti.name if bukti else "-"
        }
        st.session_state[key_gl] = pd.concat([df_gl, pd.DataFrame([new_row])], ignore_index=True)
        st.success("✅ Transaksi berhasil ditambahkan.")

# === TABEL JURNAL & FITUR HAPUS ===
st.markdown("### 📋 Tabel Jurnal Transaksi")
df_gl = st.session_state[key_gl]
if not df_gl.empty:
    if bulan_filter != "Semua":
        df_gl = df_gl[df_gl["Tanggal"].str[5:7] == bulan_filter]
    st.dataframe(df_gl, use_container_width=True)
    hapus = st.number_input("Hapus transaksi ke (baris)", min_value=1, max_value=len(df_gl), step=1)
    if st.button("🗑️ Hapus Baris"):
        st.session_state[key_gl] = df_gl.drop(df_gl.index[hapus - 1]).reset_index(drop=True)
        st.success("Baris berhasil dihapus.")
else:
    st.info("Belum ada transaksi yang dicatat.")

# === NAVIGASI LAPORAN ===
tabs = st.tabs(["📊 Laba Rugi", "📑 Neraca", "🔁 Perubahan Ekuitas", "💸 Arus Kas", "📦 Unduh Semua"])

# === PERHITUNGAN OTOMATIS ===
df = st.session_state[key_gl]
if not df.empty:
    df = df if bulan_filter == "Semua" else df[df["Tanggal"].str[5:7] == bulan_filter]
    def jumlah(akun_list, kolom):
        return df[df["Nama Akun"].isin(akun_list)][kolom].sum()

    pendapatan = jumlah(["Pendapatan Usaha", "Pendapatan Lainnya"], "Kredit")
    beban_operasional = jumlah(["Beban Operasional"], "Debit")
    beban_administrasi = jumlah(["Beban Administrasi"], "Debit")
    laba_bersih = pendapatan - (beban_operasional + beban_administrasi)

    kas = jumlah(["Kas"], "Debit") - jumlah(["Kas"], "Kredit")
    aset = jumlah(["Kas", "Bank", "Piutang", "Persediaan", "Aset Tetap"], "Debit")
    kewajiban = jumlah(["Utang Usaha", "Utang Jangka Panjang"], "Kredit")
    ekuitas = jumlah(["Modal Awal", "Penambahan Modal", "Laba Ditahan", "Laba Tahun Berjalan"], "Kredit") - jumlah(["Prive"], "Debit")

    with tabs[0]:
        st.subheader("📊 Laporan Laba Rugi")
        st.table({
            "Pendapatan Usaha": [pendapatan],
            "Beban Operasional": [beban_operasional],
            "Beban Administrasi": [beban_administrasi],
            "Laba/Rugi Bersih": [laba_bersih]
        })

    with tabs[1]:
        st.subheader("📑 Neraca")
        st.table({
            "Total Aset": [aset],
            "Total Kewajiban": [kewajiban],
            "Total Ekuitas": [ekuitas],
            "Total Kewajiban + Ekuitas": [kewajiban + ekuitas]
        })

    with tabs[2]:
        st.subheader("🔁 Laporan Perubahan Ekuitas")
        st.table({
            "Modal Awal": [jumlah(["Modal Awal"], "Kredit")],
            "Laba Tahun Berjalan": [laba_bersih],
            "Prive": [jumlah(["Prive"], "Debit")],
            "Modal Akhir": [ekuitas]
        })

    with tabs[3]:
        st.subheader("💸 Arus Kas")
        st.table({
            "Kas Masuk": [df["Debit"].sum()],
            "Kas Keluar": [df["Kredit"].sum()],
            "Saldo Kas": [kas]
        })

    with tabs[4]:
        st.download_button("📥 Unduh Jurnal Excel", data=df.to_csv(index=False).encode(), file_name="jurnal.csv")
else:
    st.warning("📭 Belum ada transaksi, laporan belum tersedia.")

# === LEMBAR PENGESAHAN ===
st.markdown("""
    <br><br><br><hr>
    <h5 style='text-align:center;'>LEMBAR PENGESAHAN</h5>
    <table width='100%' style='text-align:center;'>
        <tr><td><b>Disusun oleh</b></td><td><b>Disetujui oleh</b></td></tr>
        <tr><td><br><br><br></td><td><br><br><br></td></tr>
        <tr><td><u>{}</u><br>Bendahara</td><td><u>{}</u><br>Pimpinan Lembaga</td></tr>
        <tr><td colspan='2'><br><br></td></tr>
        <tr><td><b>Mengetahui</b></td><td><b>Mengetahui</b></td></tr>
        <tr><td><br><br><br></td><td><br><br><br></td></tr>
        <tr><td><u>{}</u><br>Kepala Desa</td><td><u>{}</u><br>Ketua BPD</td></tr>
    </table>
""".format(bendahara, direktur, kepala_desa, ketua_bpd), unsafe_allow_html=True)
