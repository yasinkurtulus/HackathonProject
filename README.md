# WordMaster AI - İngilizce Kelime Öğrenme Platformu

Modern bir arayüze sahip, Gemini AI entegrasyonlu İngilizce kelime öğrenme websitesi.

## 🚀 Özellikler

- **AI Destekli Görsel Oluşturma**: Gemini AI ile kelimeler için eğitici görseller
- **Boşluk Doldurma Egzersizleri**: AI tarafından oluşturulan interaktif cümleler
- **Modern UI/UX**: Responsive ve kullanıcı dostu arayüz
- **Gerçek Zamanlı İstatistikler**: Öğrenilen kelime sayısı ve doğru cevap oranı
- **Seviye Bazlı Öğrenme**: Farklı zorluk seviyelerinde kelimeler

## 🛠️ Teknolojiler

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **AI**: Google Gemini API
- **Styling**: Modern CSS Grid/Flexbox, Gradient tasarım

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
   http://localhost:5000
   ```

## 🔑 Gemini API Anahtarı Alma

1. [Google AI Studio](https://makersuite.google.com/app/apikey) adresine gidin
2. Google hesabınızla giriş yapın
3. "Create API Key" butonuna tıklayın
4. Oluşturulan anahtarı `.env` dosyasına ekleyin

## 🎮 Kullanım

- **Yeni Kelime**: "Yeni Kelime" butonuna tıklayın veya `N` tuşuna basın
- **Görsel Oluştur**: "Görsel Oluştur" butonuna tıklayın veya `I` tuşuna basın
- **Yeni Cümle**: "Yeni Cümle" butonuna tıklayın veya `S` tuşuna basın
- **Cevap Ver**: Boşluğu doldurun ve "Kontrol Et" butonuna tıklayın

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

## 🔧 Geliştirme

### Proje Yapısı
```
Hackathon/
├── app.py                 # Flask uygulaması
├── requirements.txt       # Python bağımlılıkları
├── env_example.txt       # Çevre değişkenleri örneği
├── README.md             # Proje dokümantasyonu
├── templates/
│   └── index.html        # Ana HTML şablonu
└── static/
    ├── css/
    │   └── style.css     # CSS stilleri
    └── js/
        └── app.js        # JavaScript uygulaması
```

### API Endpoints

- `GET /` - Ana sayfa
- `GET /api/word` - Rastgele kelime getir
- `POST /api/generate-image` - Kelime için görsel oluştur
- `POST /api/generate-sentence` - Boşluk doldurmalı cümle oluştur
- `POST /api/check-answer` - Cevabı kontrol et

## 🚀 Gelecek Özellikler

- [ ] Kullanıcı hesapları ve ilerleme takibi
- [ ] Kelime kategorileri ve filtreleme
- [ ] Sesli telaffuz özelliği
- [ ] Çoklu dil desteği
- [ ] Sosyal özellikler (arkadaşlarla yarışma)
- [ ] Mobil uygulama versiyonu

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📞 İletişim

Proje hakkında sorularınız için issue açabilir veya iletişime geçebilirsiniz.

---

**Not**: Bu proje eğitim amaçlıdır ve ticari kullanım için ek güvenlik önlemleri alınmalıdır.
