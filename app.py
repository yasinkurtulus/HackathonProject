from flask import render_template, request, jsonify, session, redirect, url_for
from database import Database
import secrets
import generator
import sound
from flask import Flask
from dotenv import load_dotenv
import email_service

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Session için güvenli key
load_dotenv()
# Veritabanı bağlantısı
db = Database()

# Eski, kullanılmayan sözlük/veri bölümleri kaldırıldı

# Hobi kategorileri
HOBBY_CATEGORIES = {
    "technology": "Teknoloji & Yazılım",
    "business": "İş & Finans",
    "health": "Sağlık & Fitness",
    "arts": "Sanat & Tasarım",
    "science": "Bilim & Araştırma",
    "travel": "Seyahat & Kültür",
    "cooking": "Yemek & Mutfak",
    "sports": "Spor & Aktivite",
    "music": "Müzik & Enstrüman",
    "education": "Eğitim & Öğretim",
    "photography": "Fotoğrafçılık",
    "gaming": "Oyun & Eğlence"
}

app.config
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_stats = db.get_user_stats(session['user_id'])
    return render_template('index.html', user=session.get('user'), stats=user_stats)

@app.route('/words')
def words_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # query parametreleri
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    q = request.args.get('q', '')

    offset = (page - 1) * per_page

    # list_user_words(user_id, limit, offset, search)
    words = db.list_user_words(
        session['user_id'],
        limit=per_page,
        offset=offset,
        search=q if q else None
    )

    return render_template(
        'words.html',
        user=session.get('user'),
        words=words,
        page=page,
        per_page=per_page,
        q=q
    )

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_stats = db.get_user_stats(session['user_id'])
    return render_template('dashboard.html', user=session.get('user'), stats=user_stats)


@app.route('/login')
def login():
    return render_template('auth.html', mode='login')


@app.route('/register')
def register():
    return render_template('auth.html', mode='register')


@app.route('/interests')
def interests():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('interests.html', hobbies=HOBBY_CATEGORIES)


@app.route('/learning')
def learning():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('learning.html')


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_stats = db.get_user_stats(session['user_id'])
    wrong_words = db.get_user_wrong_words(session['user_id'])

    return render_template('profile.html',
                           user=session.get('user'),
                           stats=user_stats,
                           wrong_words=wrong_words)


@app.route('/api/word')
def api_word_placeholder():
    return jsonify({"success": False, "error": "Bu endpoint devre dışı."})

    # Eski image generator kaldırıldı

@app.route("/api/generate", methods=["POST"])
def api_generate():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Giriş yapmanız gerekli"})

    data = request.get_json(force=True)
    word = data.get("word", "").strip()
    sample_sentence = data.get("sample_sentence", "").strip()

    if not word or not sample_sentence:
        return jsonify({"success": False, "error": "Kelime ve örnek cümle gerekli"})

    # Get user's interests from session
    user = session.get('user', {})
    interests = user.get('interests', [])

    # Fallback interests if user hasn't selected any
    if not interests:
        interests = ["technology", "education", "general"]

    # Fixed tenses for verb examples
    tenses = ["simple present", "present continuous", "simple past", "present perfect"]

    try:
        print(f"Starting generation for word: {word}, interests: {interests}")
        info, examples = generator.generate_sentences(word, sample_sentence, tenses, interests)
        print(f"Generation successful - info: {info}, examples count: {len(examples) if examples else 0}")
        normalized_word = word.casefold()
        db_result=db.add_word_entry(user_id=session["user_id"], word=normalized_word)
        if db_result:
            print("Kelime sözlüğe kaydedildi")
        return jsonify({"info": info, "examples": examples})
    except Exception as e:
        print(f"Error generating sentences: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": f"Cümleler oluşturulurken bir hata oluştu: {str(e)}"})

@app.get("/cron/run-reminders")
def run_reminders_now():
    # due kayıtlarını tüm kullanıcılar için çek
    due = db.get_due_reminders(limit=200)
    sent = 0

    mailer=email_service.EmailService()

    print(f"{len(due)} adet hatırlatma bulundu.")

    for r in due:
        to = r["email"]
        subject = f"Hatırlatma: {r['word']}"
        body = f"Bugün hatırlaman gereken kelime: {r['word']}"

        try:
            mailer.send_email(to_email=to, subject=subject, body=body)
            sent += 1

            # Gönderim sonrası interval ve next_run_at güncelle
            db.after_reminder_sent(r["rule_id"], r["interval_days"])

        except Exception as e:
            print(f"{to} için mail hatası:", e)

    return jsonify({"due": len(due), "sent": sent})

@app.route('/api/generate-sentence', methods=['POST'])
def generate_sentence():
    """Gemini ile boşluk doldurmalı cümle oluşturur"""
    try:
        data = request.get_json()
        word = data.get('word')
        definition = data.get('definition')

        # Önce basit cümleler deneyelim
        simple_sentences = {
            "serendipity": "Finding this old photo was pure _____ - it happened at the perfect moment.",
            "ephemeral": "The beauty of cherry blossoms is _____ - they bloom for only a short time.",
            "ubiquitous": "Smartphones have become _____ in modern society - you see them everywhere.",
            "mellifluous": "Her _____ voice made the poetry reading absolutely captivating.",
            "resilient": "Despite facing many challenges, she remained _____ and never gave up."
        }

        # Eğer kelime için hazır cümle varsa onu kullan
        if word.lower() in simple_sentences:
            sentence = simple_sentences[word.lower()]
        else:
            # Basit fallback cümle oluştur
            sentence = f"The word _____ means {definition}."

        return jsonify({
            "success": True,
            "sentence": sentence,
            "answer": word
        })

    except Exception as e:
        print(f"Genel hata: {e}")
        return jsonify({
            "success": True,  # Başarılı olarak döndür ama basit cümle ver
            "sentence": f"The word _____ is used in English language learning.",
            "answer": data.get('word', 'word')
        })


    # Eski check-answer kaldırıldı

# Kullanıcı API'leri
@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if not email or not password:
        return jsonify({"success": False, "error": "Email ve şifre gerekli"})

    result = db.create_user(email, password, name)

    if result["success"]:
        return jsonify({"success": True, "message": "Hesap başarıyla oluşturuldu"})
    else:
        return jsonify(result)


@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    result = db.authenticate_user(email, password)

    if result["success"]:
        user = result["user"]
        session['user_id'] = user['id']
        session['user'] = user
        return jsonify({"success": True, "user": user})
    else:
        return jsonify(result)


@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"success": True})


@app.route('/api/interests', methods=['POST'])
def api_save_interests():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Giriş yapmanız gerekli"})

    data = request.get_json()
    interests = data.get('interests', [])

    result = db.update_user_interests(session['user_id'], interests)

    if result["success"]:
        # Seçilen hobiler için basit kelime listeleri oluştur
        for interest in interests:
            try:
                generate_hobby_words(interest)
            except Exception as e:
                print(f"Hobi kelime oluşturma hatası ({interest}): {e}")
                # Devam et, hata verme
                pass

        return jsonify({"success": True})
    else:
        return jsonify(result)


@app.route('/api/words/hobby/<hobby>')
def api_get_hobby_words(hobby):
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Giriş yapmanız gerekli"})

    level = request.args.get('level')
    words = db.get_hobby_words(hobby, level)

    if not words:
        # Eğer kelime yoksa Gemini'den al
        generate_hobby_words(hobby)
        words = db.get_hobby_words(hobby, level)

    return jsonify({"success": True, "words": words})


@app.route('/api/word/attempt', methods=['POST'])
def api_save_word_attempt():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Giriş yapmanız gerekli"})

    data = request.get_json()
    word = data.get('word')
    definition = data.get('definition')
    category = data.get('category')
    level = data.get('level')
    is_correct = data.get('is_correct')

    result = db.save_word_attempt(
        session['user_id'], word, definition, category, level, is_correct
    )

    return jsonify(result)


@app.route('/api/pronounce', methods=['POST'])
def api_pronounce():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Giriş yapmanız gerekli"})

    data = request.get_json(force=True)
    text = data.get('text', '').strip()
    if not text:
        return jsonify({"success": False, "error": "Seslendirilecek metin boş olamaz"})

    try:
        audio_bytes = sound.synthesize_wav_bytes(text)
        # WAV bytes'ı direkt response olarak döndür
        from flask import Response
        return Response(audio_bytes, mimetype='audio/wav')
    except Exception as e:
        print(f"TTS error: {e}")
        return jsonify({"success": False, "error": "Ses oluşturulamadı"})


def generate_hobby_words(hobby):
    """Hobi bazlı basit kelime listeleri oluşturur"""
    try:
        # Her hobi için önceden tanımlanmış kelimeler
        hobby_words = {
            "technology": [
                {"word": "computer", "definition": "electronic device for processing data", "level": "beginner"},
                {"word": "software", "definition": "computer programs and applications", "level": "beginner"},
                {"word": "internet", "definition": "global network of computers", "level": "beginner"},
                {"word": "algorithm", "definition": "step-by-step problem solving method", "level": "intermediate"},
                {"word": "database", "definition": "organized collection of data", "level": "intermediate"},
                {"word": "programming", "definition": "writing computer code", "level": "intermediate"},
                {"word": "artificial", "definition": "made by humans, not natural", "level": "advanced"},
                {"word": "cybersecurity", "definition": "protection of digital systems", "level": "advanced"},
            ],
            "business": [
                {"word": "profit", "definition": "money gained from business", "level": "beginner"},
                {"word": "market", "definition": "place where goods are sold", "level": "beginner"},
                {"word": "customer", "definition": "person who buys goods", "level": "beginner"},
                {"word": "strategy", "definition": "plan for achieving goals", "level": "intermediate"},
                {"word": "investment", "definition": "putting money to earn more", "level": "intermediate"},
                {"word": "entrepreneur", "definition": "person who starts business", "level": "advanced"},
            ],
            "health": [
                {"word": "exercise", "definition": "physical activity for fitness", "level": "beginner"},
                {"word": "nutrition", "definition": "food needed for health", "level": "beginner"},
                {"word": "medicine", "definition": "treatment for illness", "level": "beginner"},
                {"word": "therapy", "definition": "treatment for health problems", "level": "intermediate"},
                {"word": "diagnosis", "definition": "identifying a disease", "level": "intermediate"},
                {"word": "rehabilitation", "definition": "recovery from injury", "level": "advanced"},
            ]
        }

        # Eğer hobi için kelimeler varsa onları kullan
        if hobby in hobby_words:
            words_data = hobby_words[hobby]
        else:
            # Genel fallback kelimeler
            words_data = [
                {"word": "learning", "definition": "gaining knowledge or skills", "level": "beginner"},
                {"word": "practice", "definition": "doing something repeatedly to improve", "level": "beginner"},
                {"word": "knowledge", "definition": "information and understanding", "level": "intermediate"},
                {"word": "experience", "definition": "practical contact with events", "level": "intermediate"},
                {"word": "expertise", "definition": "expert skill or knowledge", "level": "advanced"},
            ]

        # Veritabanına kaydet
        db.save_hobby_words(hobby, words_data)
        print(f"✅ {hobby} için {len(words_data)} kelime kaydedildi")

    except Exception as e:
        print(f"❌ {hobby} kelime kaydetme hatası: {e}")
        # En basit fallback
        basic_words = [
            {"word": "word", "definition": "unit of language", "level": "beginner"},
            {"word": "learn", "definition": "gain knowledge", "level": "beginner"},
        ]
        try:
            db.save_hobby_words(hobby, basic_words)
        except:
            pass  # Sessizce devam et


if __name__ == '__main__':
    print(" WordMaster AI başlatılıyor...")
    print(" http://localhost:8080 adresine gidin")
    # TTS model warmup (opsiyonel): ilk isteği hızlandırır
    try:
        sound.synthesize_wav_bytes("hello")
        print(" TTS hazır")
    except Exception as _e:
        print(" TTS warmup atlandı")
    app.run(debug=True, host='0.0.0.0', port=8080)
