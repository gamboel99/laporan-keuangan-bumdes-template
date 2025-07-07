import streamlit as st
import pandas as pd
import base64
from datetime import datetime

st.set_page_config(page_title="Laporan Keuangan BUMDes", layout="wide")

# === Logo dan Identitas ===
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/9/99/Logo_Pemdes_Keling.jpeg", width=100, caption="Pemerintah Desa Keling")
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Logo_BUMDes.svg/1200px-Logo_Bumdes_Keling.jpg", width=100, caption="BUMDes")

st.sidebar.title("Identitas Lembaga")
desa = st.sidebar.text_input("Nama Desa", "Keling")
lembaga = st.sidebar.selectbox("Lembaga", ["BUMDes", "PKK", "Karang Taruna", "LPMD", "Posyandu", "Lainnya"])
tahun = st.sidebar.number_input("Tahun Laporan", 2025, step=1)

st.title(f"📘 Buku Besar ({lembaga} {desa})")

# === Session Key per lembaga & tahun ===
key_session = f"gl_{desa}_{lembaga}_{tahun}"
if key_session not in st.session_state:
    st.session_state[key_session] = pd.DataFrame(columns=["Tanggal", "Akun", "Debit", "Kredit", "Keterangan"])

# === Form Tambah Transaksi ===
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
            new_row = pd.DataFrame([{
                "Tanggal": tanggal.strftime("%Y-%m-%d"),
                "Akun": akun,
                "Debit": debit,
                "Kredit": kredit,
                "Keterangan": keterangan
            }])
            st.session_state[key_session] = pd.concat([st.session_state[key_session], new_row], ignore_index=True)
            st.success("✅ Transaksi berhasil disimpan.")
        else:
            st.warning("⚠️ Lengkapi akun dan nilai debit/kredit.")

# === Tampilkan GL dengan opsi hapus ===
st.subheader("📋 Daftar Transaksi")
gl_df = st.session_state[key_session].copy()

if not gl_df.empty:
    gl_df["Hapus?"] = False
    edited = st.data_editor(gl_df, num_rows="dynamic", use_container_width=True, key=f"gl_editor_{key_session}")
    if st.button("🗑️ Hapus Transaksi yang Dicentang"):
        hapus_idx = edited[edited["Hapus?"] == True].index
        st.session_state[key_session].drop(index=hapus_idx, inplace=True)
        st.session_state[key_session].reset_index(drop=True, inplace=True)
        st.success("✅ Transaksi berhasil dihapus.")
else:
    st.info("Belum ada transaksi yang dimasukkan.")

# === Fungsi bantu ===
def total_akun(df, kata):
    return df[df["Akun"].str.contains(kata, case=False, na=False)]["Debit"].sum() - df[df["Akun"].str.contains(kata, case=False, na=False)]["Kredit"].sum()

# === Olah Data Keuangan ===
df = st.session_state[key_session]
pendapatan = total_akun(df, "Pendapatan")
beban = total_akun(df, "Beban")
laba_bersih = pendapatan - beban

modal_awal = total_akun(df, "Modal")
penambahan_modal = total_akun(df, "Penambahan Modal")
prive = total_akun(df, "Prive")
modal_akhir = modal_awal + laba_bersih + penambahan_modal - prive

kas_masuk = df[df["Akun"].str.contains("Kas", case=False)]["Debit"].sum()
kas_keluar = df[df["Akun"].str.contains("Kas", case=False)]["Kredit"].sum()
kas_akhir = kas_masuk - kas_keluar

piutang = total_akun(df, "Piutang")
peralatan = total_akun(df, "Peralatan")
utang = total_akun(df, "Utang")
aset = kas_akhir + piutang + peralatan
total_ke = utang + modal_akhir

# === Tampilkan Semua Laporan ===
st.header("📑 Laporan Keuangan Otomatis")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Laba Rugi")
    st.markdown(f"- **Pendapatan:** Rp {pendapatan:,.2f}")
    st.markdown(f"- **Beban:** Rp {beban:,.2f}")
    st.markdown(f"- **Laba Bersih:** Rp {laba_bersih:,.2f}")

    st.subheader("🧾 Perubahan Ekuitas")
    st.markdown(f"- **Modal Awal:** Rp {modal_awal:,.2f}")
    st.markdown(f"- **Penambahan Modal:** Rp {penambahan_modal:,.2f}")
    st.markdown(f"- **Prive:** Rp {prive:,.2f}")
    st.markdown(f"- **Laba Tahun Berjalan:** Rp {laba_bersih:,.2f}")
    st.markdown(f"- **Modal Akhir:** Rp {modal_akhir:,.2f}")

with col2:
    st.subheader("💰 Arus Kas")
    st.markdown(f"- **Kas Masuk:** Rp {kas_masuk:,.2f}")
    st.markdown(f"- **Kas Keluar:** Rp {kas_keluar:,.2f}")
    st.markdown(f"- **Saldo Kas Akhir:** Rp {kas_akhir:,.2f}")

    st.subheader("📊 Neraca")
    st.markdown(f"- **Aset (Kas + Piutang + Peralatan):** Rp {aset:,.2f}")
    st.markdown(f"- **Utang:** Rp {utang:,.2f}")
    st.markdown(f"- **Ekuitas:** Rp {modal_akhir:,.2f}")
    st.markdown(f"- **Total Kewajiban + Ekuitas:** Rp {total_ke:,.2f}")

# === Ekspor HTML ===
st.subheader("📥 Unduh Ikhtisar")

def export_html():
    html = f"""
    <h2>Ikhtisar Laporan Keuangan</h2>
    <p><strong>{lembaga} - Desa {desa} - Tahun {tahun}</strong></p>
    <h3>Laba Rugi</h3>
    <ul>
        <li>Pendapatan: Rp {pendapatan:,.2f}</li>
        <li>Beban: Rp {beban:,.2f}</li>
        <li>Laba Bersih: Rp {laba_bersih:,.2f}</li>
    </ul>
    <h3>Perubahan Ekuitas</h3>
    <ul>
        <li>Modal Awal: Rp {modal_awal:,.2f}</li>
        <li>Penambahan Modal: Rp {penambahan_modal:,.2f}</li>
        <li>Prive: Rp {prive:,.2f}</li>
        <li>Laba Tahun Berjalan: Rp {laba_bersih:,.2f}</li>
        <li>Modal Akhir: Rp {modal_akhir:,.2f}</li>
    </ul>
    <h3>Arus Kas</h3>
    <ul>
        <li>Kas Masuk: Rp {kas_masuk:,.2f}</li>
        <li>Kas Keluar: Rp {kas_keluar:,.2f}</li>
        <li>Saldo Kas Akhir: Rp {kas_akhir:,.2f}</li>
    </ul>
    <h3>Neraca</h3>
    <ul>
        <li>Aset: Rp {aset:,.2f}</li>
        <li>Utang: Rp {utang:,.2f}</li>
        <li>Ekuitas: Rp {modal_akhir:,.2f}</li>
        <li>Total Kewajiban + Ekuitas: Rp {total_ke:,.2f}</li>
    </ul>
    """
    b64 = base64.b64encode(html.encode()).decode()
    return f'<a href="data:text/html;base64,{b64}" download="ikhtisar_laporan_{lembaga}_{desa}_{tahun}.html">📤 Unduh HTML</a>'

st.markdown(export_html(), unsafe_allow_html=True)
