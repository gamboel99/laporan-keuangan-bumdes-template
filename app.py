# === app.py ===
import streamlit as st
import pandas as pd
import base64
from datetime import datetime
import matplotlib.pyplot as plt

# ----------------------------
# HAK AKSES SEDERHANA (LOGIN)
# ----------------------------
USERS = {"admin": "1234", "viewer": "abcd"}  # username: password
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🔐 Login BUMDes")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Masuk"):
        if u in USERS and USERS[u] == p:
            st.session_state.login = True
            st.session_state.user = u
        else:
            st.error("Username atau password salah")
    st.stop()

# ----------------------------
# SIDEBAR & IDENTITAS
# ----------------------------
st.sidebar.title("Identitas BUMDes")
nama_bumdes = st.sidebar.text_input("Nama BUMDes", "Buwana Raharja")
desa = st.sidebar.text_input("Desa", "Keling")
tahun_list = list(range(2022, datetime.today().year + 2))
tahun = st.sidebar.selectbox("Tahun Laporan", tahun_list, index=tahun_list.index(datetime.today().year))

# ----------------------------
# INISIALISASI DATA
# ----------------------------
if "gl" not in st.session_state:
    st.session_state.gl = pd.DataFrame(columns=["Tahun", "Tanggal", "Akun", "Debit", "Kredit", "Keterangan"])

# ----------------------------
# INPUT TRANSAKSI
# ----------------------------
st.title("📘 Buku Besar BUMDes")

with st.expander("➕ Tambah Transaksi"):
    tgl, akun, ket = st.columns(3)
    with tgl: tanggal = st.date_input("Tanggal", datetime.today())
    with akun: nama_akun = st.text_input("Akun")
    with ket: keterangan = st.text_input("Keterangan")
    deb, kre = st.columns(2)
    with deb: debit = st.number_input("Debit", 0.0)
    with kre: kredit = st.number_input("Kredit", 0.0)
    if st.button("💾 Simpan"):
        if nama_akun and (debit > 0 or kredit > 0):
            new = pd.DataFrame([{
                "Tahun": tahun,
                "Tanggal": tanggal.strftime("%Y-%m-%d"),
                "Akun": nama_akun,
                "Debit": debit,
                "Kredit": kredit,
                "Keterangan": keterangan
            }])
            st.session_state.gl = pd.concat([st.session_state.gl, new], ignore_index=True)
            st.success("✅ Transaksi ditambahkan")
        else:
            st.warning("Lengkapi akun dan nilai debit/kredit")

# ----------------------------
# FILTER DATA TAHUN AKTIF
# ----------------------------
df_all = st.session_state.gl.copy()
df = df_all[df_all["Tahun"] == tahun].reset_index(drop=True)

# ----------------------------
# TABEL DENGAN HAPUS
# ----------------------------
st.subheader("📋 Daftar Transaksi Tahun " + str(tahun))
if not df.empty:
    df["Hapus?"] = False
    edited = st.data_editor(df, use_container_width=True, key="edit_gl")
    if st.button("🗑️ Hapus yang dicentang"):
        to_delete = edited[edited["Hapus?"] == True].index
        st.session_state.gl.drop(df.index[to_delete], inplace=True)
        st.session_state.gl.reset_index(drop=True, inplace=True)
        st.success("✅ Data dihapus")
else:
    st.info("Belum ada transaksi tahun ini")

# ----------------------------
# PERHITUNGAN & LAPORAN
# ----------------------------
def total_akun(df, kata):
    return df[df["Akun"].str.contains(kata, case=False, na=False)]["Debit"].sum() - \
           df[df["Akun"].str.contains(kata, case=False, na=False)]["Kredit"].sum()

pendapatan = total_akun(df, "Pendapatan")
beban = total_akun(df, "Beban")
laba = pendapatan - beban
modal_awal = total_akun(df, "Modal")
prive = total_akun(df, "Prive")
penambahan = total_akun(df, "Penambahan Modal")
kas_masuk = df[df["Akun"].str.contains("Kas", case=False)]["Debit"].sum()
kas_keluar = df[df["Akun"].str.contains("Kas", case=False)]["Kredit"].sum()
persediaan = total_akun(df, "Persediaan")
peralatan = total_akun(df, "Peralatan")
piutang = total_akun(df, "Piutang")
utang = total_akun(df, "Utang")
kas_akhir = kas_masuk - kas_keluar
aset = kas_akhir + piutang + peralatan + persediaan
ekuitas = modal_awal + laba + penambahan - prive

# ----------------------------
# TAMPILAN LAPORAN
# ----------------------------
st.header("📑 Laporan Keuangan Otomatis")
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Laba Rugi")
    st.markdown(f"- Pendapatan: Rp {pendapatan:,.2f}")
    st.markdown(f"- Beban: Rp {beban:,.2f}")
    st.markdown(f"- Laba Bersih: Rp {laba:,.2f}")
    st.subheader("🧾 Perubahan Ekuitas")
    st.markdown(f"- Modal Awal: Rp {modal_awal:,.2f}")
    st.markdown(f"- Penambahan Modal: Rp {penambahan:,.2f}")
    st.markdown(f"- Prive: Rp {prive:,.2f}")
    st.markdown(f"- Laba Tahun Berjalan: Rp {laba:,.2f}")
    st.markdown(f"- Modal Akhir: Rp {ekuitas:,.2f}")

with col2:
    st.subheader("💰 Arus Kas")
    st.markdown(f"- Kas Masuk: Rp {kas_masuk:,.2f}")
    st.markdown(f"- Kas Keluar: Rp {kas_keluar:,.2f}")
    st.markdown(f"- Saldo Kas Akhir: Rp {kas_akhir:,.2f}")
    st.subheader("📊 Neraca")
    st.markdown(f"- Aset (Kas + Piutang + Peralatan + Persediaan): Rp {aset:,.2f}")
    st.markdown(f"- Utang: Rp {utang:,.2f}")
    st.markdown(f"- Ekuitas: Rp {ekuitas:,.2f}")
    st.markdown(f"- Total Kewajiban + Ekuitas: Rp {utang + ekuitas:,.2f}")

# ----------------------------
# GRAFIK
# ----------------------------
st.subheader("📈 Grafik Arus Kas")
kategori = ["Kas Masuk", "Kas Keluar"]
angka = [kas_masuk, kas_keluar]
fig, ax = plt.subplots()
ax.bar(kategori, angka, color=["green", "red"])
ax.set_ylabel("Jumlah (Rp)")
ax.set_title("Grafik Kas Masuk vs Kas Keluar")
st.pyplot(fig)

# ----------------------------
# EXPORT EXCEL
# ----------------------------
st.subheader("📥 Ekspor Data")
if not df_all.empty:
    to_dl = df_all.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Unduh Semua Data (.csv)", to_dl, file_name=f"GL_BUMDes_{nama_bumdes}_{tahun}.csv", mime="text/csv")
else:
    st.info("Belum ada data untuk diekspor.")
