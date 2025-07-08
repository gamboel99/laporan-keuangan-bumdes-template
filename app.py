import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import base64
import os

st.set_page_config(page_title="Laporan Keuangan Lembaga Desa", layout="wide")

# Sidebar Identitas
st.sidebar.title("🔰 Pilih Unit Lembaga")
lembaga = st.sidebar.selectbox("Lembaga", ["BUMDes", "TPK", "LPMD", "Karang Taruna", "Posyandu", "TSBD", "Pokmas"])
desa = st.sidebar.text_input("Nama Desa", "Keling")
nama_bumdes = st.sidebar.text_input("Nama Lembaga", "Buwana Raharja")
tahun = st.sidebar.number_input("Tahun Laporan", 2025, step=1)

st.sidebar.markdown("---")
st.sidebar.subheader("Pejabat Tanda Tangan")
bendahara = st.sidebar.text_input("Nama Bendahara", "Siti Aminah")
direktur = st.sidebar.text_input("Nama Ketua/Pimpinan", "Bambang Setiawan")
kepala_desa = st.sidebar.text_input("Nama Kepala Desa", "Sugeng Riyadi")
ketua_bpd = st.sidebar.text_input("Nama Ketua BPD", "Dwi Purnomo")

# Header Laporan
st.markdown(f"""
    <h3 style='text-align:center;'>Laporan Keuangan {lembaga} {nama_bumdes} Desa {desa}</h3>
    <h4 style='text-align:center;'>Alamat: Jl. Raya Keling, Bukaan, Keling, Kec. Kepung, Kabupaten Kediri, Jawa Timur 64293</h4>
    <hr>
""", unsafe_allow_html=True)

# === PEDOMAN AKUN ===
pedoman_akun = pd.DataFrame({
    "Kode Akun": ["4.1.1", "5.2.1", "1.1.1", "2.1.1", "3.1.4"],
    "Nama Akun": ["Pendapatan Usaha", "Gaji dan Tunjangan", "Kas", "Utang Usaha", "Laba Tahun Berjalan"],
    "Posisi": ["Pendapatan", "Beban Usaha", "Aset Lancar", "Kewajiban Pendek", "Ekuitas"],
    "Tipe": ["Kredit", "Debit", "Debit", "Kredit", "Kredit"]
})

st.subheader("📌 Pedoman Kode Akun")
st.dataframe(pedoman_akun, use_container_width=True)

# === INISIALISASI SESSION_STATE ===
key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Kode Akun", "Nama Akun", "Posisi", "Debit", "Kredit", "Keterangan", "Bukti"])

# === FORM INPUT JURNAL HARIAN ===
st.subheader("📝 Input Jurnal Harian")
with st.form("form_input"):
    tgl = st.date_input("Tanggal")
    akun_nama = st.selectbox("Pilih Nama Akun", pedoman_akun["Nama Akun"])
    akun_row = pedoman_akun[pedoman_akun["Nama Akun"] == akun_nama].iloc[0]
    akun_kode = akun_row["Kode Akun"]
    akun_posisi = akun_row["Posisi"]
    akun_tipe = akun_row["Tipe"]
    nominal = st.number_input("Jumlah", min_value=0.0, step=1000.0, format="%f")
    ket = st.text_input("Keterangan")
    bukti = st.file_uploader("Upload Bukti Transaksi (Opsional)", type=["jpg", "png", "pdf"])
    submitted = st.form_submit_button("Simpan")

if submitted:
    debit = nominal if akun_tipe == "Debit" else 0.0
    kredit = nominal if akun_tipe == "Kredit" else 0.0
    st.session_state[key_gl] = pd.concat([st.session_state[key_gl], pd.DataFrame.from_records([{
        "Tanggal": tgl, "Kode Akun": akun_kode, "Nama Akun": akun_nama, "Posisi": akun_posisi,
        "Debit": debit, "Kredit": kredit, "Keterangan": ket, "Bukti": bukti.name if bukti else ""
    }])], ignore_index=True)
    st.success("✅ Transaksi berhasil ditambahkan.")

# === TAMPILKAN JURNAL HARIAN ===
st.subheader("📘 Buku Besar / General Ledger")
df_gl = st.session_state[key_gl]
if not df_gl.empty:
    for i in df_gl.index:
        col1, col2 = st.columns([10, 1])
        with col1:
            st.write(df_gl.loc[i].to_dict())
        with col2:
            if st.button("❌", key=f"hapus_{i}"):
                st.session_state[key_gl] = df_gl.drop(i).reset_index(drop=True)
                st.experimental_rerun()

    st.download_button("⬇️ Download Buku Besar (Excel)", data=df_gl.to_csv(index=False).encode(), file_name=f"BukuBesar_{lembaga}_{desa}_{tahun}.csv")
else:
    st.info("Belum ada transaksi dimasukkan.")

# === LAPORAN OTOMATIS ===
st.subheader("📊 Laporan Laba Rugi")
pd_pendapatan = df_gl[df_gl["Posisi"] == "Pendapatan"]["Kredit"].sum()
pd_beban = df_gl[df_gl["Posisi"].isin(["Beban Usaha", "HPP", "Non-Usaha"])]["Debit"].sum()
labarugi = pd.DataFrame({
    "Pos": ["Total Pendapatan", "Total Beban", "Laba Bersih"],
    "Jumlah": [pd_pendapatan, pd_beban, pd_pendapatan - pd_beban]
})
st.table(labarugi)
st.download_button("⬇️ Download Laba Rugi (Excel)", data=labarugi.to_csv(index=False).encode(), file_name=f"LabaRugi_{lembaga}_{desa}_{tahun}.csv")

# === NERACA ===
st.subheader("📊 Neraca")
aset = df_gl[df_gl["Posisi"].str.contains("Aset")]["Debit"].sum()
kewajiban = df_gl[df_gl["Posisi"].str.contains("Kewajiban")]["Kredit"].sum()
ekuitas = df_gl[df_gl["Posisi"] == "Ekuitas"]["Kredit"].sum()
neraca = pd.DataFrame({
    "Pos": ["Aset", "Kewajiban", "Ekuitas"],
    "Jumlah": [aset, kewajiban, ekuitas]
})
st.table(neraca)
st.download_button("⬇️ Download Neraca (Excel)", data=neraca.to_csv(index=False).encode(), file_name=f"Neraca_{lembaga}_{desa}_{tahun}.csv")

# === ARUS KAS ===
st.subheader("📊 Arus Kas")
kasin = df_gl[df_gl["Nama Akun"] == "Kas"]["Debit"].sum()
kaskeluar = df_gl[df_gl["Nama Akun"] == "Kas"]["Kredit"].sum()
aruskas = pd.DataFrame({
    "Pos": ["Penerimaan Kas", "Pengeluaran Kas", "Saldo Kas Akhir"],
    "Jumlah": [kasin, kaskeluar, kasin - kaskeluar]
})
st.table(aruskas)
st.download_button("⬇️ Download Arus Kas (Excel)", data=aruskas.to_csv(index=False).encode(), file_name=f"ArusKas_{lembaga}_{desa}_{tahun}.csv")
