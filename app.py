# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
from datetime import datetime
from collections import Counter

nltk.download('vader_lexicon')

# Dummy login multiuser
USERS = {
    "admin": {"password": "123", "role": "Admin"},
    "editor": {"password": "456", "role": "Editor"}
}

if "page" not in st.session_state:
    st.session_state.page = "home"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = ""

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
    st.write("Silakan isi komentar atau login sebagai admin/editor.")
    st.button("📝 Isi Komentar", on_click=lambda: st.session_state.update({"page": "form"}))
    st.sidebar.markdown("## 🔐 Admin / Editor")
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

# Login Multiuser

def login():
    st.title("🔒 Login Pengguna")
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if user in USERS and USERS[user]["password"] == pw:
            st.session_state.logged_in = True
            st.session_state.user_role = USERS[user]["role"]
            st.session_state.page = "dashboard"
        else:
            st.error("Username atau password salah.")
    if st.button("Kembali"):
        st.session_state.page = "home"

# Dashboard

def dashboard():
    st.title("📊 Dashboard Admin / Editor")
    try:
        df = pd.read_csv("data_komentar.csv", names=["Waktu", "Nama", "Platform", "Pelayanan", "Komentar", "Sentimen"])

        # Filter
        df["Waktu"] = pd.to_datetime(df["Waktu"])
        st.sidebar.markdown("### Filter Data")
        start_date = st.sidebar.date_input("Dari Tanggal", df["Waktu"].min().date())
        end_date = st.sidebar.date_input("Sampai Tanggal", df["Waktu"].max().date())
        platform_filter = st.sidebar.multiselect("Pilih Platform", df["Platform"].unique(), default=list(df["Platform"].unique()))

        mask = (df["Waktu"].dt.date >= start_date) & (df["Waktu"].dt.date <= end_date) & (df["Platform"].isin(platform_filter))
        df_filtered = df[mask]

        # Tabel
        st.write("### Tabel Komentar")
        st.dataframe(df_filtered)

        # Ekspor
        st.download_button("📥 Unduh Data CSV", df_filtered.to_csv(index=False).encode('utf-8'), "data_komentar_filtered.csv", "text/csv")

        # Grafik Platform
        st.write("### Grafik Jumlah Komentar per Platform")
        st.bar_chart(df_filtered["Platform"].value_counts())

        # Grafik Sentimen
        st.write("### Grafik Sentimen Pelayanan")
        st.bar_chart(df_filtered["Sentimen"].value_counts())

        # Grafik Tren Waktu
        st.write("### Grafik Tren Komentar Harian")
        trend = df_filtered.groupby(df_filtered["Waktu"].dt.date).size()
        st.line_chart(trend)

        # Wordcloud
        st.write("### Wordcloud Komentar")
        text = " ".join(df_filtered["Komentar"].astype(str))
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)

        # Kata Negatif Teratas
        st.write("### Kata-kata Dominan dalam Komentar Negatif")
        negatif_words = " ".join(df_filtered[df_filtered["Sentimen"]=="Negatif"]["Komentar"].astype(str)).lower().split()
        common_neg = Counter(negatif_words).most_common(10)
        st.table(pd.DataFrame(common_neg, columns=["Kata", "Frekuensi"]))

        # Ranking Platform Positif
        st.write("### Peringkat Platform berdasarkan Komentar Positif")
        positive_platform = df_filtered[df_filtered["Sentimen"]=="Positif"]["Platform"].value_counts()
        st.bar_chart(positive_platform)

    except Exception as e:
        st.warning(f"Belum ada data komentar atau terjadi kesalahan: {e}")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_role = ""
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
