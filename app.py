import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# SAYFA VE TEMA AYARLARI
# ==========================================
st.set_page_config(page_title="Risk Terminali | BIST & EMTIA/KRIPTO", layout="wide", initial_sidebar_state="expanded")
plt.style.use('dark_background')

st.title("Portföy & Risk Terminali")
st.markdown("---")

# ==========================================
# GİZLİ SÖZLÜK (Otomatik BIST 100 + Kripto/Emtia)
# ==========================================
# BIST 100 Hisseleri (Temiz İsimler)
BIST_100 = [
    "AEFES", "AGHOL", "AHGAZ", "AKBNK", "AKCNS", "AKFGY", "AKSA", "AKSEN", "ALARK", "ALBRK",
    "ALFAS", "ARCLK", "ASELS", "ASTOR", "BERA", "BIENY", "BIMAS", "BRSAN", "BRYAT", "BUCIM",
    "CANTE", "CCOLA", "CEMTS", "CIMSA", "CWENE", "DOAS", "DOHOL", "ECILC", "EGEEN", "EKGYO",
    "ENJSA", "ENKAI", "EREGL", "EUPWR", "EUREN", "FROTO", "GARAN", "GENIL", "GESAN", "GLYHO",
    "GUBRF", "GWIND", "HALKB", "HEKTS", "IMASM", "INDES", "INVEO", "ISCTR", "ISGYO", "ISMEN",
    "IZENR", "KALES", "KARSN", "KCAER", "KCHOL", "KLSER", "KMPUR", "KONTR", "KONYA", "KOZAA",
    "KOZAL", "KRDMD", "KZBGY", "MAVI", "MGROS", "MIATK", "ODAS", "OTKAR", "OYAKC", "PENTA",
    "PETKM", "PGSUS", "PNLSN", "QUAGR", "SAHOL", "SASA", "SAYAS", "SISE", "SKBNK", "SMRTG",
    "SOKM", "TABGD", "TAVHL", "TCELL", "THYAO", "TKFEN", "TOASO", "TSKB", "TTKOM", "TTRAK",
    "TUKAS", "TUPRS", "ULKER", "VAKBN", "VESBE", "VESTL", "YEOTK", "YKBNK", "YYLGD", "ZOREN"
]

ASSET_MAP = {hisse: f"{hisse}.IS" for hisse in BIST_100}

ASSET_MAP.update({
    "Altın (ONS)": "GLD", 
    "Gümüş (ONS)": "SLV",
    "Petrol": "USO",
})

DISPLAY_NAMES = sorted(list(ASSET_MAP.keys()))

# ==========================================
# 1. YAN MENÜ: DİNAMİK AÇILIR MENÜ (UI)
# ==========================================
st.sidebar.header("Portföy Yönetimi")

selected_display_names = st.sidebar.multiselect(
    "Varlık Seçiniz (Arayabilir veya kaydırabilirsiniz):",
    options=DISPLAY_NAMES,
    default=[]
)

if len(selected_display_names) < 2:
    st.error("Korelasyon ve risk analizi yapabilmek için lütfen menüden en az 2 farklı varlık seçiniz.")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.subheader("Yatırım Tutarları (TRY)")

investments = {}
for name in selected_display_names:
    investments[name] = st.sidebar.number_input(f"{name} Yatırımı", min_value=0, value=10000, step=1000)

# ==========================================
# 2. VERİ ÇEKME VE GİZLİ DÖNÜŞÜM 
# ==========================================
active_display_names = [n for n, v in investments.items() if v > 0]
initial_investment = sum(investments.values())

if initial_investment == 0:
    st.warning("Lütfen portföye en az bir varlık için sıfırdan büyük bir yatırım tutarı giriniz.")
    st.stop()

real_tickers_to_fetch = [ASSET_MAP[n] for n in active_display_names]

@st.cache_data
def fetch_data(ticker_list):
    if len(ticker_list) == 1:
        data = yf.download(ticker_list[0], start="2010-01-01", progress=False)
        col = 'Adj Close' if 'Adj Close' in data.columns else 'Close'
        return data[col].to_frame(name=ticker_list[0])
    else:
        data = yf.download(ticker_list, start="2010-01-01", progress=False)
        col = 'Adj Close' if 'Adj Close' in data.columns else 'Close'
        return data[col]

raw_prices = fetch_data(real_tickers_to_fetch)

if isinstance(raw_prices, pd.Series):
    raw_prices = raw_prices.to_frame()

reverse_map = {ASSET_MAP[k]: k for k in active_display_names}
prices = raw_prices.rename(columns=reverse_map)

valid_names = [n for n in active_display_names if n in prices.columns and not prices[n].dropna().empty]

if not valid_names:
    st.error("Seçilen varlıklar için veri bulunamadı.")
    st.stop()

prices = prices[valid_names] 
current_prices = prices.dropna()
current_returns = np.log(current_prices / current_prices.shift(1)).dropna()

if current_returns.empty:
    st.error("Seçtiğiniz varlıkların ortak işlem gördüğü bir tarih bulunamadı. Lütfen listeyi değiştirin.")
    st.stop()

# ==========================================
# 3. VaR HESAPLAMA MOTORU
# ==========================================
valid_investment = sum(investments[n] for n in valid_names)
weights_array = np.array([investments[n] / valid_investment for n in current_returns.columns])
portfolio_daily_returns = current_returns.dot(weights_array)

# ==========================================
# SEKMELİ YAPI (TABS)
# ==========================================
tab1, tab2, tab3 = st.tabs(["VaR & Risk Profili", "Korelasyon & Çeşitlendirme", "Stres Testleri"])

# ------------------------------------------
# SEKME 1: VaR ANALİZİ
# ------------------------------------------
with tab1:
    var_99_percentage = np.percentile(portfolio_daily_returns, 1)
    var_99_value = valid_investment * var_99_percentage

    col1, col2, col3 = st.columns(3)
    col1.metric("Geçerli Portföy Büyüklüğü", f"₺ {valid_investment:,.0f}")
    col2.metric("Maksimum Beklenen Kayıp (99% VaR)", f"₺ {var_99_value:,.0f}", f"% {var_99_percentage*100:.2f}", delta_color="inverse")
    col3.metric("Normal Gün İhtimali", "%99")

    st.markdown("---")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.hist(portfolio_daily_returns, bins=80, alpha=0.7, color='#1f77b4', edgecolor='black')
    ax.axvline(x=var_99_percentage, color='#ff4b4b', linestyle='dashed', linewidth=2, label=f'VaR (%1 Eşik): %{var_99_percentage*100:.2f}')
    ax.set_title("Günlük Portföy Getirileri Dağılımı", color='white')
    ax.set_xlabel("Günlük Getiri", color='white')
    ax.set_ylabel("Frekans", color='white')
    ax.legend()
    ax.grid(True, alpha=0.1)
    st.pyplot(fig)

# ------------------------------------------
# SEKME 2: KORELASYON VE ÇEŞİTLENDİRME
# ------------------------------------------
with tab2:
    st.subheader("Portföy Çeşitlendirme Analizi")
    ind_vars = []
    for n in valid_names:
        t_var_pct = np.percentile(current_returns[n], 1)
        ind_vars.append(investments[n] * t_var_pct)
    
    sum_individual_var = sum(ind_vars)
    diversification_benefit = abs(sum_individual_var) - abs(var_99_value)
    
    d_col1, d_col2, d_col3 = st.columns(3)
    d_col1.metric("Ayrık Toplam Risk", f"-₺ {abs(sum_individual_var):,.0f}")
    d_col2.metric("Portföy Riski", f"-₺ {abs(var_99_value):,.0f}")
    d_col3.metric("Çeşitlendirme Faydası", f"+₺ {diversification_benefit:,.0f}", delta_color="normal")
    
    st.markdown("---")
    st.subheader("Varlık Korelasyon Matrisi")
    corr_matrix = current_returns.corr()
    st.dataframe(corr_matrix.style.background_gradient(cmap='coolwarm', axis=None).format("{:.2f}"), use_container_width=True)

# ------------------------------------------
# SEKME 3: STRES TESTLERİ
# ------------------------------------------
with tab3:
    st.subheader("Tarihsel Çöküş Senaryoları")
    
    # Kriz dönemi başlangıç tarihleri BIST'e ve Kriptolara uyumlu olarak ayarlandı
    crash_scenarios = {
        "2018 Rahip Brunson Krizi": {"start": "2018-01-01", "end": "2018-08-31"},
        "2020 Covid-19 Çöküşü": {"start": "2020-02-20", "end": "2020-03-23"},
        "2021 KKM Döviz Krizi": {"start": "2021-03-19", "end": "2021-03-24"}
    }

    prices.index = pd.to_datetime(prices.index)

    for scenario_name, dates in crash_scenarios.items():
        start_dt = pd.to_datetime(dates["start"])
        end_dt = pd.to_datetime(dates["end"])
        
        mask = (prices.index >= start_dt) & (prices.index <= end_dt)
        crash_prices = prices.loc[mask].dropna(axis=1, how='all')
        
        if crash_prices.empty or crash_prices.shape[1] == 0:
            st.warning(f"[{scenario_name}] Portföyünüzdeki varlıklar bu tarihte işleme açık değildi.")
            continue
            
        crash_returns = np.log(crash_prices / crash_prices.shift(1)).dropna()
        if crash_returns.empty:
            continue

        scenario_active_names = crash_returns.columns.tolist()
        scenario_active_investment = sum(investments[n] for n in scenario_active_names)
        scenario_active_weights = np.array([investments[n] / scenario_active_investment for n in scenario_active_names])
        
        crash_portfolio_returns = crash_returns.dot(scenario_active_weights)
        cumulative_percentage_loss = np.exp(crash_portfolio_returns.sum()) - 1
        monetary_loss = valid_investment * cumulative_percentage_loss
        
        missing_names = [n for n in valid_names if n not in scenario_active_names]
        
        with st.expander(f"{scenario_name} ({dates['start']} - {dates['end']})", expanded=True):
            st.metric("Portföy Etkisi", f"₺ {monetary_loss:,.0f}", f"% {cumulative_percentage_loss*100:.2f}", delta_color="inverse")
            if missing_names:
                st.caption(f"Bilgi: {', '.join(missing_names)} o dönemde piyasada olmadığı için teste dahil edilmedi.")