import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Laporan Keuangan BUMDes", layout="wide")
st.title("📊 Laporan Keuangan BUMDes Buwana Raharja")
st.caption("Posisi Keuangan • Laba Rugi • Arus Kas • Perubahan Ekuitas")

# Sidebar
st.sidebar.header("Identitas BUMDes")
nama_bumdes = st.sidebar.text_input("Nama BUMDes", "Buwana Raharja")
desa = st.sidebar.text_input("Desa", "Keling")
tahun = st.sidebar.number_input("Tahun Laporan", min_value=2020, max_value=2100, value=date.today().year)

# Input Template
def laporan_input(title, cols):
    st.subheader(title)
    df = st.session_state.get(title, pd.DataFrame(columns=cols))
    with st.form(f"form_{title}"):
        with st.expander("➕ Tambah Data"):
            inputs = [
                st.text_input(f"{c}", key=f"{title}_{c}") if c != cols[-1]
                else st.number_input(f"{c}", key=f"{title}_{c}", value=0.0)
                for c in cols
            ]
            if st.form_submit_button("Tambah"):
                new = pd.DataFrame([inputs], columns=cols)
                st.session_state[title] = pd.concat([df, new], ignore_index=True)
    # Tampilkan
    st.dataframe(st.session_state.get(title, df), use_container_width=True)

# Sections
laporan_input("Laporan Posisi Keuangan", ["Akun", "Kategori (Aset/Kewajiban/Ekuitas)", "Jumlah"])
laporan_input("Laporan Laba Rugi", ["Akun", "Kategori (Pendapatan/Beban)", "Jumlah"])
laporan_input("Laporan Arus Kas", ["Kegiatan", "Kategori (Operasi/Investasi/Pendanaan)", "Jumlah"])
laporan_input("Laporan Perubahan Ekuitas", ["Uraian", "Kategori (Modal Awal/Laba Ditahan/Penambahan Modal)", "Jumlah"])

st.markdown("---")
st.warning("📥 Fitur unduh PDF belum tersedia. Silakan copy ke Excel via tombol export pada tabel.")
st.markdown(f"**© {tahun} BUMDes {nama_bumdes}, Desa {desa}**")
