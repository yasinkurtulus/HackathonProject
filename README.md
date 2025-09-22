WordMaster AI - Akıllı İngilizce Kelime Öğrenme Platformu

Bu uygulama, kullanıcıların İngilizce öğrenme sürecini kolaylaştırmak ve daha kalıcı hale getirmek için tasarlanmış yapay zeka destekli bir dil öğrenme aracıdır.

🚀 Özellikler

✍️ Cümle Analizi: Kullanıcı, İngilizce’de karşılaştığı kelimeyi cümlesiyle birlikte girer. Uygulama, cümlenin türünü belirler ve Türkçe/İngilizce anlamlarını gösterir.

🤖 Kişiselleştirilmiş Örnekler: AI desteğiyle, kullanıcıların ilgi alanlarına uygun yeni örnek cümleler üretilir.

🔊 Telaffuz Desteği: Hugging Face TTS modeliyle kelimelerin doğru telaffuzları dinlenebilir.

📂 Kelimelerim Sekmesi: Öğrenilen kelimeler özel bir bölümde saklanır.

⏳ Spaced Repetition Tekniği: Aralıklı tekrar yöntemiyle hatırlatma bildirimleri gönderilir; unutma eğrisi en aza indirilir.

🛠️ Kullanılan Teknolojiler

Backend: Python Flask

Frontend: HTML5, CSS3, JavaScript (ES6+)

AI & NLP:

Google Gemini API
 → Görsel ve cümle üretimi

Hugging Face - ckartal/english-to-turkish-finetuned-model
 → İngilizce-Türkçe çeviri

Hugging Face - microsoft/speecht5_tts
 → Seslendirme (TTS)

Python NLTK
 → Cümle analizi ve dil işleme

Styling: Modern CSS (Grid/Flexbox, gradient arka planlar, animasyonlar

## 📦 Kurulum

1. **Projeyi klonlayın:**
   ```bash
   git clone <repository-url>
   cd Hackathon
   ```

2. **Sanal ortam oluşturun:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Bağımlılıkları yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Gemini API anahtarını ayarlayın:**
   ```bash
   cp env_example.txt .env
   # .env dosyasını düzenleyin ve GEMINI_API_KEY değerini ekleyin
   ```

5. **Uygulamayı çalıştırın:**
   ```bash
   python app.py
   ```

6. **Tarayıcıda açın:**
   ```
   http://localhost:8080
   ```

## 📱 Responsive Tasarım

Uygulama tüm cihazlarda mükemmel çalışır:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (320px - 767px)

## 🎨 Tasarım Özellikleri

- **Modern Gradient Arka Planlar**
- **Glassmorphism Efektleri**
- **Smooth Animasyonlar**
- **Intuitive Kullanıcı Deneyimi**
- **Accessibility Uyumlu**


## 🚀 Gelecek Özellikler

- [ ] Kullanıcı hesapları ve ilerleme takibi
- [ ] Kelime kategorileri ve filtreleme
- [ ] Sesli telaffuz özelliği
- [ ] Çoklu dil desteği
- [ ] Sosyal özellikler (arkadaşlarla yarışma)
- [ ] Mobil uygulama versiyonu

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.


## 📞 İletişim

Proje hakkında sorularınız için issue açabilir veya iletişime geçebilirsiniz.

---

**Not**: Bu proje eğitim amaçlıdır ve ticari kullanım için ek güvenlik önlemleri alınmalıdır.
