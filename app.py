import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

# SAYFA VE TEMA AYARLARI

st.set_page_config(page_title="Risk Terminali | Global", layout="wide", initial_sidebar_state="expanded")
plt.style.use('dark_background')

st.title("Portföy & Risk Terminali")
st.markdown("---")

# VARLIK EVRENİ

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

CRYPTO = {
    "Bitcoin (BTC)": "BTC-USD", "Ethereum (ETH)": "ETH-USD", "Solana (SOL)": "SOL-USD",
    "XRP": "XRP-USD", "BNB": "BNB-USD", "Cardano (ADA)": "ADA-USD",
    "Dogecoin (DOGE)": "DOGE-USD", "Avalanche (AVAX)": "AVAX-USD",
    "Polkadot (DOT)": "DOT-USD", "Chainlink (LINK)": "LINK-USD"
}

US_STOCKS = {
    "Apple (AAPL)": "AAPL", "Microsoft (MSFT)": "MSFT", "Nvidia (NVDA)": "NVDA",
    "Alphabet (GOOGL)": "GOOGL", "Amazon (AMZN)": "AMZN", "Meta (META)": "META",
    "Tesla (TSLA)": "TSLA", "Berkshire (BRK-B)": "BRK-B", "JPMorgan (JPM)": "JPM",
    "Visa (V)": "V", "Johnson & Johnson (JNJ)": "JNJ", "Exxon (XOM)": "XOM",
    "Coca-Cola (KO)": "KO", "McDonald's (MCD)": "MCD", "Disney (DIS)": "DIS",
    "Netflix (NFLX)": "NFLX", "AMD": "AMD", "Intel (INTC)": "INTC",
    "Boeing (BA)": "BA", "Caterpillar (CAT)": "CAT", "Goldman Sachs (GS)": "GS",
    "Palantir (PLTR)": "PLTR", "Uber (UBER)": "UBER", "Coinbase (COIN)": "COIN"
}

COMMODITIES = {
    "Altın (ONS)": "GC=F", "Gümüş (ONS)": "SI=F", "Brent Petrol": "BZ=F",
    "WTI Petrol": "CL=F", "Doğalgaz": "NG=F", "Bakır": "HG=F"
}

INDICES = {
    "S&P 500": "^GSPC", "Nasdaq Composite": "^IXIC", "Nasdaq 100": "^NDX",
    "Dow Jones (DJIA)": "^DJI", "BIST 100": "XU100.IS", "BIST 30": "XU030.IS"
}

ASSET_INFO = {}
for h in BIST_100:
    ASSET_INFO[h] = {"ticker": f"{h}.IS", "cur": "TRY", "cat": "BIST"}
for n, t in CRYPTO.items():
    ASSET_INFO[n] = {"ticker": t, "cur": "USD", "cat": "Kripto"}
for n, t in US_STOCKS.items():
    ASSET_INFO[n] = {"ticker": t, "cur": "USD", "cat": "ABD Hisse"}
for n, t in COMMODITIES.items():
    ASSET_INFO[n] = {"ticker": t, "cur": "USD", "cat": "Emtia"}
for n, t in INDICES.items():
    ASSET_INFO[n] = {"ticker": t, "cur": "TRY" if t.endswith(".IS") else "USD", "cat": "Endeks"}

# TAHVİL HESAPLAMA MOTORU

def bond_metrics(coupon_rate, ytm, years, freq):
    n = max(int(round(years * freq)), 1)
    c = coupon_rate / freq * 100
    y = ytm / freq
    periods = np.arange(1, n + 1)
    times = periods / freq
    cfs = np.full(n, c, dtype=float)
    cfs[-1] += 100.0
    dfs = (1 + y) ** (-periods)
    pv = cfs * dfs
    fair_price = pv.sum()
    macaulay = (times * pv).sum() / fair_price
    modified = macaulay / (1 + y)
    return fair_price, macaulay, modified

# 1. YAN MENÜ

st.sidebar.header("Portföy Yönetimi")

categories = ["BIST", "Kripto", "ABD Hisse", "Emtia", "Endeks"]
selected_cats = st.sidebar.multiselect("Kategori Filtresi:", categories, default=categories)

filtered_names = sorted([n for n, i in ASSET_INFO.items() if i["cat"] in selected_cats])

selected_display_names = st.sidebar.multiselect(
    "Varlık Seçiniz:",
    options=filtered_names,
    default=[]
)

def custom_code_input(state_key, input_label, button_label, placeholder):
    if state_key not in st.session_state:
        st.session_state[state_key] = []
    text = st.text_input(input_label, placeholder=placeholder, key=f"in_{state_key}")
    if st.button(button_label, key=f"btn_{state_key}"):
        for code in [c.strip().upper() for c in text.split(",") if c.strip()]:
            if code not in st.session_state[state_key]:
                st.session_state[state_key].append(code)
        st.session_state[f"keep_{state_key}"] = st.session_state[state_key].copy()
    if st.session_state[state_key]:
        if f"keep_{state_key}" not in st.session_state:
            st.session_state[f"keep_{state_key}"] = st.session_state[state_key].copy()
        kept = st.multiselect("Eklenenler (kaldırmak için işareti silin):",
                              options=st.session_state[state_key],
                              key=f"keep_{state_key}")
        st.session_state[state_key] = list(kept)
    return st.session_state[state_key]

with st.sidebar.expander("Listede Olmayan Varlık Ekle"):
    bist_codes = custom_code_input("custom_bist", "BIST Kodu (virgülle ayırın)", "BIST Ekle", "ör: MPARK, EBEBK")
    global_codes = custom_code_input("custom_global", "Global Sembol (Yahoo formatı)", "Sembol Ekle", "ör: LLY, SHIB-USD")

for code in bist_codes:
    name = code.replace(".IS", "")
    if name not in ASSET_INFO:
        ASSET_INFO[name] = {"ticker": f"{name}.IS", "cur": "TRY", "cat": "BIST"}
    if name not in selected_display_names:
        selected_display_names.append(name)

for code in global_codes:
    if code not in ASSET_INFO:
        ASSET_INFO[code] = {"ticker": code, "cur": "USD", "cat": "Global"}
    if code not in selected_display_names:
        selected_display_names.append(code)

with st.sidebar.expander("TEFAS Fonu Ekle"):
    st.caption("Fon kodunu giriniz (ör: AFT, TCD, YAC). Veri TEFAS'tan çekilir, en fazla 5 yıl geriye gider.")
    fund_codes = custom_code_input("custom_tefas", "Fon Kodu (virgülle ayırın)", "Fon Ekle", "ör: AFT, MAC, TCD")

for code in fund_codes:
    name = f"{code} (Fon)"
    if name not in ASSET_INFO:
        ASSET_INFO[name] = {"ticker": code, "cur": "TRY", "cat": "TEFAS Fon"}
    if name not in selected_display_names:
        selected_display_names.append(name)

# POZİSYON GİRİŞİ

positions = {}
if selected_display_names:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Pozisyon Girişi")
    st.sidebar.caption("Adet ve maliyeti varlığın kendi para biriminde giriniz.")

    for name in selected_display_names:
        cur = ASSET_INFO[name]["cur"]
        st.sidebar.markdown(f"**{name}** ({cur})")
        c1, c2 = st.sidebar.columns(2)
        qty = c1.number_input("Adet", min_value=0.0, value=0.0, step=1.0, format="%.6f", key=f"q_{name}")
        cost_unknown = st.sidebar.checkbox("Maliyeti bilmiyorum", key=f"u_{name}")
        cost = c2.number_input(f"Maliyet ({cur})", min_value=0.0, value=0.0, step=1.0,
                               format="%.4f", key=f"c_{name}", disabled=cost_unknown)
        positions[name] = {"qty": qty, "cost": cost, "cost_unknown": cost_unknown}

# TAHVİL / BONO GİRİŞİ

st.sidebar.markdown("---")
st.sidebar.subheader("Tahvil / Bono")
bond_count = st.sidebar.number_input("Tahvil sayısı", min_value=0, max_value=5, value=0, step=1)

bond_inputs = []
for i in range(int(bond_count)):
    with st.sidebar.expander(f"Tahvil {i+1}", expanded=True):
        st.caption("Fiyatları 100 birim nominal başına giriniz. Örnek: 100 TL'lik tahvil 98,5 TL'den işlem görüyorsa 98.5 yazın.")
        b_name = st.text_input("İsim", value=f"Tahvil {i+1}", key=f"bn_{i}")
        b_cur = st.selectbox("Para Birimi", ["TRY", "USD"], key=f"bc_{i}")
        b_nominal = st.number_input(f"Nominal Tutar ({b_cur})", min_value=0.0, value=0.0, step=1000.0, key=f"bnom_{i}",
                                    help="Tahvilin üzerinde yazan anapara tutarı (vade sonunda geri alacağınız tutar).")
        b_price = st.number_input("Güncel Piyasa Fiyatı", min_value=0.0, value=100.0, step=0.1, format="%.3f", key=f"bp_{i}",
                                  help="Ekranda/aracı kurumda gördüğünüz kote fiyat. 100 nominal başına.")
        b_coupon = st.number_input("Yıllık Kupon Oranı (%)", min_value=0.0, value=0.0, step=0.25, format="%.2f", key=f"bk_{i}",
                                   help="Kuponsuz bono için 0 bırakın.")
        b_freq = st.selectbox("Kupon Sıklığı (yılda kaç ödeme)", [2, 1, 4], key=f"bf_{i}")
        b_years = st.number_input("Vadeye Kalan Süre (yıl)", min_value=0.05, value=2.0, step=0.25, format="%.2f", key=f"by_{i}")
        b_unknown = st.checkbox("Maliyeti bilmiyorum", key=f"bu_{i}")
        b_cost = st.number_input("Alış Fiyatınız", min_value=0.0, value=0.0, step=0.1,
                                 format="%.3f", key=f"bcost_{i}", disabled=b_unknown,
                                 help="Tahvili aldığınız fiyat, 100 nominal başına.")
        b_ytm = st.number_input("Vadeye Kadar Getiri - YTM (%)", min_value=0.0, value=40.0 if b_cur == "TRY" else 4.5,
                                step=0.25, format="%.2f", key=f"bytm_{i}",
                                help="Tahvilin güncel piyasa getirisi. Aracı kurum ekranında veya KAP'ta 'bileşik faiz' olarak görünür.")
        if b_nominal > 0:
            bond_inputs.append({
                "name": b_name, "cur": b_cur, "nominal": b_nominal, "price": b_price,
                "coupon": b_coupon / 100, "freq": b_freq, "years": b_years,
                "cost": b_cost, "cost_unknown": b_unknown,
                "ytm": b_ytm / 100
            })

active_names = [n for n, p in positions.items() if p["qty"] > 0]

if not active_names and not bond_inputs:
    st.error("Lütfen en az bir varlık seçip adet giriniz veya bir tahvil tanımlayınız.")
    st.stop()

# 2. VERİ ÇEKME

yahoo_names = [n for n in active_names if ASSET_INFO[n]["cat"] != "TEFAS Fon"]
tefas_names = [n for n in active_names if ASSET_INFO[n]["cat"] == "TEFAS Fon"]

tickers_to_fetch = {ASSET_INFO[n]["ticker"] for n in yahoo_names} | {"TRY=X"}

@st.cache_data(ttl=900)
def fetch_data(ticker_list):
    import time
    data = None
    for attempt in range(3):
        data = yf.download(list(ticker_list), start="2000-01-01", progress=False, auto_adjust=True)
        if data is not None and not data.empty:
            break
        time.sleep(2 * (attempt + 1))
    if data is None or data.empty:
        raise RuntimeError("Yahoo Finance veri döndürmedi.")
    close = data["Close"]
    if isinstance(close, pd.Series):
        close = close.to_frame(name=ticker_list[0])
    return close

@st.cache_data(ttl=3600)
def fetch_tefas(fund_codes):
    from tefas import Crawler
    crawler = Crawler()
    end = pd.Timestamp.today().normalize()
    start = end - pd.DateOffset(years=5) + pd.DateOffset(days=1)
    result = {}
    for code in fund_codes:
        series = None
        for kind in ["YAT", "EMK", "BYF"]:
            try:
                df = crawler.fetch(start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"),
                                   name=code, columns=["date", "price"], kind=kind)
                if df is not None and not df.empty:
                    s = df.set_index("date")["price"].astype(float)
                    s.index = pd.to_datetime(s.index)
                    s = s[s > 0]
                    series = s[~s.index.duplicated(keep="last")].sort_index()
                    break
            except Exception:
                continue
        result[code] = series
    return result

def data_error(message):
    st.error(message)
    st.caption("Yahoo Finance, özellikle Streamlit Cloud gibi paylaşımlı sunucularda istekleri geçici olarak sınırlayabilir. Genellikle 1-2 dakika içinde düzelir.")
    if st.button("Yeniden Dene"):
        st.cache_data.clear()
        st.rerun()
    st.stop()

try:
    raw_prices = fetch_data(tuple(sorted(tickers_to_fetch)))
except Exception:
    data_error("Piyasa verisi çekilemedi.")

raw_prices.index = pd.to_datetime(raw_prices.index)

if "TRY=X" not in raw_prices.columns or raw_prices["TRY=X"].dropna().empty:
    data_error("USD/TRY kuru çekilemedi. Kur olmadan TL bazlı analiz yapılamıyor.")

usdtry = raw_prices["TRY=X"].ffill()
fx_now = float(usdtry.dropna().iloc[-1])

prices_try = pd.DataFrame(index=raw_prices.index)
last_price_native = {}

valid_names = []
for name in yahoo_names:
    t = ASSET_INFO[name]["ticker"]
    if t not in raw_prices.columns or raw_prices[t].dropna().empty:
        st.warning(f"{name} için veri bulunamadı, analiz dışı bırakıldı.")
        continue
    series = raw_prices[t]
    last_price_native[name] = float(series.dropna().iloc[-1])
    if ASSET_INFO[name]["cur"] == "USD":
        prices_try[name] = series * usdtry
    else:
        prices_try[name] = series
    valid_names.append(name)

if tefas_names:
    try:
        fund_data = fetch_tefas(tuple(sorted(ASSET_INFO[n]["ticker"] for n in tefas_names)))
    except ImportError:
        fund_data = {}
        st.error("TEFAS fonları için 'tefas-crawler' kütüphanesi gerekli: pip install tefas-crawler")
    for name in tefas_names:
        s = fund_data.get(ASSET_INFO[name]["ticker"])
        if s is None or s.dropna().empty:
            st.warning(f"{name} için TEFAS'tan veri çekilemedi, analiz dışı bırakıldı. Fon kodunu kontrol edin.")
            continue
        last_price_native[name] = float(s.dropna().iloc[-1])
        prices_try = prices_try.join(s.rename(name), how="outer")
        valid_names.append(name)

current_returns = pd.DataFrame()
prices = pd.DataFrame()
if valid_names:
    prices = prices_try[valid_names]
    current_prices = prices.replace(0, np.nan).dropna()
    current_returns = np.log(current_prices / current_prices.shift(1)).replace([np.inf, -np.inf], np.nan).dropna()

# 3. TAHVİL DEĞERLEME

bonds = []
for b in bond_inputs:
    ytm = b["ytm"]
    fair_price, mac, mod = bond_metrics(b["coupon"], ytm, b["years"], b["freq"])
    fx = fx_now if b["cur"] == "USD" else 1.0
    value_native = b["nominal"] * b["price"] / 100
    cost_native = np.nan if b["cost_unknown"] or b["cost"] <= 0 else b["nominal"] * b["cost"] / 100
    bonds.append({**b, "ytm_used": ytm, "fair_price": fair_price,
                  "macaulay": mac, "modified": mod, "fx": fx,
                  "value_native": value_native, "cost_native": cost_native,
                  "value_try": value_native * fx})

# 4. PORTFÖY DEĞERLEME (TRY BAZLI)

rows = []
for name in valid_names:
    info = ASSET_INFO[name]
    p = positions[name]
    fx = fx_now if info["cur"] == "USD" else 1.0
    value_native = p["qty"] * last_price_native[name]
    if p["cost_unknown"] or p["cost"] <= 0:
        cost_native, pnl_native, pnl_pct = np.nan, np.nan, np.nan
    else:
        cost_native = p["qty"] * p["cost"]
        pnl_native = value_native - cost_native
        pnl_pct = pnl_native / cost_native * 100
    rows.append({
        "Varlık": name, "Kategori": info["cat"], "PB": info["cur"],
        "Adet": p["qty"], "Ort. Maliyet": np.nan if p["cost_unknown"] else p["cost"],
        "Güncel Fiyat": last_price_native[name],
        "Maliyet Tutarı": cost_native, "Güncel Değer": value_native,
        "K/Z": pnl_native, "K/Z %": pnl_pct,
        "Değer (TRY)": value_native * fx,
        "K/Z (TRY)": pnl_native * fx if not np.isnan(pnl_native) else np.nan
    })

for b in bonds:
    pnl_native = np.nan if np.isnan(b["cost_native"]) else b["value_native"] - b["cost_native"]
    pnl_pct = np.nan if np.isnan(pnl_native) or b["cost_native"] <= 0 else pnl_native / b["cost_native"] * 100
    rows.append({
        "Varlık": b["name"], "Kategori": "Tahvil", "PB": b["cur"],
        "Adet": b["nominal"], "Ort. Maliyet": np.nan if b["cost_unknown"] else b["cost"],
        "Güncel Fiyat": b["price"],
        "Maliyet Tutarı": b["cost_native"], "Güncel Değer": b["value_native"],
        "K/Z": pnl_native, "K/Z %": pnl_pct,
        "Değer (TRY)": b["value_try"],
        "K/Z (TRY)": pnl_native * b["fx"] if not np.isnan(pnl_native) else np.nan
    })

pf = pd.DataFrame(rows).set_index("Varlık")
total_value_try = pf["Değer (TRY)"].sum()
pf["Ağırlık %"] = pf["Değer (TRY)"] / total_value_try * 100

market_value_try = pf.loc[pf["Kategori"] != "Tahvil", "Değer (TRY)"].sum()
bond_value_try = sum(b["value_try"] for b in bonds)

investments = pf["Değer (TRY)"].to_dict()
portfolio_daily_returns = pd.Series(dtype=float)
if not current_returns.empty and market_value_try > 0:
    weights_array = np.array([investments[n] / market_value_try for n in current_returns.columns])
    portfolio_daily_returns = current_returns.dot(weights_array)

# SEKMELİ YAPI

tab0, tab1, tab2, tab3 = st.tabs(["Portföy Takip", "VaR & Risk Profili", "Korelasyon & Çeşitlendirme", "Stres Testleri"])

# SEKME 0: PORTFÖY TAKİP

with tab0:
    known = pf.dropna(subset=["Maliyet Tutarı"])
    total_cost_try = (known["Maliyet Tutarı"] * known["PB"].map({"USD": fx_now, "TRY": 1.0})).sum()
    total_pnl_try = known["K/Z (TRY)"].sum()
    total_pnl_pct = (total_pnl_try / total_cost_try * 100) if total_cost_try > 0 else 0.0
    unknown_names = pf.index[pf["Maliyet Tutarı"].isna()].tolist()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Toplam Değer", f"₺ {total_value_try:,.0f}")
    m2.metric("Toplam Maliyet (bilinen)", f"₺ {total_cost_try:,.0f}")
    m3.metric("Kar / Zarar (bilinen)", f"₺ {total_pnl_try:,.0f}", f"{total_pnl_pct:+.2f}%")
    m4.metric("USD/TRY Kuru", f"{fx_now:.2f}")

    if unknown_names:
        st.caption(f"Maliyeti bilinmeyen pozisyonlar K/Z hesabına dahil edilmedi ama risk analizine dahil: {', '.join(unknown_names)}")
    st.caption("Not: Dolar bazlı varlıkların maliyeti güncel kur ile TL'ye çevrilir; kur farkı kazancı K/Z'ye dahil değildir.")

    st.markdown("---")

    left, right = st.columns([3, 2])

    with left:
        st.subheader("Pozisyonlar")
        display_df = pf[["Kategori", "PB", "Adet", "Ort. Maliyet", "Güncel Fiyat", "Güncel Değer", "K/Z", "K/Z %", "Değer (TRY)", "Ağırlık %"]]
        st.dataframe(
            display_df.style
            .format({
                "Adet": "{:,.4f}", "Ort. Maliyet": "{:,.2f}", "Güncel Fiyat": "{:,.2f}",
                "Güncel Değer": "{:,.2f}", "K/Z": "{:,.2f}", "K/Z %": "{:+.2f}%",
                "Değer (TRY)": "₺{:,.0f}", "Ağırlık %": "{:.1f}%"
            }, na_rep="—")
            .map(lambda v: "color: #00cc96" if isinstance(v, (int, float)) and v > 0 else ("color: #ff4b4b" if isinstance(v, (int, float)) and v < 0 else ""), subset=["K/Z", "K/Z %"]),
            use_container_width=True
        )

    with right:
        st.subheader("Portföy Dağılımı")
        fig_pie = px.pie(
            pf.reset_index(), values="Değer (TRY)", names="Varlık", hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_traces(textinfo="percent+label")
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_pie, use_container_width=True)

        cat_alloc = pf.groupby("Kategori")["Değer (TRY)"].sum().reset_index()
        fig_cat = px.pie(cat_alloc, values="Değer (TRY)", names="Kategori", hole=0.45)
        fig_cat.update_traces(textinfo="percent+label")
        fig_cat.update_layout(paper_bgcolor="rgba(0,0,0,0)", showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_cat, use_container_width=True)

# SEKME 1: VaR & RİSK PROFİLİ

with tab1:
    if not portfolio_daily_returns.empty:
        var_99_percentage = np.percentile(portfolio_daily_returns, 1)
        var_99_value = market_value_try * var_99_percentage

        col1, col2, col3 = st.columns(3)
        col1.metric("Piyasa Riskine Tabi Tutar", f"₺ {market_value_try:,.0f}")
        col2.metric("Maksimum Beklenen Kayıp (99% VaR)", f"₺ {var_99_value:,.0f}", f"{var_99_percentage*100:+.2f}%", delta_color="normal")
        col3.metric("Normal Gün İhtimali", "%99")

        st.caption("Not: Tarihsel VaR yalnızca piyasa fiyat serisi olan varlıkları kapsar. Dolar bazlı seriler USD/TRY ile TL'ye çevrildiğinden kur riski dahildir. Tahvil faiz riski aşağıda durasyon ile ayrıca ölçülür.")

        st.markdown("---")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.hist(portfolio_daily_returns, bins=80, alpha=0.7, color='#1f77b4', edgecolor='black')
        ax.axvline(x=var_99_percentage, color='#ff4b4b', linestyle='dashed', linewidth=2, label=f'VaR (%1 Eşik): %{var_99_percentage*100:.2f}')
        ax.set_title("Günlük Portföy Getirileri Dağılımı (TRY Bazlı)", color='white')
        ax.set_xlabel("Günlük Getiri", color='white')
        ax.set_ylabel("Frekans", color='white')
        ax.legend()
        ax.grid(True, alpha=0.1)
        st.pyplot(fig)
    else:
        st.info("Portföyde piyasa fiyat serisi olan varlık bulunmadığı için tarihsel VaR hesaplanamadı.")

    if bonds:
        st.markdown("---")
        st.subheader("Tahvil Faiz Riski (Durasyon Analizi)")

        bond_rows = []
        for b in bonds:
            dv01 = b["modified"] * b["value_try"] * 0.0001
            bond_rows.append({
                "Tahvil": b["name"], "PB": b["cur"], "YTM %": b["ytm_used"] * 100,
                "Hesaplanan Fiyat": b["fair_price"],
                "Piyasa Fiyatı": b["price"], "Macaulay D.": b["macaulay"],
                "Modified D.": b["modified"], "DV01 (₺)": dv01, "Değer (TRY)": b["value_try"]
            })
        bond_df = pd.DataFrame(bond_rows).set_index("Tahvil")

        w_mod = (bond_df["Modified D."] * bond_df["Değer (TRY)"]).sum() / bond_value_try
        total_dv01 = bond_df["DV01 (₺)"].sum()
        pf_mod = w_mod * bond_value_try / total_value_try

        b1, b2, b3, b4 = st.columns(4)
        b1.metric("Tahvil Sepeti Değeri", f"₺ {bond_value_try:,.0f}")
        b2.metric("Ağırlıklı Modified Duration", f"{w_mod:.2f} yıl")
        b3.metric("Toplam DV01", f"₺ {total_dv01:,.0f}")
        b4.metric("Portföy Düzeyi Duration Katkısı", f"{pf_mod:.2f} yıl")

        st.dataframe(
            bond_df.style.format({
                "YTM %": "{:.2f}", "Hesaplanan Fiyat": "{:.3f}", "Piyasa Fiyatı": "{:.3f}",
                "Macaulay D.": "{:.3f}", "Modified D.": "{:.3f}",
                "DV01 (₺)": "₺{:,.2f}", "Değer (TRY)": "₺{:,.0f}"
            }),
            use_container_width=True
        )

        st.markdown("**Faiz Şoku Senaryoları (paralel kayma, durasyon yaklaşımı)**")
        shocks = [-100, 100, 300, 500]
        s_cols = st.columns(len(shocks))
        for col, bps in zip(s_cols, shocks):
            impact = -w_mod * (bps / 10000) * bond_value_try
            col.metric(f"{bps:+d} bp", f"₺ {impact:,.0f}", f"{impact / bond_value_try * 100:+.2f}%", delta_color="normal")

        st.caption("DV01: faizde 1 baz puanlık (0,01%) artışın tahvil sepetinde yarattığı yaklaşık TL kaybı. Şok senaryoları basitleştirilmiş durasyon yaklaşımıdır; büyük şoklarda gerçek kayıp bir miktar daha düşük olur. Hesaplanan Fiyat, girdiğiniz YTM ile tahvilin olması gereken fiyatıdır — Piyasa Fiyatından belirgin sapıyorsa girdiğiniz YTM tahvilin gerçek getirisiyle uyumsuz demektir.")

# SEKME 2: KORELASYON VE ÇEŞİTLENDİRME

with tab2:
    if current_returns.shape[1] >= 2:
        st.subheader("Portföy Çeşitlendirme Analizi")
        ind_vars = []
        for n in current_returns.columns:
            t_var_pct = np.percentile(current_returns[n], 1)
            ind_vars.append(investments[n] * t_var_pct)

        sum_individual_var = sum(ind_vars)
        var_99_value = market_value_try * np.percentile(portfolio_daily_returns, 1)
        diversification_benefit = abs(sum_individual_var) - abs(var_99_value)

        d_col1, d_col2, d_col3 = st.columns(3)
        d_col1.metric("Ayrık Toplam Risk", f"-₺ {abs(sum_individual_var):,.0f}")
        d_col2.metric("Portföy Riski", f"-₺ {abs(var_99_value):,.0f}")
        d_col3.metric("Çeşitlendirme Faydası", f"+₺ {diversification_benefit:,.0f}", delta_color="normal")

        st.markdown("---")
        st.subheader("Varlık Korelasyon Matrisi")
        corr_matrix = current_returns.corr()
        st.dataframe(corr_matrix.style.background_gradient(cmap='coolwarm', axis=None).format("{:.2f}"), use_container_width=True)
    else:
        st.info("Korelasyon analizi için piyasa verisi olan en az 2 varlık gereklidir.")

# SEKME 3: STRES TESTLERİ

with tab3:
    if not current_returns.empty:
        st.subheader("Tarihsel Çöküş Senaryoları")

        crash_scenarios = {
            "2008 Küresel Finans Krizi (Lehman)": {"start": "2008-09-12", "end": "2009-03-09", "region": "Uluslararası"},
            "2010-11 Avrupa Borç Krizi": {"start": "2011-07-01", "end": "2011-10-04", "region": "Uluslararası"},
            "2013 Fed Taper Tantrum": {"start": "2013-05-22", "end": "2013-06-24", "region": "Uluslararası"},
            "2015 Çin Devalüasyon Şoku": {"start": "2015-08-10", "end": "2015-08-25", "region": "Uluslararası"},
            "2018 Rahip Brunson Krizi": {"start": "2018-01-01", "end": "2018-08-31", "region": "Türkiye"},
            "2018 Q4 Fed Sıkılaşma Satışı": {"start": "2018-10-01", "end": "2018-12-24", "region": "Uluslararası"},
            "2020 Covid-19 Çöküşü": {"start": "2020-02-20", "end": "2020-03-23", "region": "Uluslararası"},
            "2021 KKM Döviz Krizi": {"start": "2021-11-18", "end": "2021-12-20", "region": "Türkiye"},
            "2022 Fed Faiz Şoku & Ayı Piyasası": {"start": "2022-01-03", "end": "2022-10-12", "region": "Uluslararası"},
            "2022 Kripto Kışı (LUNA/FTX)": {"start": "2022-04-01", "end": "2022-11-21", "region": "Uluslararası"},
            "2023 SVB Bankacılık Krizi": {"start": "2023-03-08", "end": "2023-03-24", "region": "Uluslararası"},
            "2023 Seçim Sonrası TL Ayarlaması": {"start": "2023-05-26", "end": "2023-06-23", "region": "Türkiye"},
            "2024 Yen Carry Trade Çöküşü": {"start": "2024-07-31", "end": "2024-08-05", "region": "Uluslararası"},
            "2025 Nisan Tarife Şoku": {"start": "2025-04-02", "end": "2025-04-08", "region": "Uluslararası"}
        }

        region_filter = st.multiselect("Senaryo Bölgesi:", ["Türkiye", "Uluslararası"], default=["Türkiye", "Uluslararası"])

        for scenario_name, dates in crash_scenarios.items():
            if dates["region"] not in region_filter:
                continue
            start_dt = pd.to_datetime(dates["start"])
            end_dt = pd.to_datetime(dates["end"])

            mask = (prices.index >= start_dt) & (prices.index <= end_dt)
            crash_prices = prices.loc[mask].replace(0, np.nan).dropna(axis=1, how='all')

            if crash_prices.empty or crash_prices.shape[1] == 0:
                st.warning(f"[{scenario_name}] Portföyünüzdeki varlıklar bu tarihte işleme açık değildi.")
                continue

            crash_returns = np.log(crash_prices / crash_prices.shift(1)).replace([np.inf, -np.inf], np.nan).dropna()
            if crash_returns.empty:
                continue

            scenario_active_names = crash_returns.columns.tolist()
            scenario_active_investment = sum(investments[n] for n in scenario_active_names)
            scenario_active_weights = np.array([investments[n] / scenario_active_investment for n in scenario_active_names])

            crash_portfolio_returns = crash_returns.dot(scenario_active_weights)
            cumulative_percentage_loss = np.exp(crash_portfolio_returns.sum()) - 1
            monetary_loss = market_value_try * cumulative_percentage_loss

            missing_names = [n for n in valid_names if n not in scenario_active_names]

            with st.expander(f"[{dates['region']}] {scenario_name} ({dates['start']} - {dates['end']})", expanded=False):
                st.metric("Portföy Etkisi (piyasa varlıkları)", f"₺ {monetary_loss:,.0f}", f"{cumulative_percentage_loss*100:+.2f}%", delta_color="normal")
                if missing_names:
                    st.caption(f"Bilgi: {', '.join(missing_names)} o dönemde piyasada olmadığı için teste dahil edilmedi.")
    else:
        st.info("Stres testi için piyasa fiyat serisi olan varlık gereklidir.")
