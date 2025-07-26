# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import datetime
import os

# Dummy login
USERNAME = "admin"
PASSWORD = "123"

if "page" not in st.session_state:
    st.session_state.page = "home"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Halaman Utama
def home():
    st.set_page_config(page_title="Analisis Sentimen SAMSAT", layout="wide")
    col1, col2 = st.columns([8, 2])
    with col1:
        st.title("📌 Analisis Sentimen Pelayanan SAMSAT")
        st.write("Silakan pilih menu:")
        if st.button("📝 Isi Komentar"):
            st.session_state.page = "form"
    with col2:
        st.write("")
        st.write("")
        if st.button("🔐 Masuk Dashboard (Admin)"):
            st.session_state.page = "login"

# Form Komentar
def form():
    st.title("🗣️ Form Komentar Publik")

    name = st.text_input("Nama")
    tanggal = st.date_input("Tanggal Komentar", value=datetime.date.today())
    
    platform = st.selectbox("Mendapatkan informasi dari mana?", 
                            ["YouTube", "Instagram", "Google Maps", "WhatsApp", "Scan di Tempat"])

    pelayanan = st.radio("Bagaimana pelayanannya?", ["Baik", "Sedang", "Buruk"])

    comment = ""
    if pelayanan:
        comment = st.text_area("Berikan alasanmu")

    if st.button("Kirim"):
        if not name or not comment:
            st.warning("Nama dan komentar tidak boleh kosong.")
            return

        # Mapping pelayanan ke sentimen
        if pelayanan == "Baik":
            sentiment = "Positif"
        elif pelayanan == "Sedang":
            sentiment = "Netral"
        else:
            sentiment = "Negatif"

        data = {
            "Waktu": tanggal,
            "Nama": name,
            "Platform": platform,
            "Pelayanan": pelayanan,
            "Komentar": comment,
            "Sentimen": sentiment
        }

        df = pd.DataFrame([data])
        try:
            df.to_csv("data_komentar.csv", mode="a", header=not os.path.exists("data_komentar.csv"), index=False)
        except:
            df.to_csv("data_komentar.csv", index=False)

        st.session_state.page = "thanks"

# Halaman Terima Kasih
def thanks():
    st.title("✅ Terima Kasih")
    st.markdown("Komentar Anda telah dikirim. 😊")
    if st.button("Kembali ke Beranda"):
        st.session_state.page = "home"

# Login Admin
def login():
    st.title("🔒 Login Admin")
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == USERNAME and pw == PASSWORD:
            st.session_state.logged_in = True
            st.session_state.page = "dashboard"
        else:
            st.error("Username atau password salah.")
    if st.button("Kembali"):
        st.session_state.page = "home"

# Dashboard Admin
def dashboard():
    st.title("📊 Dashboard Admin: Analisis Sentimen Layanan SAMSAT")
    try:
        df = pd.read_csv("data_komentar.csv", parse_dates=["Waktu"])
        st.write("### Tabel Komentar Masuk")
        st.dataframe(df)

        # Grafik Sentimen
        st.write("### Grafik Distribusi Sentimen")
        sentimen_count = df["Sentimen"].value_counts()
        st.bar_chart(sentimen_count)

        # Grafik Platform
        st.write("### Jumlah Komentar per Platform")
        platform_count = df["Platform"].value_counts()
        st.bar_chart(platform_count)

        # Wordcloud
        st.write("### Wordcloud Komentar")
        text = " ".join(df["Komentar"].astype(str))
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)

        # Insight
        st.write("### Insight:")
        st.markdown("- **Komentar positif** menandakan pelayanan memuaskan.")
        st.markdown("- **Komentar negatif** perlu ditindaklanjuti.")
        st.markdown("- **Platform terbanyak** digunakan menunjukkan sumber pengakses layanan.")
    except Exception as e:
        st.warning(f"Belum ada data komentar atau terjadi kesalahan: {e}")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.page = "home"

# Routing
def main():
    page = st.session_state.page
    if page == "home":
        home()
    elif page == "form":
        form()
    elif page == "thanks":
        thanks()
    elif page == "login":
        login()
    elif page == "dashboard":
        if st.session_state.logged_in:
            dashboard()
        else:
            login()

if __name__ == "__main__":
    main()