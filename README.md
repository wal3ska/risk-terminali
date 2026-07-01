# 📈 Risk Terminali

**Canlı Uygulama:** [risk-terminali.streamlit.app](https://risk-terminali.streamlit.app/)

Risk Terminali, Borsa İstanbul (BIST 100) yatırımcıları ve emtia takipçileri için geliştirilmiş, portföy risklerini istatistiksel yöntemlerle analiz eden ve kriz senaryolarını simüle eden bir web uygulamasıdır. 

> ⚠️ **Önemli Uyarı:** 
> Sistemde şu an için yalnızca belirli BIST 100 hisseleri ve temel emtialar bulunmaktadır. Projenin veri seti zamanla genişletilecek ve tüm BIST 100 hisseleri ile çeşitli enstrümanlar platforma entegre edilecektir.

---

## 🎯 Projenin Amacı ve Ölçülen Metrikler

Borsada getiri odaklı düşünmek kadar, riski yönetmek de sürdürülebilir büyümenin (özellikle uzun vadeli ve temettü odaklı yatırımların) temelidir. Bu proje, portföyünüzün "karanlık yüzünü" görmenizi sağlar. Sistem şu metrikleri hesaplar:

*   **Riske Maruz Değer (VaR - Value at Risk):** Normal piyasa koşulları altında, belirli bir zaman diliminde ve belirli bir güven aralığında portföyün uğrayabileceği *maksimum olası zararı* ölçer.
*   **Stres Testleri:** "Piyasa %10 çökerse ne olur?", "Tarihsel bir kriz tekrar yaşanırsa portföyüm nasıl tepki verir?" gibi ekstrem kara gün (tail-risk) senaryolarının simülasyonudur.
*   **Korelasyon ve Kovaryans Matrisleri:** Portföydeki varlıkların birbirlerine göre nasıl hareket ettiğini (beraber mi düşüyorlar, zıt mı hareket ediyorlar?) matematiksel olarak ortaya koyar.

## 💼 Portföye Katkıları

Bu terminal, duygusal kararlar yerine veri odaklı risk yönetimi yapmanızı sağlar:
1.  **Gerçekçi Beklenti Yönetimi:** Taşıdığınız riskin boyutunu TL/Yüzde bazında somutlaştırır.
2.  **Optimum Çeşitlendirme (Diversifikasyon):** Sadece "farklı hisseler" almanın ötesine geçerek, matematiksel olarak birbirini dengeleyen varlıkları seçmenize yardımcı olur.
3.  **Krizlere Hazırlık:** Olası piyasa şoklarında portföyünüzün ne kadar eriyebileceğini önceden bilmek, panik satışlarının önüne geçer.

---

## 📊 Test Sonuçları Nasıl Yorumlanmalı?

Terminalden aldığınız sonuçları doğru okumak, portföyünüzü yeniden dengelerken size yol gösterecektir:

### 1. VaR (Riske Maruz Değer) Yorumlama
Örneğin; sistemin ürettiği **"%95 Güven Aralığında Günlük VaR: -5.000 TL"** sonucu şu anlama gelir:
*"Normal piyasa koşullarında, 100 işlem gününün 95'inde günlük kaybım 5.000 TL'yi aşmayacaktır."*
Bunun tersten okuması ise şudur: Kalan %5'lik (ekstrem) günlerde kaybınız 5.000 TL'den daha fazla olacaktır.

### 2. Korelasyon Matrisi Yorumlama (Varlıkların Bağımsızlığı)
Korelasyon, -1.0 ile +1.0 arasında değer alır. Gerçek bir portföy çeşitlendirmesi için varlıkların sürekli aynı yöne gitmemesi gerekir.
*   **+0.7 ile +1.0 (Yüksek Korelasyon):** Varlıklar neredeyse aynı anda yükselip düşer (Örn: İki farklı otomotiv şirketi). Etkili bir çeşitlendirme sağlamaz.
*   **-0.3 ile +0.3 (Düşük Korelasyon / Bağımsızlık):** Varlıklar birbirinden *bağımsız* hareket eder. Portföyünüzdeki çapraz varlıkların (hisse-emtia veya farklı sektör hisseleri) bu aralıkta olması, riskin iyi dağıtıldığını gösterir.
*   **-1.0 ile -0.5 (Negatif Korelasyon):** Biri düşerken diğeri yükselir. Borsa düşerken portföyü koruyacak (hedge) varlıklar bu aralıktan seçilebilir (Örn: BIST hissesi vs. Altın/Dolar).

### 3. Stres Testi Yorumlama
Stres testi sonuçları, portföyünüzün "Kırılganlık" haritasıdır. Eğer sistem, endeksteki %10'luk bir düşüşte portföyünüzün %15 eriyeceğini söylüyorsa, portföyünüzün piyasa dalgalanmalarına karşı yüksek hassasiyete (yüksek beta) sahip olduğunu anlarsınız.

---

## 🚀 Gelecekte Eklenecek Özellikler (Roadmap)

Proje sürekli olarak geliştirilmeye devam etmektedir. Yakın gelecekte planlanan bazı güncellemeler:

*   [ ] **Tam BIST 100 Entegrasyonu:** Endeksteki tüm hisselerin veritabanına dahil edilmesi.
*   [ ] **Monte Carlo Simülasyonu:** Rastgele fiyat yürüyüşü modelleriyle geleceğe dönük binlerce farklı senaryonun test edilmesi.
*   [ ] **Dinamik Portföy Optimizasyonu:** Modern Portföy Teorisi (Markowitz) kullanılarak, istenen risk seviyesine göre optimum hisse ağırlıklarının otomatik önerilmesi.
*   [ ] **Kripto Varlıklar:** İsteğe bağlı olarak risk ölçümlerine Bitcoin ve diğer majör kripto paraların entegrasyonu.
*   [ ] **Gelişmiş Backtest Modülü:** Geçmiş veriler üzerinde belirli risk algoritmalarının nasıl performans gösterdiğinin test edilmesi.

---

### Kurulum (Lokalde Çalıştırmak İçin)

Projeyi kendi bilgisayarınızda çalıştırmak isterseniz:

```bash
# Repoyu klonlayın
git clone [https://github.com/anilserdarunal/risk-terminali.git](https://github.com/anilserdarunal/risk-terminali.git)

# Gerekli kütüphaneleri yükleyin
pip install -r requirements.txt

# Streamlit uygulamasını başlatın
streamlit run app.py
