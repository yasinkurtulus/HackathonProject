print("🚀 Basit test başlıyor...")

try:
    from flask import Flask
    print("✅ Flask import edildi")
    
    app = Flask(__name__)
    print("✅ Flask app oluşturuldu")
    
    @app.route('/')
    def home():
        return '''
        <html>
        <head>
            <title>WordMaster AI Test</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    text-align: center; 
                    padding: 50px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }
                .container {
                    background: rgba(255,255,255,0.1);
                    padding: 30px;
                    border-radius: 20px;
                    max-width: 500px;
                    margin: 0 auto;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎉 WordMaster AI Test Başarılı!</h1>
                <p>Flask çalışıyor ve hazır!</p>
                <p><strong>Port:</strong> 8080</p>
                <p><strong>Durum:</strong> ✅ Aktif</p>
                <hr>
                <p>Ana uygulamayı başlatmaya hazırız!</p>
            </div>
        </body>
        </html>
        '''
    
    print("✅ Route tanımlandı")
    print("🌐 Sunucu başlatılıyor...")
    print("📍 http://localhost:8080 adresine gidin")
    
    app.run(host='0.0.0.0', port=8080, debug=True)
    
except ImportError as e:
    print("❌ Flask import hatası:", e)
except Exception as e:
    print("❌ Genel hata:", e)
