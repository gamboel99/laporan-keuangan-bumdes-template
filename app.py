# === STREAMLIT LAPORAN KEUANGAN BUMDes Buwana Raharja Desa Keling ===

import streamlit as st
import pandas as pd
import base64
import os
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Laporan Keuangan BUMDes", layout="wide")

# === IDENTITAS ===
st.sidebar.title("🔰 Pilih Lembaga dan Desa")
desa = st.sidebar.text_input("Nama Desa", "Keling")
lembaga = st.sidebar.text_input("Nama Lembaga", "BUMDes Buwana Raharja")
tahun = st.sidebar.number_input("Tahun Laporan", 2025, step=1)

# === HEADER KOP ===
st.markdown("""
    <div style='text-align: center;'>
        <h2>LAPORAN KEUANGAN {}</h2>
        <h3>{}</h3>
        <p>Alamat: Jl. Raya Keling, Bukaan, Keling, Kec. Kepung,<br> Kabupaten Kediri, Jawa Timur 64293</p>
    </div><hr>
""".format(lembaga.upper(), f"DESA {desa.upper()}"), unsafe_allow_html=True)

# === INISIALISASI SESSION ===
key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Akun", "Debit", "Kredit", "Keterangan"])

df_gl = st.session_state[key_gl]

# === FORM INPUT TRANSAKSI ===
st.subheader("📘 General Ledger (Buku Besar)")
with st.expander("➕ Tambah Transaksi"):
    col1, col2, col3 = st.columns(3)
    with col1:
        tanggal = st.date_input("Tanggal", datetime.today())
    with col2:
        akun = st.text_input("Akun")
    with col3:
        keterangan = st.text_input("Keterangan")

    col4, col5 = st.columns(2)
    with col4:
        debit = st.number_input("Debit", min_value=0.0, format="%.2f")
    with col5:
        kredit = st.number_input("Kredit", min_value=0.0, format="%.2f")

    if st.button("💾 Simpan Transaksi"):
        if akun and (debit > 0 or kredit > 0):
            new_row = pd.DataFrame.from_dict([{
                "Tanggal": tanggal.strftime("%Y-%m-%d"),
                "Akun": akun,
                "Debit": debit,
                "Kredit": kredit,
                "Keterangan": keterangan
            }])
            st.session_state[key_gl] = pd.concat([st.session_state[key_gl], new_row], ignore_index=True)
            st.success("✅ Transaksi berhasil ditambahkan")
        else:
            st.warning("⚠️ Masukkan akun dan salah satu nilai debit/kredit")

# === TABEL TRANSAKSI ===
st.dataframe(df_gl, use_container_width=True)

# === EKSPORT GL ===
def download_excel(df, filename):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    output.seek(0)
    b64 = base64.b64encode(output.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">📥 Download Excel</a>'
    return href

st.markdown(download_excel(df_gl, f"General_Ledger_{lembaga}_{desa}_{tahun}.xlsx"), unsafe_allow_html=True)

# === RUMUS TOTAL AKUN ===
def total_akun(df, keyword):
    sub = df[df['Akun'].str.contains(keyword, case=False, na=False)]
    return sub['Debit'].sum() - sub['Kredit'].sum()

# === LAPORAN LAIN (BERDASARKAN GL) ===
pendapatan_usaha = total_akun(df_gl, "Pendapatan Usaha")
pendapatan_lain = total_akun(df_gl, "Pendapatan Lain")
beban_operasional = total_akun(df_gl, "Beban Operasional")
beban_non_operasional = total_akun(df_gl, "Beban Non")
laba_bersih = pendapatan_usaha + pendapatan_lain - beban_operasional - beban_non_operasional

kas_operasi = total_akun(df_gl, "Kas Operasi")
kas_investasi = total_akun(df_gl, "Kas Investasi")
kas_pendanaan = total_akun(df_gl, "Kas Pendanaan")
kas_akhir = kas_operasi + kas_investasi + kas_pendanaan

aset_lancar = total_akun(df_gl, "Kas|Bank|Piutang")
aset_tetap = total_akun(df_gl, "Peralatan|Gedung")
kewajiban = total_akun(df_gl, "Utang")
ekuitas_awal = total_akun(df_gl, "Modal")
prive = total_akun(df_gl, "Prive")
ekuitas_akhir = ekuitas_awal + laba_bersih - prive

# === TAMPILKAN LAPORAN ===
st.subheader("📄 Laporan Laba Rugi")
with st.expander("Detail Laba Rugi"):
    st.write(f"Pendapatan Usaha: Rp {pendapatan_usaha:,.2f}")
    st.write(f"Pendapatan Lain-lain: Rp {pendapatan_lain:,.2f}")
    st.write(f"Beban Operasional: Rp {beban_operasional:,.2f}")
    st.write(f"Beban Non-Operasional: Rp {beban_non_operasional:,.2f}")
    st.write(f"**Laba Bersih: Rp {laba_bersih:,.2f}**")
    df_lr = pd.DataFrame({
        "Uraian": ["Pendapatan Usaha", "Pendapatan Lain", "Beban Operasional", "Beban Non-Operasional", "Laba Bersih"],
        "Jumlah": [pendapatan_usaha, pendapatan_lain, -beban_operasional, -beban_non_operasional, laba_bersih]
    })
    st.markdown(download_excel(df_lr, f"Laba_Rugi_{lembaga}_{desa}_{tahun}.xlsx"), unsafe_allow_html=True)

st.subheader("💰 Arus Kas")
with st.expander("Detail Arus Kas"):
    st.write(f"Kas dari Kegiatan Operasi: Rp {kas_operasi:,.2f}")
    st.write(f"Kas dari Investasi: Rp {kas_investasi:,.2f}")
    st.write(f"Kas dari Pendanaan: Rp {kas_pendanaan:,.2f}")
    st.write(f"**Saldo Kas Akhir: Rp {kas_akhir:,.2f}**")
    df_kas = pd.DataFrame({
        "Kategori": ["Operasi", "Investasi", "Pendanaan", "Saldo Kas Akhir"],
        "Jumlah": [kas_operasi, kas_investasi, kas_pendanaan, kas_akhir]
    })
    st.markdown(download_excel(df_kas, f"Arus_Kas_{lembaga}_{desa}_{tahun}.xlsx"), unsafe_allow_html=True)

st.subheader("📊 Neraca")
with st.expander("Detail Neraca"):
    df_neraca = pd.DataFrame({
        "Posisi": ["Aset Lancar", "Aset Tetap", "Total Aset", "Kewajiban", "Ekuitas Akhir", "Total Kewajiban + Ekuitas"],
        "Jumlah": [aset_lancar, aset_tetap, aset_lancar+aset_tetap, kewajiban, ekuitas_akhir, kewajiban+ekuitas_akhir]
    })
    st.dataframe(df_neraca, use_container_width=True)
    st.markdown(download_excel(df_neraca, f"Neraca_{lembaga}_{desa}_{tahun}.xlsx"), unsafe_allow_html=True)

st.subheader("🧾 Perubahan Ekuitas")
with st.expander("Detail Ekuitas"):
    df_eq = pd.DataFrame({
        "Keterangan": ["Modal Awal", "Laba Bersih", "Prive", "Modal Akhir"],
        "Jumlah": [ekuitas_awal, laba_bersih, -prive, ekuitas_akhir]
    })
    st.dataframe(df_eq, use_container_width=True)
    st.markdown(download_excel(df_eq, f"Perubahan_Ekuitas_{lembaga}_{desa}_{tahun}.xlsx"), unsafe_allow_html=True)
