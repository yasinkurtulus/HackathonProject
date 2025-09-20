from flask import Flask, render_template, jsonify
import random

app = Flask(__name__)

# Basit kelime listesi
WORDS = [
    {"word": "computer", "definition": "an electronic device for processing data", "level": "beginner"},
    {"word": "technology", "definition": "application of scientific knowledge", "level": "intermediate"},
    {"word": "software", "definition": "computer programs and applications", "level": "intermediate"},
    {"word": "internet", "definition": "global network of computers", "level": "beginner"},
    {"word": "algorithm", "definition": "step-by-step problem solving method", "level": "advanced"}
]

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>WordMaster AI - Quick Fix</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; padding: 50px; text-align: center; 
            }
            .container { 
                background: rgba(255,255,255,0.1); 
                padding: 40px; border-radius: 20px; max-width: 600px; margin: 0 auto; 
            }
            .word { font-size: 3rem; margin: 20px 0; }
            .definition { font-size: 1.2rem; margin: 20px 0; opacity: 0.9; }
            .sentence { 
                background: rgba(255,255,255,0.2); 
                padding: 20px; border-radius: 10px; margin: 20px 0; 
            }
            input { 
                padding: 15px; font-size: 1.1rem; border: none; 
                border-radius: 10px; margin: 10px; width: 200px; 
            }
            button { 
                padding: 15px 25px; font-size: 1.1rem; background: #ff6b6b; 
                color: white; border: none; border-radius: 10px; cursor: pointer; 
            }
            button:hover { background: #ee5a24; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 WordMaster AI</h1>
            <div id="word-display">
                <div class="word" id="word">Loading...</div>
                <div class="definition" id="definition">Loading definition...</div>
                <div class="sentence" id="sentence">Loading sentence...</div>
                <input type="text" id="answer" placeholder="Your answer">
                <button onclick="checkAnswer()">Check</button>
                <button onclick="newWord()">New Word</button>
                <div id="feedback" style="margin-top: 20px; font-weight: bold;"></div>
            </div>
        </div>

        <script>
            let currentWord = null;

            async function newWord() {
                try {
                    const response = await fetch('/api/word');
                    const word = await response.json();
                    currentWord = word;
                    
                    document.getElementById('word').textContent = word.word;
                    document.getElementById('definition').textContent = word.definition;
                    document.getElementById('sentence').textContent = `The word _____ means "${word.definition}".`;
                    document.getElementById('answer').value = '';
                    document.getElementById('feedback').textContent = '';
                } catch (error) {
                    console.error('Error:', error);
                }
            }

            function checkAnswer() {
                const userAnswer = document.getElementById('answer').value.trim();
                const feedback = document.getElementById('feedback');
                
                if (userAnswer.toLowerCase() === currentWord.word.toLowerCase()) {
                    feedback.textContent = '🎉 Correct!';
                    feedback.style.color = '#4CAF50';
                    setTimeout(newWord, 2000);
                } else {
                    feedback.textContent = `❌ Wrong. Answer: ${currentWord.word}`;
                    feedback.style.color = '#ff6b6b';
                }
            }

            // Load first word
            newWord();
        </script>
    </body>
    </html>
    '''

@app.route('/api/word')
def get_word():
    word = random.choice(WORDS)
    return jsonify(word)

if __name__ == '__main__':
    print("🚀 Quick Fix çalışıyor...")
    print("📍 http://localhost:9000 adresine git")
    app.run(host='0.0.0.0', port=9000, debug=True)
