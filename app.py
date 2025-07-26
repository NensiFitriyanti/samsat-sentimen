# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime

# Dummy login
USERNAME = "admin"
PASSWORD = "123"

if "page" not in st.session_state:
    st.session_state.page = "home"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Analisis Sentimen

def analyze_sentiment(service_quality):
    if service_quality == "Baik":
        return "Positif"
    elif service_quality == "Sedang":
        return "Netral"
    elif service_quality == "Buruk":
        return "Negatif"
    return "Netral"

# Halaman Utama

def home():
    st.title("📌 Analisis Sentimen Pelayanan SAMSAT")
    st.write("Silakan isi komentar atau login sebagai admin.")
    st.button("📝 Isi Komentar", on_click=lambda: st.session_state.update({"page": "form"}))
    st.sidebar.markdown("## 🔐 Admin")
    st.sidebar.button("Masuk Dashboard", on_click=lambda: st.session_state.update({"page": "login"}))

# Form Komentar

def form():
    st.title("🗣️ Form Komentar Publik")
    name = st.text_input("Nama")
    platform = st.selectbox("Mendapatkan informasi link dari mana?", ["", "YouTube", "Instagram", "Google Maps", "WhatsApp", "Scan di Tempat"])

    if platform:
        service_quality = st.radio("Bagaimana pelayanannya?", ["Baik", "Sedang", "Buruk"])
        if service_quality:
            comment = st.text_area("Berikan alasanmu")
            if st.button("Kirim"):
                sentiment = analyze_sentiment(service_quality)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                data = {
                    "Waktu": timestamp,
                    "Nama": name,
                    "Platform": platform,
                    "Pelayanan": service_quality,
                    "Komentar": comment,
                    "Sentimen": sentiment
                }
                df = pd.DataFrame([data])
                try:
                    df.to_csv("data_komentar.csv", mode="a", header=False, index=False)
                except:
                    df.to_csv("data_komentar.csv", index=False)
                st.session_state.page = "thanks"

# Hasil Terima Kasih

def thanks():
    st.title("😊 Terima Kasih")
    st.write("Komentar Anda sudah kami terima.")
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

# Dashboard

def dashboard():
    st.title("📊 Dashboard Admin")
    try:
        df = pd.read_csv("data_komentar.csv", names=["Waktu", "Nama", "Platform", "Pelayanan", "Komentar", "Sentimen"])

        # Filter tanggal dan platform
        st.sidebar.markdown("### Filter Data")
        df["Waktu"] = pd.to_datetime(df["Waktu"])
        start_date = st.sidebar.date_input("Dari Tanggal", df["Waktu"].min().date())
        end_date = st.sidebar.date_input("Sampai Tanggal", df["Waktu"].max().date())
        platform_filter = st.sidebar.multiselect("Pilih Platform", df["Platform"].unique(), default=list(df["Platform"].unique()))

        mask = (df["Waktu"].dt.date >= start_date) & (df["Waktu"].dt.date <= end_date) & (df["Platform"].isin(platform_filter))
        df_filtered = df[mask]

        st.write("### Tabel Komentar")
        st.dataframe(df_filtered)

        # Export button
        st.download_button("📥 Unduh Data CSV", df_filtered.to_csv(index=False).encode('utf-8'), "data_komentar_filtered.csv", "text/csv")

        st.write("### Grafik Jumlah Komentar per Platform")
        platform_counts = df_filtered["Platform"].value_counts()
        st.bar_chart(platform_counts)

        st.write("### Grafik Sentimen Pelayanan")
        sentiment_counts = df_filtered["Sentimen"].value_counts()
        st.bar_chart(sentiment_counts)

        st.write("### Wordcloud Komentar")
        text = " ".join(df_filtered["Komentar"].astype(str))
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
