# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
nltk.download('vader_lexicon')

# Dummy login
USERNAME = "admin"
PASSWORD = "123"

if "page" not in st.session_state:
    st.session_state.page = "home"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Analisis Sentimen
def analyze_sentiment(comment):
    sia = SentimentIntensityAnalyzer()
    score = sia.polarity_scores(comment)["compound"]
    if score >= 0.05:
        return "Positif"
    elif score <= -0.05:
        return "Negatif"
    else:
        return "Netral"

# Halaman Utama
def home():
    st.title("📌 Analisis Sentimen Pelayanan SAMSAT")
    st.write("Silakan pilih menu:")
    if st.button("📝 Isi Komentar"):
        st.session_state.page = "form"
    if st.button("🔐 Masuk Dashboard (Admin)"):
        st.session_state.page = "login"

# Form Komentar
def form():
    st.title("🗣️ Form Komentar Publik")
    name = st.text_input("Nama")
    comment = st.text_area("Komentar")
    if st.button("Kirim"):
        sentiment = analyze_sentiment(comment)
        data = {"Nama": name, "Komentar": comment, "Sentimen": sentiment}
        df = pd.DataFrame([data])
        try:
            df.to_csv("data_komentar.csv", mode="a", header=False, index=False)
        except:
            df.to_csv("data_komentar.csv", index=False)
        st.session_state.latest_result = data
        st.session_state.page = "thanks"

# Hasil Terima Kasih
def thanks():
    st.title("✅ Terima Kasih")
    result = st.session_state.latest_result
    st.write(f"**Nama:** {result['Nama']}")
    st.write(f"**Komentar:** {result['Komentar']}")
    st.write(f"**Sentimen:** {result['Sentimen']}")
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
        df = pd.read_csv("data_komentar.csv", names=["Nama", "Komentar", "Sentimen"])
        st.write("### Tabel Komentar")
        st.dataframe(df)

        # Grafik Bar
        st.write("### Distribusi Sentimen")
        chart = df["Sentimen"].value_counts()
        st.bar_chart(chart)

        # Wordcloud
        st.write("### Wordcloud Komentar")
        text = " ".join(df["Komentar"].astype(str))
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)

        # Insight Sederhana
        st.write("### Insight:")
        st.write("- Komentar positif menandakan pelayanan memuaskan.")
        st.write("- Komentar negatif perlu ditindaklanjuti.")
    except:
        st.warning("Belum ada data komentar.")
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
