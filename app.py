import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Laporan Keuangan Lembaga Desa", layout="wide")

# === PILIHAN MULTI LEMBAGA DAN DESA ===
st.sidebar.title("🔰 Pilih Unit Lembaga")
lembaga = st.sidebar.selectbox("Lembaga", ["BUMDes", "TPK", "LPMD", "Karang Taruna", "Posyandu", "TSBD", "Pokmas"])
desa = st.sidebar.text_input("Nama Desa", "Keling")
nama_bumdes = st.sidebar.text_input("Nama Lembaga", "Buwana Raharja")
tahun = st.sidebar.number_input("Tahun Laporan", 2025, step=1)

# === PEJABAT UNTUK PENGESAHAN ===
st.sidebar.markdown("---")
st.sidebar.subheader("Pejabat Tanda Tangan")
bendahara = st.sidebar.text_input("Nama Bendahara", "Siti Aminah")
direktur = st.sidebar.text_input("Nama Ketua/Pimpinan", "Bambang Setiawan")
kepala_desa = st.sidebar.text_input("Nama Kepala Desa", "Sugeng Riyadi")
ketua_bpd = st.sidebar.text_input("Nama Ketua BPD", "Dwi Purnomo")

# === KOP LAPORAN ===
st.markdown(f"""
    <h3 style='text-align:center;'>Laporan Keuangan {lembaga} {nama_bumdes} Desa {desa}</h3>
    <h4 style='text-align:center;'>Alamat: Jl. Raya Keling, Bukaan, Keling, Kec. Kepung, Kabupaten Kediri, Jawa Timur 64293</h4>
    <hr>
""", unsafe_allow_html=True)

# === LOGO ===
col_logo1, col_logo2 = st.columns([1, 6])
with col_logo1:
    if os.path.exists("logo_pemdes.png"):
        st.image("logo_pemdes.png", width=80)
with col_logo2:
    if os.path.exists("logo_bumdes.png"):
        st.image("logo_bumdes.png", width=80)

st.title(f"📘 Buku Besar ({lembaga})")

# === AKUN ===
daftar_akun = pd.DataFrame({
    "Kode Akun": ["4.1.1", "4.1.2", "4.1.3", "5.1.1", "5.1.2", "6.1", "1.1.1", "2.1.1", "3.1.1"],
    "Nama Akun": ["Penjualan", "Pendapatan Jasa", "Pendapatan Lain", "Pembelian", "Beban Operasional", "Pendapatan Bunga", "Kas", "Utang Usaha", "Modal Desa"],
    "Posisi": ["Pendapatan", "Pendapatan", "Pendapatan", "HPP", "Beban Usaha", "Non-Usaha", "Aset Lancar", "Kewajiban Pendek", "Ekuitas"],
    "Tipe": ["Kredit", "Kredit", "Kredit", "Debit", "Debit", "Kredit", "Debit", "Kredit", "Kredit"]
})

# === SESSION STATE ===
key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Kode Akun", "Nama Akun", "Debit", "Kredit", "Keterangan"])

# === INPUT TRANSAKSI ===
st.subheader("📝 Input Transaksi Jurnal Harian")
with st.form("input_transaksi"):
    tanggal = st.date_input("Tanggal", value=datetime.today())
    akun_pilihan = st.selectbox("Pilih Nama Akun", daftar_akun["Nama Akun"])
    keterangan = st.text_input("Keterangan")
    jumlah = st.number_input("Jumlah Transaksi", min_value=0.0, step=1000.0)
    submit = st.form_submit_button("➕ Tambahkan Transaksi")

    if submit:
        akun_row = daftar_akun[daftar_akun["Nama Akun"] == akun_pilihan].iloc[0]
        kode_akun = akun_row["Kode Akun"]
        tipe = akun_row["Tipe"]
        debit = jumlah if tipe == "Debit" else 0.0
        kredit = jumlah if tipe == "Kredit" else 0.0
        st.session_state[key_gl] = pd.concat([
            st.session_state[key_gl],
            pd.DataFrame([{"Tanggal": tanggal, "Kode Akun": kode_akun, "Nama Akun": akun_pilihan, "Debit": debit, "Kredit": kredit, "Keterangan": keterangan}])
        ], ignore_index=True)
        st.success("✅ Transaksi berhasil ditambahkan.")

# === TAMPILKAN JURNAL HARIAN ===
st.subheader("📗 Jurnal Harian")
if not st.session_state[key_gl].empty:
    edited_df = st.session_state[key_gl].copy()
    for i in range(len(edited_df)):
        col1, col2 = st.columns([8, 1])
        with col1:
            st.write(edited_df.iloc[i])
        with col2:
            if st.button("🗑️ Hapus", key=f"hapus_{i}"):
                st.session_state[key_gl] = edited_df.drop(index=i).reset_index(drop=True)
                st.experimental_rerun()

# === HITUNG DAN TAMPILKAN LAPORAN OTOMATIS ===
df_gl = st.session_state[key_gl]

st.subheader("📊 Laporan Laba Rugi")
lr = df_gl.groupby("Nama Akun")[["Debit", "Kredit"]].sum().reset_index()
st.dataframe(lr, use_container_width=True)

st.subheader("📉 Neraca")
neraca = df_gl.groupby("Kode Akun")[["Debit", "Kredit"]].sum().reset_index()
st.dataframe(neraca, use_container_width=True)

st.subheader("💸 Arus Kas")
kas_masuk = df_gl["Debit"].sum()
kas_keluar = df_gl["Kredit"].sum()
kas_akhir = kas_masuk - kas_keluar
st.table(pd.DataFrame({"Uraian": ["Kas Masuk", "Kas Keluar", "Kas Akhir"], "Jumlah": [kas_masuk, kas_keluar, kas_akhir]}))

# === TAMPILKAN DAFTAR AKUN ===
with st.expander("📚 Daftar Akun Standar SISKEUDES"):
    st.dataframe(daftar_akun, use_container_width=True)

# === LEMBAR PENGESAHAN ===
st.markdown("""
    <br><br><br>
    <table width='100%' style='text-align:center;'>
        <tr><td><b>Disusun oleh</b></td><td><b>Disetujui oleh</b></td></tr>
        <tr><td><br><br><br></td><td><br><br><br></td></tr>
        <tr><td><u>{}</u><br>Bendahara</td><td><u>{}</u><br>Direktur/Pimpinan</td></tr>
        <tr><td colspan='2'><br><br></td></tr>
        <tr><td><b>Mengetahui</b></td><td><b>Mengetahui</b></td></tr>
        <tr><td><br><br><br></td><td><br><br><br></td></tr>
        <tr><td><u>{}</u><br>Kepala Desa</td><td><u>{}</u><br>Ketua BPD</td></tr>
    </table>
    <br><br>
""".format(bendahara, direktur, kepala_desa, ketua_bpd), unsafe_allow_html=True)
