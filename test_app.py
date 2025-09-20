from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <h1>Test Başarılı! 🎉</h1>
    <p>Flask çalışıyor!</p>
    <a href="/main">Ana uygulamaya git</a>
    '''

@app.route('/main')
def main():
    return '''
    <h1>WordMaster AI Test</h1>
    <p>Gemini API entegrasyonu test ediliyor...</p>
    '''

if __name__ == '__main__':
    print("🚀 Test uygulaması başlatılıyor...")
    print("📍 http://localhost:5000 adresine gidin")
    app.run(debug=True, host='0.0.0.0', port=5000)
