import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="OLGUN CRM", layout="wide", page_icon="💪")

# --- 🔒 GÜVENLİK (ŞİFRE KONTROLÜ) ---
def check_password():
    """Returns `True` if the user had a correct password."""
    def password_entered():
        if st.session_state["password"] == st.secrets["PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Şifreyi temizle
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<h1 style='text-align: center;'>🔒 Giriş Paneli</h1>", unsafe_allow_html=True)
        st.text_input("Şifre", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("<h1 style='text-align: center;'>🔒 Giriş Paneli</h1>", unsafe_allow_html=True)
        st.text_input("Şifre", type="password", on_change=password_entered, key="password")
        st.error("😕 Yanlış şifre")
        return False
    else:
        return True

if not check_password():
    st.stop() # Şifre yanlışsa dur

# --- ☁️ GOOGLE SHEETS BAĞLANTISI ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # Cache süresini 0 yapıyoruz ki anlık güncellensin
        df = conn.read(worksheet="Sayfa1", ttl=0)
        # Tarih formatını düzelt
        if not df.empty and "Tarih" in df.columns:
            df["Tarih"] = pd.to_datetime(df["Tarih"])
        return df
    except Exception as e:
        # Eğer dosya boşsa boş bir taslak döndür
        return pd.DataFrame(columns=[
            "Tarih", "Personel", 
            "Walkin_Gelen", "Walkin_Satis", 
            "Referans_Gelen", "Referans_Satis",
            "Dis_Arama_Gelen", "Dis_Arama_Satis", 
            "Sosyal_Gelen", "Sosyal_Satis",
            "Web_Gelen", "Web_Satis",
            "Aktif_Yenileme", "Pasif_Yenileme", 
            "Tahsilat"
        ])

def save_data_to_cloud(df):
    conn.update(worksheet="Sayfa1", data=df)

# --- AYARLAR (Personel ve Hedef) ---
# Not: Online sistemde ayarları basit tutmak için şimdilik liste kullanıyoruz.
# İleride bunları da Google Sheet'te ayrı bir sayfaya kaydedebiliriz.
if "staff_list" not in st.session_state:
    st.session_state.staff_list = ["Ahmet", "Mehmet", "Ayşe", "Yönetici"] # Varsayılanlar
    
if "club_target" not in st.session_state:
    st.session_state.club_target = 500000

# --- MODERN DARK TEMA (SENİN BEĞENDİĞİN TASARIM) ---
st.markdown("""
<style>
    /* 1. TÜM ARKA PLAN (KOYU) */
    .stApp {
        background-color: #0E1117 !important;
        color: #FAFAFA !important;
    }
    
    /* 2. YAN MENÜ */
    [data-testid="stSidebar"] {
        background-color: #262730 !important;
        border-right: 1px solid #333333;
    }
    
    /* 3. KART TASARIMI */
    .css-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #333;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }
    
    /* 4. METRİK KUTULARI */
    div[data-testid="metric-container"] {
        background-color: #1A1C24 !important;
        border: 1px solid #333 !important;
        padding: 15px;
        border-radius: 10px;
    }
    div[data-testid="metric-container"] label {
        color: #9CA3AF !important; 
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #4ADE80 !important; 
        font-size: 26px !important;
    }
    
    /* 5. INPUT ALANLARI */
    .stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #262730 !important;
        color: white !important;
        border: 1px solid #4B5563 !important;
    }
    
    /* 6. TABLOLAR */
    [data-testid="stDataFrame"] {
        background-color: #1A1C24 !important;
        border-radius: 10px;
        border: 1px solid #333;
    }
    
    /* 7. BUTONLAR */
    div.stButton > button {
        background-color: #22C55E !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: none;
        border-radius: 6px;
    }
    div.stButton > button:hover {
        background-color: #16A34A !important;
        color: white !important;
    }
    
    /* 8. GENEL YAZILAR */
    h1, h2, h3, h4 { color: #FFFFFF !important; }
    p, span, div { color: #E5E7EB; }
</style>
""", unsafe_allow_html=True)

# --- VERİLERİ ÇEK ---
df = load_data()
staff_list = st.session_state.staff_list
club_target = st.session_state.club_target

# --- YAN MENÜ ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #4ADE80;'>OLGUN</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #9CA3AF; font-size: 0.8rem;'>CRM Paneli (Online)</p>", unsafe_allow_html=True)
    st.markdown("---")
    selected = st.radio("MENÜ", ["📊 Genel Bakış", "👤 Bireysel Analiz", "📝 Veri Girişi", "📑 Raporlar", "⚙️ Ayarlar"])
    st.markdown("---")
    st.caption("🟢 Sistem Online")
    if st.button("Çıkış Yap"):
        st.session_state["password_correct"] = False
        st.rerun()

# --- SAYFA 1: GENEL BAKIŞ ---
if selected == "📊 Genel Bakış":
    st.title("Genel Performans")
    
    if df.empty:
        st.warning("Veri yok. Lütfen giriş yapınız.")
    else:
        # KPI
        toplam_ciro = df["Tahsilat"].sum()
        kalan = club_target - toplam_ciro
        yuzde = (toplam_ciro / club_target) * 100 if club_target > 0 else 0
        
        k1, k2, k3 = st.columns(3)
        k1.metric("TOPLAM CİRO", f"{toplam_ciro:,.0f} ₺")
        k2.metric("HEDEF", f"{club_target:,.0f} ₺")
        k3.metric("KALAN", f"{kalan:,.0f} ₺", delta=f"%{yuzde:.1f}", delta_color="normal")
        
        st.write("")
        
        # --- KAYNAK ANALİZİ (TÜM EKİP) ---
        st.subheader("🎯 Kaynak Dönüşüm Oranları")
        st.markdown("<div style='background-color:#1A1C24; padding:15px; border-radius:10px; border:1px solid #333;'>", unsafe_allow_html=True)
        
        sources = [
            ("Walk-in", "Walkin_Gelen", "Walkin_Satis"),
            ("Referans", "Referans_Gelen", "Referans_Satis"),
            ("Dış Arama", "Dis_Arama_Gelen", "Dis_Arama_Satis"),
            ("Sosyal Medya", "Sosyal_Gelen", "Sosyal_Satis"),
            ("Web Sitesi", "Web_Gelen", "Web_Satis")
        ]
        
        s_data = []
        for name, cg, cs in sources:
            tg = df[cg].sum()
            ts = df[cs].sum()
            ratio = (ts / tg * 100) if tg > 0 else 0
            s_data.append({"Kanal": name, "Gelen": int(tg), "Satış": int(ts), "Başarı %": ratio})
            
        st.dataframe(
            pd.DataFrame(s_data),
            column_config={
                "Başarı %": st.column_config.ProgressColumn("Dönüşüm", format="%.1f%%", min_value=0, max_value=100)
            },
            use_container_width=True, hide_index=True
        )
        st.markdown("</div>", unsafe_allow_html=True)
        st.write("")

        # EKİP TABLOSU & WHATSAPP
        c_main, c_side = st.columns([2, 1])
        
        cols_num = df.select_dtypes(include=['number']).columns
        cols_all = ["Personel"] + list(cols_num)
        summ = df[cols_all].groupby("Personel").sum().reset_index()
        summ["TopSatis"] = (summ["Walkin_Satis"] + summ["Referans_Satis"] + summ["Dis_Arama_Satis"] + summ["Sosyal_Satis"] + summ["Web_Satis"] + summ["Aktif_Yenileme"] + summ["Pasif_Yenileme"])
        
        max_c = summ["Tahsilat"].max()
        summ["Personel_G"] = summ.apply(lambda x: f"👑 {x['Personel']}" if x['Tahsilat'] == max_c and max_c > 0 else x['Personel'], axis=1)

        with c_main:
            st.subheader("🏆 Liderlik Tablosu")
            st.dataframe(
                summ[["Personel_G", "Tahsilat", "TopSatis"]],
                column_config={"Personel_G": "Personel", "Tahsilat": st.column_config.NumberColumn("Ciro", format="%.0f ₺")},
                use_container_width=True, hide_index=True
            )
            
        with c_side:
            st.subheader("📱 WhatsApp Rapor")
            with st.container():
                st.markdown("<div style='background-color:#1A1C24; padding:10px; border-radius:10px;'>", unsafe_allow_html=True)
                rd = st.date_input("Tarih", datetime.now())
                df['Tarih'] = pd.to_datetime(df['Tarih'])
                ddf = df[df['Tarih'].dt.date == rd].copy()
                
                if not ddf.empty:
                    dsum = ddf[cols_all].groupby("Personel").sum().reset_index()
                    dsum["GS"] = (dsum["Walkin_Satis"] + dsum["Referans_Satis"] + dsum["Dis_Arama_Satis"] + dsum["Sosyal_Satis"] + dsum["Web_Satis"] + dsum["Aktif_Yenileme"] + dsum["Pasif_Yenileme"])
                    dsum["GG"] = (dsum["Walkin_Gelen"] + dsum["Referans_Gelen"] + dsum["Dis_Arama_Gelen"] + dsum["Sosyal_Gelen"] + dsum["Web_Gelen"])
                    
                    txt = f"📅 *{rd.strftime('%d.%m')} OLGUN RAPOR*\n💰 Ciro: {ddf['Tahsilat'].sum():,.0f} TL\n✅ Satış: {int(dsum['GS'].sum())} Adet\n---\n"
                    for _, r in dsum.iterrows():
                        txt += f"👤 {r['Personel']}: {int(r['GG'])} Gör / {int(r['GS'])} Satış\n"
                    st.text_area("Kopyala:", txt, height=150)
                else:
                    st.info("Kayıt yok.")
                st.markdown("</div>", unsafe_allow_html=True)

# --- SAYFA 2: BİREYSEL ANALİZ ---
elif selected == "👤 Bireysel Analiz":
    st.title("Bireysel Performans Analizi")
    
    if df.empty:
        st.warning("Veri yok.")
    else:
        # Personel Seçimi
        personels = df["Personel"].unique()
        # Eğer veri yoksa ve personel listesi boşsa hata vermesin
        if len(personels) > 0:
            selected_p = st.selectbox("Personel Seçiniz:", personels)
            
            # Filtrele
            p_df = df[df["Personel"] == selected_p].copy()
            
            if not p_df.empty:
                # Toplamlar
                p_total_ciro = p_df["Tahsilat"].sum()
                
                # Kanal Bazlı Toplamlar
                channels = {
                    "Walk-in": ("Walkin_Gelen", "Walkin_Satis"),
                    "Referans": ("Referans_Gelen", "Referans_Satis"),
                    "Dış Arama": ("Dis_Arama_Gelen", "Dis_Arama_Satis"),
                    "Sosyal Medya": ("Sosyal_Gelen", "Sosyal_Satis"),
                    "Web": ("Web_Gelen", "Web_Satis")
                }
                
                p_stats = []
                for name, (cg, cs) in channels.items():
                    g = p_df[cg].sum()
                    s = p_df[cs].sum()
                    r = (s/g*100) if g > 0 else 0
                    p_stats.append({"Kanal": name, "Gelen": g, "Satış": s, "Oran": r})
                
                df_p_stats = pd.DataFrame(p_stats)
                total_sales = df_p_stats["Satış"].sum() + p_df["Aktif_Yenileme"].sum() + p_df["Pasif_Yenileme"].sum()
                
                # En İyi Kanalı Bul
                best_channel = df_p_stats.loc[df_p_stats["Satış"].idxmax()]["Kanal"] if not df_p_stats.empty and df_p_stats["Satış"].sum() > 0 else "-"
                
                # ÜST KARTLAR
                col1, col2, col3 = st.columns(3)
                col1.metric("Toplam Ciro", f"{p_total_ciro:,.0f} ₺")
                col2.metric("Toplam Satış Adedi", f"{int(total_sales)}")
                col3.metric("En Güçlü Kanal", best_channel)
                
                st.write("---")
                
                # GRAFİKLER
                g1, g2 = st.columns(2)
                
                with g1:
                    st.subheader("📊 Kanal Dönüşüm Grafiği")
                    # Grouped Bar Chart
                    fig_bar = go.Figure()
                    fig_bar.add_trace(go.Bar(x=df_p_stats["Kanal"], y=df_p_stats["Gelen"], name='Gelen (Potansiyel)', marker_color='#60A5FA'))
                    fig_bar.add_trace(go.Bar(x=df_p_stats["Kanal"], y=df_p_stats["Satış"], name='Satış (Kapanan)', marker_color='#4ADE80'))
                    fig_bar.update_layout(barmode='group', template="plotly_dark", height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_bar, use_container_width=True)
                    
                with g2:
                    st.subheader("🥧 Satış Dağılımı")
                    # Pie Chart (Sadece satışlar)
                    fig_pie = px.pie(df_p_stats, values='Satış', names='Kanal', template="plotly_dark", hole=0.4)
                    fig_pie.update_traces(textinfo='percent+label')
                    fig_pie.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                st.write("---")
                st.subheader("📈 Günlük Ciro Trendi")
                p_daily = p_df.groupby("Tarih")["Tahsilat"].sum().reset_index()
                fig_line = px.line(p_daily, x="Tarih", y="Tahsilat", template="plotly_dark", markers=True)
                fig_line.update_traces(line_color="#F59E0B")
                fig_line.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.info("Bu personele ait veri yok.")
        else:
            st.info("Henüz veri girişi yapılmamış.")

# --- SAYFA 3: VERİ GİRİŞİ ---
elif selected == "📝 Veri Girişi":
    st.title("Günlük Giriş")
    if not staff_list:
        st.error("Personel ekleyiniz (Ayarlar).")
    else:
        with st.form("entry"):
            c1, c2 = st.columns(2)
            d_val = c1.date_input("Tarih", datetime.now())
            p_val = c2.selectbox("Personel", staff_list)
            st.markdown("---")
            
            h1, h2 = st.columns(2)
            h1.markdown("<h4 style='color:#60A5FA'>📥 POTANSİYEL</h4>", unsafe_allow_html=True)
            h2.markdown("<h4 style='color:#4ADE80'>✅ SATIŞ</h4>", unsafe_allow_html=True)
            
            def row(l, k):
                a, b = st.columns(2)
                v1 = a.number_input(f"{l} Gelen", min_value=0, key=f"{k}_g")
                v2 = b.number_input(f"{l} Satış", min_value=0, key=f"{k}_s")
                return v1, v2

            wg, ws = row("Walk-in", "w")
            rg, rs = row("Referans", "r")
            dg, ds = row("Dış Arama", "d")
            sg, ss = row("Sosyal Medya", "s")
            wbg, wbs = row("Web", "wb")
            
            st.markdown("---")
            f1, f2, f3 = st.columns(3)
            ay = f1.number_input("Aktif Yenileme", min_value=0)
            py = f2.number_input("Pasif Yenileme", min_value=0)
            tahsilat = f3.number_input("TOPLAM TAHSİLAT (TL)", min_value=0.0, step=100.0)
            
            if st.form_submit_button("KAYDET", use_container_width=True):
                # Yeni veriyi DataFrame olarak hazırla
                new_row = pd.DataFrame([{
                    "Tarih": d_val.strftime("%Y-%m-%d"),
                    "Personel": p_val,
                    "Walkin_Gelen": wg, "Walkin_Satis": ws,
                    "Referans_Gelen": rg, "Referans_Satis": rs,
                    "Dis_Arama_Gelen": dg, "Dis_Arama_Satis": ds,
                    "Sosyal_Gelen": sg, "Sosyal_Satis": ss,
                    "Web_Gelen": wbg, "Web_Satis": wbs,
                    "Aktif_Yenileme": ay, "Pasif_Yenileme": py,
                    "Tahsilat": tahsilat
                }])
                
                # Mevcut veriye ekle
                updated_df = pd.concat([df, new_row], ignore_index=True)
                
                # Buluta kaydet
                save_data_to_cloud(updated_df)
                st.success("✅ Google Sheets'e Başarıyla Kaydedildi!")
                st.rerun()

# --- SAYFA 4: RAPORLAR ---
elif selected == "📑 Raporlar":
    st.title("Raporlar")
    if not df.empty:
        pf = st.multiselect("Filtrele", df["Personel"].unique())
        sd = df[df["Personel"].isin(pf)] if pf else df
        st.dataframe(sd, use_container_width=True)
    else:
        st.info("Veri yok.")

# --- SAYFA 5: AYARLAR ---
elif selected == "⚙️ Ayarlar":
    st.title("Ayarlar")
    st.warning("⚠️ Not: Online versiyonda personel ve hedef ayarları geçicidir (sayfa yenilenince sıfırlanabilir).")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Hedef")
        nt = st.number_input("Hedef (TL)", value=club_target, step=5000)
        if st.button("Kaydet"):
            st.session_state.club_target = nt
            st.success("Tamam")
            st.rerun()
    with c2:
        st.subheader("Personel")
        np = st.text_input("Ekle")
        if st.button("Ekle"):
            if np and np not in st.session_state.staff_list:
                st.session_state.staff_list.append(np)
                st.success(f"{np} eklendi!")
                st.rerun()
        st.write("---")
        st.write("Mevcut Personel:")
        for s in staff_list:
            st.text(f"👤 {s}")
