import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64

st.set_page_config(page_title="Laporan Keuangan BUMDes", layout="wide")

# === Sidebar Identitas ===
st.sidebar.image("logo_bumdes.png") if os.path.exists("logo_bumdes.png") else None
st.sidebar.image("logo_pemdes.png") if os.path.exists("logo_pemdes.png") else None

st.sidebar.title("🔧 Pengaturan")
desa = st.sidebar.text_input("Desa", "Keling")
lembaga = st.sidebar.text_input("Nama Lembaga", "BUMDes Buwana Raharja")
tahun = st.sidebar.number_input("Tahun", 2025, step=1)

# === Judul Utama ===
st.title("📘 Buku Besar (General Ledger)")

# === Inisialisasi GL ===
if "gl" not in st.session_state:
    st.session_state.gl = pd.DataFrame(columns=["Tanggal", "Akun", "Debit", "Kredit", "Keterangan", "Bukti"])

# === Form Tambah Transaksi ===
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
        bukti = st.file_uploader("Upload Bukti Transaksi", type=["png", "jpg", "jpeg", "pdf"])

    if st.button("💾 Simpan Transaksi"):
        if akun and (debit > 0 or kredit > 0):
            new_row = {
                "Tanggal": tanggal.strftime("%Y-%m-%d"),
                "Akun": akun,
                "Debit": debit,
                "Kredit": kredit,
                "Keterangan": keterangan,
                "Bukti": bukti.name if bukti else ""
            }
            st.session_state.gl = pd.concat([st.session_state.gl, pd.DataFrame([new_row])], ignore_index=True)
            if bukti:
                with open(os.path.join("bukti", bukti.name), "wb") as f:
                    f.write(bukti.read())
            st.success("✅ Transaksi disimpan.")
        else:
            st.warning("⚠️ Lengkapi akun dan nilai debit/kredit.")

# === Tabel Data Editor untuk Hapus ===
st.subheader("📋 Daftar Transaksi")
gl_df = st.session_state.gl.copy()
if not gl_df.empty:
    gl_df["Hapus"] = False
    edited = st.data_editor(gl_df, num_rows="dynamic", use_container_width=True, key="gl_editor")
    if st.button("🗑️ Hapus yang Dicentang"):
        to_drop = edited[edited["Hapus"] == True].index
        st.session_state.gl.drop(index=to_drop, inplace=True)
        st.session_state.gl.reset_index(drop=True, inplace=True)
        st.success("✅ Transaksi dihapus.")
else:
    st.info("Belum ada transaksi.")

# === Fungsi Hitung Otomatis ===
def total_akun(df, kata):
    return df[df["Akun"].str.contains(kata, case=False, na=False)]["Debit"].sum() - \
           df[df["Akun"].str.contains(kata, case=False, na=False)]["Kredit"].sum()

df = st.session_state.gl
pendapatan = total_akun(df, "Pendapatan")
beban = total_akun(df, "Beban")
laba_bersih = pendapatan - beban

modal_awal = total_akun(df, "Modal Awal")
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

# === Tampilkan Laporan ===
st.header("📑 Laporan Keuangan Otomatis")

col1, col2 = st.columns(2)
with col1:
    st.subheader("📄 Laba Rugi")
    st.markdown(f"- **Pendapatan:** Rp {pendapatan:,.2f}")
    st.markdown(f"- **Beban:** Rp {beban:,.2f}")
    st.markdown(f"- **Laba Bersih:** Rp {laba_bersih:,.2f}")

    st.subheader("🧾 Perubahan Ekuitas")
    st.markdown(f"- Modal Awal: Rp {modal_awal:,.2f}")
    st.markdown(f"- Penambahan Modal: Rp {penambahan_modal:,.2f}")
    st.markdown(f"- Prive: Rp {prive:,.2f}")
    st.markdown(f"- Laba Tahun Berjalan: Rp {laba_bersih:,.2f}")
    st.markdown(f"- Modal Akhir: Rp {modal_akhir:,.2f}")

with col2:
    st.subheader("💰 Arus Kas")
    st.markdown(f"- Kas Masuk: Rp {kas_masuk:,.2f}")
    st.markdown(f"- Kas Keluar: Rp {kas_keluar:,.2f}")
    st.markdown(f"- Saldo Kas Akhir: Rp {kas_akhir:,.2f}")

    st.subheader("📊 Neraca")
    st.markdown(f"- Aset: Rp {aset:,.2f}")
    st.markdown(f"- Utang: Rp {utang:,.2f}")
    st.markdown(f"- Ekuitas: Rp {modal_akhir:,.2f}")
    st.markdown(f"- Total Kewajiban + Ekuitas: Rp {total_ke:,.2f}")

# === Lembar Pengesahan ===
st.markdown("---")
st.subheader("🖊️ Lembar Pengesahan")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Disusun Oleh**")
    st.markdown("<br><br><br>__________________________", unsafe_allow_html=True)
    st.markdown("Bendahara")

with col2:
    st.markdown("**Disetujui Oleh**")
    st.markdown("<br><br><br>__________________________", unsafe_allow_html=True)
    st.markdown("Direktur Utama BUMDes")

col3, col4 = st.columns(2)
with col3:
    st.markdown("**Mengetahui**")
    st.markdown("<br><br><br>__________________________", unsafe_allow_html=True)
    st.markdown("Kepala Desa")

with col4:
    st.markdown("**Mengetahui**")
    st.markdown("<br><br><br>__________________________", unsafe_allow_html=True)
    st.markdown("Ketua BPD")

# === Export HTML (PDF jika lokal saja) ===
def export_html():
    html = f"""
    <html><body><h2>Laporan Keuangan {lembaga} - Desa {desa} - Tahun {tahun}</h2>
    <p><strong>Laba Rugi:</strong><br>Pendapatan: Rp {pendapatan:,.2f}<br>Beban: Rp {beban:,.2f}<br>Laba Bersih: Rp {laba_bersih:,.2f}</p>
    <p><strong>Perubahan Ekuitas:</strong><br>Modal Awal: Rp {modal_awal:,.2f}<br>Penambahan Modal: Rp {penambahan_modal:,.2f}<br>Prive: Rp {prive:,.2f}<br>Modal Akhir: Rp {modal_akhir:,.2f}</p>
    <p><strong>Arus Kas:</strong><br>Kas Masuk: Rp {kas_masuk:,.2f}<br>Kas Keluar: Rp {kas_keluar:,.2f}<br>Saldo Kas: Rp {kas_akhir:,.2f}</p>
    <p><strong>Neraca:</strong><br>Aset: Rp {aset:,.2f}<br>Utang: Rp {utang:,.2f}<br>Ekuitas: Rp {modal_akhir:,.2f}</p>
    <hr>
    <p><strong>Pengesahan:</strong><br><br>
    Disusun oleh:<br><br><br>__________________________<br>Bendahara<br><br>
    Disetujui oleh:<br><br><br>__________________________<br>Direktur Utama<br><br>
    Mengetahui:<br><br><br>__________________________<br>Kepala Desa<br><br>
    Mengetahui:<br><br><br>__________________________<br>Ketua BPD</p>
    </body></html>
    """
    b64 = base64.b64encode(html.encode()).decode()
    return f'<a href="data:text/html;base64,{b64}" download="laporan_keuangan.html">📥 Unduh Laporan (HTML)</a>'

st.markdown(export_html(), unsafe_allow_html=True)
