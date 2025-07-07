import streamlit as st
import pandas as pd
import base64
from datetime import datetime
import os

st.set_page_config(page_title="Laporan Keuangan BUMDes", layout="wide")

# === IDENTITAS ===
st.sidebar.title("Identitas BUMDes")
nama_bumdes = st.sidebar.text_input("Nama BUMDes", "Buwana Raharja")
desa = st.sidebar.text_input("Desa", "Keling")
tahun = st.sidebar.number_input("Tahun Laporan", 2025, step=1)

# === PEJABAT UNTUK PENGESAHAN ===
st.sidebar.markdown("---")
st.sidebar.subheader("Pejabat Tanda Tangan")
bendahara = st.sidebar.text_input("Nama Bendahara", "Siti Aminah")
direktur = st.sidebar.text_input("Nama Direktur Utama", "Bambang Setiawan")
kepala_desa = st.sidebar.text_input("Nama Kepala Desa", "Sugeng Riyadi")
ketua_bpd = st.sidebar.text_input("Nama Ketua BPD", "Dwi Purnomo")

st.title("📘 Buku Besar (General Ledger)")

# === INISIALISASI ===
if "gl" not in st.session_state:
    st.session_state.gl = pd.DataFrame(columns=["Tanggal", "Akun", "Debit", "Kredit", "Keterangan", "Bukti"])

# === FORM TAMBAH TRANSAKSI ===
with st.expander("➕ Tambah Transaksi"):
    col1, col2, col3 = st.columns(3)
    with col1:
        tanggal = st.date_input("Tanggal", datetime.today())
    with col2:
        akun = st.text_input("Akun")
    with col3:
        keterangan = st.text_input("Keterangan")

    col4, col5, col6 = st.columns(3)
    with col4:
        debit = st.number_input("Debit", min_value=0.0, format="%.2f")
    with col5:
        kredit = st.number_input("Kredit", min_value=0.0, format="%.2f")
    with col6:
        bukti_file = st.file_uploader("Upload Nota/Bukti", type=["png", "jpg", "jpeg", "pdf"])

    if st.button("💾 Simpan Transaksi"):
        if akun and (debit > 0 or kredit > 0):
            if bukti_file:
                bukti_path = f"bukti_{datetime.now().strftime('%Y%m%d%H%M%S')}_{bukti_file.name}"
                with open(bukti_path, "wb") as f:
                    f.write(bukti_file.read())
            else:
                bukti_path = ""
            new_row = pd.DataFrame([{
                "Tanggal": tanggal.strftime("%Y-%m-%d"),
                "Akun": akun,
                "Debit": debit,
                "Kredit": kredit,
                "Keterangan": keterangan,
                "Bukti": bukti_path
            }])
            st.session_state.gl = pd.concat([st.session_state.gl, new_row], ignore_index=True)
            st.success("✅ Transaksi berhasil disimpan.")
        else:
            st.warning("⚠️ Lengkapi akun dan nilai debit/kredit.")

# === TAMPILKAN GL ===
st.subheader("📋 Daftar Transaksi")
gl_df = st.session_state.gl.copy()
if not gl_df.empty:
    for idx, row in gl_df.iterrows():
        st.write(f"**{row['Tanggal']} - {row['Akun']}** | Debit: Rp{row['Debit']}, Kredit: Rp{row['Kredit']}")
        st.caption(row['Keterangan'])
        if row['Bukti'] and os.path.exists(row['Bukti']):
            if row['Bukti'].endswith(".pdf"):
                st.markdown(f"[📄 Lihat Bukti PDF]({row['Bukti']})")
            else:
                st.image(row['Bukti'], width=200)
    if st.button("🗑️ Hapus Semua Transaksi"):
        st.session_state.gl = pd.DataFrame(columns=gl_df.columns)
        st.success("✅ Semua transaksi dihapus.")
else:
    st.info("Belum ada transaksi yang dimasukkan.")

# === FUNGSI BANTU ===
def total_akun(df, kata):
    return df[df["Akun"].str.contains(kata, case=False, na=False)]["Debit"].sum() - df[df["Akun"].str.contains(kata, case=False, na=False)]["Kredit"].sum()

# === HITUNG OTOMATIS ===
df = st.session_state.gl
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

# === TAMPILKAN RINGKASAN ===
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

# === EKSPOR HTML ===
st.subheader("📥 Unduh Ikhtisar")
def export_html():
    html = f"""
    <h2>Ikhtisar Laporan Keuangan BUMDes</h2>
    <p><strong>{nama_bumdes} - Desa {desa} - Tahun {tahun}</strong></p>
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
    <br><br>
    <p style="text-align: right;">Keling, Juli {tahun}</p>
    <table style="width:100%; text-align: center;">
      <tr>
        <td>Dibuat oleh</td>
        <td>Disetujui oleh</td>
      </tr>
      <tr>
        <td>Bendahara</td>
        <td>Direktur Utama BUMDes</td>
      </tr>
      <tr><td colspan="2"><br><br><br><br></td></tr>
      <tr>
        <td><u>{bendahara}</u></td>
        <td><u>{direktur}</u></td>
      </tr>
    </table>
    <br><br>
    <table style="width:100%; text-align: center;">
      <tr>
        <td>Mengetahui,</td>
      </tr>
      <tr>
        <td>Kepala Desa</td>
        <td>Ketua BPD</td>
      </tr>
      <tr><td colspan="2"><br><br><br><br></td></tr>
      <tr>
        <td><u>{kepala_desa}</u></td>
        <td><u>{ketua_bpd}</u></td>
      </tr>
    </table>
    """
    b64 = base64.b64encode(html.encode()).decode()
    return f'<a href="data:text/html;base64,{b64}" download="ikhtisar_laporan.html">📤 Unduh HTML</a>'

st.markdown(export_html(), unsafe_allow_html=True)
