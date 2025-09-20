#!/usr/bin/env python3
print("🚀 WordMaster AI Quick Start")
print("=" * 50)

try:
    print("✅ Python çalışıyor")
    
    import flask
    print(f"✅ Flask kurulu (v{flask.__version__})")
    
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>WordMaster AI - Quick Start</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-align: center;
                    padding: 50px;
                    margin: 0;
                }
                .container {
                    background: rgba(255,255,255,0.1);
                    padding: 30px;
                    border-radius: 20px;
                    max-width: 600px;
                    margin: 0 auto;
                }
                .success { color: #4CAF50; font-weight: bold; }
                .button {
                    background: #4CAF50;
                    color: white;
                    padding: 15px 30px;
                    border: none;
                    border-radius: 10px;
                    font-size: 16px;
                    cursor: pointer;
                    margin: 10px;
                    text-decoration: none;
                    display: inline-block;
                }
                .button:hover { background: #45a049; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎉 WordMaster AI Test Başarılı!</h1>
                <p class="success">✅ Flask çalışıyor</p>
                <p class="success">✅ Port 8080 aktif</p>
                <p class="success">✅ Web sunucusu hazır</p>
                
                <hr style="margin: 30px 0; border: 1px solid rgba(255,255,255,0.3);">
                
                <h2>🚀 Ana Uygulama Hazır!</h2>
                <p>Ana WordMaster AI uygulamasını başlatmak için:</p>
                <ol style="text-align: left; max-width: 400px; margin: 20px auto;">
                    <li>Terminal'i açın</li>
                    <li><code style="background: rgba(0,0,0,0.3); padding: 5px;">python app.py</code> komutunu çalıştırın</li>
                    <li>Bu sayfayı yenileyin</li>
                </ol>
                
                <a href="/" class="button">🔄 Sayfayı Yenile</a>
                <a href="http://localhost:8080" class="button">🏠 Ana Sayfa</a>
            </div>
        </body>
        </html>
        '''
    
    print("✅ Flask app hazırlandı")
    print("🌐 http://localhost:8080 adresinde başlatılıyor...")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=8080, debug=True)
    
except ImportError as e:
    print(f"❌ Import hatası: {e}")
    print("🔧 Çözüm: pip install flask")
except Exception as e:
    print(f"❌ Genel hata: {e}")
    print("🔧 Lütfen tekrar deneyin")
