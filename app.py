
import streamlit as st
import pandas as pd
import pdfkit
from jinja2 import Template

st.set_page_config(page_title="Laporan Keuangan BUMDes", layout="wide")

# Identitas BUMDes
st.sidebar.title("Identitas BUMDes")
nama_bumdes = st.sidebar.text_input("Nama BUMDes", "Buwana Raharja")
desa = st.sidebar.text_input("Desa", "Keling")
tahun = st.sidebar.number_input("Tahun Laporan", 2025, step=1)

st.title("📊 Laporan Keuangan BUMDes")

menu = st.selectbox("Pilih Laporan", [
    "Laporan Posisi Keuangan",
    "Laporan Laba Rugi",
    "Laporan Arus Kas",
    "Laporan Perubahan Ekuitas"
])

if "data" not in st.session_state:
    st.session_state.data = {}

if menu not in st.session_state.data:
    st.session_state.data[menu] = pd.DataFrame(columns=["Uraian", "Kategori", "Jumlah"])

with st.expander("➕ Tambah Data"):
    col1, col2, col3 = st.columns(3)
    with col1:
        uraian = st.text_input("Uraian")
    with col2:
        kategori = st.text_input("Kategori")
    with col3:
        jumlah = st.number_input("Jumlah", value=0.0)
    if st.button("Tambah"):
        if uraian and kategori:
            st.session_state.data[menu] = pd.concat([
                st.session_state.data[menu],
                pd.DataFrame([{"Uraian": uraian, "Kategori": kategori, "Jumlah": jumlah}])
            ], ignore_index=True)
        else:
            st.warning("Mohon lengkapi uraian dan kategori.")

st.dataframe(st.session_state.data[menu], use_container_width=True)

# Export PDF
def export_pdf():
    df = st.session_state.data[menu]
    template_path = os.path.join(os.path.dirname(__file__), "pdf_template.html")
    with open(template_path) as file_:
        template = Template(file_.read())

    html_out = template.render(
        nama_bumdes=nama_bumdes,
        desa=desa,
        tahun=tahun,
        judul=menu,
        tabel=df.to_dict(orient="records")
    )

    output_path = os.path.join(os.path.dirname(__file__), "laporan.pdf")
    pdfkit.from_string(html_out, output_path)
    with open(output_path, "rb") as pdf_file:
        st.download_button("📄 Unduh PDF", data=pdf_file, file_name="laporan_keuangan.pdf", mime="application/pdf")

export_pdf()
