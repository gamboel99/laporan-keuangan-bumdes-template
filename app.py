import streamlit as st
import pandas as pd
import base64
from datetime import datetime

st.set_page_config(page_title="Laporan Keuangan BUMDes - Terintegrasi", layout="wide")

# Sidebar Identitas
st.sidebar.title("Identitas BUMDes")
nama_bumdes = st.sidebar.text_input("Nama BUMDes", "Buwana Raharja")
desa = st.sidebar.text_input("Desa", "Keling")
tahun = st.sidebar.number_input("Tahun Laporan", 2025, step=1)

st.title("📚 General Ledger (Buku Besar) BUMDes")

# Inisialisasi Data GL
if "gl" not in st.session_state:
    st.session_state.gl = pd.DataFrame(columns=["Tanggal", "Akun", "Debit", "Kredit", "Keterangan"])

# Form Input Transaksi
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

    if st.button("Simpan Transaksi"):
        if akun and (debit > 0 or kredit > 0):
            new = pd.DataFrame([{
                "Tanggal": tanggal.strftime("%Y-%m-%d"),
                "Akun": akun,
                "Debit": debit,
                "Kredit": kredit,
                "Keterangan": keterangan
            }])
            st.session_state.gl = pd.concat([st.session_state.gl, new], ignore_index=True)
        else:
            st.warning("Akun dan nominal debit/kredit harus diisi.")

# Tampilkan GL
st.dataframe(st.session_state.gl, use_container_width=True)

# ===== Fungsi Pembantu =====
def filter_akun(df, nama):
    return df[df["Akun"].str.contains(nama, case=False, na=False)]

def total_akun(df, nama):
    filtered = filter_akun(df, nama)
    return filtered["Debit"].sum() - filtered["Kredit"].sum()

# ===== Buat Laporan Otomatis =====
def buat_laporan():
    df = st.session_state.gl

    # --- Laba Rugi
    pendapatan = total_akun(df, "Pendapatan")
    beban = total_akun(df, "Beban")
    laba_bersih = pendapatan - beban

    # --- Perubahan Ekuitas
    modal_awal = total_akun(df, "Modal")
    prive = total_akun(df, "Prive")
    penambahan = total_akun(df, "Penambahan Modal")
    modal_akhir = modal_awal + laba_bersih + penambahan - prive

    # --- Arus Kas (sederhana)
    kas_masuk = df[df["Akun"].str.contains("Kas", case=False)]["Debit"].sum()
    kas_keluar = df[df["Akun"].str.contains("Kas", case=False)]["Kredit"].sum()
    kas_akhir = kas_masuk - kas_keluar

    # --- Neraca
    aset = kas_akhir + total_akun(df, "Piutang") + total_akun(df, "Peralatan")
    kewajiban = total_akun(df, "Utang")
    ekuitas = modal_akhir
    total_kewajiban_ekuitas = kewajiban + ekuitas

    return {
        "laba_bersih": laba_bersih,
        "modal_akhir": modal_akhir,
        "kas_akhir": kas_akhir,
        "aset": aset,
        "kewajiban": kewajiban,
        "ekuitas": ekuitas,
        "total_ke": total_kewajiban_ekuitas,
        "pendapatan": pendapatan,
        "beban": beban
    }

laporan = buat_laporan()

# ===== Tampilan Laporan =====
st.header("📄 Laporan Keuangan Otomatis")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Laba Rugi")
    st.markdown(f"- **Pendapatan:** Rp {laporan['pendapatan']:,.2f}")
    st.markdown(f"- **Beban:** Rp {laporan['beban']:,.2f}")
    st.markdown(f"- **Laba Bersih:** Rp {laporan['laba_bersih']:,.2f}")

    st.subheader("Perubahan Ekuitas")
    st.markdown(f"- **Modal Awal:** Rp {total_akun(st.session_state.gl, 'Modal'):,.2f}")
    st.markdown(f"- **Penambahan Modal:** Rp {total_akun(st.session_state.gl, 'Penambahan Modal'):,.2f}")
    st.markdown(f"- **Prive:** Rp {total_akun(st.session_state.gl, 'Prive'):,.2f}")
    st.markdown(f"- **Laba Tahun Berjalan:** Rp {laporan['laba_bersih']:,.2f}")
    st.markdown(f"- **Modal Akhir:** Rp {laporan['modal_akhir']:,.2f}")

with col2:
    st.subheader("Arus Kas")
    st.markdown(f"- **Kas Masuk:** Rp {st.session_state.gl[st.session_state.gl['Akun'].str.contains('Kas', case=False)]['Debit'].sum():,.2f}")
    st.markdown(f"- **Kas Keluar:** Rp {st.session_state.gl[st.session_state.gl['Akun'].str.contains('Kas', case=False)]['Kredit'].sum():,.2f}")
    st.markdown(f"- **Saldo Kas Akhir:** Rp {laporan['kas_akhir']:,.2f}")

    st.subheader("Neraca")
    st.markdown(f"- **Total Aset:** Rp {laporan['aset']:,.2f}")
    st.markdown(f"- **Total Kewajiban:** Rp {laporan['kewajiban']:,.2f}")
    st.markdown(f"- **Total Ekuitas:** Rp {laporan['ekuitas']:,.2f}")
    st.markdown(f"- **Total Kewajiban + Ekuitas:** Rp {laporan['total_ke']:,.2f}")

# ===== Export HTML (Ikhtisar) =====
def export_ikhtisar():
    html = f"""
    <h2>Ikhtisar Laporan Keuangan BUMDes</h2>
    <p><strong>{nama_bumdes} - Desa {desa} - Tahun {tahun}</strong></p>
    <h3>Laba Rugi</h3>
    <ul>
        <li>Pendapatan: Rp {laporan['pendapatan']:,.2f}</li>
        <li>Beban: Rp {laporan['beban']:,.2f}</li>
        <li>Laba Bersih: Rp {laporan['laba_bersih']:,.2f}</li>
    </ul>
    <h3>Perubahan Ekuitas</h3>
    <ul>
        <li>Modal Awal: Rp {total_akun(st.session_state.gl, 'Modal'):,.2f}</li>
        <li>Penambahan Modal: Rp {total_akun(st.session_state.gl, 'Penambahan Modal'):,.2f}</li>
        <li>Prive: Rp {total_akun(st.session_state.gl, 'Prive'):,.2f}</li>
        <li>Laba Tahun Berjalan: Rp {laporan['laba_bersih']:,.2f}</li>
        <li>Modal Akhir: Rp {laporan['modal_akhir']:,.2f}</li>
    </ul>
    <h3>Arus Kas</h3>
    <ul>
        <li>Kas Masuk: Rp {st.session_state.gl[st.session_state.gl['Akun'].str.contains('Kas', case=False)]['Debit'].sum():,.2f}</li>
        <li>Kas Keluar: Rp {st.session_state.gl[st.session_state.gl['Akun'].str.contains('Kas', case=False)]['Kredit'].sum():,.2f}</li>
        <li>Saldo Kas Akhir: Rp {laporan['kas_akhir']:,.2f}</li>
    </ul>
    <h3>Neraca</h3>
    <ul>
        <li>Total Aset: Rp {laporan['aset']:,.2f}</li>
        <li>Total Kewajiban: Rp {laporan['kewajiban']:,.2f}</li>
        <li>Total Ekuitas: Rp {laporan['ekuitas']:,.2f}</li>
        <li>Total Kewajiban + Ekuitas: Rp {laporan['total_ke']:,.2f}</li>
    </ul>
    """
    b64 = base64.b64encode(html.encode()).decode()
    return f'<a href="data:text/html;base64,{b64}" download="ikhtisar_bumdes.html">📥 Unduh Ikhtisar (HTML)</a>'

st.markdown(export_ikhtisar(), unsafe_allow_html=True)
