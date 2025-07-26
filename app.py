# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
from datetime import datetime

nltk.download('vader_lexicon')

# Dummy login
USERNAME = "admin"
PASSWORD = "123"

if "page" not in st.session_state:
    st.session_state.page = "home"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Analisis Sentimen
def analyze_sentiment(pelayanan_rating):
    if pelayanan_rating == "Baik":
        return "Positif"
    elif pelayanan_rating == "Sedang":
        return "Netral"
    elif pelayanan_rating == "Buruk":
        return "Negatif"
    else:
        return "Netral"

# Halaman Utama
def home():
    st.title("📌 Analisis Sentimen Pelayanan SAMSAT")
    st.write("Silakan pilih menu:")
    if st.button("📝 Isi Komentar"):
        st.session_state.page = "form"
    st.markdown(
        "<div style='text-align: right;'>"
        "<button onclick='window.location.reload();' style='float:right;'>🔐 Masuk Dashboard (Admin)</button>"
        "</div>",
        unsafe_allow_html=True
    )
    if st.session_state.logged_in:
        st.session_state.page = "dashboard"

# Form Komentar
def form():
    st.title("🗣️ Form Komentar Publik")
    name = st.text_input("Nama")
    date = st.date_input("Tanggal Komentar")
    platform = st.selectbox("Mendapatkan informasi link dari mana?", ["YouTube", "Instagram", "Google Maps", "WhatsApp", "Scan di Tempat"])
    pelayanan = st.radio("Bagaimana pelayanannya?", ["Baik", "Sedang", "Buruk"])
    
    comment = ""
    if pelayanan:
        comment = st.text_area("Berikan alasanmu")

    if st.button("Kirim") and name and pelayanan and comment:
        sentiment = analyze_sentiment(pelayanan)
        data = {
            "Waktu": date.strftime("%Y-%m-%d"),
            "Nama": name,
            "Platform": platform,
            "Pelayanan": pelayanan,
            "Komentar": comment,
            "Sentimen": sentiment
        }
        df = pd.DataFrame([data])
        try:
            df.to_csv("data_komentar.csv", mode="a", header=not pd.io.common.file_exists("data_komentar.csv"), index=False)
        except Exception as e:
            st.error(f"Gagal menyimpan komentar: {e}")
        st.session_state.page = "thanks"

# Terima Kasih
def thanks():
    st.title("✅ Terima Kasih 😊")
    st.write("Komentar Anda telah dikirim.")
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
    st.title("📊 Dashboard Sentimen Layanan")
    try:
        df = pd.read_csv("data_komentar.csv", parse_dates=["Waktu"])
        st.sidebar.title("Filter Data")
        date_range = st.sidebar.date_input("Pilih Rentang Tanggal", [])
        platform_filter = st.sidebar.multiselect("Pilih Platform", df["Platform"].unique(), default=list(df["Platform"].unique()))
        
        if len(date_range) == 2:
            df = df[(df["Waktu"] >= pd.to_datetime(date_range[0])) & (df["Waktu"] <= pd.to_datetime(date_range[1]))]
        df = df[df["Platform"].isin(platform_filter)]

        st.write("### Tabel Komentar")
        st.dataframe(df)

        st.download_button("📥 Download Data", df.to_csv(index=False).encode("utf-8"), "data_filtered.csv", "text/csv")

        st.write("### Distribusi Sentimen")
        chart = df["Sentimen"].value_counts()
        st.bar_chart(chart)

        st.write("### Distribusi Platform")
        platform_chart = df["Platform"].value_counts()
        st.bar_chart(platform_chart)

        st.write("### Wordcloud Komentar")
        text = " ".join(df["Komentar"].astype(str))
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)

        st.write("### Insight:")
        st.write("- Komentar positif menunjukkan pelayanan memuaskan.")
        st.write("- Komentar negatif menandakan perlunya perbaikan.")
        st.write("- Pantau platform dominan untuk strategi layanan.")

    except FileNotFoundError:
        st.warning("Belum ada data komentar.")
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
    
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