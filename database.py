import sqlite3
import hashlib
import json
from datetime import datetime
import os

class Database:
    def __init__(self, db_path='wordmaster.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Veritabanını ve tabloları oluşturur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Kullanıcılar tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                interests TEXT,  -- JSON formatında hobiler
                level_preference TEXT DEFAULT 'mixed',
                total_words_learned INTEGER DEFAULT 0,
                total_correct_answers INTEGER DEFAULT 0,
                current_streak INTEGER DEFAULT 0
            )
        ''')
        
        # Kullanıcı kelime geçmişi tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                word TEXT NOT NULL,
                definition TEXT,
                category TEXT,
                level TEXT,
                is_correct BOOLEAN,
                attempts INTEGER DEFAULT 1,
                first_attempt_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_attempt_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Hobi bazlı kelime listeleri
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hobby_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hobby TEXT NOT NULL,
                word TEXT NOT NULL,
                definition TEXT,
                level TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Kullanıcı oturumları
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_token TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print(" Veritabanı başarıyla oluşturuldu")
    
    def hash_password(self, password):
        """Şifreyi hashler"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, email, password, name=None):
        """Yeni kullanıcı oluşturur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (email, password_hash, name)
                VALUES (?, ?, ?)
            ''', (email, password_hash, name))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return {"success": True, "user_id": user_id}
            
        except sqlite3.IntegrityError:
            conn.close()
            return {"success": False, "error": "Bu email adresi zaten kayıtlı"}
        except Exception as e:
            conn.close()
            return {"success": False, "error": str(e)}
    
    def authenticate_user(self, email, password):
        """Kullanıcı girişi doğrular"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        cursor.execute('''
            SELECT id, email, name, interests, level_preference,
                   total_words_learned, total_correct_answers, current_streak
            FROM users 
            WHERE email = ? AND password_hash = ?
        ''', (email, password_hash))
        
        user = cursor.fetchone()
        
        if user:
            # Son giriş tarihini güncelle
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (user[0],))
            conn.commit()
            
            user_data = {
                "id": user[0],
                "email": user[1],
                "name": user[2],
                "interests": json.loads(user[3]) if user[3] else [],
                "level_preference": user[4],
                "total_words_learned": user[5],
                "total_correct_answers": user[6],
                "current_streak": user[7]
            }
            conn.close()
            return {"success": True, "user": user_data}
        
        conn.close()
        return {"success": False, "error": "Email veya şifre hatalı"}
    
    def update_user_interests(self, user_id, interests):
        """Kullanıcının ilgi alanlarını günceller"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        interests_json = json.dumps(interests)
        cursor.execute('''
            UPDATE users SET interests = ? WHERE id = ?
        ''', (interests_json, user_id))
        
        conn.commit()
        conn.close()
        return {"success": True}
    
    def save_word_attempt(self, user_id, word, definition, category, level, is_correct):
        """Kullanıcının kelime denemesini kaydeder"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Daha önce bu kelimeyi denemiş mi kontrol et
        cursor.execute('''
            SELECT id, attempts FROM user_words 
            WHERE user_id = ? AND word = ?
        ''', (user_id, word))
        
        existing = cursor.fetchone()
        
        if existing:
            # Mevcut kaydı güncelle
            new_attempts = existing[1] + 1
            cursor.execute('''
                UPDATE user_words 
                SET attempts = ?, last_attempt_date = CURRENT_TIMESTAMP, is_correct = ?
                WHERE id = ?
            ''', (new_attempts, is_correct, existing[0]))
        else:
            # Yeni kayıt oluştur
            cursor.execute('''
                INSERT INTO user_words 
                (user_id, word, definition, category, level, is_correct)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, word, definition, category, level, is_correct))
        
        # Kullanıcı istatistiklerini güncelle
        if is_correct:
            cursor.execute('''
                UPDATE users 
                SET total_correct_answers = total_correct_answers + 1,
                    current_streak = current_streak + 1
                WHERE id = ?
            ''', (user_id,))
        else:
            cursor.execute('''
                UPDATE users 
                SET current_streak = 0
                WHERE id = ?
            ''', (user_id,))
        
        conn.commit()
        conn.close()
        return {"success": True}
    
    def get_user_wrong_words(self, user_id, limit=10):
        """Kullanıcının yanlış yaptığı kelimeleri getirir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT word, definition, category, level, attempts, last_attempt_date
            FROM user_words 
            WHERE user_id = ? AND is_correct = 0
            ORDER BY last_attempt_date DESC
            LIMIT ?
        ''', (user_id, limit))
        
        words = cursor.fetchall()
        conn.close()
        
        return [
            {
                "word": word[0],
                "definition": word[1],
                "category": word[2],
                "level": word[3],
                "attempts": word[4],
                "last_attempt": word[5]
            }
            for word in words
        ]
    
    def get_user_stats(self, user_id):
        """Kullanıcı istatistiklerini getirir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT total_words_learned, total_correct_answers, current_streak,
                   (SELECT COUNT(*) FROM user_words WHERE user_id = ? AND is_correct = 0) as wrong_words,
                   (SELECT COUNT(*) FROM user_words WHERE user_id = ?) as total_attempts
            FROM users WHERE id = ?
        ''', (user_id, user_id, user_id))
        
        stats = cursor.fetchone()
        conn.close()
        
        if stats:
            return {
                "words_learned": stats[0],
                "correct_answers": stats[1],
                "current_streak": stats[2],
                "wrong_words": stats[3],
                "total_attempts": stats[4],
                "accuracy": round((stats[1] / stats[4] * 100) if stats[4] > 0 else 0, 1)
            }
        
        return None
    
    def save_hobby_words(self, hobby, words):
        """Hobi bazlı kelimeleri kaydeder"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for word_data in words:
            cursor.execute('''
                INSERT OR REPLACE INTO hobby_words (hobby, word, definition, level)
                VALUES (?, ?, ?, ?)
            ''', (hobby, word_data['word'], word_data['definition'], word_data['level']))
        
        conn.commit()
        conn.close()
        return {"success": True}
    
    def get_hobby_words(self, hobby, level=None, limit=50):
        """Hobi bazlı kelimeleri getirir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if level:
            cursor.execute('''
                SELECT word, definition, level FROM hobby_words 
                WHERE hobby = ? AND level = ?
                ORDER BY RANDOM() LIMIT ?
            ''', (hobby, level, limit))
        else:
            cursor.execute('''
                SELECT word, definition, level FROM hobby_words 
                WHERE hobby = ?
                ORDER BY RANDOM() LIMIT ?
            ''', (hobby, limit))
        
        words = cursor.fetchall()
        conn.close()
        
        return [
            {
                "word": word[0],
                "definition": word[1],
                "level": word[2],
                "category": hobby
            }
            for word in words
        ]
