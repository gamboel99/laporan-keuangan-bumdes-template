import streamlit as st
import pandas as pd
import base64
from datetime import datetime
import os
import io

st.set_page_config(page_title="Laporan Keuangan BUMDes", layout="wide")

# === PILIHAN MULTI LEMBAGA DAN DESA ===
st.sidebar.title("🔰 Pilih Unit Lembaga")
lembaga = st.sidebar.selectbox("Lembaga", ["BUMDes", "PKK", "Karang Taruna", "LPMD", "BPD"])
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

st.title(f"📘 Buku Besar ({lembaga})")

# === LOGO ===
col_logo1, col_logo2 = st.columns([1, 6])
with col_logo1:
    if os.path.exists("logo_pemdes.png"):
        st.image("logo_pemdes.png", width=80)
with col_logo2:
    if os.path.exists("logo_bumdes.png"):
        st.image("logo_bumdes.png", width=80)

# === INISIALISASI ===
key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Akun", "Debit", "Kredit", "Keterangan", "Bukti"])

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
            st.session_state[key_gl] = pd.concat([st.session_state[key_gl], new_row], ignore_index=True)
            st.success("✅ Transaksi berhasil disimpan.")
        else:
            st.warning("⚠️ Lengkapi akun dan nilai debit/kredit.")

# === TAMPILKAN GL ===
st.subheader("📋 Daftar Transaksi")
gl_df = st.session_state[key_gl].copy()
if not gl_df.empty:
    for idx, row in gl_df.iterrows():
        st.write(f"**{row['Tanggal']} - {row['Akun']}** | Debit: Rp{row['Debit']}, Kredit: Rp{row['Kredit']}")
        st.caption(row['Keterangan'])
        if row['Bukti'] and os.path.exists(row['Bukti']):
            if row['Bukti'].endswith(".pdf"):
                st.markdown(f"[📄 Lihat Bukti PDF]({row['Bukti']})")
            else:
                st.image(row['Bukti'], width=200)
        col_del = st.columns([1, 5])
        with col_del[0]:
            if st.button(f"❌ Hapus", key=f"hapus_{idx}"):
                st.session_state[key_gl].drop(index=idx, inplace=True)
                st.session_state[key_gl].reset_index(drop=True, inplace=True)
                st.experimental_rerun()
else:
    st.info("Belum ada transaksi yang dimasukkan.")

# === TAMPILKAN PENGESAHAN DI WEB ===
st.markdown("---")
st.markdown("**LEMBAR PENGESAHAN**")
st.markdown(f"Desa {desa}, Juli {tahun}")
col_atas = st.columns(2)
with col_atas[0]:
    st.markdown("Dibuat oleh:")
    st.markdown("**Bendahara**")
    st.markdown("<br><br><br>**<u>{}</u>**".format(bendahara), unsafe_allow_html=True)
with col_atas[1]:
    st.markdown("Disetujui oleh:")
    st.markdown(f"**Ketua {lembaga}**")
    st.markdown("<br><br><br>**<u>{}</u>**".format(direktur), unsafe_allow_html=True)

col_bawah = st.columns(2)
with col_bawah[0]:
    st.markdown("Mengetahui:")
    st.markdown("**Kepala Desa**")
    st.markdown("<br><br><br>**<u>{}</u>**".format(kepala_desa), unsafe_allow_html=True)
with col_bawah[1]:
    st.markdown("Mengetahui:")
    st.markdown("**Ketua BPD**")
    st.markdown("<br><br><br>**<u>{}</u>**".format(ketua_bpd), unsafe_allow_html=True)

# Selanjutnya bisa ditambahkan ekspor PDF jika diperlukan
