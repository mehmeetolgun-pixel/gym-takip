import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="OLGUN CRM", layout="wide", page_icon="💪")

# --- GÜVENLİ GİRİŞ SİSTEMİ (Basit Şifreleme) ---
def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        if st.session_state["password"] == st.secrets["PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Şifreyi hemen sil
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # İlk açılış, şifre sor
        st.text_input("Lütfen Şifre Giriniz", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # Yanlış şifre
        st.text_input("Lütfen Şifre Giriniz", type="password", on_change=password_entered, key="password")
        st.error("😕 Yanlış şifre")
        return False
    else:
        # Doğru şifre
        return True

if not check_password():
    st.stop()  # Şifre yanlışsa aşağıyı çalıştırma

# --- CSS TASARIMI (DARK MODE) ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: white; }
    [data-testid="stSidebar"] { background-color: #262730; }
    .css-card { background-color: #1E1E1E; padding: 20px; border-radius: 10px; border: 1px solid #333; }
    div[data-testid="metric-container"] { background-color: #1A1C24; border: 1px solid #333; border-radius: 10px; padding: 10px; }
    div[data-testid="metric-container"] label { color: #9CA3AF; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #4ADE80; font-size: 24px; }
    div.stButton > button { background-color: #22C55E; color: black; font-weight: bold; border: none; }
</style>
""", unsafe_allow_html=True)

# --- VERİTABANI BAĞLANTISI (GOOGLE SHEETS) ---
# "gsheets" ismini secrets.toml dosyasında tanımlayacağız
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    # Cache süresini 0 yapıyoruz ki her girişte güncel veri gelsin
    return conn.read(worksheet="Sayfa1", ttl=0)

def save_data(df):
    conn.update(worksheet="Sayfa1", data=df)

# --- VERİLERİ ÇEK ---
try:
    df = load_data()
    # Tarih formatını düzelt
    if not df.empty:
        df["Tarih"] = pd.to_datetime(df["Tarih"])
except Exception as e:
    st.error(f"Veri çekilemedi. İnternet bağlantınızı kontrol edin. Hata: {e}")
    df = pd.DataFrame()

# --- SABİT AYARLAR (Basitlik için kod içine gömüldü, istenirse bu da Sheet'e taşınabilir) ---
STAFF_LIST = ["Ahmet", "Mehmet", "Ayşe", "Fatma", "Oğuz", "Yönetici"]
CLUB_TARGET = 500000

# --- YAN MENÜ ---
with st.sidebar:
    st.header("OLGUN CRM")
    st.success("🟢 Online")
    menu = st.radio("MENÜ", ["📊 Genel Bakış", "📝 Veri Girişi", "📑 Raporlar"])
    if st.button("Çıkış Yap"):
        st.session_state["password_correct"] = False
        st.rerun()

# --- SAYFA 1: GENEL BAKIŞ ---
if menu == "📊 Genel Bakış":
    st.title("Genel Durum")
    if df.empty:
        st.info("Veri yok.")
    else:
        # KPI
        total_ciro = df["Tahsilat"].sum()
        kalan = CLUB_TARGET - total_ciro
        yuzde = (total_ciro / CLUB_TARGET)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Ciro", f"{total_ciro:,.0f} ₺")
        c2.metric("Hedef", f"{CLUB_TARGET:,.0f} ₺")
        c3.metric("Kalan", f"{kalan:,.0f} ₺")
        st.progress(min(yuzde, 1.0))
        
        # Grafik
        st.subheader("Günlük Ciro")
        daily = df.groupby("Tarih")["Tahsilat"].sum().reset_index()
        fig = px.area(daily, x="Tarih", y="Tahsilat", template="plotly_dark")
        fig.update_traces(line_color="#4ADE80")
        st.plotly_chart(fig, use_container_width=True)

# --- SAYFA 2: VERİ GİRİŞİ ---
elif menu == "📝 Veri Girişi":
    st.title("Veri Girişi")
    with st.form("entry"):
        c1, c2 = st.columns(2)
        d_val = c1.date_input("Tarih", datetime.now())
        p_val = c2.selectbox("Personel", STAFF_LIST)
        
        st.divider()
        wg, ws = st.columns(2)[0].number_input("Walkin Gelen", min_value=0), st.columns(2)[1].number_input("Walkin Satış", min_value=0)
        rg, rs = st.columns(2)[0].number_input("Referans Gelen", min_value=0), st.columns(2)[1].number_input("Referans Satış", min_value=0)
        tahsilat = st.number_input("TOPLAM TAHSİLAT (TL)", min_value=0.0)
        
        # Diğer alanlar basitlik için özetlendi, tamamını ekleyebilirsiniz
        
        if st.form_submit_button("KAYDET"):
            new_row = pd.DataFrame([{
                "Tarih": d_val.strftime("%Y-%m-%d"),
                "Personel": p_val,
                "Walkin_Gelen": wg, "Walkin_Satis": ws,
                "Referans_Gelen": rg, "Referans_Satis": rs,
                # Diğer sütunları 0 veya girilen değer yapın
                "Dis_Arama_Gelen":0, "Dis_Arama_Satis":0,
                "Sosyal_Gelen":0, "Sosyal_Satis":0,
                "Web_Gelen":0, "Web_Satis":0,
                "Aktif_Yenileme":0, "Pasif_Yenileme":0,
                "Tahsilat": tahsilat
            }])
            
            updated_df = pd.concat([df, new_row], ignore_index=True)
            save_data(updated_df)
            st.success("✅ Google Sheets'e Kaydedildi!")
            st.rerun()

# --- SAYFA 3: RAPORLAR ---
elif menu == "📑 Raporlar":
    st.title("Raporlar")
    st.dataframe(df, use_container_width=True)