import sqlite3
import hashlib
import json
from datetime import datetime
from datetime import datetime, timedelta
import os

class Database:
    def __init__(self, db_path='wordmaster.db'):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Veritabanını ve tabloları (SQLite uyumlu) oluşturur"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")  # FK'ler için şart (her connection'da)
        cursor = conn.cursor()


        # users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                interests TEXT,                  -- JSON text
                level_preference TEXT DEFAULT 'mixed',
                total_words_learned INTEGER DEFAULT 0,
                total_correct_answers INTEGER DEFAULT 0,
                current_streak INTEGER DEFAULT 0
            );
        """)

        # user_words (mevcut yapın korunuyor)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                word TEXT NOT NULL,
                definition TEXT,
                category TEXT,
                level TEXT,
                is_correct INTEGER,              -- SQLite'ta boolean yok; 0/1 kullanıyoruz
                attempts INTEGER DEFAULT 1,
                first_attempt_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_attempt_date  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # hobby_words
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hobby_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hobby TEXT NOT NULL,
                word TEXT NOT NULL,
                definition TEXT,
                level TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # user_sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # word_entries  (ÖNEMLİ: NOW() yerine CURRENT_TIMESTAMP, FK öncesi virgül!)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS word_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                word TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                next_reminder_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id, word COLLATE NOCASE)  -- aynı kullanıcı için aynı kelimeyi engelle
            );
        """)

        # Defensive migration: add next_reminder_at if missing
        cursor.execute("PRAGMA table_info(word_entries)")
        cols = [r[1] for r in cursor.fetchall()]
        if 'next_reminder_at' not in cols:
            cursor.execute("ALTER TABLE word_entries ADD COLUMN next_reminder_at TIMESTAMP")

        # reminder_rules  (end_at YOK, BOOLEAN yerine INTEGER, sabit virgüller)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminder_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                entry_id INTEGER NOT NULL,
                interval_days INTEGER NOT NULL,              -- 0 => tek seferlik
                start_at TIMESTAMP NOT NULL,                 -- CURRENT_TIMESTAMP ile set edeceğiz
                is_active INTEGER NOT NULL DEFAULT 1,        -- 1/0
                next_run_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (entry_id) REFERENCES word_entries(id) ON DELETE CASCADE
            );
        """)

        # (Önerilir) Aynı kullanıcı aynı kelimeyi iki kez ekleyemesin (case-insensitive)
        cursor.execute('''
            CREATE UNIQUE INDEX IF NOT EXISTS idx_word_entries_user_word_nocase
            ON word_entries(user_id, word COLLATE NOCASE)
        ''')

        conn.commit()
        conn.close()
        print("Veritabanı başarıyla oluşturuldu")

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

    def add_word_entry(self, user_id: int, word: str):
        """
        1) Aynı kullanıcı için aynı kelime varsa eklemez (NOCASE).
        2) Yoksa word_entries'e ekler.
        3) Başarılı eklemeden sonra reminder_rules'ta kural açar:
           - 10 saniye sonra 1 kez mail (interval_days = 0)
        """
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("PRAGMA foreign_keys = ON")
            cur = conn.cursor()

            # 1) Duplicate kontrolü (Apple == apple)
            cur.execute("""
                SELECT id FROM word_entries
                WHERE user_id = ? AND word = ? COLLATE NOCASE
                LIMIT 1
            """, (user_id, word.strip()))
            row = cur.fetchone()
            if row:
                return {"success": False, "error": "Bu kelime daha önce eklenmiş.", "entry_id": row[0]}

            # 2) Kelimeyi ekle
            cur.execute("""
                INSERT INTO word_entries (user_id, word, created_at, next_reminder_at)
                VALUES (?, ?, CURRENT_TIMESTAMP, datetime(CURRENT_TIMESTAMP, '+' || ? || ' days'))
            """, (user_id, word.strip(), 1))
            entry_id = cur.lastrowid

            # İstatistik güncelle (opsiyonel)
            cur.execute("""
                UPDATE users SET total_words_learned = total_words_learned + 1
                WHERE id = ?
            """, (user_id,))

            conn.commit()  # kelimeyi kesinleştir
        except Exception as e:
            conn.close()
            return {"success": False, "error": str(e)}

        # 3) Reminder kuralını AYNı DB için ayrı bir transaction’da oluştur
        rule_res = self.create_reminder_rule_for_entry(
            user_id=user_id,
            entry_id=entry_id,
            interval_days=1  # 0 => tek seferlik
        )
        if not rule_res.get("success"):
            # Kelime eklendi ama kural açılamadı; loglamak yeterli.
            print("Reminder rule creation failed:", rule_res.get("error"))

        return {"success": True, "entry_id": entry_id}

    def _dt(dt: datetime) -> str:
        # SQLite için 'YYYY-MM-DD HH:MM:SS'
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def create_reminder_rule_for_entry(self, user_id: int, entry_id: int,
                                       interval_days: int = 1):  # varsayılan 1 gün
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute("""
              INSERT INTO reminder_rules
                (user_id, entry_id, interval_days, start_at, is_active, next_run_at)
              VALUES
                (?, ?, ?, CURRENT_TIMESTAMP, 1,
                 datetime(CURRENT_TIMESTAMP, '+' || ? || ' days'))
            """, (user_id, entry_id, interval_days, interval_days))
            conn.commit()
            return {"success": True, "rule_id": cur.lastrowid}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    def _next_interval_days(current_days: int | None) -> int:
        ladder = [1, 2, 4, 7, 15, 30, 60, 120]  # tavan: 120
        if not current_days or current_days < ladder[0]:
            return ladder[0]
        for v in ladder:
            if v > current_days:
                return v
        return ladder[-1]  # zaten tavanda ise tavanda kal

    def after_reminder_sent(self, rule_id: int, current_interval: int | None):
        new_interval = self._next_interval_days(current_interval)
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            # Find entry_id for updating word_entries as well
            cur.execute("SELECT entry_id FROM reminder_rules WHERE id = ?", (rule_id,))
            row = cur.fetchone()
            entry_id = row[0] if row else None

            # Update next_run_at and interval on the rule
            cur.execute("""
                UPDATE reminder_rules
                SET interval_days = ?,
                    next_run_at   = datetime(CURRENT_TIMESTAMP, '+' || ? || ' days')
                WHERE id = ?
                  AND next_run_at <= CURRENT_TIMESTAMP
            """, (new_interval, new_interval, rule_id))

            # Mirror the next reminder to word_entries for convenience
            if entry_id is not None:
                cur.execute("""
                    UPDATE word_entries
                    SET next_reminder_at = datetime(CURRENT_TIMESTAMP, '+' || ? || ' days')
                    WHERE id = ?
                """, (new_interval, entry_id))
            conn.commit()

    def get_due_reminders(self, limit=100):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            SELECT
              rr.id           AS rule_id,
              rr.user_id,
              rr.interval_days,
              u.email         AS email,
              we.word         AS word
            FROM reminder_rules rr
            JOIN users       u  ON u.id = rr.user_id
            JOIN word_entries we ON we.id = rr.entry_id
            WHERE rr.is_active = 1
              AND rr.next_run_at <= CURRENT_TIMESTAMP
            ORDER BY rr.next_run_at ASC
            LIMIT ?
        """, (limit,))
        rows = cur.fetchall()
        conn.close()
        return rows

    # Manual updates for reminder time are intentionally not supported; schedule is automatic.

    def list_user_words(self, user_id: int, limit: int = 100, offset: int = 0, search: str | None = None):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        if search:
            cur.execute(
                """SELECT id, word, created_at, next_reminder_at
                   FROM word_entries
                   WHERE user_id = ? AND word LIKE ?
                   ORDER BY created_at DESC
                   LIMIT ? OFFSET ?""",
                (user_id, f"%{search}%", limit, offset)
            )
        else:
            cur.execute(
                """SELECT id, word, created_at, next_reminder_at
                   FROM word_entries
                   WHERE user_id = ?
                   ORDER BY created_at DESC
                   LIMIT ? OFFSET ?""",
                (user_id, limit, offset)
            )

        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

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



