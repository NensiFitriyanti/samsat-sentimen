# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
from datetime import datetime

nltk.download("vader_lexicon")

# Dummy login
USERNAME = "admin"
PASSWORD = "123"

if "page" not in st.session_state:
    st.session_state.page = "home"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Analisis Sentimen
def analyze_sentiment(pelayanan):
    if pelayanan == "Baik":
        return "Positif"
    elif pelayanan == "Sedang":
        return "Netral"
    elif pelayanan == "Buruk":
        return "Negatif"
    return "Netral"

# Halaman Utama
def home():
    st.title("📌 Analisis Sentimen Pelayanan SAMSAT")

    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔐 Masuk Admin"):
            st.session_state.page = "login"

    st.write("Selamat datang! Silakan isi komentar:")
    st.session_state.page = "form"

# Form Komentar Publik
def form():
    st.title("🗣️ Form Komentar Publik")

    nama = st.text_input("Nama Lengkap")
    tanggal = st.date_input("Tanggal Kunjungan")
    platform = st.selectbox("Mendapatkan informasi dari mana?", ["YouTube", "Instagram", "Google Maps", "WhatsApp", "Scan di Tempat"])
    pelayanan = st.radio("Bagaimana pelayanannya?", ["Baik", "Sedang", "Buruk"])
    
    if pelayanan:
        komentar = st.text_area("Berikan alasanmu")

        if st.button("Kirim"):
            sentimen = analyze_sentiment(pelayanan)
            data = {
                "Nama": nama,
                "Tanggal": tanggal.strftime("%Y-%m-%d"),
                "Platform": platform,
                "Pelayanan": pelayanan,
                "Komentar": komentar,
                "Sentimen": sentimen
            }

            df = pd.DataFrame([data])
            try:
                df.to_csv("data_komentar_old.csv", mode="a", header=not pd.read_csv("data_komentar_old.csv").empty, index=False)
            except:
                df.to_csv("data_komentar.csv_old.", index=False)

            st.session_state.page = "thanks"

# Halaman Terima Kasih
def thanks():
    st.title("😊 Terima Kasih!")
    st.write("Komentar Anda telah berhasil dikirim.")
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
    st.title("📊 Dashboard Sentimen Layanan SAMSAT")
    try:
        df = pd.read_csv("data_komentar.csv")

        st.write("### Tabel Komentar Publik")
        st.dataframe(df)

        # Grafik Sentimen
        st.write("### Distribusi Sentimen")
        sentimen_counts = df["Sentimen"].value_counts()
        st.bar_chart(sentimen_counts)

        # Grafik Platform
        st.write("### Total Komentar per Platform")
        platform_counts = df["Platform"].value_counts()
        st.bar_chart(platform_counts)

        # WordCloud Komentar
        st.write("### WordCloud Komentar")
        text = " ".join(df["Komentar"].astype(str))
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)

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
