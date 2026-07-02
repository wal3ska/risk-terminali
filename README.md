# Portföy & Risk Terminali

BIST, ABD hisseleri, kripto paralar, emtialar, endeksler ve tahvillerden oluşan çoklu varlık portföyleri için Streamlit tabanlı risk analizi ve portföy takip uygulaması. Tüm analizler TL bazında yapılır; dolar bazlı varlıklar USD/TRY kuru ile çevrildiğinden kur riski hesaplamalara dahildir.

## Özellikler

### Portföy Takip
- Adet ve ortalama maliyet girişiyle pozisyon bazlı kar/zarar takibi
- Maliyeti bilinmeyen pozisyonlar için "Maliyeti bilmiyorum" seçeneği: pozisyon K/Z hesabından çıkarılır, risk analizine dahil kalır
- Varlık ve kategori bazında portföy dağılımı (donut grafik)
- Toplam değer, toplam maliyet ve K/Z metrikleri ile canlı USD/TRY kuru

### Varlık Evreni
- **BIST:** BIST 100 hazır listesi + serbest kod girişiyle tüm Borsa İstanbul hisseleri
- **ABD Hisseleri:** S&P 500 / Nasdaq / DJIA'nın öne çıkan isimleri + serbest sembol girişi
- **Kripto:** BTC, ETH, SOL ve diğer büyük coinler
- **Emtia:** Altın, gümüş, Brent, WTI, doğalgaz, bakır (vadeli kontrat fiyatları)
- **Endeksler:** S&P 500, Nasdaq, Dow Jones, BIST 100, BIST 30
- **Tahvil/Bono:** Nominal, piyasa fiyatı, kupon oranı, kupon sıklığı, vade ve YTM girişiyle 5 adede kadar sabit getirili pozisyon

### Risk Analizi
- **Tarihsel Simülasyon VaR (%99):** Portföyün TL bazlı günlük getiri dağılımı üzerinden maksimum beklenen kayıp ve getiri histogramı
- **Durasyon Analizi:** Tahvil başına Macaulay ve Modified Duration, DV01; sepet düzeyinde değer ağırlıklı durasyon ve portföy katkısı
- **Faiz Şoku Senaryoları:** -100 / +100 / +300 / +500 baz puan paralel kayma etkisi
- **Korelasyon & Çeşitlendirme:** Varlık korelasyon matrisi ve çeşitlendirme faydasının TL karşılığı

### Stres Testleri
Türkiye / Uluslararası filtresiyle 14 tarihsel kriz senaryosu:

| Bölge | Senaryolar |
|---|---|
| Türkiye | 2018 Brunson Krizi · 2021 KKM Döviz Krizi · 2023 Seçim Sonrası TL Ayarlaması |
| Uluslararası | 2008 Küresel Finans Krizi · 2011 Avrupa Borç Krizi · 2013 Taper Tantrum · 2015 Çin Devalüasyonu · 2018 Q4 Fed Satışı · 2020 Covid-19 · 2022 Fed Faiz Şoku · 2022 Kripto Kışı · 2023 SVB Krizi · 2024 Yen Carry Trade · 2025 Nisan Tarife Şoku |

## Kurulum

```bash
git clone https://github.com/wal3ska/risk-terminali
cd risk-terminali
pip install -r requirements.txt
streamlit run app.py
```

**requirements.txt**
```
streamlit
yfinance
pandas
numpy
matplotlib
plotly
```

## Kullanım

1. Yan menüden kategori filtresi ile varlıklarını seç (listede olmayan BIST veya global sembolleri elle ekleyebilirsin)
2. Her pozisyon için adet ve ortalama maliyet gir; maliyeti hatırlamıyorsan "Maliyeti bilmiyorum" işaretle
3. Tahvil eklemek için nominal tutar, piyasa fiyatı (100 nominal başına), kupon bilgileri ve YTM gir
4. Sekmeler arasında gezerek portföy takibi, VaR, korelasyon ve stres testi sonuçlarını incele

## Metodoloji Notları

- **VaR:** Tarihsel Simülasyon yöntemi, logaritmik günlük getiriler, %99 güven düzeyi (1. yüzdelik). Yalnızca piyasa fiyat serisi olan varlıkları kapsar; tahvil faiz riski durasyon ile ayrıca ölçülür.
- **Kur dönüşümü:** USD bazlı varlıkların fiyat serileri `TRY=X` kuru ile TL'ye çevrilir; getiri serileri bu nedenle kur oynaklığını da içerir.
- **Durasyon:** Kupon akışlarının bugünkü değerinden Macaulay Duration, oradan Modified Duration türetilir. Faiz şoku etkileri birinci derece (durasyon) yaklaşımıdır, konveksite içermez.
- **Stres testleri:** Senaryo penceresindeki gerçekleşmiş getiriler mevcut portföy ağırlıklarına uygulanır. Senaryo tarihinde işlem görmeyen varlıklar testten düşülür ve ayrıca raporlanır.

## Sınırlamalar

- Veri kaynağı yfinance'tir (resmi olmayan Yahoo Finance API); veri gecikmeli olabilir ve yoğun kullanımda rate limit uygulanabilir. Ticari kullanım için lisanslı bir veri kaynağına geçilmelidir.
- BIST hisselerinin çoğunda Yahoo verisi 2010 öncesine gitmediğinden 2008 senaryosu ağırlıklı olarak ABD varlıklarında çalışır.
- Tahvil değerlemesi birikmiş kupon faizini ihmal eder; dolar bazlı pozisyonlarda maliyet güncel kurla çevrildiğinden kur farkı kazancı K/Z'ye yansımaz.
- Kripto 7/24, hisse senetleri 5 gün işlem gördüğünden ortak getiri serisi yalnızca ortak işlem günlerini kapsar.

## Yasal Uyarı

Bu uygulama yalnızca eğitim ve kişisel analiz amaçlıdır; yatırım danışmanlığı değildir. Yatırım danışmanlığı hizmeti, yetkili kuruluşlarca kişilerin risk ve getiri tercihleri dikkate alınarak sunulur. Burada yer alan analizler genel niteliktedir ve alım satım kararlarına tek başına dayanak oluşturmaz.
